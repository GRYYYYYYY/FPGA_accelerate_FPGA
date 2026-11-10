#!/usr/bin/env python3
"""Observe authoritative guard aborts and the prepared nonzero encoded entries."""
import argparse
import json
from pathlib import Path
import re
from experiment_status_v12 import collect as collect_previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=collect_previous(root,base,proc_root)
    control=root/'data/derived/route_tree_rtl_recovery_control_20261027_v1/state.json'
    if control.exists():
        record=json.loads(control.read_text())
        if record.get('status')=='failed' and record.get('resource_abort') is True:
            row=next(t for t in result['tasks'] if t['task']=='route_tree_recovery_rtl')
            if not row['owner_verified']:
                row.update(status='resource_aborted',terminal_authority=str(control),recorded_raw_free_bytes=record['observed_free_bytes'])
    definitions=[('paired_binary_nonzero_supervisor',root/'data/derived/paired_binary_nonzero_supervision_20261029_v1','supervise_paired_binary_nonzero_full44_v1.py',None),
                 ('csr_binary_nonzero_rtl',base/'compressed_batch_bus64_binary_nonzero_rtl_v1','run_binary_nonzero_full44_v1.py',0),
                 ('compact_binary_nonzero_rtl',base/'compressed_batch_compact_bus64_binary_nonzero_rtl_v1','run_binary_nonzero_full44_v1.py',1)]
    for label,folder,script,mode in definitions:
        row=workflow(label,folder,script,proc_root)
        row['entry_preparation_exists']=(root/'results/paired_binary_nonzero_entries_preparation_20261029_v1.json').exists()
        row['nonzero_native_audit_exists']=(root/'results/compact_nonzero_native_rtl_audit_20261029_v1.json').exists()
        if mode is not None:
            row['graph_mode']=mode
            if row['owner_verified']:
                owner=process(row['owner_pid'],proc_root)
                if owner['command'].split()[-2:]!=['--mode',str(mode)]:
                    row.update(owner_verified=False,status='owner_missing_or_mismatched_no_terminal_receipt')
            row['audit_report_exists']=(root/'results'/('compressed_bus64_binary_nonzero_rtl_audit_20261029_v1.json' if mode==0 else 'compressed_compact_bus64_binary_nonzero_rtl_audit_20261029_v1.json')).exists()
            log=folder/'rtl.log';row['last_logged_progress']=None
            if log.exists():
                for line in log.read_text(errors='replace').splitlines():
                    m=re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"',line)
                    if m:row['last_logged_progress']=dict(completed=int(m[1]),total=int(m[2]),simulation_time_ps=int(m[3]))
        row['evidence_note']='Read-only state/identity/report-existence observation, not SHA revalidation or acceptance.'
        result['tasks'].append(row)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');args=p.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            p=row.get('last_logged_progress');suffix=f" logged {p['completed']}/{p['total']}" if p else ''
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')
