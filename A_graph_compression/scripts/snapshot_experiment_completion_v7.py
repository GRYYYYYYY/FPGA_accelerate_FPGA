#!/usr/bin/env python3
"""Freeze candidate preparation evidence without promoting it to full RTL proof."""
import json
from pathlib import Path
from datetime import datetime, timezone
from check_vitis_kernel import digest, require
from experiment_status_v6 import collect
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    previous = ROOT / 'EXPERIMENT_STATUS_20261025_v6.json'
    output = ROOT / 'EXPERIMENT_STATUS_20261025_v7.json'
    require(not output.exists(), 'Refuse overwrite')
    result = json.loads(previous.read_text())
    original = json.loads((ROOT / 'EXPERIMENT_STATUS.json').read_text())
    config = json.loads((ROOT / 'configs/experiment.json').read_text())
    require([(r['id'], r['requirement']) for r in result['requirements']] ==
            [(r['id'], r['requirement']) for r in original['requirements']],
            'Original requirement text or identities changed')
    require(len(result['requirements']) == 9 and
            [v['id'] for v in result['configured_variants']] ==
            [v['id'] for v in config['variants']] and len(config['variants']) == 8,
            'Original scope changed')
    checked = {}

    def verify(path, expected):
        if str(path) not in checked:
            checked[str(path)] = digest(path)
        require(checked[str(path)] == expected, 'Evidence changed: ' + str(path))

    for path, expected in result['bindings'].items():
        verify(path, expected)
    names = [
        'hls_binary_fsm_candidate_edit_audit',
        'hls_compact_binary_fsm_candidate_edit_audit',
        'hls_binary_fsm_state_relation_audit',
        'hls_compact_binary_fsm_state_relation_audit',
        'fsm_binary_four_state_regression',
        'paired_binary_fsm_candidates_preparation_audit',
        'binary_fsm_full44_entry_preparation',
        'compact_binary_fsm_full44_entry_preparation',
        'snapshot_dpi_v3_entry_preparation',
        'read_control_v2_entry_preparation',
    ]
    for name in names:
        path = ROOT / 'results' / (name + '_20261025_v1.json')
        report = json.loads(path.read_text())
        for source, expected in report['files'].items():
            verify(source, expected)
        result['bindings'][str(path)] = digest(path)
        result['evidence'][name] = dict(
            path=str(path), sha256=digest(path), status=report['status'],
            scope='Bound preparation or explicitly scoped mechanism evidence; not full IP RTL acceptance')
    hardware = next(r for r in result['requirements'] if r['id'] == 'hardware')
    hardware['status'] = 'native_recovery_active_paired_encoded_rtl_snapshot_and_staged_search_serialized_pending'
    hardware['evidence_keys'] = list(dict.fromkeys(hardware['evidence_keys'] + names))
    hardware['remaining'] = (
        'Native compact full4 recovery must independently pass. CSR and compact encoded full44 '
        'candidates, original full30 snapshot and staged full2 search are serialized, not accepted. '
        'Legal-state relations and the seven-state four-state regression do not prove full IP execution. '
        'Encoded candidate physical resource/timing results are absent; earlier onehot HLS estimates '
        'do not describe these candidates. Packet64 physical timing remains negative. '
        'Full device semantics, platform integration, DDR/HBM board measurements, power and '
        'end-to-end experiments remain outstanding; local XRT previously found zero devices.')
    result['active_process_observations'] = collect()['tasks']
    result['observed_utc'] = datetime.now(timezone.utc).isoformat()
    result['completion_proven'] = False
    result['status'] = 'active'
    result['scope'] = 'Original nine requirements and eight variants retained; candidate preparation is not full RTL, physical or board proof.'
    result['bindings'][str(previous)] = digest(previous)
    for path in [Path(__file__).resolve(), ROOT / 'scripts/experiment_status_v6.py']:
        result['bindings'][str(path)] = digest(path)
    result['findings']['candidate_preparation_binding_files_rechecked'] = len(checked)
    require(all(not r['complete'] for r in result['requirements']), 'Full completion remains unproven')
    atomic(output, result)
    print(f'Frozen v7; {len(checked)} unique bindings verified; original 9 requirements/8 variants; completion false.')


if __name__ == '__main__':
    main()
