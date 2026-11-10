#!/usr/bin/env python3
"""Read-only status including native v3 and its current serial downstream owner."""
import argparse
import json
from pathlib import Path
import re

from experiment_status_v8 import collect as collect_previous
from experiment_status_v6 import ROOT, BASE, workflow, process


def collect(root=ROOT, base=BASE, proc_root=Path('/proc')):
    result = collect_previous(root, base, proc_root)
    definitions = [
        ('compact_native_recovery_v3', base/'compact_native_stack_recovery_v3', 'run_compact_native_stack_recovery_v3.py'),
        ('compact_native_audit_v3', base/'compact_native_stack_final_audit_v3', 'supervise_compact_native_stack_recovery_audit_v3.py'),
        ('integrated_recovery_chain', root/'data/derived/integrated_rtl_recovery_supervision_20261027_v1', 'supervise_integrated_rtl_recovery_v1.py'),
        ('csr_encoded_recovery', base/'compressed_batch_bus64_binary_fsm_rtl_v2', 'run_compressed_bus64_binary_fsm_rtl_v2.py'),
        ('compact_encoded_recovery', base/'compressed_batch_compact_bus64_binary_fsm_rtl_v2', 'run_compressed_compact_bus64_binary_fsm_rtl_v2.py'),
        ('snapshot_recovery_v4', base/'snapshot_dpi_rtl_v4', 'run_snapshot_dpi_rtl_v4.py'),
        ('read_control_recovery_v3', base/'search_read_control_staging_dpi_rtl_v3', 'run_search_read_control_staging_dpi_rtl_v3.py'),
    ]
    for label, folder, script in definitions:
        row = workflow(label, folder, script, proc_root)
        if label == 'integrated_recovery_chain' and row.get('owner_verified') and row.get('stage') == 'waiting_native_v3_independent_acceptance' and row['status'] == 'waiting_dependency_or_memory':
            row['status'] = 'waiting_dependency'
        log = folder/'rtl.log'
        if log.is_file():
            row['last_logged_progress'] = None
            with log.open(errors='replace') as stream:
                for line in stream:
                    m = re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"', line)
                    if m:
                        row['last_logged_progress'] = dict(completed=int(m[1]), total=int(m[2]), simulation_time_ps=int(m[3]))
        if label == 'compact_native_recovery_v3':
            actual = folder/'actual_runtime_limits.json'
            if actual.exists():
                expected = json.loads(actual.read_text())
                live = process(expected['pid'], proc_root)
                try:
                    cwd = str((proc_root/str(expected['pid'])/'cwd').resolve(strict=True))
                except FileNotFoundError:
                    cwd = None
                row['kernel_pid'] = expected['pid']
                row['kernel_identity_verified'] = bool(live and live['state'] != 'Z' and
                    live['start_ticks'] == expected['start_ticks'] and live['command'] == expected['command'] and cwd == expected['cwd'])
            row['audit_report_exists'] = (root/'results/compact_native_stack_recovery_rtl_audit_20261027_v3.json').exists()
        row['evidence_note'] = 'Observation only; no audit SHA revalidation or complete-experiment acceptance.'
        result['tasks'].append(row)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = collect()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for row in result['tasks']:
            progress = row.get('last_logged_progress')
            suffix = f" logged {progress['completed']}/{progress['total']}" if progress else ''
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')


if __name__ == '__main__':
    main()
