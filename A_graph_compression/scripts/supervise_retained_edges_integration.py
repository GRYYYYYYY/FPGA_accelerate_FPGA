#!/usr/bin/env python3
"""Observe the original randomized run, audit it, and advance the real experiment once."""
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def identity(pid):
    p=Path('/proc')/str(pid)
    return ((p/'stat').read_text().rsplit(')',1)[1].split()[19],(p/'cmdline').read_bytes().decode())
def main():
    bundle=ROOT/'data/derived/retained_edges_integration_20261024_v1'
    folder=bundle/'real_supervisor';folder.mkdir(exist_ok=False)
    original=json.loads((bundle/'run_state.json').read_text());pid=original['owner_pid']
    observed=identity(pid) if original['status']=='running' else None
    if observed:require('run_retained_edges_integration.py' in observed[1],'Wrong original owner')
    names=['check_retained_edges_integration.py','prepare_retained_edges_real.py','retained_edges_router_pipeline.py','check_retained_edges_router.py','retained_edges_routes_transform.py','check_vitis_kernel.py']
    files={str(ROOT/'scripts'/n):digest(ROOT/'scripts'/n) for n in names}
    files[str(Path(__file__).resolve())]=digest(__file__)
    (folder/'plan.json').write_text(json.dumps(dict(files=files,original_owner=pid,original_identity=observed),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='await_original_randomized_run')
    def save():
        p=folder/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(folder/'state.json')
    def run(stage,command):
        for p,h in files.items():require(digest(p)==h,'Changed continuation input '+p)
        state['stage']=stage;save()
        with (folder/(stage+'.log')).open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;save();code=child.wait()
        (folder/(stage+'.receipt.json')).write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(folder/(stage+'.log'))),indent=2)+'\n')
        require(code==0,'Continuation failed '+stage)
    save()
    try:
        while True:
            current=json.loads((bundle/'run_state.json').read_text())
            require(current['owner_pid']==pid,'Original owner changed')
            if current['status']!='running':break
            require(observed is not None and identity(pid)==observed,'Original owner missing; reconcile instead of restarting')
            time.sleep(10)
        require(current['status']=='complete','Original randomized comparison failed')
        run('audit_random',['python3',str(ROOT/'scripts/check_retained_edges_integration.py'),'--bundle',str(bundle),'--output',str(ROOT/'results/retained_edges_component_20261024_v1.json')])
        run('prepare_real',['python3',str(ROOT/'scripts/prepare_retained_edges_real.py')])
        run('full_real',['python3',str(ROOT/'scripts/retained_edges_router_pipeline.py'),'--bundle',str(ROOT/'data/derived/retained_edges_router_20261024_v1'),'--output',str(ROOT/'results/retained_edges_router_audit_20261024_v1.json')])
        state.update(status='complete',stage='full_real_independently_audited');save()
    except BaseException as error:
        state.update(status='failed',error=str(error));save();raise
if __name__=='__main__':main()
