#!/usr/bin/env python3
"""Verify actual complete randomized routing with raw-path edge retention."""
import argparse
import hashlib
import json
from pathlib import Path
from retained_edges_routes_transform import routes,search

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.bundle.resolve();require(not a.output.exists(),'Existing audit')
    root=Path(__file__).resolve().parents[1];base=root/'data/derived/round_control_router_20261024_v1'
    plan=json.loads((out/'plan.json').read_text());state=json.loads((out/'run_state.json').read_text())
    require(state['status']=='complete' and state['exit_code']==0 and state['full_router_differential_verified'],'Integration not complete')
    require(state['plan_sha256']==sha(out/'plan.json') and state['binary_sha256']==sha(out/'differential') and state['log_sha256']==sha(out/'differential.log'),'Run provenance changed')
    for path,h in plan['files'].items():require(sha(path)==h,'Changed integration input '+path)
    changes={'site_routes.hpp':routes,'snapshot_test_routes.hpp':routes,'search_kernel_route_adapter.hpp':search}
    for source in (base/'source').iterdir():
        expected=changes[source.name](source.read_text()) if source.name in changes else source.read_text()
        require((out/'source'/source.name).read_text()==expected,'Unexpected source derivation '+source.name)
    for name in ['search_retained_edges.hpp','search_retained_edges_top.cpp']:
        require(sha(out/'source'/name)==sha(root/'hardware/vitis'/name),'Wrong edge core')
    require(sha(out/'source/retained_edges_adapter.hpp')==sha(root/'src/native/retained_edges_adapter.hpp'),'Wrong edge adapter')
    command=json.loads((out/'compile_command.json').read_text())
    require(str(out/'source/driver.cpp') in command and str(out/'edge_top.o') in command and '-fsanitize=address,undefined' in command,'Missing actual sanitized edge link')
    require(state['command']==['taskset','-c','119',str(out/'differential'),str(out/'source/sites.txt')],'Wrong differential invocation')
    expected=('ROUND_CONTROL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 '
              'node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nROUND_CONTROL_ROUTE_FULL_RESULTS_PASS\n')
    require((out/'differential.log').read_text()==expected,'Incomplete semantic comparison')
    files=dict(plan['files'])
    for path in [out/'plan.json',out/'run_state.json',out/'differential',out/'differential.log',Path(__file__).resolve(),root/'scripts/retained_edges_routes_transform.py']:
        files[str(path)]=sha(path)
    result=dict(status='retained_edges_full_random_router_differential_verified_real_workload_pending',files=files,cases=400,searches=4938,hardware_executed=False,full_real_workload_executed=False,limitations=plan['limitations'])
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['status'])
if __name__=='__main__':main()
