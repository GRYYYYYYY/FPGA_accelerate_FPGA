"""Independently audit complete59 three-payload observer controls."""
from pathlib import Path
import json,re,sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from prepare_stage_static_cp_shadow_protocol_v5 import render
from audit_shadow_cp_protocol_controls_v3 import expected_counts

LEGACY={
'matching':(None,None),'ready_nba':('READY_NBA',None),
'stall_data_flip':('DATA_FLIP_STALL','CP_DATA_MISMATCH phase=0 ready=0'),
'active_data_flip':('DATA_FLIP_ACTIVE','CP_DATA_MISMATCH'),
'edge_only_data_flip':('EDGE_ONLY_FLIP','CP_DATA_MISMATCH phase=1 ready=1'),
'active_unknown_both':('DATA_X_BOTH','CP_DATA_UNKNOWN'),
'valid_unknown_both':('VALID_X_BOTH','CP_VALID_UNKNOWN'),
'idle_valid_unknown_both':('IDLE_VALID_X_BOTH','CP_VALID_UNKNOWN'),
'valid_drop':('VALID_DROP','CP_VALID_MISMATCH'),'metadata_flip':('META_FLIP','CP_META_MISMATCH'),
'other_control_flip':('OTHER_FLIP','FULL_SHADOW_MISMATCH port=boot_pending'),
'other_control_x':('OTHER_X','FULL_SHADOW_MISMATCH port=boot_pending'),
'other_control_z':('OTHER_Z','FULL_SHADOW_MISMATCH port=boot_pending'),
'short_reset':('SHORT_RESET','FULL_SHADOW_INCOMPLETE'),
'no_stream':('NO_STREAM','CP_PROTOCOL_COVERAGE_MISSING'),
'no_transfers':('NO_TRANSFERS','CP_PROTOCOL_COVERAGE_MISSING'),
'no_stalls':('NO_STALLS','CP_PROTOCOL_COVERAGE_MISSING'),
'cp_data_z':('DATA_Z_BOTH','CP_DATA_UNKNOWN'),'cp_valid_z':('VALID_Z_BOTH','CP_VALID_UNKNOWN'),
'cp_idle_valid_z':('IDLE_VALID_Z_BOTH','CP_VALID_UNKNOWN'),
'cp_meta_x':('CP_META_X_BOTH','CP_META_UNKNOWN'),'cp_meta_z':('CP_META_Z_BOTH','CP_META_UNKNOWN'),
'cp_ready_x':('CP_READY_X','CP_READY_UNKNOWN')}
ADDITIONAL={
'stall_flip':('DATA_FLIP_STALL','DATA_MISMATCH phase=0 ready=0'),
'active_flip':('DATA_FLIP_ACTIVE','DATA_MISMATCH'),'edge_flip':('EDGE_ONLY_FLIP','DATA_MISMATCH phase=1 ready=1'),
'data_x':('DATA_X_BOTH','DATA_UNKNOWN'),'data_z':('DATA_Z_BOTH','DATA_UNKNOWN'),
'valid_x':('VALID_X_BOTH','VALID_UNKNOWN'),'valid_z':('VALID_Z_BOTH','VALID_UNKNOWN'),
'idle_valid_x':('IDLE_VALID_X_BOTH','VALID_UNKNOWN'),'idle_valid_z':('IDLE_VALID_Z_BOTH','VALID_UNKNOWN'),
'valid_drop':('VALID_DROP','VALID_MISMATCH'),'meta_flip':('META_FLIP','META_MISMATCH'),
'meta_x':('META_X_BOTH','META_UNKNOWN'),'meta_z':('META_Z_BOTH','META_UNKNOWN'),
'ready_x':('READY_X','READY'),'no_stream':('NO_STREAM','PROTOCOL_COVERAGE_MISSING'),
'no_transfers':('NO_TRANSFERS','PROTOCOL_COVERAGE_MISSING'),'no_stalls':('NO_STALLS','PROTOCOL_COVERAGE_MISSING')}
EXPECTED={**LEGACY,**{g.lower()+'_'+n:(g+'_'+d,g+'_'+e) for g in ['KA','PW'] for n,(d,e) in ADDITIONAL.items()},'ka_node_only_flip':('KA_NODE_ONLY_FLIP','KA_DATA_MISMATCH'),'ka_net_only_flip':('KA_NET_ONLY_FLIP','KA_DATA_MISMATCH')}


def coverage_fields(fatal,name):
    c=re.search(r'active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+)',fatal);assert c
    active,stalled,transfers,edges,idle=map(int,c.groups())
    assert idle>0
    if name.endswith('no_stream'):assert active==stalled==transfers==edges==0
    elif name.endswith('no_transfers'):assert active>0 and stalled>0 and transfers==0 and edges>0
    elif name.endswith('no_stalls'):assert active>0 and stalled==0 and transfers==edges==5
    else:raise AssertionError(name)


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'shadow_payload_contract_controls_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete'
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/run_shadow_payload_contract_controls_v1.py')
    assert m['planned_cases']==len(EXPECTED)==59 and set(m['cases'])==set(EXPECTED)
    prep=ROOT/'results/shadow_payload_contract_controls_v1_preparation_20261030.json'
    for f,h in read(prep)['tools'].items():assert sha(f)==h
    v=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5';parent=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4'
    assert m['checker_sha256']==sha(v/'shadow.sv') and m['checker_manifest_sha256']==sha(v/'manifest.json')
    assert render((parent/'shadow.sv').read_text())==(v/'shadow.sv').read_text()
    admission=m['memory_admission'];assert admission['stable_seconds']>=60 and admission['current_bytes']*4<=admission['limit_bytes']*3
    outcomes={};source_hashes=set()
    for name,(define,error) in EXPECTED.items():
        c=m['cases'][name];d=p/name;assert c['status']=='observed'
        for n,h in c['inputs'].items():assert sha(d/n)==h
        assert sha(d/'shadow.sv')==m['checker_sha256']
        source_hashes.add(sha(d/'control.sv'));source=(d/'control.sv').read_text()
        for advance in ['if(stream_valid&&cp_m_ready)word_index<=word_index+1;','if(ka_stream&&ka_ready)ka_index<=ka_index+1;','if(pw_stream&&p_m_wready)pw_index<=pw_index+1;']:
            assert advance in source
        commands=c['commands'];assert [x['stage'] for x in commands]==['compile','elaborate','simulate']
        a=commands[0]['argv'];macros=[a[i+1] for i,s in enumerate(a) if s=='-d'];assert macros==['SHADOW_NETLIST_TOP=protocol_gate']+([define] if define else [])
        for command in commands:
            assert command['exit_code']==0 and sha(d/(command['stage']+'.stdout.log'))==command['stdout_sha256']
        log=(d/'simulate.stdout.log').read_text();fatal=re.findall(r'^Fatal:.*$',log,re.M)
        if error is None:
            assert not fatal and '$finish called at time : 1202 ns' in log
            pattern=r'^FULL_SHADOW_PROTOCOL_PASS outputs=346 unconditional=342 qualified=cp_m_data,k_a_node,k_a_net,p_m_wdata checks=(\d+) reset_edges=(\d+) original_end=(\d+) last_checked=(\d+) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$'
            rows=re.findall(pattern,log,re.M);assert len(rows)==1
            values=list(map(int,rows[0]));assert values[:4]==[190,5,1000000,1201000]
            expected=expected_counts(205 if name=='ready_nba' else 200)
            groups={'CP':values[4:]}
            rows=re.findall(r'^PAYLOAD_GROUP_PASS group=(KA|PW) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$',log,re.M)
            assert len(rows)==2 and {r[0] for r in rows}=={'KA','PW'}
            groups.update({row[0]:list(map(int,row[1:])) for row in rows})
            for group,vv in groups.items():
                assert vv[:4]==expected and vv[4]==vv[5] and all(x>0 for x in vv), (name,group,vv,expected)
            outcomes[name]=dict(verdict='match',groups=groups)
        else:
            assert len(fatal)==1 and error in fatal[0],(name,fatal)
            assert 'FULL_SHADOW_PROTOCOL_PASS' not in log
            if 'COVERAGE_MISSING' in error:coverage_fields(fatal[0],name)
            outcomes[name]=dict(verdict='expected_rejection',fatal=fatal[0])
    assert len(source_hashes)==1
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),preparation_sha256=sha(prep),checker_sha256=m['checker_sha256'],outcomes=outcomes,complete_contract_controls_passed=True,completed_expected_cases=59,unconditional_outputs=342,valid_qualified_outputs=['cp_m_data','k_a_node','k_a_net','p_m_wdata'],all_pin_strict_equivalence=False,full_system_functional_netlist_validated=False,scope='59 bounded fake-model controls: two legal5-beat streams per group with idle X/0 and stalls;57 faults/nonvacuity negatives. CP task unchanged,342 comparisons exact. No actual FPGA netlist result.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('THREE_PAYLOAD_CONTROLS59_INDEPENDENTLY_AUDITED')


if __name__=='__main__':main()
