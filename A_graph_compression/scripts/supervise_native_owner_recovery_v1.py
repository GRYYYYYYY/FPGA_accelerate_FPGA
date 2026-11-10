#!/usr/bin/env python3
"""Wait for surviving compiler evidence, independently audit, then run full RTL."""
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
from check_orphaned_native_compiler_v1 import ROOT, OBSERVER, REPORT as COMPILE_AUDIT
from run_recovered_native_rtl_v1 import OUT as TRIAL

OUT = ROOT/'data/derived/native_owner_recovery_supervision_20261030_v1'


def main():
    def interrupted(signum, frame): raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists() and not TRIAL.exists() and not COMPILE_AUDIT.exists(), 'Refuse duplicate recovery chain')
    current = json.loads((OBSERVER/'state.json').read_text()); identity = process(current['owner_pid'])
    require(current['status'] == 'running' and identity and identity['state'] != 'Z' and
            'observe_orphaned_native_compiler_v1.py' in identity['command'], 'Existing compiler observer not verified')
    check = ROOT/'scripts/check_orphaned_native_compiler_v1.py'; run = ROOT/'scripts/run_recovered_native_rtl_v1.py'
    files = {str(p):digest(p) for p in [check,run,Path(__file__).resolve(),ROOT/'scripts/observe_orphaned_native_compiler_v1.py',
             ROOT/'scripts/owned_sim_resource_policy_v1.py',ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py']}
    OUT.mkdir(); atomic(OUT/'plan.json',dict(files=files,observer_identity=identity,steps=['compiler_independent_audit','full4tx_RTL_and_C'],
                       no_compile_restart=True,no_physical_launch=True))
    state = dict(owner_pid=os.getpid(),status='running',stage='waiting_surviving_compiler_observer',completed=[])
    atomic(OUT/'state.json',state); child = None
    try:
        while True:
            current = json.loads((OBSERVER/'state.json').read_text()); live = process(identity['pid'])
            matches = bool(live and live['state'] != 'Z' and live['start_ticks'] == identity['start_ticks'] and live['command'] == identity['command'])
            require(current['owner_pid'] == identity['pid'] and current['status'] != 'failed', 'Observer failed/changed; preserve evidence')
            if current['status'] == 'complete':
                require(current['stage'] == 'compiler_terminal_evidence_pending_independent_recovery_audit', 'Unexpected observer terminal')
                if not matches: break
            else: require(matches, 'Observer missing without completion')
            atomic(OUT/'observation.json',dict(observer_verified=matches,stage=current['stage'],monotonic_seconds=time.monotonic()))
            time.sleep(10)
        for phase, script in [('compiler_independent_audit',check),('full4tx_RTL_and_C',run)]:
            for name, checksum in files.items(): require(digest(name) == checksum, 'Frozen recovery entry changed '+name)
            command = ([ 'prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--']
                       if phase == 'compiler_independent_audit' else [])+[sys.executable,str(script)]
            state['stage'] = phase; atomic(OUT/'state.json',state); started = time.monotonic()
            with (OUT/(phase+'.log')).open('x') as log:
                child = subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid'] = child.pid; atomic(OUT/'state.json',state)
                code = child.wait(); child = None
            atomic(OUT/(phase+'.receipt.json'),dict(command=command,exit_code=code,elapsed_seconds=time.monotonic()-started,
                   log_sha256=digest(OUT/(phase+'.log'))))
            require(code == 0, 'Failed recovery '+phase)
            state['completed'].append(phase); atomic(OUT/'state.json',state)
        completed = json.loads((TRIAL/'state.json').read_text())
        require(completed['status'] == 'complete' and completed['stage'] == 'recovered_full4tx_independent_final_audit_pending', 'Incomplete recovered RTL')
        state.update(status='complete',stage='recovered_RTL_requires_independent_final_audit');atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None: stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__ == '__main__':main()
