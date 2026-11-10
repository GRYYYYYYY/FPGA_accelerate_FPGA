#!/usr/bin/env python3
"""Read-only status of the naming diagnosis and new isolated HLS candidate."""
import argparse
import json
from pathlib import Path
from experiment_status_v19 import collect as previous
from experiment_status_v6 import ROOT,BASE,workflow


def collect(root=ROOT,base=BASE,proc_root=Path('/proc')):
    result=previous(root,base,proc_root)
    for label,folder,script in [
        ('native_failure_capture_v1',base/'native_nonzero_failure_capture_v1','capture_native_nonzero_failure_v1.py'),
        ('native_failure_capture_v2',base/'native_nonzero_failure_capture_v2','capture_native_nonzero_failure_v2.py'),
        ('collision_safe_compact_hls_v1',base/'collision_safe_batch_hls_v1','run_collision_safe_batch_hls_v1.py')]:
        row=workflow(label,folder,script,proc_root)
        row['diagnostic_or_candidate_only']=True
        row['full_kernel_accepted']=False
        if (folder/'diagnostic_stop_reason.json').exists():
            row['stop_reason']=json.loads((folder/'diagnostic_stop_reason.json').read_text())['reason']
        if (folder/'state.json').exists():
            state=json.loads((folder/'state.json').read_text())
            row['completed_stages']=state.get('completed',[])
        row['evidence_note']='Live observation only; no repeated large-file audit and no downstream release.'
        result['tasks'].append(row)
    result['new_evidence_reports']={name:(root/'results'/name).exists() for name in [
        'trace_root_address_diagnostic_20261030_v1.json',
        'hls_root_name_reproducer_20261030_v1.json',
        'hls_collided_port_inventory_20261030_v1.json',
        'collision_safe_batch_full44_cpu_20261030_v1.json',
        'collision_safe_batch_cpu_integrity_20261030_v1.json']}
    result['new_chain_note']='New HLS candidate only. Original native/paired/tree/snapshot-read chain failed; new RTL and physical are not submitted by this entry.'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        names={'training_order_control_cpu','compact_nonzero_native_rtl_v2','paired_binary_nonzero_supervisor',
               'route_tree_recovery_supervisor_v2','snapshot_read_serial_supervisor',
               'native_failure_capture_v1','native_failure_capture_v2','collision_safe_compact_hls_v1'}
        for row in result['tasks']:
            if row['task'] in names:print(f"{row['task']}: {row['status']} ({row.get('stage')})")
        print(result['new_chain_note'])
        print('Full experiment completion remains unproven.')
