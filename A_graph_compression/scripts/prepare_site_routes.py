#!/usr/bin/env python3
"""Independently validate site-aware results before serializing FIXED_ROUTE."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'adapters'), str(ROOT/'scripts')]
from import_vivado import read_export, sha256
from netlist import read_snapshot
from lut_equation import truth_table, MASK
from site_netlist_routing import validate_site_routes
from prepare_netlist_routes import directed_route


def checked_json(path, bindings=None):
    path = path.resolve()
    if bindings is not None and bindings.get(str(path)) != sha256(path):
        raise ValueError('Unbound or changed input: '+str(path))
    return json.loads(path.read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('experiment', type=Path)
    p.add_argument('--base', type=Path, default=ROOT/'data/derived/region_all_nets_cap8_20261022_v1')
    p.add_argument('--config', type=Path, default=ROOT/'configs/region_u280_v1.json')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    plan = checked_json(a.experiment/'plan.json')
    for name, digest in plan['files'].items():
        if sha256(Path(name)) != digest:
            raise ValueError('Frozen site experiment changed: '+name)
    cfg = checked_json(a.config, plan['files'])
    capture_path = ROOT/cfg['output_dir']/'capture.json'
    capture = checked_json(capture_path, plan['files'])
    snapshot_path = ROOT/cfg['snapshot']
    checked_json(a.base/'fixed_site_state_v2.json', plan['files'])
    audit = checked_json(a.base/'report.json')
    for path, key in ((a.config, 'config'), (capture_path, 'capture'), (snapshot_path, 'snapshot')):
        if sha256(path) != audit['inputs'][key]:
            raise ValueError('Base audit input changed: '+str(path))
    for item in capture['files'].values():
        if sha256(ROOT/item['path']) != item['sha256']:
            raise ValueError('Capture changed: '+item['path'])
    query_path = a.base/'queries.json'
    if sha256(query_path) != audit['artifacts']['queries.json']:
        raise ValueError('Frozen queries changed')
    queries = checked_json(query_path)
    if len(queries) != plan['total_frozen_queries']:
        raise ValueError('Frozen query count changed')
    if plan['probe_net'] is not None:
        queries = [q for q in queries if q['net'] == plan['probe_net']]
    if not queries or len(queries) != plan['selected_queries']:
        raise ValueError('Selected query count differs')
    fixed = checked_json(a.base/'fixed_site_state_v2.json', plan['files'])
    for path, digest in fixed['files'].items():
        if sha256(ROOT/path) != digest:
            raise ValueError('Fixed-state evidence changed: '+path)
    proofs = []
    for version in (1, 2):
        path = ROOT/f'data/netlist/lut_route_probes_20261023_v{version}/verification.json'
        proof = checked_json(path, plan['files'])
        for name, digest in proof['files'].items():
            if sha256(path.parent/name) != digest:
                raise ValueError('Probe evidence changed: '+name)
        proofs.append(proof)
    equations = {c['pip']: c for c in proofs[0]['checks']}
    requirements = {}
    for check in proofs[1]['checks']:
        source = equations[check['pip']]
        bel = source['bel']; signals = [bel+'/O6']; values = []
        if check['output_mux']:
            mux = check['output_mux'].split(':')[0]
            signals.append(mux+'/OUT'); values.append((mux, 'D6'))
        requirements[check['pip']] = {
            'signal_resources': signals,
            'configuration_bits': [(bel+'/INIT', MASK, truth_table(source['expected_equation']))],
            'configuration_values': values}
    if len(requirements) != plan['verified_pseudo_instances']:
        raise ValueError('Verified-instance coverage differs')
    bits = [r['configuration_bits'] for r in fixed['fixed_functional_luts']]
    bits.extend(r['configuration_bits'] for r in fixed['unoccupied_constant_configurations']
                if r['status'] == 'isolated_vivado_conflict_verified')
    source_path = a.experiment/'routes.json'
    result = checked_json(source_path)
    report_path = a.experiment/'report.json'
    report = checked_json(report_path)
    if result['status'] != 'routed' or report['status'] != 'routed':
        raise ValueError('Only completed routed batches may be serialized')
    graph_path = ROOT/capture['graph']['path']
    validation = validate_site_routes(read_export(graph_path), read_snapshot(snapshot_path),
                                      queries, result, requirements, fixed_bits=bits)
    if not validation['all_nets_site_compatible'] or not validation['canonical']['all_nets_routed_without_conflicts']:
        raise ValueError('Independent route validation failed')
    if validation != report['validation']:
        raise ValueError('Published validation differs from recomputed validation')
    lines = ['meta\tschema\tcanonical_routes_v1',
             'meta\tinput_sha256\t'+sha256(source_path),
             'meta\tgraph_sha256\t'+sha256(graph_path),
             'meta\treport_sha256\t'+sha256(report_path),
             'meta\tplan_sha256\t'+sha256(a.experiment/'plan.json'),
             'meta\tsite_scope\ttested_instances_only_physical_validation_required']
    for name, route in sorted(result['routes'].items()):
        if any(c in name for c in '\t\n\r'):
            raise ValueError('Control character in net name')
        lines.append('\t'.join(['net', name, directed_route(route)]))
        lines.extend('\t'.join(['node', name, n]) for n in sorted(route['nodes']))
        lines.extend('\t'.join(['pip', name, n]) for n in sorted({e['pip'] for e in route['edges']}))
    lines.append('complete\t'+str(len(result['routes'])))
    with a.output.open('x') as stream:
        stream.write('\n'.join(lines)+'\n')
    print(json.dumps({'output':str(a.output), 'sha256':sha256(a.output),
                      'selected_queries':len(queries), 'validation':validation}, indent=2))


if __name__ == '__main__':
    main()
