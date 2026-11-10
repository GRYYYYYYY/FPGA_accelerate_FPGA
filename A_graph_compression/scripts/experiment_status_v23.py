#!/usr/bin/env python3
"""Read-only new native and paired HLS status with explicit dependency labels."""
import argparse
import json
from pathlib import Path
from experiment_status_v22 import collect as previous
from experiment_status_v6 import ROOT, BASE, workflow, process


def collect(root=ROOT, base=BASE, proc_root=Path('/proc')):
    result = previous(root, base, proc_root)
    for label, folder, script in [
        ('collision_safe_native_final_audit', root/'data/derived/collision_safe_native_audit_supervision_20261030_v1',
         'supervise_collision_safe_native_audit_v1.py'),
        ('collision_safe_bus64_pair', base/'collision_safe_bus64_pair_v1', 'run_collision_safe_bus64_pair_v1.py')]:
        row = workflow(label, folder, script, proc_root)
        if row['status'] == 'waiting_dependency_or_memory': row['status'] = 'waiting_dependency'
        row['free_memory_gate'] = False
        state_path = folder/'state.json'
        if state_path.exists():
            state = json.loads(state_path.read_text())
            row['completed_modes'] = state.get('completed_modes')
            row['mode'] = state.get('mode')
            if label == 'collision_safe_bus64_pair' and state.get('stage') == 'csim_csynth':
                actual_path = folder/f'mode_{state["mode"]}'/'actual_limits.json'
                row['phase_process_verified'] = False
                if actual_path.exists():
                    actual = json.loads(actual_path.read_text()); live = process(actual['pid'], proc_root)
                    row['phase_process_verified'] = bool(live and live['state'] != 'Z' and
                        live['start_ticks'] == actual['start_ticks'] and live['command'] == actual['command'])
                    row['phase_process_pid'] = actual['pid']
        row['evidence_note'] = 'Live observation only; no functional acceptance.'
        result['tasks'].append(row)
    result['new_chain_note'] = ('Existing native compiler→full4tx RTL→C postcheck→independent audit. '
        'After compiler exits successfully: CSR then compact full44 C/HLS; paired independent audit and fresh RTL still required. '
        'No physical/board launch is implied.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--json', action='store_true')
    args = parser.parse_args(); result = collect()
    if args.json: print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for row in result['tasks']:
            if row['task'] in {'collision_safe_native_rtl_v1', 'collision_safe_native_final_audit', 'collision_safe_bus64_pair'}:
                extra = f" phase_process_verified={row['phase_process_verified']}" if 'phase_process_verified' in row else ''
                print(f"{row['task']}: {row['status']} ({row.get('stage')}) owner_verified={row['owner_verified']}{extra}")
        print(result['new_chain_note'])
        print('Full experiment completion remains unproven.')
