#!/usr/bin/env python3
"""Build the already differentially verified integrated sink-loop real router."""
import json
import os
from pathlib import Path
import subprocess
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'data/derived/net_router_20261025_v1';base=ROOT/'data/derived/retained_edges_integration_20261024_v1'
    evidence=ROOT/'results/net_component_20261025_v1.json';proof=json.loads(evidence.read_text())
    require(proof['status']=='net_full_negotiation_intermediate_differential_verified_real_workload_pending','Missing integrated differential')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed verified source '+p)
    source=out/'source';cmd=json.loads((base/'compile_router.receipt.json').read_text())['command']
    cmd=[x.replace(str(base/'source'),str(source)).replace(str(base/'router'),str(out/'router')) for x in cmd];cmd[2]='125'
    for mode in ['csr','compact']:cmd.insert(cmd.index('-o'),str(out/('sink_'+mode+'_regular.o')))
    jobs=[]
    for mode,name in [(0,'csr'),(1,'compact')]:
        jobs.append(('compile_'+name+'_regular',['taskset','-c','125','g++','-std=c++14','-O2','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas','-DSEARCH_SINK_LOOP_OBSERVE=1','-DSEARCH_GRAPH_MODE='+str(mode),'-DSEARCH_TOP_NAME=search_net_'+name,'-c',str(source/'search_net_observed_top.cpp'),'-o',str(out/('sink_'+name+'_regular.o'))]))
    jobs.append(('compile_router',cmd));files=dict(proof['files'])
    for p in [evidence,Path(__file__).resolve()]:files[str(p)]=digest(p)
    for x in cmd:
        if x.endswith('.o') and Path(x).exists():files[x]=digest(x)
    plan=out/'regular_build_plan.json'
    with plan.open('x') as f:json.dump(dict(owner_pid=os.getpid(),files=files,commands=[c for _,c in jobs]),f,indent=2);f.write('\n')
    for name,command in jobs:
        with (out/(name+'.log')).open('x') as f:code=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
        with (out/(name+'.receipt.json')).open('x') as f:json.dump(dict(command=command,exit_code=code,log_sha256=digest(out/(name+'.log')),plan_sha256=digest(plan)),f,indent=2);f.write('\n')
        require(code==0,'Compile failed '+name);print(name,'PASS',flush=True)
    for p,h in files.items():require(digest(p)==h,'Changed regular input '+p)
    with (out/'regular_build_complete.json').open('x') as f:json.dump(dict(status='compiled',plan_sha256=digest(plan),binary_sha256=digest(out/'router'),objects={str(out/('sink_'+m+'_regular.o')):digest(out/('sink_'+m+'_regular.o')) for m in ['csr','compact']}),f,indent=2);f.write('\n')
if __name__=='__main__':main()
