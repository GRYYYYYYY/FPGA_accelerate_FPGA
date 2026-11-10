#!/usr/bin/env python3
"""Read-only view of directory-preserving native RTL and the current bus64 pair."""
import argparse
import json
from pathlib import Path
from experiment_status_v25 import collect as previous
from experiment_status_v6 import ROOT, BASE, workflow, process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=previous(root,base,proc_root)
    for label,folder,script in [
        ('native_directory_recovery_supervisor_v2',root/'data/derived/native_directory_recovery_supervision_20261030_v2','supervise_native_directory_recovery_v2.py'),
        ('native_directory_recovery_RTL_v2',base/'collision_safe_native_owner_recovery_v2','run_recovered_native_rtl_v2.py')]:
        row=workflow(label,folder,script,proc_root)
        if row['status']=='waiting_dependency_or_memory':row['status']='waiting_dependency'
        if label=='native_directory_recovery_RTL_v2' and row.get('stage') in ['rtl','postcheck']:
            phase=row['stage'];path=folder/(phase+'.actual_limits.json');row['phase_process_verified']=False
            if path.exists():
                actual=json.loads(path.read_text());live=process(actual['pid'],proc_root)
                row['phase_process_verified']=bool(live and live['state']!='Z' and
                    live['start_ticks']==actual['start_ticks'] and live['command']==actual['command'])
                row['phase_pid']=actual['pid'];row['actual_address_space']=actual['address_space']
            log=folder/(phase+'.log')
            if log.exists():
                with log.open('rb') as stream:
                    stream.seek(max(0,log.stat().st_size-32768));tail=stream.read().decode(errors='replace')
                progress=[line for line in tail.splitlines() if line.startswith('// RTL Simulation :') and '"Inter-' not in line]
                row['last_logged_progress']=progress[-1] if progress else None
        row['evidence_note']='Process/log observation only, not functional acceptance.'
        result['tasks'].append(row)
    result['new_chain_note']='Original compiler independently audited. Directory-preserving native v2 must finish all4 RTL transactions, original C and independent audit. Bus64 CSR→compact HLS has its own independent gate; no physical/board acceptance implied.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            if row['task'] in {'native_directory_recovery_supervisor_v2','native_directory_recovery_RTL_v2','bus64_pair_execution_v2','recovery_acceptance_supervisor'}:
                extra=' '.join(f'{key}={row[key]}' for key in ['owner_verified','phase_process_verified','completed_modes'] if key in row)
                print(f"{row['task']}: {row['status']} ({row.get('stage')}) {extra}")
                if row.get('last_logged_progress'):print('  '+row['last_logged_progress'])
        print(result['new_chain_note'])
