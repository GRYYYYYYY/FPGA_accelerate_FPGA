#!/usr/bin/env python3
"""One owner: wait for current HLS, independently audit, prepare fresh full44 setup."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
HLS=BASE/'collision_safe_batch_hls_v1'
SETUP=BASE/'collision_safe_compact_cosim_setup_v1'
OUT=ROOT/'data/derived/collision_safe_compact_setup_supervision_20261030_v1'
CHECK=ROOT/'scripts/check_collision_safe_batch_hls_v1.py'
PREPARE=ROOT/'scripts/prepare_collision_safe_compact_cosim_v1.py'
AUDIT=ROOT/'results/collision_safe_compact_hls_audit_20261030_v1.json'


def main():
    require(not OUT.exists() and not SETUP.exists() and not AUDIT.exists(),'Refuse duplicate supervisor/setup/audit')
    original=json.loads((HLS/'state.json').read_text())
    identity=process(original['owner_pid'])
    require(original['status']=='running' and identity is not None and identity['state']!='Z' and
            'scripts/run_collision_safe_batch_hls_v1.py' in identity['command'],'Current HLS owner not verified')
    OUT.mkdir()
    files={str(p):digest(p) for p in [CHECK,PREPARE,Path(__file__).resolve(),
           ROOT/'scripts/run_collision_safe_batch_hls_v1.py',ROOT/'scripts/owned_sim_resource_policy_v1.py']}
    atomic(OUT/'plan.json',dict(files=files,prerequisite_owner=identity,prerequisite_state=str(HLS/'state.json'),
           steps=['independent_new_HLS_audit','fresh_full44_csim_and_cosim_setup'],
           no_rtl_or_physical_launch=True,no_failed_entry_restart=True))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_current_collision_safe_hls_terminal',
               prerequisite_owner=identity,completed=[],rtl_executed=False)
    atomic(OUT/'state.json',state);child=None
    try:
        while True:
            current=json.loads((HLS/'state.json').read_text());live=process(identity['pid'])
            matches=bool(live and live['state']!='Z' and live['start_ticks']==identity['start_ticks'] and
                         live['command']==identity['command'])
            if current['status']=='failed':raise RuntimeError('Prerequisite HLS failed')
            if current['status']=='synthesized_pending_independent_audit':
                require(current['owner_pid']==identity['pid'],'Different terminal owner')
                if not matches:break
            else:
                require(matches,'Original HLS owner missing/mismatched without success receipt; do not restart')
            atomic(OUT/'observation.json',dict(prerequisite_status=current['status'],stage=current['stage'],
                   owner_verified=matches,process=live,observed_monotonic_seconds=time.monotonic()))
            time.sleep(30)
        for phase,script in [('independent_hls_audit',CHECK),('fresh_full44_setup',PREPARE)]:
            for n,h in files.items():require(digest(n)==h,'Bound entry changed '+n)
            state.update(stage=phase);atomic(OUT/'state.json',state)
            command=([ 'prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--']
                     if phase=='independent_hls_audit' else [])+[sys.executable,str(script)]
            # The setup Python owner has no inherited hard-AS cap; its HLS
            # child applies the explicit64GiB cap from the bound setup script.
            start=time.monotonic()
            with (OUT/(phase+'.log')).open('x') as log:
                child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                code=child.wait();child=None
            atomic(OUT/(phase+'.receipt.json'),dict(command=command,exit_code=code,
                   elapsed_seconds=time.monotonic()-start,log_sha256=digest(OUT/(phase+'.log'))))
            require(code==0,'Failed '+phase)
            if phase=='independent_hls_audit':
                report=json.loads(AUDIT.read_text())
                require(report['status']=='collision_safe_native_compact_hls_all9_dynamic_connections_and_full44_C_verified_rtl_pending',
                        'Wrong HLS audit status')
            else:
                report=json.loads((SETUP/'setup.json').read_text())
                require(report['status']=='collision_safe_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending',
                        'Wrong full setup status')
            state['completed'].append(phase);atomic(OUT/'state.json',state)
        state.update(status='complete',stage='fresh_setup_complete_no_rtl_launched');atomic(OUT/'state.json',state)
        print(state['status'])
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__=='__main__':main()
