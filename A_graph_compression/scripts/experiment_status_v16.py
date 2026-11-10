#!/usr/bin/env python3
"""Observe authoritative guard aborts and the prepared nonzero encoded entries."""
import argparse
import json
from pathlib import Path
import re
from experiment_status_v15 import collect as collect_previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=collect_previous(root,base,proc_root)
    for row in result['tasks']:
        if row['task'] in ['paired_binary_nonzero_supervisor','csr_binary_nonzero_rtl','compact_binary_nonzero_rtl']:
            row['task'] += '_v2'
    definitions=[('paired_binary_nonzero_supervisor',root/'data/derived/paired_binary_nonzero_supervision_20261029_v3','supervise_paired_binary_nonzero_full44_v3.py',None),
                 ('csr_binary_nonzero_rtl',base/'compressed_batch_bus64_binary_nonzero_rtl_v3','run_binary_nonzero_full44_v3.py',0),
                 ('compact_binary_nonzero_rtl',base/'compressed_batch_compact_bus64_binary_nonzero_rtl_v3','run_binary_nonzero_full44_v3.py',1)]
    for label,folder,script,mode in definitions:
        row=workflow(label,folder,script,proc_root)
        row['entry_version']=3
        row['free_memory_gate_removed_by_user']=True
        row['entry_preparation_exists']=(root/'results/paired_binary_nonzero_entries_preparation_20261029_v3.json').exists()
        if row['status']=='not_started' and row['entry_preparation_exists']:row['status']='prepared_not_started'
        row['nonzero_native_audit_exists']=(root/'results/compact_nonzero_native_rtl_audit_20261029_v2.json').exists()
        if mode is not None:
            row['graph_mode']=mode
            if row['owner_verified']:
                owner=process(row['owner_pid'],proc_root)
                if owner['command'].split()[-2:]!=['--mode',str(mode)]:
                    row.update(owner_verified=False,status='owner_missing_or_mismatched_no_terminal_receipt')
            row['audit_report_exists']=(root/'results'/('compressed_bus64_binary_nonzero_rtl_audit_20261029_v2.json' if mode==0 else 'compressed_compact_bus64_binary_nonzero_rtl_audit_20261029_v2.json')).exists()
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
        current={'compact_nonzero_native_supervisor_v2','compact_nonzero_native_rtl_v2','paired_binary_nonzero_supervisor','csr_binary_nonzero_rtl','compact_binary_nonzero_rtl','route_tree_recovery_rtl','site_occupancy_component_rtl','retained_nodes_component_rtl','retained_edges_component_rtl','source_to_route_fresh_training_v2'}
        for row in result['tasks']:
            if row['task'] not in current:continue
            p=row.get('last_logged_progress');suffix=f" logged {p['completed']}/{p['total']}" if p else ''
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')
