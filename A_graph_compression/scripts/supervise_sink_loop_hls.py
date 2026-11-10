#!/usr/bin/env python3
"""Wait for the existing HLS owner, then audit once; never start/restart an HLS flow."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]


def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')


def identity(pid):
    p=Path('/proc')/str(pid)
    # After the parenthesized comm, Linux stat field22 is index19.
    return dict(start_ticks=(p/'stat').read_text().rsplit(')',1)[1].split()[19],
                command=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();bundle=a.bundle.resolve();output=a.output.resolve()
    directory=bundle/'audit_supervisor';directory.mkdir(exist_ok=False)
    require(not output.exists(),'Existing review; reconcile instead of duplicating audit')
    original=json.loads((bundle/'state.json').read_text());pid=original['owner_pid']
    observed=identity(pid) if original['status']=='running' else None
    if observed:require('scripts/search_sink_loop_hls.py' in observed['command'],'Unexpected original owner')
    checker=ROOT/'scripts/check_integrated_control_hls.py'
    files={str(f):digest(f) for f in [bundle/'plan.json',checker,Path(__file__).resolve(),ROOT/'scripts/check_vitis_kernel.py']}
    save(directory/'plan.json',dict(files=files,original_owner=pid,original_identity=observed,output=str(output)))
    state=dict(owner_pid=os.getpid(),status='running',stage='await_original_hls',observed_owner=pid)
    def update():
        temp=directory/'state.tmp';temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(directory/'state.json')
    update()
    try:
        while True:
            current=json.loads((bundle/'state.json').read_text())
            require(current['owner_pid']==pid,'Original owner changed')
            if current['status']!='running':break
            require(observed is not None and identity(pid)==observed,'Original HLS owner missing/changed; do not restart')
            time.sleep(10)
        require(current['status']=='complete','Original HLS flow failed; retained without retry')
        for path,h in files.items():require(digest(path)==h,'Audit dependency changed '+path)
        state['stage']='independent_synthesis_audit';update()
        command=['taskset','-c','115','python3',str(checker),'--kind','sink_loop','--bundle',str(bundle),'--output',str(output)]
        with (directory/'audit.log').open('x') as f:code=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
        save(directory/'receipt.json',dict(command=command,exit_code=code,log_sha256=digest(directory/'audit.log')))
        require(code==0,'Independent synthesis review failed; inspect retained log')
        state.update(status='complete',stage='independently_audited');update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise


if __name__=='__main__':main()
