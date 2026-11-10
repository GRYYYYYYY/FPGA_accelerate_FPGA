"""Summarize saved Vivado reports; preserve warnings as unresolved evidence."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/vivado_state_quality_20261022'


def main():
    config = json.loads((ROOT / 'results/research_chain_20261022T183749Z/matrix_config.json').read_text())
    hashes = {d['id']: d['reference_results'] for d in config['datasets']}
    cases = [
        ('logicnets_jscl', 'serial', 'logicnets_restored', 'physical_restore_20261022T185253Z'),
        ('logicnets_jscl', 'batch', 'logicnets_batch', 'static_restore_logicnets_batch_20261022T190223Z'),
        ('vtr_mcml', 'serial', 'vtr_mcml_serial', 'static_restore_vtr_mcml_serial_20261022T190224Z'),
        ('vtr_mcml', 'batch', 'vtr_mcml_batch', 'static_restore_vtr_mcml_batch_20261022T191417Z'),
    ]
    rows = []
    for dataset, mode, prefix, restored in cases:
        route = OUT / (prefix + '_route_status.rpt')
        drc = OUT / (prefix + '_route_drc.rpt')
        restore = ROOT / 'results' / restored / 'restore.log'
        text = route.read_text()
        def count(label):
            return int(re.search(re.escape(label) + r'\.+\s*:\s*(\d+)', text)[1])
        assert 'differences=0' in restore.read_text()
        violations = int(re.search(r'Violations found:\s*(\d+)', drc.read_text())[1])
        row = dict(dataset=dataset, mode=mode, cpp_result_sha256=hashes[dataset][mode],
                   strict_original_physical_differences=0,
                   fully_routed_nets=count('# of fully routed nets'),
                   routable_nets=count('# of routable nets'),
                   routing_errors=count('# of nets with routing errors'),
                   rtstat_violations=violations,
                   status='routing_passed_with_unresolved_warning' if violations else 'routing_passed',
                   evidence={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (route, drc, restore)})
        assert row['routing_errors'] == 0 and row['fully_routed_nets'] == row['routable_nets']
        if violations:
            row['warning'] = 'RTSTAT-10: 72 nets have no routable loads; absent in unrouted input. Cause unresolved.'
        rows.append(row)
    record = dict(vivado_version='2022.2', outputs=rows, full_drc='not_measured', timing='not_measured',
                  scope='Four unique result hashes only; storage variants covered only when result hashes match.',
                  normalization='Remove proved preprocessing-only static annotations; restore original static/clock PIPs.',
                  input_warning_baseline=json.loads((OUT / 'vtr_mcml_warning_baseline.json').read_text()))
    (OUT / 'all_outputs_quality_manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('dataset', 'mode', 'fully_routed_nets', 'rtstat_violations')} for r in rows], indent=2))


if __name__ == '__main__':
    main()
