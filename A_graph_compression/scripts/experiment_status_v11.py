#!/usr/bin/env python3
"""Observe current RTL recoveries and the independent training-inclusive CPU experiment."""
import argparse
import json
from pathlib import Path

from experiment_status_v10 import collect as collect_previous
from experiment_status_v6 import ROOT, BASE, workflow, process


def collect(root=ROOT, base=BASE, proc_root=Path('/proc')):
    result = collect_previous(root, base, proc_root)
    row = workflow('source_to_route_fresh_training_v2', root/'data/derived/source_to_route_training_supervision_20261027_v2',
                   'supervise_source_to_route_training_v2.py', proc_root)
    row['worker_observations'] = []
    row['successful_worker_receipts'] = dict(validation=0, statistics=0)
    for label, folder, pattern in [
        ('validation', root/'data/derived/source_to_route_training_validation_20261027_v2', 'worker_*.submission.json'),
        ('statistics', root/'data/derived/source_to_route_training_statistics_20261027_v2', 'block_*/worker_*.submission.json'),
    ]:
        for path in sorted(folder.glob(pattern)):
            record = json.loads(path.read_text())
            owner = process(record['child_pid'], proc_root)
            command_path = proc_root/str(record['child_pid'])/'cmdline'
            try:
                actual_command = command_path.read_bytes().rstrip(b'\0').decode().split('\0')
            except FileNotFoundError:
                actual_command = None
            verified = bool(owner and owner['state'] != 'Z' and actual_command == record['command'])
            receipt = path.with_name(path.name.replace('.submission.json', '.receipt.json'))
            completed = receipt.is_file() and json.loads(receipt.read_text()).get('exit_code') == 0
            row['successful_worker_receipts'][label] += int(completed)
            if verified:
                row['worker_observations'].append(dict(kind=label, submission=str(path), pid=record['child_pid'],
                                                       owner_verified=True, declared_cpu=record['cpu']))
    row['validation_audit_exists'] = (root/'results/source_to_route_training_validation_audit_20261027_v2.json').exists()
    row['statistics_audit_exists'] = (root/'results/source_to_route_training_statistics_audit_20261027_v2.json').exists()
    row['evidence_note'] = 'Receipt counts and live command matches only; no semantic audit/SHA revalidation or complete-experiment proof.'
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
            if 'successful_worker_receipts' in row:
                suffix += ' worker receipts '+str(row['successful_worker_receipts'])
            print(f"{row['task']}: {row['status']} ({row.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')


if __name__ == '__main__':
    main()
