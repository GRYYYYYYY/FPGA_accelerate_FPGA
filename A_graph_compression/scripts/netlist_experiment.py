#!/usr/bin/env python3
"""Real placed-netlist routing integration with explicitly bound search domains."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'adapters')]
from canonical_graph import compare, validate
from heldout import encode_frozen, heldout_stats, object_digest
from import_vivado import read_export, sha256
from netlist import read_snapshot, routing_queries
from netlist_routing import route_batch, validate_routes
from packed_graph import PackedGraph, write_packed
from real_experiment import write_new
from row_cache import RowCache
from search_experiment import ExplicitCSR, LazyTemplates, edge_order
from template_codec import PreparedDecoder


class MemoizedTemplates(LazyTemplates):
    """Lazy decoded-row cache: stored rows are additional memory, not free compression."""
    def __init__(self, compact):
        super().__init__(compact, PreparedDecoder)
        self.cache = {}
        self.hits = self.misses = 0

    def neighbors(self, node):
        if node in self.cache:
            self.hits += 1
            return self.cache[node]
        result = super().neighbors(node)
        self.misses += 1
        self.cache[node] = result
        return result


def reference_trees(graph, snapshot, queries):
    adjacency = defaultdict(list)
    for edge in graph['edges']:
        adjacency[edge['src']].append(edge)
    routes = {}
    for q in queries:
        net = snapshot['nets'][q['net']]
        pips, nodes = set(net['pips']), set(net['nodes']) | {q['source'], *q['sinks']}
        reached, todo, edges = {q['source']}, [q['source']], []
        for src in todo:
            for edge in adjacency[src]:
                if edge['pip'] in pips and edge['dst'] in nodes and edge['dst'] not in reached:
                    reached.add(edge['dst']); todo.append(edge['dst']); edges.append(edge)
        if {e['pip'] for e in edges} != pips or not set(q['sinks']) <= reached:
            raise ValueError('Captured domain cannot reconstruct complete reference PIPs: '+q['net'])
        routes[q['net']] = {'source':q['source'], 'sinks':q['sinks'], 'nodes':sorted(reached),
                            'edges':edges, 'complete':True}
    result = {'routes':routes, 'status':'routed'}
    return result, validate_routes(graph, snapshot, queries, result)


def domain_paths(root, cfg, capture, config_digest, bank_meta, bank_digest):
    """Bind an independent domain to the original frozen training, without refitting."""
    raw_dir=root/cfg['output_dir']
    independent=capture.get('scope_kind')=='independent_endpoint_region'
    if bank_digest!=bank_meta['bank_file_sha256']:
        raise ValueError('Frozen bank changed')
    if independent:
        if capture['config_sha256']!=config_digest:
            raise ValueError('Independent capture/config changed')
        if bank_digest!=cfg['training_bank_sha256'] or bank_digest!=capture['training_bank_sha256']:
            raise ValueError('Independent domain uses a different frozen bank')
        return (root/capture['training']['path'],root/capture['graph']['path'],
                root/capture['source_selection']['path'],True)
    if config_digest!=bank_meta['config_sha256']:
        raise ValueError('Frozen bank/config changed')
    return raw_dir/'training.tsv',raw_dir/'reference_domain.tsv',root/cfg['reference_sources'],False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'configs/netlist_u280_v2.json')
    parser.add_argument('--bank-dir', type=Path, default=ROOT/'data/derived/netlist_u280_bank_20261022_v1')
    parser.add_argument('--max-nets', type=int, default=0, help='0 means every eligible net; positive is integration subset')
    parser.add_argument('--iterations', type=int, default=20)
    parser.add_argument('--max-expansions', type=int, default=200000)
    parser.add_argument('--present-cap',type=int,default=1048576)
    parser.add_argument('--template-provider', choices=['memoized','prepared'], default='memoized')
    parser.add_argument('--row-cache-capacity',type=int,default=None,
                        help='Identical LRU capacity for CSR and prepared templates; 0 disables both caches')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args(argv)
    if args.row_cache_capacity is not None and args.row_cache_capacity<0:
        raise ValueError('Negative row cache capacity')
    cfg = json.loads(args.config.read_text())
    bank_meta = json.loads((args.bank_dir/'manifest.json').read_text())
    bank_path = args.bank_dir/'bank.json'
    raw_dir = ROOT/cfg['output_dir']
    capture_path = raw_dir/'capture.json'
    capture = json.loads(capture_path.read_text())
    training_path,graph_path,sources_path,independent=domain_paths(
        ROOT,cfg,capture,sha256(args.config),bank_meta,sha256(bank_path))
    if sha256(training_path) != bank_meta['training_sha256']:
        raise ValueError('Training input changed')
    for entry in capture['files'].values():
        if sha256(ROOT/entry['path']) != entry['sha256']:
            raise ValueError('Captured input changed: '+entry['path'])
    bank = json.loads(bank_path.read_text())
    snapshot_path = ROOT/cfg['snapshot']
    if sha256(snapshot_path) != cfg['snapshot_sha256']:
        raise ValueError('Netlist snapshot changed')
    snapshot = read_snapshot(snapshot_path)
    graph = read_export(graph_path); validate(graph)
    if graph['metadata']['part'] != cfg['part'] or snapshot['metadata']['part'] != cfg['part'] or bank_meta['part'] != cfg['part']:
        raise ValueError('Device data mismatch')
    if set(graph['roots']) != set(sources_path.read_text().splitlines()):
        raise ValueError('Declared source domain differs')
    if set(graph['roots']) & set(bank['training_sources']):
        raise ValueError('Training/evaluation source overlap')
    queries = routing_queries(snapshot)
    if queries != json.loads((ROOT/cfg['queries']).read_text()):
        raise ValueError('Preregistered net selection changed')
    if args.max_nets < 0:
        raise ValueError('Negative net count')
    total = len(queries)
    queries = queries[:args.max_nets] if args.max_nets else queries
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = args.output_dir or ROOT/'data/derived'/('netlist_'+stamp)
    out.mkdir(parents=True, exist_ok=False)
    timings = {}
    def timed(name, action):
        start = perf_counter(); value = action(); timings[name] = (perf_counter()-start)*1000
        return value
    if independent:
        # Reference containment is diagnostic only: never extend or filter the
        # independently selected resource graph to reproduce a known path.
        available_pips=set(graph['pips'])
        missing={q['net']:sorted(set(snapshot['nets'][q['net']]['pips'])-available_pips) for q in queries}
        reference_check={'status':'external_baseline_only','nets_with_reference_pips_outside_domain':
                         {net:pips for net,pips in missing.items() if pips}}
        write_new(out/'reference_availability.json',reference_check)
    else:
        reference, reference_check = reference_trees(graph, snapshot, queries)
        write_new(out/'reference_routes.json', reference)
    write_new(out/'queries.json', queries)
    compact = timed('exceptions_build', lambda: encode_frozen(graph, bank))
    coverage = heldout_stats(graph, compact)
    write_new(out/'coverage.json', coverage)
    layouts = {}
    for mode in ['csr','compact']:
        path = out/(mode+'.agr')
        layouts[mode] = timed(mode+'_serialize', lambda:write_packed(path, graph, mode, bank if mode=='compact' else None))
        reader = PackedGraph(path)
        if not compare(graph, reader.materialize())['equal']:
            raise ValueError('Packed canonical roundtrip differs')
    providers = {
        'csr':timed('csr_initialize', lambda:ExplicitCSR(graph)),
        'templates':timed('templates_initialize', lambda:MemoizedTemplates(compact)
                         if args.template_provider=='memoized' and args.row_cache_capacity is None
                         else LazyTemplates(compact,PreparedDecoder))}
    if args.row_cache_capacity is not None:
        providers={name:RowCache(provider,args.row_cache_capacity) for name,provider in providers.items()}
    checks, results = {}, {}
    for name, provider in providers.items():
        def progress(*values):
            print('ROUTING_PROGRESS',name,*values,flush=True)
        result = route_batch(provider,snapshot,queries,args.iterations,args.max_expansions,
                             full_trace=False,progress=progress,present_cap=args.present_cap)
        write_new(out/(name+'_routes.json'), result)
        checks[name] = validate_routes(graph,snapshot,queries,result)
        results[name] = result
    left = {k:v for k,v in results['csr'].items() if k != 'wall_ms'}
    right = {k:v for k,v in results['templates'].items() if k != 'wall_ms'}
    same = left == right
    if not same:
        raise ValueError('Routing providers differ in paths, occupancy, costs or search outcomes')
    provider = providers['templates']
    report = {'status':'equivalent', 'created_utc':datetime.now(timezone.utc).isoformat(),
              'eligible_nets':total, 'selected_nets':len(queries),'scope':cfg.get('domain_stage',cfg.get('scope')),
              'template_provider':args.template_provider, 'checks':checks, 'reference_check':reference_check,
              'shared_row_cache_capacity':args.row_cache_capacity,
              'shared_cache_statistics':{name:provider.statistics() for name,provider in providers.items()
                                         if isinstance(provider,RowCache)},
              'provider_results_identical_except_time':same, 'layouts':layouts, 'preparation_ms':timings,
              'route_wall_ms':{k:v['wall_ms'] for k,v in results.items()},
              'iterations':len(results['csr']['iterations']), 'frozen_bank_sha256':object_digest(bank),
              'route_settings':{'max_iterations':args.iterations,'max_expansions':args.max_expansions,
                                'present_cap':args.present_cap},
              'cache':{'rows':len(provider.cache),'edges':sum(map(len,provider.cache.values())),
                       'hits':provider.hits,'misses':provider.misses} if hasattr(provider,'cache') else None,
              'limitations':[('Independent endpoint-defined regional graph; exterior adjacency remains unknown.' if independent else
                  'Reference-conditioned partial graph; unknown branches are recorded, not physical sinks.'),
                  'Python hop/congestion router; no calibrated delays, no global path optimality claim.',
                  'Memoized rows are additional decoded host allocations; no compressed-memory advantage inferred.',
                  'One batch per provider, no statistical performance conclusion. Vivado rewrite/DRC/timing checked separately.']}
    report['inputs'] = {'capture':sha256(capture_path),'snapshot':sha256(snapshot_path),'config':sha256(args.config)}
    report['code_sha256']={str(p.relative_to(ROOT)):sha256(p) for p in
        [Path(__file__),ROOT/'src/netlist_routing.py',ROOT/'src/search_experiment.py',
         ROOT/'src/template_codec.py',ROOT/'src/row_cache.py',ROOT/'scripts/real_experiment.py']}
    report['artifacts'] = {p.name:sha256(p) for p in out.iterdir()}
    write_new(out/'report.json',report)
    print(json.dumps({'report':str(out/'report.json'),'checks':checks,'route_wall_ms':report['route_wall_ms']},indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
