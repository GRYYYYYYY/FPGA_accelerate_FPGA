#!/usr/bin/env python3
"""One-owner fixed-mode Csim/synthesis/RTL/implementation validation chain."""
from datetime import datetime,timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def main():
    variant=sys.argv[1]
    if variant not in ['csr','compact']:raise ValueError('Unknown fixed variant')
    prefix=ROOT/'results'/('hls_fixed_'+variant+'_20261022_v1')
    lock=prefix.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state={'owner_pid':os.getpid(),'variant':variant,'status':'running','steps':[],
           'started_utc':datetime.now(timezone.utc).isoformat()}
    def save():
        path=prefix.with_suffix('.json');tmp=prefix.with_suffix('.tmp')
        tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(path)
    save()
    try:
        base=ROOT/'data/derived/hls_fixed_modes_20261022_v1'
        manifest=json.loads((base/'manifest.json').read_text())
        for name,digest in manifest['files'].items():
            if hashlib.sha256((base/name).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen source/stimulus changed')
        for stage in ['synth','cosim','impl']:
            state['stage']=stage;save()
            env=os.environ.copy();env.update(LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1',
                A_FIXED_SOURCE=str(base/variant),A_FIXED_PROJECT=str(ROOT/'build'/('hls_fixed_'+variant+'_20261022_v1')),A_FIXED_STAGE=stage)
            log=prefix.with_name(prefix.name+'_'+stage+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen([str(HLS),'-f',str(ROOT/'hardware/hls/run_fixed.tcl')],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
                state['child_pid']=child.pid;save();code=child.wait()
            content=log.read_text();marker='FIXED_'+stage.upper()+'_COMPLETE'
            state['steps'].append({'stage':stage,'exit_code':code,'log':str(log.relative_to(ROOT)),
                                   'completion_marker':marker in content})
            state.pop('child_pid',None);save()
            if code or marker not in content or 'ERROR:' in content:raise RuntimeError(stage+' failed; inspect '+str(log))
        state['status']='completed';state['stage']='await_report';save()
    except BaseException as exc:
        state['status']='failed';state['error']=str(exc);save();raise


if __name__=='__main__':main()
