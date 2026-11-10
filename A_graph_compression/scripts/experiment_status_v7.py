#!/usr/bin/env python3
"""Extend the frozen v6 read-only observer with component RTL workflow states."""
import argparse
import json
import re
from pathlib import Path

from experiment_status_v6 import BASE, ROOT, collect as collect_previous, workflow


def collect(root=ROOT, base=BASE, proc_root=Path('/proc')):
    result = collect_previous(root, base, proc_root)
    for name in ['site_occupancy', 'route_tree', 'retained_nodes', 'retained_edges']:
        folder = root / 'data/derived' / (name + '_rtl_20261024_v1')
        row = workflow(name + '_component_rtl', folder, name + '_rtl_pipeline.py', proc_root)
        log = folder / 'rtl.log'
        if log.exists():
            with log.open(errors='replace') as stream:
                progress = None
                for line in stream:
                    match = re.search(r'RTL Simulation :\s*(\d+)\s*/\s*(\d+).*@\s*"(\d+)"', line)
                    if match:
                        progress = dict(completed=int(match[1]), total=int(match[2]), simulation_time_ps=int(match[3]))
            row['last_logged_progress'] = progress
        report = root / 'results' / (name + '_rtl_audit_20261024_v1.json')
        row['audit_report_exists'] = report.exists()
        row['audit_report'] = str(report)
        row['evidence_note'] = 'Workflow/log observation only; this command does not verify audit bindings or infer full experiment acceptance.'
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
            progress = task.get('last_logged_progress')
            suffix = f" logged {progress['completed']}/{progress['total']}" if progress else ''
            print(f"{task['task']}: {task['status']} ({task.get('stage')}){suffix}")
        print('Full experiment completion remains unproven. Read-only local observation; no audit binding revalidation.')


if __name__ == '__main__':
    main()
