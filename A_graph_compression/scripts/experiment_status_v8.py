#!/usr/bin/env python3
"""Read-only status including the independent full50 route-tree recovery."""
import argparse
import json
from pathlib import Path
import re

from experiment_status_v7 import collect as collect_previous
from experiment_status_v6 import ROOT, BASE, workflow


def collect(root=ROOT, base=BASE, proc_root=Path('/proc')):
    result = collect_previous(root, base, proc_root)
    for label, directory, script in [
        ('route_tree_recovery_supervisor', 'route_tree_recovery_supervision_20261027_v1', 'supervise_route_tree_recovery_v1.py'),
        ('route_tree_recovery_control', 'route_tree_rtl_recovery_control_20261027_v1', 'run_route_tree_full50_recovery_v1.py'),
        ('route_tree_recovery_rtl', 'route_tree_rtl_recovery_20261027_v1', 'route_tree_rtl_pipeline.py'),
    ]:
        folder = root / 'data/derived' / directory
        row = workflow(label, folder, script, proc_root)
        if label == 'route_tree_recovery_rtl':
            log = folder / 'rtl.log'
            if log.exists():
                with log.open(errors='replace') as stream:
                    progress = None
                    for line in stream:
                        m = re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"', line)
                        if m:
                            progress = dict(completed=int(m[1]), total=int(m[2]), simulation_time_ps=int(m[3]))
                row['last_logged_progress'] = progress
            report = root / 'results/route_tree_rtl_recovery_audit_20261027_v1.json'
            row['audit_report_exists'] = report.exists()
            row['audit_report'] = str(report)
        row['evidence_note'] = 'Workflow observation only; does not revalidate audit bindings or prove full experiment completion.'
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
        for task in result['tasks']:
            p = task.get('last_logged_progress')
            suffix = f" logged {p['completed']}/{p['total']}" if p else ''
            print(f"{task['task']}: {task['status']} ({task.get('stage')}){suffix}")
        print('Full experiment completion remains unproven; observations are not acceptance audits.')


if __name__ == '__main__':
    main()
