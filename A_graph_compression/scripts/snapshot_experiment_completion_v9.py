#!/usr/bin/env python3
"""Add accepted component RTL and interrupted tree evidence, preserving full scope."""
import json
from datetime import datetime, timezone
from pathlib import Path
from check_vitis_kernel import digest, require
from experiment_status_v7 import collect
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    previous = ROOT / 'EXPERIMENT_STATUS_20261025_v8.json'
    output = ROOT / 'EXPERIMENT_STATUS_20261027_v9.json'
    require(not output.exists(), 'Refuse overwrite')
    result = json.loads(previous.read_text())
    original = json.loads((ROOT / 'EXPERIMENT_STATUS.json').read_text())
    config = json.loads((ROOT / 'configs/experiment.json').read_text())
    require(len(result['requirements']) == 9 and
            [(r['id'], r['requirement']) for r in result['requirements']] ==
            [(r['id'], r['requirement']) for r in original['requirements']], 'Changed original requirements')
    require(len(result['configured_variants']) == 8 and
            [v['id'] for v in result['configured_variants']] ==
            [v['id'] for v in config['variants']], 'Changed original variants')
    for path, checksum in result['bindings'].items():
        require(digest(path) == checksum, 'Historical evidence changed: ' + path)
    additions = {}
    for name, count in [('site_occupancy', 52), ('retained_nodes', 37), ('retained_edges', 37)]:
        path = ROOT / ('results/' + name + '_rtl_audit_20261024_v1.json')
        report = json.loads(path.read_text())
        require(report['status'] == 'production_' + name + '_full_depth_' + str(count) + '_transactions_rtl_verified',
                'Wrong accepted component status')
        require(report['transactions'] == count and len(report['cycles']) == count and
                all(c > 0 for c in report['cycles']), 'Incomplete component transactions')
        additions[name + '_accepted_component_rtl'] = (path, 'Component full-depth RTL function only; not board or integrated acceptance')
    additions['route_tree_interruption'] = (ROOT / 'results/route_tree_interruption_20261027_v1.json',
                                           'Interrupted at7/50 without terminal receipt; cause unknown')
    additions['route_tree_recovery_inventory'] = (ROOT / 'results/route_tree_rtl_recovery_inventory_20261027_v1.json',
                                                 'Compiled snapshot identity only; recovery unexecuted')
    for key, (path, scope) in additions.items():
        report = json.loads(path.read_text())
        for source, checksum in report['files'].items():
            require(digest(source) == checksum, 'Changed added evidence: ' + source)
        result['bindings'][str(path)] = digest(path)
        result['evidence'][key] = dict(path=str(path), sha256=digest(path), status=report['status'], scope=scope)
    hardware = next(r for r in result['requirements'] if r['id'] == 'hardware')
    hardware['status'] = 'three_components_rtl_verified_tree_interrupted_integrated_chain_failed'
    hardware['evidence_keys'] = list(dict.fromkeys(hardware['evidence_keys'] + list(additions)))
    hardware['remaining'] = (
        'Site occupancy52, retained nodes37 and retained edges37 full-depth synthetic RTL transactions '
        'are independently verified. Route tree stopped at7/50 without terminal receipt and remains '
        'unaccepted. Native full44 and its dependent chain remain failed; paired encoded full44 RTL, '
        'full30 snapshot and staged full2 RTL remain unexecuted. Physical inputs are preparation only. '
        'Resource admission, full special-resource semantics, physical timing, platform integration, '
        'DDR/HBM board bandwidth, power and end-to-end measurements remain outstanding.')
    result['active_process_observations'] = collect()['tasks']
    result['observed_utc'] = datetime.now(timezone.utc).isoformat()
    result['status'] = 'active'
    result['completion_proven'] = False
    for path in [previous, Path(__file__).resolve(), ROOT / 'scripts/experiment_status_v7.py',
                 ROOT / 'scripts/check_route_tree_recovery_preflight_v1.py']:
        result['bindings'][str(path)] = digest(path)
    require(all(not r['complete'] for r in result['requirements']), 'Full completion remains unproven')
    atomic(output, result)
    print('Frozen v9: original9 requirements/8variants; three accepted components; tree interrupted; full completion false.', flush=True)


if __name__ == '__main__':
    main()
