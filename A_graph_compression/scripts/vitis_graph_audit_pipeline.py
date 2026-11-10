#!/usr/bin/env python3
"""Wait for one identified HLS owner, then independently audit once; never retry."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]

def identity(pid):
    proc=Path('/proc')/str(pid)
    try:
        stat=(proc/'stat').read_text().split(') ',1)[1].split()
        return stat[19],stat[0],(proc/'cmdline').read_bytes()
    except FileNotFoundError:return None

def save(path,state):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(path)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True);p.add_argument('--owner',type=int,required=True)
    p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.state.exists() and not a.output.exists(),'Refusing existing audit state/output')
    current=identity(a.owner);require(current and current[1]!='Z' and b'vitis_graph_pipeline_v2.py' in current[2],'Expected HLS owner not live')
    files={str(x):digest(x) for x in [Path(__file__).resolve(),ROOT/'scripts/check_vitis_kernel.py',ROOT/'results/regression_vitis_kernel_audit_20261023_v3.log']}
    state={'owner_pid':os.getpid(),'upstream_owner_pid':a.owner,'upstream_start_ticks':current[0],
           'status':'running','stage':'wait_hls_owner','files':files,'output':str(a.output.resolve()),'created_utc':datetime.now(timezone.utc).isoformat()}
    with a.state.open('x') as f:json.dump(state,f,indent=2);f.write('\n')
    try:
        while True:
            observed=identity(a.owner)
            if observed is None or observed[1]=='Z':break
            require(observed[0]==current[0] and b'vitis_graph_pipeline_v2.py' in observed[2],'Upstream process identity changed')
            time.sleep(10)
        upstream=json.loads((a.bundle/'pipeline.json').read_text());require(upstream['status']=='complete','HLS pipeline not complete')
        for path,value in files.items():require(digest(path)==value,'Frozen audit dependency changed')
        state.update(stage='independent_audit');save(a.state,state)
        command=[sys.executable,str(ROOT/'scripts/check_vitis_kernel.py'),'--bundle',str(a.bundle.resolve()),'--output',str(a.output.resolve())]
        with a.output.with_suffix('.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            state.update(child_pid=child.pid,command=command);save(a.state,state);code=child.wait()
        state.pop('child_pid',None);state['exit_code']=code
        require(code==0 and a.output.exists(),'Independent kernel audit failed')
        state.update(status='complete',stage='audited',report_sha256=digest(a.output));save(a.state,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(a.state,state);raise

if __name__=='__main__':main()
