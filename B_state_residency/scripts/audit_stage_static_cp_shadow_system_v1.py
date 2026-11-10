"""Independently audit the full host RTL and delayed netlist-shadow outcomes."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,load,restored
from check_host_edit_trace_v1 import check

from stage_static_cp_shadow_common_v1 import TARGET,REFERENCE,SYNTH,VARIANT,evidence
from namespace_functional_netlist_v1 import namespace


def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['mode']=='full_netlist_shadow'
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    rm,proof=evidence();ref=REFERENCE;_,ra,_=restored(ref)
    tb=(VARIANT/'tb_query_fault.sv').read_text()
    preparation=ROOT/'results/stage_static_cp_shadow_system_tools_preparation_20261030.json'
    pr=read(preparation);assert pr['status']=='full_shadow_system_tools_prepared_not_executed'
    for name,digest in pr['tools'].items():assert sha(name)==digest
    proof.update(pr['tools']);proof[str(preparation)]=sha(preparation)
    fixed={}
    assert m['stage_reference']==str(ref) and m['stage_reference_audit_sha256']==sha(ref/'source_bound_audit.json')
    assert m['predecessors']==proof and m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_shadow_system_v1.py')
    assert {e['source']:e['sha256'] for e in m['bound'].values()}==proof
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    assert m['rtl']==rm['rtl'] and len(m['rtl'])==136
    assert set(m['sources'])==set(rm['sources'])
    changed=set(fixed)|{'tb_query_fault.sv','runner.py'}
    for name,e in m['sources'].items():
        assert sha(p/'sources'/name)==e['sha256']
        if name not in changed:assert e['sha256']==rm['sources'][name]['sha256']
    assert (p/'sources/tb_query_fault.sv').read_text()==tb
    assert sha(p/'sources/runner.py')==sha(ROOT/'scripts/run_stage_static_cp_shadow_system_v1.py')
    net,ns=namespace((SYNTH/'synth.v').read_text())
    assert (p/'sources/shadow_netlist.v').read_text()==net
    ns.update(source_sha256=sha(SYNTH/'synth.v'),output_sha256=sha(p/'sources/shadow_netlist.v'))
    assert read(p/'namespace.json')==ns and sha(p/'namespace.json')==m['namespace_sha256']
    assert m['synthesis_netlist_sha256']==sha(SYNTH/'synth.v')
    assert sha(p/'sources/shadow.sv')==sha(VARIANT/'shadow.sv')
    glbl=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/data/verilog/src/glbl.v')
    assert sha(p/'sources/glbl.v')==sha(glbl)==m['original_vendor_glbl_sha256']
    assert set(m['shadow_inputs'])=={'shadow_netlist.v','shadow.sv','glbl.v'}
    for name,digest in m['shadow_inputs'].items():assert sha(p/'sources'/name)==digest
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
        if stage=='compile':expected+=['--define','SHADOW_NETLIST_TOP='+ns['shadow_top']]+[str(p/'sources'/n) for n in ['shadow_netlist.v','shadow.sv','glbl.v']]
        elif stage=='elaborate':expected+=['stage_static_cp_shadow','glbl','-L','unisims_ver','--O0']
        assert new['stage']==stage and new['argv']==expected and new['exit_code']==0
        if new['start_ticks'] is not None:assert identity(new['pid'])!=str(new['start_ticks'])
        out=d/(stage+'.stdout.log');assert sha(out)==new['stdout_sha256']
        text=out.read_text();assert 'ERROR:' not in text and 'FATAL_ERROR:' not in text
        assert ('[VRFC ' in text) if stage=='compile' else ('2022.2' in text)
    admission=m['memory_admission'];assert admission['stable_seconds']>=60 and admission['current_bytes']*4<=admission['limit_bytes']*3
    files=sorted(ra['exact_comparisons']);assert len(files)==27
    assert {file.name for file in d.iterdir() if file.is_file() and file.suffix in ['.txt','.bin','.dat']}==set(files)
    assert sum(name.endswith('_axi.txt') for name in files)==12
    comparisons={}
    for name in files:
        entry=dict(bytes=(d/name).stat().st_size,sha256=sha(d/name))
        assert entry==ra['exact_comparisons'][name] and (original/name).stat().st_size==entry['bytes'] and sha(original/name)==entry['sha256'],name
        comparisons[name]=entry
    log,oldlog=(d/'simulate.log').read_text(),(original/'simulate.log').read_text()
    assert 'Fatal:' not in log and 'ERROR:' not in log
    finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log)
    assert ra['finish_time']=='48292280 ns'
    assert finish==['48292482 ns']
    shadow=re.findall(r'^FULL_SHADOW_PASS outputs=346 bits=14384 checks=(\d+) reset_edges=(\d+) original_end=(\d+) last_checked=(\d+)$',log,re.M)
    assert shadow==[('9658446','5','48292280000','48292481000')]
    assert 'FULL_SHADOW_MISMATCH' not in log and 'FULL_SHADOW_INCOMPLETE' not in log
    assert 'FULL_SHADOW_WATCHDOG' not in log
    he=check((d/'natural_trace.txt').read_text(),log,(original/'natural_trace.txt').read_text())
    assert he==ra['host_edit']
    tags=['BACKEND_EXCLUSION_PASS','CAPTURE_RETIREMENT_PASS','QUERY_INTERFACE_EXCLUSION_PASS',
          'CHECKPOINT_EDIT_EXCLUSION_PASS','HOST_EDIT_NATIVE_PASS','THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS']
    for tag in tags:
        pattern='^'+tag+r'[^\r\n]*$'
        assert re.findall(pattern,log,re.M)==re.findall(pattern,oldlog,re.M)
    observations={}
    schemas={'path':('ROUTE_PATH_BANK_PASS',['cycles','node_writes','publications','checked_cycles']),
             'stage':('ROUTE_STAGE_BANK_PASS',['cycles','captures','imports','checked_cycles'])}
    for name,(tag,columns) in schemas.items():
        pattern='^'+tag+' '+' '.join(key+r'=(\d+)' for key in columns)+'$'
        rows=re.findall(pattern,log,re.M);assert len(rows)==1
        observations[name]=dict(zip(columns,map(int,rows[0])))
        assert all(value>0 for value in observations[name].values())
    assert observations['path']['cycles']==observations['stage']['cycles']
    assert observations==ra['route_bank_observations']
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        common_gate_sha256=sha(ROOT/'scripts/stage_static_cp_shadow_common_v1.py'),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
        exact_comparisons=comparisons,finish_time=finish[0],host_edit=he,
        original_coverage=ra['original_coverage'],route_bank_observations=observations,
        modified_production_sources=sorted(fixed),production_sources=133,verification_sources=3,
        predecessor_evidence=m['predecessors'],timing_qualified=False,board_acceptance=False,
        full_system_functional_netlist_validated=True,
        shadow_checks=9658446,shadow_outputs=346,transport_shift_ns=200,
        scope='Complete host-driven delayed structural-netlist shadow, all346 outputs strictly compared after complete cold reset. Original RTL closed-loop fixture and internal assertions retained,27 external files exact. Gate side shares recorded live RTL-driven inputs rather than independent memory agents. No arbitrary-input formal, physical timing or board proof.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('FULL_NETLIST_SHADOW_SYSTEM_AUDITED',len(comparisons),finish[0],observations)


if __name__=='__main__':main()
