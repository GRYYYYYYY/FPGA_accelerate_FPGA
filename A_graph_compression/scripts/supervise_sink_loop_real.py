#!/usr/bin/env python3
"""Finish the authorized full experiment after the original regular build succeeds."""
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def identity(pid):
    p=Path('/proc')/str(pid);return ((p/'stat').read_text().rsplit(')',1)[1].split()[19],(p/'cmdline').read_bytes().decode())
def main():
    build=ROOT/'data/derived/sink_loop_router_20261025_v1';folder=build/'real_supervisor';folder.mkdir(exist_ok=False)
    plan=json.loads((build/'regular_build_plan.json').read_text());pid=plan['owner_pid'];original=identity(pid) if not (build/'regular_build_complete.json').exists() else None
    if original:require('compile_sink_loop_router.py' in original[1],'Wrong build owner')
    deps=[ROOT/'scripts'/name for name in ['prepare_sink_loop_real.py','sink_loop_router_pipeline.py','check_sink_loop_router.py','check_vitis_kernel.py']]+[Path(__file__).resolve(),build/'regular_build_plan.json']
    files={str(p):digest(p) for p in deps};(folder/'plan.json').write_text(json.dumps(dict(files=files,build_owner=pid,identity=original),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='await_original_regular_build')
    def save():
        p=folder/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(folder/'state.json')
    def run(phase,cmd):
        for p,h in files.items():require(digest(p)==h,'Changed continuation '+p)
        state['stage']=phase;save()
        with (folder/(phase+'.log')).open('x') as f:
            child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (folder/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(folder/(phase+'.log'))),indent=2)+'\n');require(code==0,'Continuation failed '+phase)
    save()
    try:
        while not (build/'regular_build_complete.json').exists():
            require(original is not None and identity(pid)==original,'Original build missing; reconcile without restarting');time.sleep(10)
        run('prepare_real',['python3',str(ROOT/'scripts/prepare_sink_loop_real.py')])
        run('full_real',['python3',str(ROOT/'scripts/sink_loop_router_pipeline.py'),'--bundle',str(ROOT/'data/derived/sink_loop_router_full_20261025_v1'),'--output',str(ROOT/'results/sink_loop_router_audit_20261025_v1.json')])
        state.update(status='complete',stage='full_real_independently_audited');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
