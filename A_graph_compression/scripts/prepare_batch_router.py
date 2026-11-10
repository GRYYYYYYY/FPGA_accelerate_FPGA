#!/usr/bin/env python3
"""One actual top executes the entire negotiated batch; compare every intermediate."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
from batch_router_transform import adapt
ROOT=Path(__file__).resolve().parents[1]
def main():
    base=ROOT/'data/derived/net_router_20261025_v1';evidence=ROOT/'results/net_component_20261025_v1.json';proof=json.loads(evidence.read_text())
    for p,h in proof['files'].items():require(digest(p)==h,'Changed complete net differential '+p)
    out=ROOT/'data/derived/batch_router_20261025_v1';out.mkdir(exist_ok=False);source=out/'source';shutil.copytree(base/'source',source)
    for name in ['search_round_control.hpp']:
        shutil.copyfile(ROOT/'hardware/vitis'/name,source/name)
    adapt(source)
    command=json.loads((base/'plan.json').read_text())['command'];command=[x.replace(str(base/'source'),str(source)).replace(str(base/'differential'),str(out/'differential')).replace(str(base/'sink_csr.o'),str(out/'batch_csr.o')).replace(str(base/'sink_compact.o'),str(out/'batch_compact.o')) for x in command]
    command[2]='125'
    files=dict(proof['files'])
    for p in [evidence,ROOT/'hardware/vitis/search_batch_observed_top.cpp',ROOT/'hardware/vitis/search_round_control.hpp',ROOT/'scripts/batch_router_transform.py',Path(__file__).resolve()]:files[str(p)]=digest(p)
    generated={str(p):digest(p) for p in source.iterdir()};(out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated,command=command),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='prepare')
    def save():
        q=out/'state.tmp';q.write_text(json.dumps(state,indent=2)+'\n');q.replace(out/'state.json')
    def run(phase,cmd):
        state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
        with (out/(phase+'.log')).open('x') as f:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n');require(code==0,'Batch routing phase failed '+phase);print(phase,'PASS',flush=True)
    save()
    try:
        for mode,name in [(0,'csr'),(1,'compact')]:run('compile_'+name,['taskset','-c','125','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_SINK_LOOP_OBSERVE=1','-DSEARCH_GRAPH_MODE='+str(mode),'-DSEARCH_TOP_NAME=search_batch_'+name,'-c',str(source/'search_batch_observed_top.cpp'),'-o',str(out/('batch_'+name+'.o'))])
        run('compile_differential',command)
        run('differential',['taskset','-c','125',str(out/'differential'),str(source/'sites.txt')])
        expected='ROUND_CONTROL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nROUND_CONTROL_ROUTE_FULL_RESULTS_PASS\n'
        require((out/'differential.log').read_text()==expected,'Different complete negotiated scope')
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed batch integration '+p)
        state.update(status='complete',stage='all_net_round_intermediate_differential_verified');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
