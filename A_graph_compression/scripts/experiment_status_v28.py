#!/usr/bin/env python3
"""Read-only live tasks plus independently generated audit report receipts."""
import argparse
import hashlib
import json

from experiment_status_v27 import collect as previous
from experiment_status_v6 import ROOT, BASE, workflow


def collect(root=ROOT, base=BASE):
    result = previous(root, base)
    row = workflow('route_tree_recovery_supervisor_v3',
                   root / 'data/derived/route_tree_recovery_supervision_20261031_v3',
                   'supervise_route_tree_recovery_v3.py')
    if row['status'] == 'waiting_dependency_or_memory':
        row['status'] = 'waiting_dependency'
    result['tasks'].append(row)
    row = workflow('snapshot_read_serial_supervisor_v2',
                   root / 'data/derived/snapshot_read_serial_supervision_20261031_v2',
                   'supervise_snapshot_read_serial_v2.py')
    if row['status'] == 'waiting_dependency_or_memory':
        row['status'] = 'waiting_dependency'
    result['tasks'].append(row)
    folder = root / 'data/derived/bus64_audit_recovery_supervision_20261030_v3'
    result['audit_receipts'] = []
    for step in ('pair_independent_audit', 'mode_0_setup_audit',
                 'mode_0_nonzero_audit', 'mode_1_setup_audit',
                 'mode_1_nonzero_audit'):
        row = {'step': step, 'report_receipt_verified': False}
        try:
            recorded = json.loads((folder / (step + '.result.json')).read_text())
            receipt = json.loads((folder / (step + '.receipt.json')).read_text())
            report_path = root / recorded['report']
            report_bytes = report_path.read_bytes()
            report = json.loads(report_bytes)
            log_bytes = (folder / (step + '.log')).read_bytes()
            row.update(report=str(report_path), status=report['status'])
            row['report_receipt_verified'] = (
                receipt['exit_code'] == 0 and receipt['abort_reason'] is None
                and hashlib.sha256(report_bytes).hexdigest() == recorded['sha256']
                and report['status'] == recorded['status']
                and hashlib.sha256(log_bytes).hexdigest() == receipt['log_sha256']
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            row['observation_error'] = str(exc)
        result['audit_receipts'].append(row)
    result['audit_receipt_note'] = (
        'Report/result/log/exit receipts checked now; underlying artifact bindings '
        'are not re-audited by this observer. These are C/HLS/setup/input audits, '
        'not full RTL, physical or board acceptance.'
    )
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = collect()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        current = {'native_directory_recovery_supervisor_v2',
                   'native_directory_recovery_RTL_v2', 'bus64_pair_execution_v2',
                   'bus64_audit_recovery_supervisor_v3', 'bus64_full_rtl_supervisor_v3',
                   'route_tree_recovery_supervisor_v3', 'snapshot_read_serial_supervisor_v2'}
        for row in result['tasks']:
            if row['task'] not in current:
                continue
            stage = row.get('stage')
            if row['task'] == 'bus64_pair_execution_v2' and row['status'] == 'complete':
                stage = 'C_and_HLS_execution_complete'
            extra = ' '.join(f'{key}={row[key]}' for key in
                             ('owner_verified', 'phase_process_verified', 'completed_modes')
                             if key in row)
            print(f"{row['task']}: {row['status']} ({stage}) {extra}")
            if row.get('last_logged_progress'):
                print('  ' + row['last_logged_progress'])
        for row in result['audit_receipts']:
            print(f"{row['step']}: report_receipt_verified={row['report_receipt_verified']}")
        print(result['audit_receipt_note'])
        print(result['new_chain_note'])
