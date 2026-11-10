"""Read-only admission gate for a future fresh native physical implementation.

This does not prepare a run directory or launch Vivado. Check the accepted report
before touching the synthesis root, which may still be owned by restoration.
"""
from config_native_publication_synth_common_v1 import (
    ROOT, TARGET, FULL, sha, read, identity, restored, validate_production_rtl,
    runtime_environment,
)
from host_edit_system_common_v1 import verify_freeze


def evidence():
    accepted = ROOT/'results/config_native_publication_synth_20261030.json'
    assert accepted.exists(), 'Wait for native OOC actual restore and freeze'
    report = read(accepted)
    assert report['status'] == 'matched_native_publication_ooc_actual_restored'
    frozen = verify_freeze(ROOT/'results/config_native_publication_synth_sources_20261030')
    m, a, files = restored(TARGET)
    assert m['stage'] == 'complete' and m['exit_code'] == 0
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert report['audit'] == a
    assert a['check_timing_counts']['loops'] == 0
    assert not a['timing_loop_warnings'] and not a['critical_warnings']
    assert a['facts']['latches'] == a['facts']['blackboxes'] == 0
    assert m['part'] == 'xcu280-fsvh2892-2L-e'
    validate_production_rtl(m['rtl'])
    assert sha(TARGET/'synth.dcp') == a['artifact_sha256']['synth.dcp']
    assert (TARGET/'clock.xdc').read_text() == 'create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    fm, fa, more = restored(FULL)
    assert len(fa['exact_comparisons']) == 27
    assert fa['native_publication']['publications'] > 0
    assert fm['stage'] == 'complete'
    for name in m['rtl']:
        assert sha(TARGET/'sources'/name) == m['sources'][name]
        assert sha(FULL/'sources'/name) == fm['sources'][name]['sha256'] == m['sources'][name]
    runtime_environment()
    files += more + [accepted, frozen, TARGET/'synth.dcp', TARGET/'clock.xdc',
                     ROOT/'hardware/scripts/implement_state_ooc.tcl']
    return {str(p): sha(p) for p in files}


if __name__ == '__main__':
    print('NATIVE_PHYSICAL_INPUTS_ACCEPTED', len(evidence()))
