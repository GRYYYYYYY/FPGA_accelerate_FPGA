#!/usr/bin/env python3
"""Independently audit recovered RTL and paired HLS when each existing owner finishes."""
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

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
OUT = ROOT/'data/derived/recovery_acceptance_supervision_20261030_v1'


def main():
    def interrupted(signum, frame): raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM,interrupted)
    require(not OUT.exists(), 'Refuse duplicate acceptance supervisor')
    jobs = [dict(name='recovered_native_RTL', folder=str(ROOT/'data/derived/native_owner_recovery_supervision_20261030_v1'),
                 owner_script='supervise_native_owner_recovery_v1.py', terminal_stage='recovered_RTL_requires_independent_final_audit',
                 command=[sys.executable,str(ROOT/'scripts/check_recovered_native_rtl_v1.py')],
                 report=str(ROOT/'results/collision_safe_recovered_native_rtl_audit_20261030_v1.json'),
                 accepted_status='recovered_collision_safe_native_full4tx_full44_original_C_independently_verified'),
            dict(name='paired_bus64_HLS',folder=str(BASE/'collision_safe_bus64_pair_execution_v2'),
                 owner_script='run_collision_safe_bus64_pair_v2.py',terminal_stage='paired_hls_complete_independent_audit_pending',
                 command=[sys.executable,str(ROOT/'scripts/check_collision_safe_bus64_pair_v1.py'),'--execution-root',
                          str(BASE/'collision_safe_bus64_pair_execution_v2'),'--output',str(ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v2.json')],
                 report=str(ROOT/'results/collision_safe_bus64_pair_hls_audit_20261030_v2.json'),
                 accepted_status='collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending')]
    files = {str(Path(__file__).resolve()):digest(__file__)}
    for name in ['check_recovered_native_rtl_v1.py','check_collision_safe_bus64_pair_v1.py','check_vitis_kernel.py',
                 'owned_sim_resource_policy_v1.py','check_collision_safe_batch_hls_v1.py','run_recovered_native_rtl_v1.py',
                 'check_orphaned_native_compiler_v1.py','run_collision_safe_bus64_pair_v2.py']:
        p = ROOT/'scripts'/name;files[str(p)]=digest(p)
    for job in jobs:
        require(not Path(job['report']).exists(), 'Acceptance already exists')
        current = json.loads((Path(job['folder'])/'state.json').read_text()); owner = process(current['owner_pid'])
        require(current['status'] == 'running' and owner and owner['state'] != 'Z' and
                job['owner_script'] in owner['command'], 'Existing prerequisite owner not verified')
        job['owner'] = owner
    OUT.mkdir();atomic(OUT/'plan.json',dict(files=files,jobs=jobs,launches_only_auditors=True,no_execution_restart=True))
    state = dict(owner_pid=os.getpid(),status='running',stage='waiting_existing_recovery_jobs',
                 jobs={job['name']:dict(status='waiting') for job in jobs})
    atomic(OUT/'state.json',state); child = None
    try:
        while any(row['status'] == 'waiting' for row in state['jobs'].values()):
            observations = []
            for job in jobs:
                row = state['jobs'][job['name']]
                if row['status'] != 'waiting': continue
                current = json.loads((Path(job['folder'])/'state.json').read_text()); live = process(job['owner']['pid'])
                matches = bool(live and live['state'] != 'Z' and live['start_ticks'] == job['owner']['start_ticks'] and
                               live['command'] == job['owner']['command'])
                observations.append(dict(job=job['name'],owner_verified=matches,stage=current['stage'],status=current['status']))
                if current['owner_pid'] != job['owner']['pid'] or current['status'] == 'failed' or (not matches and current['status'] != 'complete'):
                    row.update(status='failed',reason='Prerequisite failed/changed/disappeared without success; no restart')
                    atomic(OUT/'state.json',state); continue
                if current['status'] != 'complete' or matches: continue
                if current['stage'] != job['terminal_stage']:
                    row.update(status='failed',reason='Unexpected terminal stage');atomic(OUT/'state.json',state);continue
                for name, checksum in files.items(): require(digest(name) == checksum, 'Bound acceptance code changed '+name)
                state['stage'] = 'auditing_'+job['name'];atomic(OUT/'state.json',state)
                command = ['prlimit','--as=17179869184:17179869184','--stack=67108864:67108864','--core=0:0','--']+job['command']
                initial = observe();started=time.monotonic();reason=None;log=OUT/(job['name']+'.log')
                with log.open('x') as output:
                    child=subprocess.Popen(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
                    state['child_pid']=child.pid;atomic(OUT/'state.json',state)
                    while child.poll() is None:
                        reason=abort_reason(initial,observe())
                        if reason:stop(child);break
                        time.sleep(1)
                    code=child.wait();child=None
                final=observe();reason=reason or abort_reason(initial,final)
                atomic(OUT/(job['name']+'.receipt.json'),dict(command=command,exit_code=code,abort_reason=reason,
                       elapsed_seconds=time.monotonic()-started,log_sha256=digest(log),initial_memory=initial,final_memory=final))
                if code != 0 or reason:
                    row.update(status='failed',reason='Independent audit failed or aborted; preserve outputs')
                else:
                    result=json.loads(Path(job['report']).read_text())
                    require(result['status'] == job['accepted_status'], 'Unexpected typed acceptance')
                    row.update(status='accepted',report=job['report'],report_sha256=digest(job['report']))
                state['stage']='waiting_existing_recovery_jobs';atomic(OUT/'state.json',state)
            atomic(OUT/'observation.json',dict(jobs=observations,monotonic_seconds=time.monotonic()))
            if any(row['status'] == 'waiting' for row in state['jobs'].values()):time.sleep(10)
        state.update(status='complete' if all(row['status']=='accepted' for row in state['jobs'].values()) else 'failed',
                     stage='independent_audits_terminal_not_full_experiment_acceptance')
        atomic(OUT/'state.json',state)
    except BaseException as exc:
        if child is not None and child.poll() is None:stop(child)
        state.update(status='failed',error=str(exc));atomic(OUT/'state.json',state);raise


if __name__ == '__main__':main()
