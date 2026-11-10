#!/usr/bin/env python3
"""Observe nonzero native recovery alongside original failed and live workflows."""
import argparse
import json
from pathlib import Path
import re
from experiment_status_v14 import collect as collect_previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=collect_previous(root,base,proc_root)
    for label,folder,script in [
        ('compact_nonzero_native_supervisor_v2',root/'data/derived/compact_nonzero_native_supervision_20261029_v2','supervise_compact_nonzero_native_rtl_v2.py'),
        ('compact_nonzero_native_rtl_v2',base/'compact_nonzero_native_rtl_v2','run_compact_nonzero_native_rtl_v2.py'),
    ]:
        row=workflow(label,folder,script,proc_root)
        if label=='compact_nonzero_native_rtl_v2':
            log=folder/'rtl.log';row['last_logged_progress']=None
            if log.exists():
                for line in log.read_text(errors='replace').splitlines():
                    match=re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"',line)
                    if match:row['last_logged_progress']=dict(completed=int(match[1]),total=int(match[2]),simulation_time_ps=int(match[3]))
            path=folder/(str(row.get('stage'))+'.actual_limits.json')
            if path.exists():
                expected=json.loads(path.read_text());actual=process(expected['pid'],proc_root)
                try:cwd=str((proc_root/str(expected['pid'])/'cwd').resolve(strict=True))
                except FileNotFoundError:cwd=None
                row['phase_process_pid']=expected['pid']
                row['phase_process_identity_verified']=bool(actual and actual['state']!='Z' and actual['start_ticks']==expected['start_ticks'] and actual['command']==expected['command'] and cwd==expected['cwd'])
        row['entry_version']=2
        row['free_memory_gate_removed_by_user']=True
        row['audit_report_exists']=(root/'results/compact_nonzero_native_rtl_audit_20261029_v2.json').exists()
        row['evidence_note']='Read-only observation; no SHA revalidation or full-experiment acceptance. Original native v3 failure remains separate.'
        result['tasks'].append(row)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');args=p.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            progress=row.get('last_logged_progress');suffix=f" logged {progress['completed']}/{progress['total']}" if progress else ''
            if 'successful_worker_receipts' in row:suffix+=' worker receipts '+str(row['successful_worker_receipts'])
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')
