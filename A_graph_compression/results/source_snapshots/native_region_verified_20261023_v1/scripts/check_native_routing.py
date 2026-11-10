#!/usr/bin/env python3
"""Compare complete native canonical routing to frozen audited Python results."""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from packed_graph import PackedGraph
from import_vivado import sha256
from real_experiment import write_new


def check_mode(directory,mode,plan,reference):
    inputs=plan['inputs'][mode];fixture=Path(inputs['directory'])
    manifest=json.loads((fixture/'manifest.json').read_text())
    if sha256(fixture/'manifest.json')!=inputs['manifest_sha256']:raise ValueError('Input manifest changed')
    for name,digest in manifest['files'].items():
        if sha256(Path(name))!=digest:raise ValueError('Frozen fixture evidence changed: '+name)
    for name,digest in manifest['outputs'].items():
        if sha256(fixture/name)!=digest:raise ValueError('Fixture output changed')
    receipt_path=directory/(mode+'_receipt.json');receipt=json.loads(receipt_path.read_text())
    raw_path=directory/(mode+'_routes.json');log_path=directory/(mode+'.log')
    if receipt['exit_code'] or sha256(raw_path)!=receipt['output_sha256'] or sha256(log_path)!=receipt['log_sha256']:
        raise ValueError('Native execution failed or result changed')
    raw=json.loads(raw_path.read_text());image=PackedGraph(inputs['image'])
    queries=json.loads((fixture/'queries.json').read_text());net_names={q['net_id']:q['net'] for q in queries}
    names=[image.text(n[0]) for n in image.nodes]
    def node(n):return names[n]
    @lru_cache(maxsize=4096)
    def row(n):return set(image.numeric_neighbors(n))
    def edge(record):
        if len(record)!=8:raise ValueError('Malformed native edge')
        src,dst,tile,pip,up,down,attr,direction=record
        if tuple(record[1:]) not in row(src):raise ValueError('Native edge/attribute absent from image')
        tn=image.text(image.tiles[tile][0]);un=tn+'/'+image.text(up);dn=tn+'/'+image.text(down)
        sw,dw=(dn,un) if direction else (un,dn)
        return {'src':node(src),'dst':node(dst),'pip':tn+'/'+image.text(pip),
                'src_wire':sw,'dst_wire':dw,'direction':'reverse' if direction else 'forward'}
    if raw['status']!=reference['status']:raise ValueError('Native final status differs')
    converted={}
    for r in raw['routes']:
        name=net_names[r['net_id']]
        if name in converted:raise ValueError('Duplicate native net route')
        converted[name]={'source':node(r['source']),'sinks':list(map(node,r['sinks'])),
            'nodes':list(map(node,r['nodes'])),'edges':list(map(edge,r['edges'])),'complete':r['complete']}
    if converted!=reference['routes']:raise ValueError('Native final canonical trees differ')
    history={node(n):v for n,v in raw['history']}
    if history!=reference['history']:raise ValueError('Native negotiated history differs')
    if len(raw['iterations'])!=len(reference['iterations']):raise ValueError('Native round count differs')
    connections=0
    for index,(actual,expected) in enumerate(zip(raw['iterations'],reference['iterations'])):
        if actual['present_factor']!=expected['present_factor']:raise ValueError('Present factor differs')
        conflicts={node(n):sorted(net_names[v] for v in users) for n,users in actual['conflicts']}
        if conflicts!=expected['conflicts']:raise ValueError('Round conflicts differ: '+str(index))
        if sorted(net_names[n] for n in actual['incomplete_nets'])!=expected['incomplete_nets']:
            raise ValueError('Round incomplete nets differ')
        if sorted(map(node,actual['unknown_sources']))!=expected['unknown_sources']:raise ValueError('Round unknown sources differ')
        if len(actual['outcomes'])!=len(queries) or len(expected['outcomes'])!=len(queries):raise ValueError('Outcome domain differs')
        for query,outcome,old in zip(queries,actual['outcomes'],expected['outcomes']):
            targets=sorted(query['sinks'])
            if old['net']!=query['net'] or len(outcome)!=len(targets) or len(old['connections'])!=len(targets):
                raise ValueError('Connection/query domain differs')
            for target,c,e in zip(targets,outcome,old['connections']):
                if node(target)!=e['target']:raise ValueError('Connection target differs')
                for key in ('status','cost','expanded','examined','fetched','blocked_edges'):
                    if c[key]!=e[key]:raise ValueError(f'Connection {key} differs: round {index}, {query["net"]}, {e["target"]}')
                if len(c['path'])!=e['path_length'] or len(c['unknown_sources'])!=e['unknown_count']:
                    raise ValueError('Connection path/unknown count differs')
                # Reference full_trace=False omits connection paths; validate
                # native path records against the image without claiming equality.
                path=list(map(edge,c['path']))
                if path and (path[-1]['dst']!=node(target) or any(a['dst']!=b['src'] for a,b in zip(path,path[1:]))):
                    raise ValueError('Broken native connection path')
                connections+=1
    return {'status':'matches_audited_python_canonical_routing','nets':len(converted),
        'rounds':len(raw['iterations']),'connections_checked':connections,
        'pips':sum(len(r['edges']) for r in converted.values()),
        'measurements':{k:raw[k] for k in ('preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses')},
        'artifacts':{str(p):sha256(p) for p in (receipt_path,raw_path,log_path,fixture/'manifest.json')}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path)
    p.add_argument('--mode',nargs='+',choices=['csr','compact'],default=['csr','compact'])
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plan=json.loads((a.experiment/'plan.json').read_text())
    for name,digest in plan['code_and_binary'].items():
        if sha256(Path(name))!=digest:raise ValueError('Frozen native code changed')
    base=ROOT/'data/derived/region_all_nets_cap8_20261022_v1';audit=json.loads((base/'report.json').read_text())
    reference_path=base/'csr_routes.json'
    if sha256(reference_path)!=audit['artifacts']['csr_routes.json']:raise ValueError('Audited Python route changed')
    reference=json.loads(reference_path.read_text())
    results={mode:check_mode(a.experiment,mode,plan,reference) for mode in a.mode}
    report={'status':'verified_canonical_native_routing','modes':results,
        'plan_sha256':sha256(a.experiment/'plan.json'),'reference_sha256':sha256(reference_path),
        'limitations':['Canonical-node workload only: its old physical candidate failed site legality.',
            'Final trees, all round states and retained Python counters compared; omitted per-connection reference paths cannot be compared.',
            'Single runs with concurrent host workload; not statistical performance or whole physical/site router validation.']}
    write_new(a.output,report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
