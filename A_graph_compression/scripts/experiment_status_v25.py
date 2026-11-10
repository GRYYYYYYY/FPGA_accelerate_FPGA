#!/usr/bin/env python3
"""Read-only status of all currently owned compiler-recovery workflows."""
import argparse
import json
from pathlib import Path
from experiment_status_v24 import collect as previous
from experiment_status_v6 import ROOT, BASE, workflow, process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=previous(root,base,proc_root)
    for label,folder,script in [
        ('native_recovery_supervisor',root/'data/derived/native_owner_recovery_supervision_20261030_v1','supervise_native_owner_recovery_v1.py'),
        ('recovered_native_RTL',base/'collision_safe_native_owner_recovery_v1','run_recovered_native_rtl_v1.py'),
        ('bus64_pair_execution_v2',base/'collision_safe_bus64_pair_execution_v2','run_collision_safe_bus64_pair_v2.py'),
        ('recovery_acceptance_supervisor',root/'data/derived/recovery_acceptance_supervision_20261030_v1','supervise_recovery_acceptance_v1.py')]:
        row=workflow(label,folder,script,proc_root)
        if row['status']=='waiting_dependency_or_memory':row['status']='waiting_dependency'
        path=folder/'state.json'
        if path.exists():
            state=json.loads(path.read_text());phase=state.get('stage');actual_path=None
            if label=='recovered_native_RTL' and phase in ['rtl','postcheck']:
                actual_path=folder/(phase+'.actual_limits.json')
            if label=='bus64_pair_execution_v2':
                row['completed_modes']=state['completed_modes']
                if phase=='csim_csynth':
                    plan=json.loads((folder/'execution_plan.json').read_text())
                    job=next(j for j in plan['jobs'] if j['mode']==state['mode'])
                    actual_path=Path(job['cwd'])/'actual_limits.json';row['mode']=state['mode']
            if label=='recovery_acceptance_supervisor':row['audits']=state['jobs']
            if actual_path is not None:
                row['phase_process_verified']=False
                if actual_path.exists():
                    actual=json.loads(actual_path.read_text());live=process(actual['pid'],proc_root)
                    row['phase_process_verified']=bool(live and live['state']!='Z' and
                        live['start_ticks']==actual['start_ticks'] and live['command']==actual['command'])
                    row['phase_pid']=actual['pid']
        result['tasks'].append(row)
    result['new_chain_note']='Original owner loss remains recorded. Recovery and paired HLS have separate owned execution and independent audits. Live state is not functional acceptance; physical/board and full experiment remain unverified.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            if row['task'] in {'surviving_native_compiler_observer','native_recovery_supervisor','recovered_native_RTL','bus64_pair_execution_v2','recovery_acceptance_supervisor'}:
                extra=' '.join(f'{key}={row[key]}' for key in ['owner_verified','compiler_verified','timer_verified','phase_process_verified','completed_modes'] if key in row)
                print(f"{row['task']}: {row['status']} ({row.get('stage')}) {extra}")
        print(result['new_chain_note'])
