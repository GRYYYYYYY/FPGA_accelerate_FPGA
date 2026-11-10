#!/usr/bin/env python3
"""Run site-aware routing on the unchanged regional graph; scope stays explicit."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import read_export,sha256
from netlist import read_snapshot
from search_experiment import ExplicitCSR
from site_netlist_routing import route_batch,validate_site_routes
from lut_equation import truth_table,MASK
from real_experiment import write_new


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,default=ROOT/'data/derived/region_all_nets_cap8_20261022_v1')
    p.add_argument('--config',type=Path,default=ROOT/'configs/region_u280_v1.json')
    p.add_argument('--net',help='Explicit integration probe only; default retains all frozen queries')
    p.add_argument('--iterations',type=int,default=80);p.add_argument('--max-expansions',type=int,default=200000)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    audit=json.loads((a.experiment/'report.json').read_text());cfg=json.loads(a.config.read_text())
    capture_path=ROOT/cfg['output_dir']/'capture.json';capture=json.loads(capture_path.read_text())
    snapshot_path=ROOT/cfg['snapshot']
    for path,key in ((a.config,'config'),(capture_path,'capture'),(snapshot_path,'snapshot')):
        if sha256(path)!=audit['inputs'][key]:raise ValueError('Audited input changed')
    for entry in capture['files'].values():
        if sha256(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Capture changed')
    if sha256(a.experiment/'queries.json')!=audit['artifacts']['queries.json']:raise ValueError('Queries changed')
    queries=json.loads((a.experiment/'queries.json').read_text());total=len(queries)
    if a.net:
        queries=[q for q in queries if q['net']==a.net]
        if len(queries)!=1:raise ValueError('Probe query missing/ambiguous')
    fixed_path=a.experiment/'fixed_site_state_v2.json'
    fixed=json.loads(fixed_path.read_text())
    for path,digest in fixed['files'].items():
        if sha256(ROOT/path)!=digest:raise ValueError('Fixed-state input changed')
    proof_path=ROOT/'data/netlist/lut_route_probes_20261023_v2/verification.json'
    proof=json.loads(proof_path.read_text())
    for name,digest in proof['files'].items():
        if sha256(proof_path.parent/name)!=digest:raise ValueError('Probe evidence changed')
    # Only tested physical LUT instances admitted; other pseudo PIPs remain unknown.
    requirements={}
    equation_proof_path=ROOT/'data/netlist/lut_route_probes_20261023_v1/verification.json'
    equation_proof=json.loads(equation_proof_path.read_text())
    for name,digest in equation_proof['files'].items():
        if sha256(equation_proof_path.parent/name)!=digest:raise ValueError('Equation probe evidence changed')
    equation_checks={x['pip']:x for x in equation_proof['checks']}
    for check in proof['checks']:
        # Physical BEL identity comes from the equation probe, not coordinate guessing.
        source=equation_checks[check['pip']]
        bel=source['bel'];signals=[bel+'/O6'];values=[]
        if check['output_mux']:
            mux=check['output_mux'].split(':')[0];signals.append(mux+'/OUT');values.append((mux,'D6'))
        requirements[check['pip']]={'signal_resources':signals,
            'configuration_bits':[(bel+'/INIT',MASK,truth_table(source['expected_equation']))],
            'configuration_values':values}
    bits=[r['configuration_bits'] for r in fixed['fixed_functional_luts']]
    bits.extend(r['configuration_bits'] for r in fixed['unoccupied_constant_configurations'] if r['status']=='isolated_vivado_conflict_verified')
    a.output.mkdir(parents=True,exist_ok=False)
    write_new(a.output/'plan.json',{'total_frozen_queries':total,'selected_queries':len(queries),
        'probe_net':a.net,'verified_pseudo_instances':len(requirements),'max_expansions':a.max_expansions,
        'iterations':a.iterations,'files':{str(x):sha256(x) for x in (a.config,capture_path,snapshot_path,fixed_path,proof_path,equation_proof_path,Path(__file__),ROOT/'src/site_search.py',ROOT/'src/site_netlist_routing.py',ROOT/'src/site_resources.py',ROOT/'src/lut_equation.py')}})
    print('SITE_ROUTER_LOADING_COMPLETE_REGION',flush=True)
    graph=read_export(ROOT/capture['graph']['path']);snapshot=read_snapshot(snapshot_path)
    provider=ExplicitCSR(graph)
    print('SITE_ROUTER_BEGIN',len(queries),flush=True)
    result=route_batch(provider,snapshot,queries,requirements,fixed_bits=bits,
        max_iterations=a.iterations,max_expansions=a.max_expansions,
        progress=lambda *x:print('SITE_ROUTING_PROGRESS',*x,flush=True))
    write_new(a.output/'routes.json',result)
    validation=validate_site_routes(graph,snapshot,queries,result,requirements,fixed_bits=bits)
    write_new(a.output/'report.json',{'status':result['status'],'validation':validation,
        'scope':'Full unchanged independent regional graph; explicit tested-instance site semantics only; unknown pseudo demands retained as unknown.',
        'total_frozen_queries':total,'selected_queries':len(queries),'full_goal_complete':False,
        'limitations':['Partial site semantics integration, not complete hardware/resource legality or statistical performance.',
                       'Protected intra-site ownership coverage still incomplete; Vivado validation remains required.']})
    print('SITE_ROUTER_COMPLETE',result['status'],flush=True)


if __name__=='__main__':main()
