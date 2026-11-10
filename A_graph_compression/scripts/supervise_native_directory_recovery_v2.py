#!/usr/bin/env python3
"""One new directory-preserving trial followed by its independent full RTL audit."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
from run_recovered_native_rtl_v2 import ROOT, BASE, OUT as TRIAL
from check_recovered_native_rtl_v2 import REPORT

OUT=ROOT/'data/derived/native_directory_recovery_supervision_20261030_v2'


def main():
    def interrupted(signum,frame):raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists() and not TRIAL.exists() and not REPORT.exists(), 'Refuse duplicate recovery')
    old=json.loads((BASE/'collision_safe_native_owner_recovery_v1/state.json').read_text())
    require(old['status']=='failed' and process(old['owner_pid']) is None and process(old['child_pid']) is None, 'Old trial not terminal')
    scripts=[ROOT/'scripts/run_recovered_native_rtl_v2.py',ROOT/'scripts/check_recovered_native_rtl_v2.py']
    files={str(p):digest(p) for p in [*scripts,Path(__file__).resolve(),ROOT/'results/recovered_native_output_directory_failure_20261030_v1.json']}
    OUT.mkdir();atomic(OUT/'plan.json',dict(files=files,steps=['full_RTL_C','independent_final_audit'],no_compile_restart=True))
    state=dict(owner_pid=os.getpid(),status='running',stage='starting_directory_preserving_trial',completed=[])
    atomic(OUT/'state.json',state);child=None
    try:
        for phase,script in zip(['full_RTL_C','independent_final_audit'],scripts):
            for name,checksum in files.items():require(digest(name)==checksum,'Frozen entry changed '+name)
            state['stage']=phase;atomic(OUT/'state.json',state)
            command=(['prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--']
                     if phase=='independent_final_audit' else [])+[sys.executable,str(script)]
            start=time.monotonic();log=OUT/(phase+'.log')
            with log.open('x') as output:
                child=subprocess.Popen(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                code=child.wait();child=None
            atomic(OUT/(phase+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(log)))
            require(code==0,'Failed '+phase)
            state['completed'].append(phase);atomic(OUT/'state.json',state)
        result=json.loads(REPORT.read_text())
        require(result['status']=='recovered_collision_safe_native_full4tx_full44_original_C_independently_verified', 'Wrong acceptance')
        state.update(status='complete',stage='native_full_RTL_independent_audit_complete',report_sha256=digest(REPORT));atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__=='__main__':main()
