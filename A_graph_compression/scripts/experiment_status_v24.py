#!/usr/bin/env python3
"""Expose owner loss and the separately verified surviving compiler observer."""
import argparse
import json
from pathlib import Path
from experiment_status_v23 import collect as previous
from experiment_status_v6 import ROOT, BASE, workflow, process


def collect(root=ROOT, base=BASE, proc_root=Path('/proc')):
    result = previous(root,base,proc_root)
    folder = root/'data/derived/collision_safe_native_compiler_observation_20261030_v1'
    row = workflow('surviving_native_compiler_observer',folder,'observe_orphaned_native_compiler_v1.py',proc_root)
    path = folder/'plan.json'
    if path.exists():
        plan = json.loads(path.read_text())
        for name in ['compiler','timer']:
            recorded = plan[name]; live = process(recorded['pid'],proc_root)
            row[name+'_verified'] = bool(live and live['state'] != 'Z' and
                live['start_ticks'] == recorded['start_ticks'] and live['command'] == recorded['command'])
            row[name+'_pid'] = recorded['pid']
    row['rtl_accepted'] = False
    result['tasks'].append(row)
    result['new_chain_note'] = ('Original native driver exited143; both dependent supervisors stopped. '
        'A separate observer tracks the surviving original compiler without restarting it. '
        'Compiler terminal evidence requires independent recovery audit before a new full4tx RTL/C execution. '
        'Prepared bus64 pair has not run. Full experiment remains incomplete.')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',action='store_true')
    args=parser.parse_args();result=collect()
    if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        for row in result['tasks']:
            if row['task'] in {'collision_safe_native_rtl_v1','collision_safe_native_final_audit','collision_safe_bus64_pair','surviving_native_compiler_observer'}:
                extra=' '.join(f'{key}={row[key]}' for key in ['owner_verified','phase_process_verified','compiler_verified','timer_verified'] if key in row)
                print(f"{row['task']}: {row['status']} ({row.get('stage')}) {extra}")
        print(result['new_chain_note'])
