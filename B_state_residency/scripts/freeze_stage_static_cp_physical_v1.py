"""Freeze only actually restored physical evidence, without selecting a candidate."""
from pathlib import Path
import json
import shutil
from prepare_stage_static_cp_physical_v3 import OUTPUT
from check_stage_static_cp_physical_inputs_v3 import evidence
from config_native_publication_synth_common_v1 import ROOT, sha, read, identity
from host_edit_system_common_v1 import restored, verify_freeze


def main():
    proof = evidence()
    receipt = ROOT/'results'/f'{OUTPUT.name}_restore_20261025.json'
    assert receipt.exists(), 'Wait for physical archive actual restoration and byte-identical audit'
    m, a, files = restored(OUTPUT)
    assert m['stage'] == 'implementation_complete_pending_independent_inspection'
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_stage_static_cp_physical_v1.py')
    assert a['independent_reopened_dcp_matches'] and not a['timing_qualified']
    for name, digest in a['artifact_sha256'].items(): assert sha(OUTPUT/name) == digest
    for name, digest in a['inspection_artifact_sha256'].items(): assert sha(OUTPUT/'inspection'/name) == digest
    reference = ROOT/'results/checkpoint_edit_route_recovery_20261030.json'
    r = read(reference)
    assert r['status'] == 'full_system_route_recovery_artifacts_restored'
    assert r['restoration']['status'] == 'passed' and r['restoration']['audit_byte_identical']
    ra = r['audit']
    assert sha(Path(r['restoration']['restored_root'])/'source_bound_audit.json') == r['restoration']['audit_sha256']
    assert read(Path(r['restoration']['restored_root'])/'source_bound_audit.json') == ra
    delta = {key: a['resources']['routed'][key]-ra['resources']['routed'][key]
             for key in ['LUT', 'FF', 'BRAM', 'DSP', 'URAM']}
    report = ROOT/'results/stage_static_cp_physical_v3_20261030.json'
    freeze = ROOT/'results/stage_static_cp_physical_v3_sources_20261030'
    assert not report.exists() and not freeze.exists()
    record = dict(status='fresh_static_stage_physical_artifacts_actual_restored', audit=a,
        restoration=read(receipt), reference_report_sha256=sha(reference),
        routed_utilization_delta_candidate_minus_reference=delta,
        routed_wns_delta_ns=a['timing_summaries']['routed']['WNS_ns']-ra['timing_summaries']['routed']['WNS_ns'],
        candidate_selected=False, timing_qualified=False, board_acceptance=False,
        full_behavior_matrix_complete=False,
        scope='Fresh static-stage opt/place/route compared with restored CP physical reference under original '
              '2022.2/U280/10ns research conditions. Different critical endpoints and mapping may occur; '
              'slack difference is not a same-path causal proof or platform frequency measurement.')
    report.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    freeze.mkdir()
    copied = {}

    def copy(source, relative):
        dest = freeze/relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        copied[str(relative)] = dict(source=str(source), sha256=sha(source))
        assert sha(dest) == copied[str(relative)]['sha256']

    for name in m['rtl']: copy(OUTPUT/'sources'/name, Path('sources')/name)
    for name in m['inputs']:
        if name.startswith('bound/'): copy(OUTPUT/name, Path(name))
    tools = ['check_stage_static_cp_physical_inputs_v3.py', 'prepare_stage_static_cp_physical_v3.py',
             'run_stage_static_cp_physical_v1.py', 'inspect_stage_static_cp_physical_v1.py',
             'audit_stage_static_cp_physical_v1.py', 'freeze_stage_static_cp_physical_v1.py',
             'config_native_publication_synth_common_v1.py', 'host_edit_system_common_v1.py',
             'audit_state_ooc_physical_v2.py', 'audit_state_route_recovery_v2.py', 'parse_state_timing_paths.py',
             'archive_offer_result.py', 'verify_search_retire_restore.py', 'restore_offer_result.py']
    for name in tools: copy(ROOT/'scripts'/name, Path('tools')/name)
    for source in files + [report, reference, OUTPUT/'inspection/manifest.json']:
        copy(source, Path('reports')/(str(len(copied))+'_'+source.name))
    for name in a['artifact_sha256']:
        if not name.endswith('.dcp'): copy(OUTPUT/name, Path('artifacts')/name)
    for name in a['inspection_artifact_sha256']:
        copy(OUTPUT/'inspection'/name, Path('inspection')/name)
    for name in ['implement_state_ooc.tcl', 'inspect_state_route_v1.tcl']:
        copy(ROOT/'hardware/scripts'/name, Path('templates')/name)
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen', files=copied,
        candidate_selected=False, timing_qualified=False, board_acceptance=False), indent=2, sort_keys=True)+'\n')
    verify_freeze(freeze)
    print('STATIC_STAGE_PHYSICAL_ACTUAL_RESTORE_FROZEN', len(copied))


if __name__ == '__main__': main()
