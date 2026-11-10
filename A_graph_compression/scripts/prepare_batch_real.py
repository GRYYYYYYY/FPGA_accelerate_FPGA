#!/usr/bin/env python3
"""Bind the verified randomized integration and compiled real router for full runs."""
import json
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'data/derived/batch_router_20261025_v1'
    evidence=ROOT/'results/batch_component_20261025_v1.json'
    proof=json.loads(evidence.read_text())
    require(proof['status']=='batch_full_negotiation_intermediate_differential_verified_real_workload_pending','Randomized integration not verified')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed verified integration '+p)
    build=json.loads((source/'regular_build_complete.json').read_text())
    require(build['status']=='compiled' and digest(source/'regular_build_plan.json')==build['plan_sha256'] and digest(source/'router')==build['binary_sha256'],'Wrong compiled router')
    build_plan=json.loads((source/'regular_build_plan.json').read_text())
    for p,h in build_plan['files'].items():require(digest(p)==h,'Changed regular input '+p)
    for name,cmd in zip(['compile_csr_regular','compile_compact_regular','compile_router'],build_plan['commands']):
        r=json.loads((source/(name+'.receipt.json')).read_text())
        require(r['exit_code']==0 and r['command']==cmd and r['log_sha256']==digest(source/(name+'.log')) and r['plan_sha256']==build['plan_sha256'],'Failed build '+name)
    base=ROOT/'data/derived/net_router_full_20261025_v1';prior=json.loads((base/'plan.json').read_text())
    out=ROOT/'data/derived/batch_router_full_20261025_v1';out.mkdir(exist_ok=False)
    bindings=dict(proof['files']);bindings.update(build_plan['files'])
    for p in [evidence,source/'regular_build_complete.json',source/'regular_build_plan.json',source/'router',ROOT/'scripts/batch_router_pipeline.py',ROOT/'scripts/check_batch_router.py',Path(__file__).resolve()]:bindings[str(p)]=digest(p)
    limitations=['CPU execution of the actual integrated whole-batch top; no device proof.','One top executes all-net, all-sink, round termination and history advancement. CPU-only callbacks reconstruct complete observations and are excluded from synthesis.','The batch control algorithm is internal, but HLS/RTL/physical/platform execution remain separate evidence. No global or cross-stage rollback.','Full physical special-resource semantics, physical timing and board measurements remain incomplete.']
    plan=dict(files=bindings,inputs=prior['inputs'],references=prior['references'],prior_bundle=str(base),binary=str(source/'router'),jobs=prior['jobs'],limitations=limitations)
    report=dict(status='batch_full_search_cpu_differential_verified_full_workload_pending',files=bindings,artifacts={},limitations=limitations)
    for name,value in [('plan.json',plan),('report.json',report),('prepare_state.json',dict(status='complete'))]:(out/name).write_text(json.dumps(value,indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
