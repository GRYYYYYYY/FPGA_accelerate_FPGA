#!/usr/bin/env python3
"""One-owner continuation: wait for the existing capture, verify, route 16/all nets."""
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'results/netlist_pipeline_20261022_v1.json'
LOCK=ROOT/'results/netlist_pipeline_20261022_v1.lock'
CAPTURE_PID=2173511


def main():
    lock=LOCK.open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state={'owner_pid':os.getpid(),'capture_pid':CAPTURE_PID,'started_utc':datetime.now(timezone.utc).isoformat(),
           'status':'running','stage':'wait_existing_capture','steps':[]}
    def save():
        temporary=STATE.with_suffix('.tmp')
        temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.replace(STATE)
    save()
    try:
        while True:
            proc=Path('/proc')/str(CAPTURE_PID)
            try:
                command=(proc/'cmdline').read_bytes()
                status=(proc/'stat').read_text().split(') ',1)[1].split()[0]
            except FileNotFoundError:
                break
            if status=='Z':break
            if b'export_netlist_domain.tcl' not in command:
                raise RuntimeError('Capture PID no longer identifies the expected process')
            time.sleep(30)
        def run(label,command):
            state['stage']=label;save()
            log=ROOT/'results'/('netlist_pipeline_'+label+'_20261022_v1.log')
            start=time.perf_counter()
            with log.open('x') as stream:
                child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;save();code=child.wait()
            state.pop('child_pid',None)
            state['steps'].append({'stage':label,'command':command,'exit_code':code,
                                   'wall_seconds':time.perf_counter()-start,'log':str(log.relative_to(ROOT))})
            save()
            if code:raise RuntimeError(label+' failed; inspect '+str(log))
        capture=ROOT/'data/raw/netlist_u280_20261022_v1/capture.json'
        if capture.exists():raise RuntimeError('Capture manifest already exists; reconcile rather than duplicate the chain')
        run('finalize',[sys.executable,'scripts/finalize_netlist_capture.py'])
        for label,count in [('integration16',16),('all_nets',0)]:
            out='data/derived/netlist_'+label+'_20261022_v1'
            run(label,[sys.executable,'-u','scripts/run.py','netlist-check','--max-nets',str(count),'--output-dir',out])
        state['status']='software_stages_complete';state['stage']='await_vivado_candidate_validation';save()
    except BaseException as exc:
        state['status']='failed';state['error']=str(exc);save();raise


if __name__=='__main__':main()
