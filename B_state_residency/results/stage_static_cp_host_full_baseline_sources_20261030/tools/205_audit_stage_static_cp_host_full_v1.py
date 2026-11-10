"""Audit full-capacity host behavior using a full-capacity prefix and paired run."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,load,restored,verify_freeze
from check_host_edit_trace_v1 import check
from check_stage_static_cp_fixture_parameters_v1 import defines,fixture_parameters

TARGETS={'baseline':BASE/'stage_static_cp_host_full_baseline_v1',
         'static':BASE/'stage_static_cp_host_full_static_v1'}


def main():
    p=Path(sys.argv[1]).resolve();mode=next(k for k,v in TARGETS.items() if v==p)
    m=read(p/'manifest.json')
    assert m['status']=='observed' and m['stage']=='complete' and m['mode']==mode+'_full_capacity'
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    builder=ROOT/'hardware/variants/stage_static_cp_system_v1/build.py'
    b=load('full_capacity_host_audit_builder',builder);ref=b.REFERENCE
    fixed,proof=b.sources(ref)
    if mode=='baseline':fixed={}
    rm,_,_=restored(ref)
    tb=b.monitored_tb((ref/'sources/tb_query_fault.sv').read_text())
    synth=BASE/'stage_static_cp_synth_v1';sm,sa,se=restored(synth)
    accepted=ROOT/'results/stage_static_cp_synth_20261030.json'
    sf=verify_freeze(ROOT/'results/stage_static_cp_synth_sources_20261030')
    assert read(accepted)['audit']==sa
    proof.update({str(q):sha(q) for q in se+[accepted,sf]})
    if mode=='static':
        paired=ROOT/'results/stage_static_cp_host_full_baseline_20261030.json'
        bm,ba,be=restored(TARGETS['baseline'])
        assert read(paired)['audit']==ba
        bf=verify_freeze(ROOT/'results/stage_static_cp_host_full_baseline_sources_20261030')
        proof.update({str(q):sha(q) for q in be+[paired,bf]})
    prep=ROOT/'results/stage_static_cp_host_full_tools_preparation_20261030.json'
    pr=read(prep);assert pr['status']=='full_capacity_host_tools_prepared_not_executed'
    for name,digest in pr['tools'].items():assert sha(name)==digest
    proof.update(pr['tools']);proof[str(prep)]=sha(prep)
    assert m['predecessors']==proof
    assert {e['source']:e['sha256'] for e in m['bound'].values()}==proof
    for name,e in m['bound'].items():assert sha(e['source'])==sha(p/'bound'/name)==e['sha256']
    runner=ROOT/'scripts/run_stage_static_cp_host_full_v2.py'
    assert m['runner_sha256']==sha(runner)==sha(p/'sources/runner.py')
    assert m['stage_reference']==str(ref) and m['stage_reference_audit_sha256']==sha(ref/'source_bound_audit.json')
    assert m['rtl']==rm['rtl'] and len(m['rtl'])==136 and set(m['sources'])==set(rm['sources'])
    changed=set(fixed)|{'runner.py','tb_query_fault.sv'}
    for name,e in m['sources'].items():
        assert sha(p/'sources'/name)==e['sha256']
        if name not in changed:assert e['sha256']==rm['sources'][name]['sha256']
    for name,text in fixed.items():assert (p/'sources'/name).read_text()==text
    assert (p/'sources/tb_query_fault.sv').read_text()==tb
    for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
        assert m[key]==rm[key]
        for name,digest in m[key].items():assert sha(p/name)==digest
    assert m['binding_sha256']==rm['binding_sha256']==sha(m['binding'])
    d=p/'full';assert sha(d/'run.tcl')==m['run_tcl_sha256']==sha(ref/'pressure/run.tcl')
    assert list(m['cases'])==['full'] and m['cases']['full']['status']=='observed'
    commands=m['cases']['full']['commands'];assert len(commands)==3
    for old,new in zip(rm['cases']['pressure']['commands'],commands):
        stage=old['stage'];argv=[a.replace(str(ref/'pressure'),str(d)).replace(str(ref),str(p)) for a in old['argv']]
        if stage=='compile':
            at=argv.index('PRESSURE');assert argv[at-1]=='--define';del argv[at-1:at+1]
        assert new['stage']==stage and new['argv']==argv and new['exit_code']==0
        if new['start_ticks'] is not None:assert identity(new['pid'])!=str(new['start_ticks'])
        stdout=d/(stage+'.stdout.log');assert sha(stdout)==new['stdout_sha256']
        assert 'ERROR:' not in stdout.read_text() and 'FATAL_ERROR:' not in stdout.read_text()
    macros=defines(commands[0]['argv']);assert 'PRESSURE' not in macros
    parameters=fixture_parameters(tb,(synth/'sources/query_residency_system.sv').read_text(),macros)
    assert parameters==sm['parameters']==m['parameters'] and parameters['SLOTS']==32
    assert sorted(macros)==m['compile_defines']
    adm=m['memory_admission'];assert adm['stable_seconds']>=60 and adm['current_bytes']*4<=adm['limit_bytes']*3
    # Full-capacity independent prefix oracle, never the one-slot pressure trace.
    anchor=BASE/'checkpoint_matrix_retry_crc_full_v1';_,aa,af=restored(anchor)
    matrix=read(ROOT/'results/checkpoint_edit_matrix_20261030.json')
    ac=next(c for c in matrix['cases'] if c['target']==anchor.name)
    assert ac['case']=='full' and ac['audit_sha256']==sha(anchor/'source_bound_audit.json')
    verify_freeze(ROOT/'results/checkpoint_edit_matrix_sources_20261030')
    log=(d/'simulate.log').read_text();assert 'Fatal:' not in log and 'ERROR:' not in log
    finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log);assert len(finish)==1
    host=check((d/'natural_trace.txt').read_text(),log,(anchor/'full/natural_trace.txt').read_text())
    observations={}
    schemas={
      'backend':('BACKEND_EXCLUSION_PASS',['cycles','authority','owner']),
      'capture':('CAPTURE_RETIREMENT_PASS',['cycles','nonzero','replies']),
      'query':('QUERY_INTERFACE_EXCLUSION_PASS',['cycles','service_req','service_rsp','search_req','search_rsp','route_req','route_rsp']),
      'cp':('CHECKPOINT_EDIT_EXCLUSION_PASS',['cycles','safe','edit','busy','requests','replies','imports','exports']),
      'path':('ROUTE_PATH_BANK_PASS',['cycles','node_writes','publications','checked_cycles']),
      'stage':('ROUTE_STAGE_BANK_PASS',['cycles','captures','imports','checked_cycles'])}
    for name,(tag,columns) in schemas.items():
        pattern='^'+tag+' '+' '.join(c+r'=(\d+)' for c in columns)+'$'
        rows=re.findall(pattern,log,re.M);assert len(rows)==1
        observations[name]=dict(zip(columns,map(int,rows[0])))
        assert all(v>0 for v in observations[name].values())
    assert len({o['cycles'] for o in observations.values()})==1
    q=observations['query'];assert [q[k] for k in ['service_req','service_rsp','search_req','search_rsp','route_req','route_rsp']]==[43,43,7,7,6,6]
    cp=observations['cp'];assert [cp[k] for k in ['edit','requests','replies','imports','exports']]==[1,15,15,60,90]
    markers={}
    for tag in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS','HOST_EDIT_NATIVE_PASS']:
        rows=re.findall('^'+tag+r'[^\r\n]*$',log,re.M);assert len(rows)==1;markers[tag]=rows[0]
    assert markers['FOURTH_WARM_PASS']=='FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231'
    expected=set(aa['exact_comparisons']);assert len(expected)==27
    actual={f.name for f in d.iterdir() if f.is_file() and f.suffix in ['.txt','.bin','.dat']}
    assert actual==expected
    outputs={name:dict(bytes=(d/name).stat().st_size,sha256=sha(d/name)) for name in sorted(expected)}
    if mode=='static':
        assert outputs==ba['outputs'] and finish[0]==ba['finish_time']
        assert host==ba['host_edit'] and observations==ba['observations'] and markers==ba['markers']
        for name,e in outputs.items():assert sha(TARGETS['baseline']/'full'/name)==e['sha256']
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                mode=mode,parameters=parameters,outputs=outputs,finish_time=finish[0],host_edit=host,
                observations=observations,markers=markers,production_sources=133,verification_sources=3,
                modified_production_sources=sorted(fixed),
                full_capacity_prefix_anchor_audit_sha256=sha(anchor/'source_bound_audit.json'),
                full_capacity_prefix_anchor_restore_sha256=sha(af[2]),
                paired_exact_comparisons=27 if mode=='static' else 0,
                timing_qualified=False,full_system_functional_netlist_validated=False,
                scope='SLOTS32 host RTL fixture, original full-capacity FOURTH_PASS prefix and independently checked host edit/CRC/atomicity suffix. Static mode compares all27 files and complete timing with new baseline. No full-system gate or physical timing claim.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('FULL_CAPACITY_HOST_AUDITED',mode,finish[0],len(outputs))


if __name__=='__main__':main()
