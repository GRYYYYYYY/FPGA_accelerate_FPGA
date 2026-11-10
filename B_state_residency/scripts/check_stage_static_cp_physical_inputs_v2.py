"""Admit fresh physical inputs only after matching full-capacity gate evidence."""
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,restored,verify_freeze
from config_native_publication_synth_common_v1 import validate_production_rtl,runtime_environment

TARGET=BASE/'stage_static_cp_synth_v1'
FULL=BASE/'stage_static_cp_shadow_system_v3'


def evidence():
    # No read of the possibly active shadow/restore roots until accepted report.
    accepted=ROOT/'results/stage_static_cp_shadow_system_v3_20261030.json'
    assert accepted.exists(),'Wait for matched SLOTS32 full-system functional shadow actual restore/freeze'
    ff=verify_freeze(ROOT/'results/stage_static_cp_shadow_system_v3_sources_20261030')
    fm,fa,fe=restored(FULL)
    report=read(accepted)
    assert report['status']=='full_capacity_host_netlist_shadow_actual_restored'
    assert report['audit']==fa and report['full_system_functional_netlist_validated']
    assert fa['full_system_functional_netlist_validated'] and fa['shadow_checks']>0
    assert fa['shadow_outputs']==346 and len(fa['exact_comparisons'])==27
    assert fm['stage']=='complete' and identity(fm['runner_pid'])!=str(fm['runner_start_ticks'])
    synth_report=ROOT/'results/stage_static_cp_synth_20261030.json'
    sf=verify_freeze(ROOT/'results/stage_static_cp_synth_sources_20261030')
    m,a,se=restored(TARGET)
    assert read(synth_report)['audit']==a
    assert m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert not a['critical_warnings'] and not a['timing_loop_warnings']
    assert a['check_timing_counts']['loops']==0 and a['facts']['latches']==a['facts']['blackboxes']==0
    assert m['parameters']==fm['parameters']==fa['parameters'] and m['parameters']['SLOTS']==32
    assert m['part']=='xcu280-fsvh2892-2L-e'
    validate_production_rtl(m['rtl'])
    assert sha(TARGET/'synth.dcp')==a['artifact_sha256']['synth.dcp']
    assert fm['synthesis_netlist_sha256']==a['artifact_sha256']['synth.v']
    assert (TARGET/'clock.xdc').read_text()=='create_clock -name core_clk -period 10.000 [get_ports clk]\n'
    for name in m['rtl']:
        assert sha(TARGET/'sources'/name)==m['sources'][name]==fm['sources'][name]['sha256']
    runtime_environment()
    files=fe+se+[accepted,ff,synth_report,sf,TARGET/'synth.dcp',TARGET/'clock.xdc',
                 ROOT/'hardware/scripts/implement_state_ooc.tcl']
    return {str(p):sha(p) for p in files}


if __name__=='__main__':
    print('STATIC_STAGE_PHYSICAL_INPUTS_ACCEPTED',len(evidence()))
