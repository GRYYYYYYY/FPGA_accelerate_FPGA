#!/usr/bin/env python3
"""Observe authoritative guard aborts and the prepared nonzero encoded entries."""
import argparse
import json
from pathlib import Path
import re
from experiment_status_v17 import collect as collect_previous
from experiment_status_v6 import ROOT,BASE,workflow,process


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=collect_previous(root,base,proc_root)
    definitions=[('snapshot_read_serial_supervisor',root/'data/derived/snapshot_read_serial_supervision_20261029_v1','supervise_snapshot_read_serial_v1.py',None),
                 ('snapshot_current_full30',base/'snapshot_dpi_rtl_v5','run_snapshot_dpi_rtl_v5.py','snapshot_dpi_rtl_audit_20261029_v5.json'),
                 ('read_control_current_full2tx',base/'search_read_control_staging_dpi_rtl_v4','run_search_read_control_staging_dpi_rtl_v4.py','search_read_control_staging_rtl_audit_20261029_v4.json')]
    for label,folder,script,report in definitions:
        row=workflow(label,folder,script,proc_root)
        row['entry_preparation_exists']=(root/'results/snapshot_read_serial_preparation_20261029_v1.json').exists()
        if row['status']=='not_started' and row['entry_preparation_exists']:row['status']='prepared_not_started'
        if row['owner_verified'] and str(row.get('stage','')).startswith('waiting_'):row['status']='waiting_dependency_only'
        row['free_memory_gate_removed_by_user']=True
        if report:row['audit_report_exists']=(root/'results'/report).exists()
        row['last_logged_progress']=None
        log=folder/'rtl.log'
        if log.exists():
            for line in log.read_text(errors='replace').splitlines():
                m=re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"',line)
                if m:row['last_logged_progress']=dict(completed=int(m[1]),total=int(m[2]),simulation_time_ps=int(m[3]))
        row['evidence_note']='Read-only live observation; no SHA re-audit or full-experiment acceptance.'
        result['tasks'].append(row)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--json',action='store_true');args=p.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        current={'snapshot_read_serial_supervisor','snapshot_current_full30','read_control_current_full2tx','route_tree_recovery_supervisor_v2','route_tree_recovery_control_v2','route_tree_recovery_rtl_v2','compact_nonzero_native_supervisor_v2','compact_nonzero_native_rtl_v2','paired_binary_nonzero_supervisor','csr_binary_nonzero_rtl','compact_binary_nonzero_rtl','route_tree_recovery_rtl','site_occupancy_component_rtl','retained_nodes_component_rtl','retained_edges_component_rtl','source_to_route_fresh_training_v2'}
        for row in result['tasks']:
            if row['task'] not in current:continue
            p=row.get('last_logged_progress');suffix=f" logged {p['completed']}/{p['total']}" if p else ''
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')
