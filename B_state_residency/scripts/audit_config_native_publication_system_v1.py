"""Audit the native candidate against the actual-restored CP host-edit system."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,load,restored
from check_host_edit_trace_v1 import check

BUILDER=ROOT/'hardware/variants/config_native_publication_system_v1/build.py'


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'config_native_publication_system_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['mode']=='native_publication'
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    b=load('native_publication_audit_builder',BUILDER);ref=b.REFERENCE
    fixed,model,tb,proof=b.sources(ref);rm,ra,_=restored(ref)
    assert m['native_reference']==str(ref) and m['native_reference_audit_sha256']==sha(ref/'source_bound_audit.json')
    assert m['predecessors']==proof and m['runner_sha256']==sha(ROOT/'scripts/run_config_native_publication_system_v1.py')
    assert {e['source']:e['sha256'] for e in m['bound'].values()}==proof
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    assert m['rtl']==rm['rtl']+[b.MODEL] and len(m['rtl'])==137
    assert set(m['sources'])==set(rm['sources'])|{b.MODEL}
    changed=set(fixed)|{'tb_query_fault.sv','runner.py',b.MODEL}
    assert set(fixed)=={'config_restore_controller.sv','residency_system.sv'}
    for name,e in m['sources'].items():
        assert sha(p/'sources'/name)==e['sha256']
        if name not in changed:assert e['sha256']==rm['sources'][name]['sha256']
    for name,text in fixed.items():assert (p/'sources'/name).read_text()==text
    assert (p/'sources'/b.MODEL).read_text()==model
    assert m['sources'][b.MODEL]['original_controller_sha256']==sha(b.CANDIDATE/'baseline/config_restore_controller.sv')
    assert (p/'sources/tb_query_fault.sv').read_text()==tb
    assert sha(p/'sources/runner.py')==sha(ROOT/'scripts/run_config_native_publication_system_v1.py')
    for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
        assert m[key]==rm[key]
        for name,digest in m[key].items():assert sha(p/name)==digest
    assert m['binding_sha256']==rm['binding_sha256']==sha(m['binding'])
    d=p/'pressure';original=ref/'pressure'
    assert sha(d/'run.tcl')==m['run_tcl_sha256']==sha(original/'run.tcl')
    assert list(m['cases'])==['pressure'] and m['cases']['pressure']['status']=='observed'
    c=m['cases']['pressure'];assert len(c['commands'])==3
    for old,new in zip(rm['cases']['pressure']['commands'],c['commands']):
        stage=old['stage'];expected=[a.replace(str(ref),str(p)) for a in old['argv']]
        if stage=='compile':expected.append(str(p/'sources'/b.MODEL))
        assert new['stage']==stage and new['argv']==expected and new['exit_code']==0
        if new['start_ticks'] is not None:assert identity(new['pid'])!=str(new['start_ticks'])
        out=d/(stage+'.stdout.log');assert sha(out)==new['stdout_sha256']
        text=out.read_text();assert 'ERROR:' not in text and 'FATAL_ERROR:' not in text
        assert ('[VRFC ' in text) if stage=='compile' else ('2022.2' in text)
    admission=m['memory_admission'];assert admission['stable_seconds']>=60 and admission['current_bytes']*4<=admission['limit_bytes']*3
    files=sorted(ra['outputs']);assert len(files)==27
    assert {file.name for file in d.iterdir() if file.is_file() and file.suffix in ['.txt','.bin','.dat']}==set(files)
    assert sum(name.endswith('_axi.txt') for name in files)==12
    comparisons={}
    for name in files:
        entry=dict(bytes=(d/name).stat().st_size,sha256=sha(d/name))
        assert entry==ra['outputs'][name] and (original/name).stat().st_size==entry['bytes'] and sha(original/name)==entry['sha256'],name
        comparisons[name]=entry
    log,oldlog=(d/'simulate.log').read_text(),(original/'simulate.log').read_text()
    assert 'Fatal:' not in log and 'ERROR:' not in log
    finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log)
    assert len(finish)==1 and finish[0]==ra['finish_time']
    assert finish==re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',oldlog)
    he=check((d/'natural_trace.txt').read_text(),log,(original/'natural_trace.txt').read_text())
    assert he==ra['host_edit']
    tags=['BACKEND_EXCLUSION_PASS','CAPTURE_RETIREMENT_PASS','QUERY_INTERFACE_EXCLUSION_PASS',
          'CHECKPOINT_EDIT_EXCLUSION_PASS','HOST_EDIT_NATIVE_PASS','THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS']
    for tag in tags:
        pattern='^'+tag+r'[^\r\n]*$'
        assert re.findall(pattern,log,re.M)==re.findall(pattern,oldlog,re.M)
    columns=['cycles','checks','loads','replies','stages','captures','publications','discards','prepared']
    pattern=r'^CONFIG_NATIVE_SYSTEM_PASS '+' '.join(name+r'=(\d+)' for name in columns)+'$'
    lines=re.findall(pattern,log,re.M);assert len(lines)==1;values=list(map(int,lines[0]))
    observation=dict(zip(columns,values))
    assert all(observation[name]>0 for name in columns if name!='discards') and observation['discards']>=0
    assert observation['cycles']==observation['checks']==ra['coverage']['checkpoint_edit_exclusion']['cycles']
    assert observation['loads']==observation['replies']
    assert observation['publications']<=observation['captures']<=observation['stages']<=observation['loads']
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        builder_sha256=sha(BUILDER),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
        exact_comparisons=comparisons,finish_time=finish[0],host_edit=he,
        original_coverage=ra['coverage'],native_publication=observation,
        observer_original_controller_sha256=sha(b.CANDIDATE/'baseline/config_restore_controller.sv'),
        observer_source_sha256=sha(p/'sources'/b.MODEL),modified_production_sources=sorted(fixed),
        production_sources=133,verification_sources=4,state_bits=4810,output_bits=7238,
        predecessor_evidence=m['predecessors'],timing_qualified=False,board_acceptance=False,
        scope='Native candidate full system with passive original-controller own stage feedback, complete four-state state/output comparisons each non-cold-reset edge, actual aliases and27 exact external files/cycles. Original host-edit and prior monitors retained. No formal arbitrary-input, synthesis, physical timing or board conclusion; actual archive/restore still required.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('NATIVE_PUBLICATION_SYSTEM_AUDITED',len(comparisons),finish[0],observation)


if __name__=='__main__':main()
