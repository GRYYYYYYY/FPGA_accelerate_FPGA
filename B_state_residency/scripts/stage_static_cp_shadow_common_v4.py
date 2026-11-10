"""Full-capacity shadow gates: verify actual fixture parameters before launch."""
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,restored,verify_freeze
from check_stage_static_cp_fixture_parameters_v1 import defines,fixture_parameters

TARGET=BASE/'stage_static_cp_shadow_system_v4'
REFERENCE=BASE/'stage_static_cp_host_full_static_v1'
SYNTH=BASE/'stage_static_cp_synth_v1'
VARIANT=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4'


def evidence():
    controls=ROOT/'results/shadow_cp_protocol_controls_20261030.json'
    monitor_report=ROOT/'results/shadow_cp_transfer_monitor_controls_20261030.json'
    assert controls.exists() and monitor_report.exists(),'Wait for actual-restored17 protocol controls and transfer monitor controls'
    accepted=ROOT/'results/stage_static_cp_host_full_static_20261030.json'
    assert accepted.exists(),'Wait for SLOTS32 host static/baseline actual restore and freeze'
    ff=verify_freeze(ROOT/'results/stage_static_cp_host_full_static_sources_20261030')
    fm,fa,fe=restored(REFERENCE)
    assert read(accepted)['status']=='full_capacity_host_static_actual_restored'
    assert read(accepted)['audit']==fa and fa['paired_exact_comparisons']==27
    assert fm['stage']=='complete' and fm['cases']['full']['status']=='observed'
    assert identity(fm['runner_pid'])!=str(fm['runner_start_ticks']) and not fm.get('active_process')
    sf=verify_freeze(ROOT/'results/stage_static_cp_synth_sources_20261030')
    sm,sa,se=restored(SYNTH)
    sr=ROOT/'results/stage_static_cp_synth_20261030.json'
    main=ROOT/'results/stage_static_cp_synth_main_review_20261030.json'
    assert read(sr)['audit']==sa and read(main)['audit_sha256']==sha(SYNTH/'source_bound_audit.json')
    assert sm['stage']=='complete' and sm['exit_code']==0
    assert identity(sm['runner_pid'])!=str(sm['runner_start_ticks'])
    assert not sa['critical_warnings'] and not sa['timing_loop_warnings']
    assert sa['check_timing_counts']['loops']==0
    compile=fm['cases']['full']['commands'][0]['argv'];macros=defines(compile)
    assert 'PRESSURE' not in macros
    actual=fixture_parameters((REFERENCE/'sources/tb_query_fault.sv').read_text(),
                              (SYNTH/'sources/query_residency_system.sv').read_text(),macros)
    assert actual==fm['parameters']==fa['parameters']==sm['parameters'] and actual['SLOTS']==32
    assert len(sm['rtl'])==133 and len(fm['rtl'])==136
    for name in sm['rtl']:
        assert sha(SYNTH/'sources'/name)==sm['sources'][name]==fm['sources'][name]['sha256']
    vm=read(VARIANT/'manifest.json')
    for name,digest in vm['files'].items():assert sha(VARIANT/name)==digest
    assert sha(REFERENCE/'sources/tb_query_fault.sv')==vm['source_tb_sha256']
    assert vm['unconditional_outputs']==345 and set(vm['qualified_outputs'])=={'cp_m_data'}
    assert vm['all_345_original_comparison_blocks_exact'] and vm['pre_clock_cp_transfer_checks']
    assert vm['active_payload_and_metadata_require_known'] and not vm['all_pin_strict_equivalence']
    assert vm['input_and_expected_transport_ns']==200 and vm['clock_lead_ps']==1
    from prepare_stage_static_cp_shadow_protocol_v4 import render
    parent_clock=ROOT/'hardware/variants/stage_static_cp_shadow_clock_v2/shadow.sv'
    assert sha(parent_clock)==vm['parent_clock_shadow_sha256']
    assert render(parent_clock.read_text())==(VARIANT/'shadow.sv').read_text()
    files=fe+se+[accepted,ff,sf,sr,main,VARIANT/'manifest.json']
    files += [VARIANT/name for name in vm['files']]
    cf=verify_freeze(ROOT/'results/shadow_cp_protocol_controls_sources_20261030')
    _,ca,ce=restored(BASE/'shadow_cp_protocol_controls_v5')
    assert read(controls)['status']=='cp_export_contract_controls_actual_restored'
    assert read(controls)['audit']==ca and ca['complete_contract_controls_passed'] and len(ca['outcomes'])==17
    assert ca['checker_sha256']==sha(VARIANT/'shadow.sv')
    mf=verify_freeze(ROOT/'results/shadow_cp_transfer_monitor_controls_sources_20261030')
    _,ma,me=restored(BASE/'shadow_cp_transfer_monitor_controls_v1')
    assert read(monitor_report)['audit']==ma and len(ma['cases'])==2
    monitor=ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv'
    assert ma['monitor_sha256']==sha(monitor)
    clock=ROOT/'results/shadow_clock_sampling_controls_20261030.json'
    kf=verify_freeze(ROOT/'results/shadow_clock_sampling_controls_sources_20261030')
    assert read(clock)['status']=='shadow_clock_sampling_controls_actual_restored'
    files += ce+me+[controls,cf,monitor_report,mf,monitor,clock,kf,parent_clock,ROOT/'results/stage_static_cp_port_schema_20261030.json']
    return fm,{str(p):sha(p) for p in files}
