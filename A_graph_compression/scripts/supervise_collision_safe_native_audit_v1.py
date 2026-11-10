#!/usr/bin/env python3
"""Observe the existing native owner and audit only its successful terminal run."""
import json
import os
import subprocess
import sys
import time
from check_vitis_kernel import digest, require
from experiment_status_v6 import process
from run_compact_native_stack_recovery_v3 import atomic
from run_collision_safe_batch_hls_v1 import stop
from owned_sim_resource_policy_v1 import observe, abort_reason
from check_collision_safe_native_rtl_v1 import ROOT, OUT as TRIAL, REPORT

OUT = ROOT/'data/derived/collision_safe_native_audit_supervision_20261030_v1'
CHECK = ROOT/'scripts/check_collision_safe_native_rtl_v1.py'


def main():
    require(not OUT.exists() and not REPORT.exists(), 'Refuse duplicate auditor')
    current = json.loads((TRIAL/'state.json').read_text())
    identity = process(current['owner_pid'])
    require(current['status'] == 'running' and identity and identity['state'] != 'Z' and
            'scripts/run_collision_safe_native_rtl_v1.py' in identity['command'], 'Existing live native owner required')
    files = {str(p):digest(p) for p in [CHECK, ROOT/'scripts/run_collision_safe_native_rtl_v1.py',
             ROOT/'scripts/owned_sim_resource_policy_v1.py', ROOT/'scripts/check_collision_safe_batch_hls_v1.py',
             ROOT/'scripts/check_vitis_kernel.py', __file__]}
    OUT.mkdir()
    atomic(OUT/'plan.json', dict(files=files, prerequisite_owner=identity, trial=str(TRIAL),
                               launches_only_independent_auditor=True))
    state = dict(owner_pid=os.getpid(), status='running', stage='waiting_existing_native_terminal')
    atomic(OUT/'state.json', state)
    child = None
    try:
        while True:
            current = json.loads((TRIAL/'state.json').read_text())
            live = process(identity['pid'])
            matches = bool(live and live['state'] != 'Z' and live['start_ticks'] == identity['start_ticks'] and
                           live['command'] == identity['command'])
            require(current['owner_pid'] == identity['pid'], 'Native owner changed')
            require(current['status'] != 'failed', 'Native execution failed; preserve evidence, no restart')
            if current['status'] == 'complete':
                require(current['stage'] == 'independent_final_rtl_audit_pending', 'Unexpected terminal stage')
                if not matches: break
            else:
                require(matches, 'Original owner missing without success; no restart')
            atomic(OUT/'observation.json', dict(native_status=current['status'], stage=current['stage'],
                   owner_verified=matches, process=live, monotonic_seconds=time.monotonic()))
            time.sleep(30)
        for name, checksum in files.items(): require(digest(name) == checksum, 'Bound auditor changed '+name)
        initial = observe(); start = time.monotonic()
        command = ['prlimit', '--as=17179869184:17179869184', '--stack=67108864:67108864', '--core=0:0',
                   '--', sys.executable, str(CHECK)]
        state['stage'] = 'independent_full_rtl_audit'; atomic(OUT/'state.json', state)
        reason = None
        with (OUT/'audit.log').open('x') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            state['child_pid'] = child.pid; atomic(OUT/'state.json', state)
            while child.poll() is None:
                reason = abort_reason(initial, observe())
                if reason: stop(child); break
                time.sleep(1)
            code = child.wait(); child = None
        atomic(OUT/'audit.receipt.json', dict(command=command, exit_code=code, abort_reason=reason,
               elapsed_seconds=time.monotonic()-start, log_sha256=digest(OUT/'audit.log')))
        require(code == 0 and reason is None, 'Independent audit failed')
        report = json.loads(REPORT.read_text())
        require(report['status'] == 'collision_safe_native_full4tx_full44_original_C_oracle_independently_verified',
                'Wrong final acceptance')
        state.update(status='complete', stage='native_independent_audit_complete', report_sha256=digest(REPORT))
        atomic(OUT/'state.json', state)
    except BaseException as exc:
        if child is not None and child.poll() is None: stop(child)
        state.update(status='failed', error=str(exc)); atomic(OUT/'state.json', state)
        raise


if __name__ == '__main__': main()
