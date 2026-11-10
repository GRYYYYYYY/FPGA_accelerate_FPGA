#!/usr/bin/env python3
"""After independent paired HLS acceptance, serially prepare and audit both full setups."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from owned_sim_resource_policy_v1 import observe, abort_reason
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
from prepare_collision_safe_bus64_cosim_v1 import ROOT, BASE, REVIEW

OUT=ROOT/'data/derived/bus64_fresh_setup_supervision_20261030_v1'
PARENT=ROOT/'data/derived/recovery_acceptance_supervision_20261030_v1'


def main():
    def interrupted(signum,frame):raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists(), 'Refuse duplicate setup supervisor')
    current=json.loads((PARENT/'state.json').read_text());owner=process(current['owner_pid'])
    require(owner and owner['state']!='Z' and 'supervise_recovery_acceptance_v1.py' in owner['command'] and
            current['jobs']['paired_bus64_HLS']['status']=='waiting', 'Existing paired acceptance owner not verified')
    prepare=ROOT/'scripts/prepare_collision_safe_bus64_cosim_v1.py';check=ROOT/'scripts/check_collision_safe_bus64_cosim_v1.py'
    steps=[]
    for mode in [0,1]:
        output=BASE/'collision_safe_bus64_cosim_setup_v1'/f'mode_{mode}'
        accepted=ROOT/f'results/collision_safe_bus64_cosim_mode_{mode}_audit_20261030_v1.json'
        require(not output.exists() and not accepted.exists(), 'Setup/audit already exists')
        steps.extend([dict(phase=f'mode_{mode}_fresh_setup',script=str(prepare),mode=mode,audit=False),
                      dict(phase=f'mode_{mode}_independent_setup_audit',script=str(check),mode=mode,audit=True,report=str(accepted))])
    files={str(p):digest(p) for p in [prepare,check,Path(__file__).resolve(),ROOT/'scripts/run_collision_safe_bus64_pair_v1.py',
           ROOT/'scripts/search_kernel_memory_plan.py',ROOT/'scripts/owned_sim_resource_policy_v1.py',ROOT/'scripts/run_collision_safe_batch_hls_v1.py']}
    OUT.mkdir();atomic(OUT/'plan.json',dict(files=files,parent_owner=owner,steps=steps,no_rtl_or_physical_launch=True))
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_independent_paired_HLS_acceptance',completed=[])
    atomic(OUT/'state.json',state);child=None
    try:
        while True:
            current=json.loads((PARENT/'state.json').read_text());row=current['jobs']['paired_bus64_HLS']
            live=process(owner['pid']);matches=bool(live and live['state']!='Z' and live['start_ticks']==owner['start_ticks'] and live['command']==owner['command'])
            require(current['owner_pid']==owner['pid'], 'Acceptance owner changed')
            if row['status']=='accepted':
                require(row['report']==str(REVIEW) and row['report_sha256']==digest(REVIEW), 'Changed paired acceptance')
                report=json.loads(REVIEW.read_text())
                require(report['status']=='collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending', 'Wrong independent pair gate')
                for name,checksum in report['files'].items():require(digest(name)==checksum, 'Changed paired gate input '+name)
                receipt=PARENT/'paired_bus64_HLS.receipt.json';r=json.loads(receipt.read_text())
                require(r['exit_code']==0 and r['abort_reason'] is None and r['log_sha256']==digest(PARENT/'paired_bus64_HLS.log'), 'Pair audit failed')
                atomic(OUT/'gate.json',dict(report=str(REVIEW),sha256=digest(REVIEW),receipt=str(receipt),receipt_sha256=digest(receipt)))
                break
            require(row['status']=='waiting' and matches and current['status']=='running', 'Paired audit unavailable/failed; no restart')
            atomic(OUT/'observation.json',dict(parent_owner_verified=matches,pair_status=row['status'],parent_stage=current['stage'],monotonic_seconds=time.monotonic()))
            time.sleep(10)
        initial=observe()
        for step in steps:
            for name,checksum in files.items():require(digest(name)==checksum, 'Frozen setup entry changed '+name)
            require(abort_reason(initial,observe()) is None, 'New OOM/reset before setup step')
            state['stage']=step['phase'];atomic(OUT/'state.json',state)
            command=(['prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--'] if step['audit'] else [])
            command += [sys.executable,step['script'],'--mode',str(step['mode'])]
            log=OUT/(step['phase']+'.log');started=time.monotonic();reason=None
            with log.open('x') as output:
                child=subprocess.Popen(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
                state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                while child.poll() is None:
                    reason=abort_reason(initial,observe())
                    if reason:stop(child);break
                    time.sleep(1)
                code=child.wait();child=None
            reason=reason or abort_reason(initial,observe())
            atomic(OUT/(step['phase']+'.receipt.json'),dict(command=command,exit_code=code,abort_reason=reason,
                   elapsed_seconds=time.monotonic()-started,log_sha256=digest(log)))
            require(code==0 and reason is None, 'Failed '+step['phase'])
            if step['audit']:
                report=json.loads(Path(step['report']).read_text())
                require(report['status']=='collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending' and
                        report['graph_mode']==step['mode'], 'Wrong setup acceptance')
            state['completed'].append(step['phase']);atomic(OUT/'state.json',state)
        state.update(status='complete',stage='both_full44_setups_independently_audited_RTL_pending');atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__=='__main__':main()
