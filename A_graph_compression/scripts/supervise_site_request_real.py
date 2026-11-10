#!/usr/bin/env python3
"""Start the prepared full tree experiment once its original predecessor is audited.

The original predecessor is only observed, never restarted or audited twice.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest, require
from supervise_site_request_hls import identity, save

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();bundle=a.bundle.resolve();output=a.output.resolve()
    predecessor=ROOT/'data/derived/route_tree_router_20261024_v1'
    require(not (bundle/'state.json').exists() and not output.exists(),'Existing full experiment; reconcile instead')
    require(json.loads((bundle/'prepare_state.json').read_text())['status']=='complete','Preparation incomplete')
    proof=ROOT/'results/site_request_component_20261024_v1.json'
    require(json.loads(proof.read_text())['status']=='site_request_packed_commit_and_full_search_differential_independently_verified','Missing independent integration gate')
    folder=bundle/'real_supervisor';folder.mkdir(exist_ok=False)
    current=json.loads((predecessor/'state.json').read_text());pid=current['owner_pid']
    observed=identity(pid) if current['status']=='running' else None
    if observed:require('scripts/route_tree_router_pipeline.py' in observed['command'],'Unexpected predecessor process')
    runner=ROOT/'scripts/site_request_router_pipeline.py'
    dependencies=[runner,ROOT/'scripts/check_site_request_router.py',ROOT/'scripts/check_vitis_kernel.py',
                  ROOT/'scripts/supervise_site_request_hls.py',Path(__file__).resolve(),proof,bundle/'plan.json',bundle/'report.json']
    files={str(f):digest(f) for f in dependencies}
    save(folder/'plan.json',dict(files=files,original_owner=pid,original_identity=observed,output=str(output)))
    state=dict(owner_pid=os.getpid(),status='running',stage='await_predecessor_full_audit',observed_owner=pid)
    def update():
        tmp=folder/'state.tmp';tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(folder/'state.json')
    update()
    try:
        while current['status']=='running':
            require(observed is not None and identity(pid)==observed,'Predecessor owner missing/changed; do not restart')
            time.sleep(10)
            current=json.loads((predecessor/'state.json').read_text())
            require(current['owner_pid']==pid,'Predecessor owner changed')
        require(current['status']=='complete','Predecessor failed; retaining failure without retry')
        for path,sha in files.items():require(digest(path)==sha,'Launch dependency changed '+path)
        command=['python3',str(runner),'--bundle',str(bundle),'--output',str(output)]
        state['stage']='full_real_experiment';update()
        with (folder/'pipeline.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;update();code=child.wait()
        save(folder/'receipt.json',dict(command=command,exit_code=code,log_sha256=digest(folder/'pipeline.log')))
        require(code==0,'Full tree experiment failed; no retry')
        require(json.loads(output.read_text())['status']=='site_request_two_full_router_conditions_independently_verified','Missing final full audit')
        state.update(status='complete',stage='independently_audited');update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise


if __name__=='__main__':main()
