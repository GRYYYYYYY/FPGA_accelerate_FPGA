#!/usr/bin/env python3
"""Record the terminal native guard abort without narrowing original scope."""
import json
from datetime import datetime, timezone
from pathlib import Path
from check_vitis_kernel import digest, require
from experiment_status_v6 import collect
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    previous = ROOT / 'EXPERIMENT_STATUS_20261025_v7.json'
    output = ROOT / 'EXPERIMENT_STATUS_20261025_v8.json'
    require(not output.exists(), 'Refuse overwrite')
    result = json.loads(previous.read_text())
    original = json.loads((ROOT / 'EXPERIMENT_STATUS.json').read_text())
    config = json.loads((ROOT / 'configs/experiment.json').read_text())
    require([(r['id'], r['requirement']) for r in result['requirements']] ==
            [(r['id'], r['requirement']) for r in original['requirements']] and
            len(result['requirements']) == 9, 'Original requirements changed')
    require([v['id'] for v in result['configured_variants']] ==
            [v['id'] for v in config['variants']] and len(config['variants']) == 8,
            'Original variants changed')
    for path, checksum in result['bindings'].items():
        require(digest(path) == checksum, 'Historical binding changed: ' + path)
    additions = {
        'compact_native_v2_terminal_guard_abort': ROOT / 'results/compact_native_v2_guard_abort_20261025_v1.json',
        'paired_encoded_physical_preparation': ROOT / 'results/paired_binary_fsm_physical_preparation_20261025_v1.json',
        'post_abort_memory_observation': ROOT / 'data/derived/compact_native_v2_post_abort_memory_observation_20261025_v1.json',
    }
    for key, path in additions.items():
        report = json.loads(path.read_text())
        for source, checksum in report.get('files', {}).items():
            require(digest(source) == checksum, 'Changed new evidence: ' + source)
        result['bindings'][str(path)] = digest(path)
        result['evidence'][key] = dict(path=str(path), sha256=digest(path),
            status=report['status'], scope='Terminal failure, preparation or bounded observation; not acceptance')
    incident = json.loads(additions['compact_native_v2_terminal_guard_abort'].read_text())
    require(incident['receipt']['resource_abort'] is True and incident['receipt']['exit_code'] == -15
            and incident['completed_transactions'] == 0, 'Wrong terminal incident')
    require(all(not Path(p).exists() for p in incident['acceptance_reports_absent']),
            'Acceptance changed; inspect before freezing')
    hardware = next(r for r in result['requirements'] if r['id'] == 'hardware')
    hardware['status'] = 'native_v2_runtime_guard_aborted_entire_dependent_chain_failed_physical_prepared_only'
    hardware['evidence_keys'] = list(dict.fromkeys(hardware['evidence_keys'] + list(additions)))
    hardware['remaining'] = (
        'Native compact v2 was memory-guard terminated at0/4 after26125.140s; no accepted native '
        'full44 result exists. All four dependent supervisors failed without creating trials. '
        'Paired encoded full44 RTL, full30 snapshot and staged full2 search remain unexecuted. '
        'Encoded physical inputs are frozen only; no execution entry or physical run. '
        'Four independent component RTL runs require terminal output and independent audits. '
        'Resource admission, full special-resource semantics, physical timing closure, platform '
        'integration, DDR/HBM board measurements, power and end-to-end proof remain outstanding.')
    result['active_process_observations'] = collect()['tasks']
    result['observed_utc'] = datetime.now(timezone.utc).isoformat()
    result['status'] = 'active'
    result['completion_proven'] = False
    result['findings']['native_v2_terminal_runtime'] = dict(exit_code=-15, resource_abort=True,
        completed_transactions=0, elapsed_seconds=incident['receipt']['elapsed_seconds'])
    for path in [previous, Path(__file__).resolve(), ROOT / 'scripts/experiment_status_v6.py']:
        result['bindings'][str(path)] = digest(path)
    require(all(not r['complete'] for r in result['requirements']), 'Completion remains unproven')
    atomic(output, result)
    print('Frozen v8: original9 requirements/8variants retained; terminal chain failure recorded; completion false.')


if __name__ == '__main__':
    main()
