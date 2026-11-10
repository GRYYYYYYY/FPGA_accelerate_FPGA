"""Immutable source and predecessor gates for native-publication unit comparisons."""
from pathlib import Path
from host_edit_system_common_v1 import ROOT, BASE, sha, read, identity, load, restored, verify_freeze

TARGET=BASE/'config_native_publication_units_v1'
VARIANT=ROOT/'hardware/variants/config_native_publication_v1'
PREPARATION=ROOT/'results/config_publication_unit_benches_v2_preparation_20261030.json'
TOOL_PREPARATION=ROOT/'results/config_publication_units_tools_preparation_20261030.json'
CASES=['generic_original','generic_default','native_original','native_default','native_enabled']
PAIRS=[('generic_original','generic_default'),('native_original','native_default'),('native_original','native_enabled')]
TOOLS=['config_publication_units_common_v1.py','run_config_publication_units_v1.py',
       'audit_config_publication_units_v1.py','freeze_config_publication_units_v1.py',
       'check_config_publication_bank_trace_v1.py','audit_config_publication_probe_v1.py',
       'audit_config_native_feedback_probe_v1.py','archive_offer_result.py',
       'verify_search_retire_restore.py','restore_offer_result.py','host_edit_system_common_v1.py',
       'prepare_config_native_publication_v1.py','prepare_config_publication_unit_benches_v1.py',
       'prepare_config_publication_unit_benches_v2.py']
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')


def host_pair_evidence():
    report=ROOT/'results/checkpoint_host_edit_system_20261030.json'
    assert report.exists(),'Wait for actual restored/frozen real host-edit pair'
    # The final freeze is checked before opening either restored experiment root.
    freeze=verify_freeze(ROOT/'results/checkpoint_host_edit_system_sources_20261030')
    r=read(report);assert r['status']=='real_host_edit_baseline_cp_exact_pair_restored'
    assert r['exact_file_comparisons']==27 and r['host_edit_exercised']
    files=[report,freeze]
    for mode,name in [('baseline','query_host_edit_system_v1'),('cp','checkpoint_host_edit_system_v1')]:
        m,a,evidence=restored(BASE/name)
        assert m['stage']=='complete' and m['mode']==mode and not m.get('active_process')
        assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
        assert r['cases'][mode]['manifest']==m and r['cases'][mode]['audit']==a
        assert a['host_edit']['host_writes']==1 and a['host_edit']['final_dirty']==1 and a['host_edit']['final_pending']==0
        files+=evidence
    return {str(p):sha(p) for p in files}


def source_evidence():
    tr=read(TOOL_PREPARATION)
    assert tr['status']=='publication_unit_tools_prepared_not_rtl_executed'
    assert set(tr['tools'])=={str(ROOT/'scripts'/n) for n in TOOLS}
    for p,h in tr['tools'].items():assert sha(p)==h
    m=read(VARIANT/'manifest.json');assert m['status']=='prepared_not_compiled_or_simulated'
    assert m['reference']==str(BASE/'checkpoint_edit_synth_v1')
    assert m['parameter']==dict(name='NATIVE_FEEDBACK_PUBLICATION',default=0,native_residency_instance=1)
    for p,h in m['bound'].items():assert sha(p)==h
    for n,entry in m['sources'].items():
        for role in ['baseline','fixed']:assert sha(VARIANT/role/n)==entry[role]
    builder=load('publication_candidate_checked_builder',ROOT/'scripts/prepare_config_native_publication_v1.py')
    texts=builder.candidate((VARIANT/'baseline/config_restore_controller.sv').read_text(),
                            (VARIANT/'baseline/residency_system.sv').read_text())
    for n,text in texts.items():assert (VARIANT/'fixed'/n).read_text()==text
    prep=read(PREPARATION)
    assert prep['status']=='five_binary_four_state_unit_benches_prepared_not_compiled_or_simulated'
    assert set(prep['cases'])==set(CASES) and prep['state_bits']==4810 and prep['output_bits']==7238
    assert prep['exact_comparisons']==[list(p) for p in PAIRS]
    for p,h in prep['bound'].items():assert sha(p)==h
    bench=load('publication_original_observer_builder',ROOT/'scripts/prepare_config_publication_unit_benches_v1.py')
    files=[VARIANT/'manifest.json',PREPARATION,TOOL_PREPARATION]
    files+=[VARIANT/role/n for role in ['baseline','fixed'] for n in m['sources']]
    references={}
    for kind,name in [('generic','config_publication_probe_v1'),('native','config_native_feedback_probe_v1')]:
        original=BASE/name;rm,ra,evidence=restored(original)
        assert rm['stage']=='complete' and identity(rm['runner_pid'])!=str(rm['runner_start_ticks'])
        assert sha(VARIANT/'baseline/config_restore_controller.sv')==rm['dut_sha256']
        references[kind]=dict(root=str(original),audit_sha256=sha(original/'source_bound_audit.json'))
        files+=evidence+[original/'events.txt',original/'simulate.log']
    for name,case in prep['cases'].items():
        kind,mode=name.split('_',1);tb=Path(case['testbench']);source=Path(case['source'])
        assert sha(tb)==case['testbench_sha256'] and sha(source)==case['source_sha256']
        original=read(Path(references[kind]['root'])/'manifest.json')
        assert case['source_sha256']==original['tb_sha256']
        generated,top=bench.instrument(source.read_text(),kind=='native',mode)
        assert generated.count('"BANK %0d %0t %h %h"')==1
        generated=generated.replace('"BANK %0d %0t %h %h"','"BANK %0d %0t %b %b"')
        assert tb.read_text()==generated and case['top']==top
        assert case['parameter']==(None if mode=='original' else int(mode=='enabled'))
        files+=[tb,source]
    files+=[ROOT/'scripts'/n for n in TOOLS]
    return prep,references,list(dict.fromkeys(files))


def commands(directory,top):
    return [('compile',[str(BIN/'xvlog'),'--sv',str(directory/'config_restore_controller.sv'),str(directory/'tb.sv')]),
            ('elaborate',[str(BIN/'xelab'),top,'-s','publication_unit','--debug','typical','--mt','2']),
            ('simulate',[str(BIN/'xsim'),'publication_unit','--tclbatch','run.tcl','--log','simulate.log',
                         '--testplusarg','events='+str(directory/'events.txt'),
                         '--testplusarg','publication_bank_trace='+str(directory/'bank_trace.txt')])]
