"""Restore the original accepted OOC artifact and bind it to the full-capacity RTL fixture."""
from pathlib import Path
import datetime
import json
import sys
from recover_probe_inputs_new_host_v2 import ROOT, DEST, ARCHIVES, recover, sha

sys.path.insert(0, str(ROOT / 'scripts'))
from check_stage_static_cp_fixture_parameters_v1 import defines, fixture_parameters


def main():
    name = 'stage_static_cp_synth_v1'
    index = json.loads((ARCHIVES / (name + '.json')).read_text())
    recovered = recover(name, sorted(index['members']))
    synth = DEST / name
    reference = DEST / 'stage_static_cp_host_full_static_v1'
    sm = json.loads((synth / 'manifest.json').read_text())
    sa = json.loads((synth / 'source_bound_audit.json').read_text())
    fm = json.loads((reference / 'manifest.json').read_text())
    fa = json.loads((reference / 'source_bound_audit.json').read_text())
    accepted = ROOT / 'results/stage_static_cp_synth_20261030.json'
    ar = json.loads(accepted.read_text())
    assert ar['status'] == 'matched_static_stage_ooc_actual_restored' and ar['audit'] == sa
    assert sm['status'] == fm['status'] == 'observed'
    assert sa['manifest_sha256'] == sha(synth / 'manifest.json')
    assert len(sm['rtl']) == 133 and len(fm['rtl']) == 136
    for n in sm['rtl']:
        assert sha(synth / 'sources' / n) == sm['sources'][n] == fm['sources'][n]['sha256'] == sha(reference / 'sources' / n), n
    macros = defines(fm['cases']['full']['commands'][0]['argv'])
    actual = fixture_parameters((reference / 'sources/tb_query_fault.sv').read_text(),
                                (synth / 'sources/query_residency_system.sv').read_text(), macros)
    assert actual == sm['parameters'] == fm['parameters'] == fa['parameters'] and actual['SLOTS'] == 32
    report = {
        'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'original_synthesis_archive_restored_and_full_fixture_sources_parameters_matched',
        'recovered': recovered, 'production_sources': 133, 'full_compile_files': 136,
        'parameters': actual, 'synth_netlist_sha256': sha(synth / 'synth.v'),
        'synth_audit_sha256': sha(synth / 'source_bound_audit.json'),
        'accepted_report_sha256': sha(accepted),
        'reference_audit_sha256': sha(reference / 'source_bound_audit.json'),
        'tool_sha256': sha(Path(__file__)),
        'scope': 'Recovery and source/parameter comparison only. No new synthesis, full shadow simulation, or physical acceptance. Remaining checker, logger, proof and predecessor gates still required.',
        'full_system_functional_netlist_validated': False, 'physical_gate_open': False,
    }
    out = ROOT / 'results/shadow_synthesis_new_host_recovery_review_20261102.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'files': len(index['members']),
                      'production_sources': 133, 'parameters': actual}))


if __name__ == '__main__':
    main()
