#!/usr/bin/env python3
"""Observe authoritative guard aborts and the prepared nonzero encoded entries."""
import argparse
import json
from pathlib import Path
import re
from experiment_status_v16 import collect as collect_previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=collect_previous(root,base,proc_root)
    definitions=[('route_tree_recovery_supervisor_v2',root/'data/derived/route_tree_recovery_supervision_20261029_v2','supervise_route_tree_recovery_v2.py'),
                 ('route_tree_recovery_control_v2',root/'data/derived/route_tree_rtl_recovery_control_20261029_v2','run_route_tree_full50_recovery_v2.py'),
                 ('route_tree_recovery_rtl_v2',root/'data/derived/route_tree_rtl_recovery_20261029_v2','route_tree_rtl_pipeline_v2.py')]
    for label,folder,script in definitions:
        row=workflow(label,folder,script,proc_root)
        row['entry_preparation_exists']=(root/'results/route_tree_serial_recovery_preparation_20261029_v2.json').exists()
        if row['status']=='not_started' and row['entry_preparation_exists']:row['status']='prepared_not_started'
        row['free_memory_gate_removed_by_user']=True
        row['audit_report_exists']=(root/'results/route_tree_rtl_recovery_audit_20261029_v2.json').exists()
        row['last_logged_progress']=None
        log=folder/'rtl.log'
        if log.exists():
            for line in log.read_text(errors='replace').splitlines():
                m=re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"',line)
                if m:row['last_logged_progress']=dict(completed=int(m[1]),total=int(m[2]),simulation_time_ps=int(m[3]))
        control=root/'data/derived/route_tree_rtl_recovery_control_20261029_v2/state.json'
        if label=='route_tree_recovery_rtl_v2' and control.exists() and not row['owner_verified']:
            record=json.loads(control.read_text())
            if record.get('status')=='failed' and record.get('resource_abort') is True:
                row.update(status='resource_aborted',terminal_authority=str(control))
        row['evidence_note']='Read-only workflow/identity/report existence, not independent acceptance or SHA audit.'
        result['tasks'].append(row)
    for row in result['tasks']:
        if row['task'] in ['paired_binary_nonzero_supervisor','route_tree_recovery_supervisor_v2'] and row['owner_verified'] and str(row.get('stage','')).startswith('waiting_'):
            row['status']='waiting_dependency_only'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');args=p.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        current={'route_tree_recovery_supervisor_v2','route_tree_recovery_control_v2','route_tree_recovery_rtl_v2','compact_nonzero_native_supervisor_v2','compact_nonzero_native_rtl_v2','paired_binary_nonzero_supervisor','csr_binary_nonzero_rtl','compact_binary_nonzero_rtl','route_tree_recovery_rtl','site_occupancy_component_rtl','retained_nodes_component_rtl','retained_edges_component_rtl','source_to_route_fresh_training_v2'}
        for row in result['tasks']:
            if row['task'] not in current:continue
            p=row.get('last_logged_progress');suffix=f" logged {p['completed']}/{p['total']}" if p else ''
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')
