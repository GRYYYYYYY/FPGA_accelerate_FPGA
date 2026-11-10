#!/usr/bin/env python3
"""Read-only live ownership view including the versioned bus64 audit recovery."""
import argparse,json
from pathlib import Path
from experiment_status_v26 import collect as previous
from experiment_status_v6 import ROOT,BASE,workflow

def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=previous(root,base,proc_root)
    for label,folder,script in [
        ('bus64_fresh_setup_supervisor_v1',root/'data/derived/bus64_fresh_setup_supervision_20261030_v1','supervise_bus64_fresh_setup_v1.py'),
        ('bus64_audit_recovery_supervisor_v1',root/'data/derived/bus64_audit_recovery_supervision_20261030_v1','supervise_bus64_audit_recovery_v1.py'),
        ('bus64_full_rtl_supervisor_v1',root/'data/derived/bus64_full_rtl_supervision_20261030_v1','supervise_bus64_full_rtl_v1.py'),
        ('bus64_audit_recovery_supervisor_v2',root/'data/derived/bus64_audit_recovery_supervision_20261030_v2','supervise_bus64_audit_recovery_v2.py'),
        ('bus64_full_rtl_supervisor_v2',root/'data/derived/bus64_full_rtl_supervision_20261030_v2','supervise_bus64_full_rtl_v2.py'),
        ('bus64_audit_recovery_supervisor_v3',root/'data/derived/bus64_audit_recovery_supervision_20261030_v3','supervise_bus64_audit_recovery_v3.py'),
        ('bus64_full_rtl_supervisor_v3',root/'data/derived/bus64_full_rtl_supervision_20261030_v3','supervise_bus64_full_rtl_v3.py')]:
        row=workflow(label,folder,script,proc_root)
        if row['status']=='waiting_dependency_or_memory':row['status']='waiting_dependency'
        row['evidence_note']='Ownership and state only; completed steps are not complete-experiment acceptance.'
        result['tasks'].append(row)
    result['new_chain_note']='Bus64 RTL waits for the native full4-transaction independent audit and both nonzero-input audits. Process activity is not transaction acceptance. Use --json for complete historical states; physical/board validation remains pending.'
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true');args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            if row['task'] in {'native_directory_recovery_supervisor_v2','native_directory_recovery_RTL_v2','bus64_pair_execution_v2','bus64_audit_recovery_supervisor_v3','bus64_full_rtl_supervisor_v3'}:
                extra=' '.join(f'{key}={row[key]}' for key in ['owner_verified','phase_process_verified','completed_modes'] if key in row)
                print(f"{row['task']}: {row['status']} ({row.get('stage')}) {extra}")
                if row.get('last_logged_progress'):print('  '+row['last_logged_progress'])
        print(result['new_chain_note'])
