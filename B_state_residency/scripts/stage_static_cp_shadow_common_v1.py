"""Acceptance gates for the actual complete-system shadow run."""
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity, restored, verify_freeze

TARGET = BASE / 'stage_static_cp_shadow_system_v1'
REFERENCE = BASE / 'stage_static_cp_system_v1'
SYNTH = BASE / 'stage_static_cp_synth_v1'
VARIANT = ROOT / 'hardware/variants/stage_static_cp_shadow_v1'


def evidence():
    # Do not inspect a live synthesis root or an owner-controlled restore root.
    accepted = ROOT / 'results/stage_static_cp_synth_20261030.json'
    assert accepted.exists(), 'Wait for independent OOC audit, actual restore and freeze'
    sf = verify_freeze(ROOT / 'results/stage_static_cp_synth_sources_20261030')
    sm, sa, se = restored(SYNTH)
    assert read(accepted)['status'] == 'matched_static_stage_ooc_actual_restored'
    assert read(accepted)['audit'] == sa
    assert sm['stage'] == 'complete' and sm['exit_code'] == 0
    assert identity(sm['runner_pid']) != str(sm['runner_start_ticks'])
    assert not sm.get('active_process')
    assert sa['check_timing_counts']['loops'] == 0
    assert not sa['critical_warnings'] and not sa['timing_loop_warnings']
    assert sa['facts']['latches'] == sa['facts']['blackboxes'] == 0
    ff = verify_freeze(ROOT / 'results/stage_static_cp_system_sources_20261030')
    fm, fa, fe = restored(REFERENCE)
    assert read(ROOT / 'results/stage_static_cp_system_20261030.json')['audit'] == fa
    assert len(fa['exact_comparisons']) == 27
    assert len(sm['rtl']) == 133 and len(fm['rtl']) == 136
    for name in sm['rtl']:
        assert sha(SYNTH/'sources'/name) == sm['sources'][name] == fm['sources'][name]['sha256']
    cf = verify_freeze(ROOT / 'results/stage_static_cp_shadow_controls_sources_20261030')
    _, ca, ce = restored(BASE / 'stage_static_cp_shadow_controls_v1')
    cr = ROOT / 'results/stage_static_cp_shadow_controls_20261030.json'
    assert read(cr)['audit'] == ca and len(ca['outcomes']) == 5
    vm = read(VARIANT/'manifest.json')
    assert vm['all_original_stimuli_and_assertions_retained']
    assert vm['strict_four_state_output_comparison'] and not vm['valid_masks']
    assert vm['transport_shift_ns'] == 200
    for name, digest in vm['files'].items(): assert sha(VARIANT/name) == digest
    assert sha(REFERENCE/'sources/tb_query_fault.sv') == vm['source_tb_sha256']
    files = se+fe+ce+[accepted,sf,ff,cf,cr,VARIANT/'manifest.json']
    files += [VARIANT/name for name in vm['files']]
    return fm, {str(p):sha(p) for p in files}
