"""Full v7 independent terminal audit; retain all original 27-file and protocol checks."""
from pathlib import Path
import json,re,sys,hashlib
from shadow_recovered_evidence_v7 import ROOT,BASE,sha,read,identity,restored
from stage_static_cp_shadow_common_v7_revision2 import TARGET,REFERENCE,SYNTH,VARIANT,evidence
from shadow_prepared_runtime_v7 import validate_preparation,check_admission
from namespace_functional_netlist_v1 import namespace
from check_host_edit_trace_v1 import check
from check_shadow_payload_transfer_logs_v1 import check_ka,check_pw

def main():
    p=Path(sys.argv[1]).resolve();assert p==TARGET
    pr=validate_preparation(p);m=read(p/'manifest.json');rm,proof=evidence();ref=REFERENCE;_,ra,_=restored(ref);fixed={}
    assert m['status']=='observed' and m['stage']=='complete' and m['mode']=='full_netlist_shadow_fixture_ready_v7'
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['preparation_sha256']==sha(p/'preparation.json')
    assert m['preparation_review_sha256']==sha(ROOT/'results/stage_static_cp_shadow_v7_preparation_review_20261102.json')
    assert m['stage_reference']==str(ref) and m['stage_reference_audit_sha256']==sha(ref/'source_bound_audit.json')
    assert m['predecessors']==pr['predecessors'] and all(m['predecessors'].get(k)==v for k,v in proof.items())
    assert m['bound']==pr['bound'] and m['sources']==pr['sources']
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_shadow_system_v7.py')
    assert m['rtl']==rm['rtl'] and len(m['rtl'])==136 and set(m['sources'])==set(rm['sources'])
    for n,e in m['sources'].items():
        assert sha(p/'sources'/n)==e['sha256']
        if n not in ['tb_query_fault.sv','runner.py']:assert e['sha256']==rm['sources'][n]['sha256']
    assert (p/'sources/tb_query_fault.sv').read_bytes()==(VARIANT/'tb_query_fault.sv').read_bytes()
    assert sha(p/'sources/runner.py')==m['runner_sha256']
    net,ns=namespace((SYNTH/'synth.v').read_text());assert (p/'sources/shadow_netlist.v').read_text()==net
    ns.update(source_sha256=sha(SYNTH/'synth.v'),output_sha256=sha(p/'sources/shadow_netlist.v'))
    assert read(p/'namespace.json')==ns and m['namespace_sha256']==sha(p/'namespace.json')
    assert m['synthesis_netlist_sha256']==sha(SYNTH/'synth.v')
    assert m['shadow_inputs']==pr['shadow_inputs'] and sha(p/'sources/shadow.sv')==sha(VARIANT/'shadow.sv')
    assert m['unconditional_outputs']==342 and m['qualified_outputs']==['cp_m_data','k_a_node','k_a_net','p_m_wdata'] and m['clock_lead_ps']==1 and not m['all_pin_strict_equivalence']
    for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
        assert m[key]==rm[key]
        for n,h in rm[key].items():assert sha(p/n)==h
    assert m['parameters']==rm['parameters'] and m['binding_sha256']==rm['binding_sha256']==sha(m['binding'])
    regions=read(p/'input_plan.json')['regions'];expected={n:regions[k]['sha256'] for n,k in [('design.bin','design'),('cost.bin','cost_history_prices_nets'),('allocator.bin','owner_allocator')]}
    digest=hashlib.sha256()
    for k in ['owners','owner_pool','owner_allocator']:
        with Path(regions[k]['path']).open('rb') as f:
            for chunk in iter(lambda:f.read(1048576),b''):digest.update(chunk)
    expected.update({n:digest.hexdigest() for n in ['owners.bin','pool.bin','snapshot.bin','g3.bin']})
    expected['labels.bin']=hashlib.sha256(bytes(3145728)).hexdigest();assert m['fresh_input_sha256']==expected
    d=p/'full';original=ref/'full'
    assert sha(d/'run.tcl')==m['run_tcl_sha256']==sha(original/'run.tcl')
    assert list(m['cases'])==['full'] and m['cases']['full']['status']=='observed'
    c=m['cases']['full'];assert len(c['commands'])==3
    for old,new in zip(rm['cases']['full']['commands'],c['commands']):
        stage=old['stage'];expected=pr['commands'][['compile','elaborate','simulate'].index(stage)]['argv']
        assert new['stage']==stage and new['argv']==expected and new['exit_code']==0
        if new['start_ticks'] is not None:assert identity(new['pid'])!=str(new['start_ticks'])
        out=d/(stage+'.stdout.log');assert sha(out)==new['stdout_sha256']
        text=out.read_text();assert 'ERROR:' not in text and 'FATAL_ERROR:' not in text
        assert ('[VRFC ' in text) if stage=='compile' else ('2022.2' in text)
    admission=check_admission(m)
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
    reference_finish=re.fullmatch(r'(\d+) ns',ra['finish_time']);assert reference_finish
    end=int(reference_finish[1]);assert end%10==0 and end>1000
    assert finish==[str(end+202)+' ns']
    expected_checks=(end-55)//5+1
    pattern=r'^FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS outputs=346 unconditional=342 qualified=cp_m_data,k_a_node,k_a_net,p_m_wdata checks=(\d+) reset_edges=(\d+) original_end=(\d+) last_checked=(\d+) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$'
    shadow=re.findall(pattern,log,re.M);assert len(shadow)==1
    counts=list(map(int,shadow[0]));assert counts[:4]==[expected_checks,5,end*1000,(end+201)*1000]
    cp=dict(zip(['active','stalled','transfers','edges','idle','idle_differences'],counts[4:]))
    assert all(cp[key]>0 for key in ['active','stalled','transfers','edges','idle'])
    assert 'FULL_SHADOW_MISMATCH' not in log and 'FULL_SHADOW_INCOMPLETE' not in log and 'FULL_SHADOW_WATCHDOG' not in log
    original_words=re.findall(r'^BPATH (\d+) ([0-9a-fA-F]{8}) ([01])$',(original/'natural_trace.txt').read_text(),re.M)
    assert len(original_words)==1560
    for i,(idx,data,last) in enumerate(original_words):assert int(idx)==i%156 and int(last)==int(i%156==155)
    actual_text=(d/'shadow_cp_export.log').read_text()
    actual_words=re.findall(r'^CP_WORD (\d+) (\d+) ([0-9a-fA-F]{8}) ([01])$',actual_text,re.M)
    assert len(actual_words)==len(actual_text.splitlines())==cp['transfers']==len(original_words)
    assert [(int(i),int(data,16),int(last)) for _,i,data,last in actual_words]==[(int(i),int(data,16),int(last)) for i,data,last in original_words]
    times=[int(row[0]) for row in actual_words]
    assert all(a<b for a,b in zip(times,times[1:])) and all(t%10000==5000 for t in times)
    assert times[-1]<=(end+200)*1000
    assert re.findall(r'^CP_TRANSFER_MONITOR_END words=(\d+)$',log,re.M)==[str(len(original_words))]
    group_rows=re.findall(r'^PAYLOAD_GROUP_PASS group=(KA|PW) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$',log,re.M)
    assert len(group_rows)==2 and {row[0] for row in group_rows}=={'KA','PW'}
    group_counts={row[0]:dict(zip(['active','stalled','transfers','edges','idle','idle_differences'],map(int,row[1:]))) for row in group_rows}
    for group,values in group_counts.items():
        assert all(values[k]>0 for k in ['active','transfers','edges','idle'])
        assert values['stalled']==0 if group=='KA' else values['stalled']>0
    assert 'FULL_SHADOW_PROTOCOL_PASS' not in log and 'KA_FIXTURE_READY_INVARIANT' not in log
    golden_ka=re.findall(r'^KA (\d+) (\d+) (\d+) (\d+) (\d+)$',(original/'natural_trace.txt').read_text(),re.M)
    assert len(golden_ka)==26
    source=(ref/'sources/tb_query_fault.sv').read_text()
    assert "bench_rst=1;k_cold_rst=1;design_id=64'h123456789abcdef0;" in source
    ka_transfers=check_ka((d/'shadow_ka_requests.log').read_text(),[tuple(map(int,row[1:])) for row in golden_ka],0x123456789abcdef0)
    golden_pw=re.findall(r'^W ([0-9a-fA-F]+) ([0-9a-fA-F]{16}) ([0-9a-fA-F]{128})$',(original/'label_axi.txt').read_text(),re.M)
    assert len(golden_pw)==8223
    pw_transfers=check_pw((d/'shadow_pw_beats.log').read_text(),[tuple(int(x,16) for x in row) for row in golden_pw])
    assert group_counts['KA']['transfers']==ka_transfers['requests']==26
    assert group_counts['PW']['transfers']==pw_transfers['write_beats']==8223
    assert re.findall(r'^PAYLOAD_TRANSFER_MONITOR_END ka=(\d+) pw=(\d+) aw=(\d+)$',log,re.M)==[('26','8223',str(pw_transfers['addresses']))]
    assert max(ka_transfers['last_time_ps'],pw_transfers['last_time_ps'])<=(end+200)*1000

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
    assert observations=={key:ra['observations'][key] for key in ['path','stage']}
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        common_gate_sha256=sha(ROOT/'scripts/stage_static_cp_shadow_common_v7_revision2.py'),reference_audit_sha256=sha(ref/'source_bound_audit.json'),
        exact_comparisons=comparisons,finish_time=finish[0],host_edit=he,
        original_coverage=ra['observations'],route_bank_observations=observations,
        modified_production_sources=sorted(fixed),production_sources=133,verification_sources=3,
        predecessor_evidence=m['predecessors'],timing_qualified=False,board_acceptance=False,
        full_system_functional_netlist_validated=True,physical_gate_open=False,
        preparation_sha256=sha(p/'preparation.json'),memory_admission=admission,
        fixture_ready_policy='KA valid requires known ready1 at sample/pre-edge; zero KA stalls, nonzero CP/PW stalls',
        shadow_checks=expected_checks,shadow_outputs=346,transport_shift_ns=200,
        parameters=m['parameters'],original_rtl_files=136,additional_shadow_compiled_files=5,compiled_file_count=141,
        unconditional_outputs=342,qualified_outputs=['cp_m_data','k_a_node','k_a_net','p_m_wdata'],clock_lead_ps=1,all_pin_strict_equivalence=False,
        payload_group_counts=group_counts,authority_transfers=ka_transfers,pager_write_transfers=pw_transfers,
        payload_log_sha256={n:sha(d/n) for n in ['shadow_ka_requests.log','shadow_pw_beats.log']},
        transfer_parser_sha256=sha(ROOT/'scripts/check_shadow_payload_transfer_logs_v1.py'),
        cp_protocol_counts=cp,cp_export_words=len(original_words),cp_export_frames=len(original_words)//156,
        cp_transfer_log_sha256=sha(d/'shadow_cp_export.log'),
        scope='Complete SLOTS32 host-driven functional shadow:342 outputs retain unconditional comparisons; cp_m_data,k_a_node,k_a_net,p_m_wdata are explicitly valid-qualified with known control/data, CP/PW stalls, KA ready1 invariant and all pre-edge transfers checked,1560 CP words,26 authority requests and8223 AXI write beats/address/strobes/last compared to accepted reference. Clock lead1ps before200ns data transport. Not unconditional all-pin equivalence. Original RTL closed-loop fixture and internal assertions retained,27 external files exact. Gate side shares recorded live RTL-driven inputs rather than independent memory agents. No arbitrary-input formal, physical timing or board proof.')
    assert not (p/'source_bound_audit.json').exists()
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('FULL_NETLIST_SHADOW_SYSTEM_AUDITED',len(comparisons),finish[0],observations)


if __name__=='__main__':main()
