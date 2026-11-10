"""Full-capacity shadow gates: verify actual fixture parameters before launch."""
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,restored,verify_freeze
from check_stage_static_cp_fixture_parameters_v1 import defines,fixture_parameters

TARGET=BASE/'stage_static_cp_shadow_system_v2'
REFERENCE=BASE/'stage_static_cp_host_full_static_v1'
SYNTH=BASE/'stage_static_cp_synth_v1'
VARIANT=ROOT/'hardware/variants/stage_static_cp_shadow_v1'


def evidence():
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
    assert vm['strict_four_state_output_comparison'] and not vm['valid_masks']
    assert vm['transport_shift_ns']==200
    files=fe+se+[accepted,ff,sf,sr,main,VARIANT/'manifest.json']
    files += [VARIANT/name for name in vm['files']]
    for suffix in ['controls','stateful_controls']:
        stem='stage_static_cp_shadow_'+suffix
        report=ROOT/'results'/f'{stem}_20261030.json'
        frozen=verify_freeze(ROOT/'results'/f'{stem}_sources_20261030')
        _,ca,ce=restored(BASE/(stem+'_v1'))
        assert read(report)['audit']==ca and len(ca['outcomes'])==5
        files += ce+[report,frozen]
    return fm,{str(p):sha(p) for p in files}
