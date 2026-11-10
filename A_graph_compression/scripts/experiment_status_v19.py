#!/usr/bin/env python3
"""Observe the original RTL chain and the supplemental complete CPU order control."""
import argparse
import json
from pathlib import Path
import re
from experiment_status_v18 import collect as collect_previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=collect_previous(root,base,proc_root)
    definitions=[('training_order_control_supervisor',root/'data/derived/training_order_control_supervision_20261029_v1','supervise_training_order_control_v1.py',None),
                 ('training_order_control_cpu',root/'data/derived/training_order_control_20261029_v1','run_training_order_control_v1.py','training_order_control_audit_20261029_v1.json')]
    for label,folder,script,report in definitions:
        row=workflow(label,folder,script,proc_root)
        row['entry_preparation_exists']=(root/'results/training_order_control_preparation_20261029_v1.json').exists()
        if row['status']=='not_started' and row['entry_preparation_exists']:row['status']='prepared_not_started'
        if row['owner_verified'] and str(row.get('stage','')).startswith('waiting_'):row['status']='waiting_dependency_only'
        row['free_memory_gate_removed_by_user']=True
        if report:row['audit_report_exists']=(root/'results'/report).exists()
        row['last_logged_progress']=None
        state_path=folder/'state.json'
        if state_path.exists():
            state=json.loads(state_path.read_text())
            row['completed_workers']=state.get('completed_workers')
            row['completed_blocks']=state.get('completed_blocks')
            row['condition']=state.get('condition')
            row['position']=state.get('position')
        row['planned_workers']=18
        row['evidence_note']='Read-only live observation; no SHA re-audit or full-experiment acceptance.'
        result['tasks'].append(row)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');args=p.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        current={'training_order_control_supervisor','training_order_control_cpu','snapshot_read_serial_supervisor','snapshot_current_full30','read_control_current_full2tx','route_tree_recovery_supervisor_v2','route_tree_recovery_control_v2','route_tree_recovery_rtl_v2','compact_nonzero_native_supervisor_v2','compact_nonzero_native_rtl_v2','paired_binary_nonzero_supervisor','csr_binary_nonzero_rtl','compact_binary_nonzero_rtl','route_tree_recovery_rtl','site_occupancy_component_rtl','retained_nodes_component_rtl','retained_edges_component_rtl','source_to_route_fresh_training_v2'}
        for row in result['tasks']:
            if row['task'] not in current:continue
            p=row.get('last_logged_progress');suffix=f" logged {p['completed']}/{p['total']}" if p else ''
            if row.get('completed_workers') is not None:suffix+=f" workers {row['completed_workers']}/18, audited blocks {row['completed_blocks']}/6"
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')
