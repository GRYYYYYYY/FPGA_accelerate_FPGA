"""Independently audit complete v5 controls or preserved partial v4 evidence."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from prepare_stage_static_cp_shadow_protocol_v4 import render

EXPECTED={
 'matching':(None,None),'ready_nba':('READY_NBA',None),
 'stall_data_flip':('DATA_FLIP_STALL','CP_DATA_MISMATCH phase=0 ready=0'),
 'active_data_flip':('DATA_FLIP_ACTIVE','CP_DATA_MISMATCH'),
 'edge_only_data_flip':('EDGE_ONLY_FLIP','CP_DATA_MISMATCH phase=1 ready=1'),
 'active_unknown_both':('DATA_X_BOTH','CP_DATA_UNKNOWN'),
 'valid_unknown_both':('VALID_X_BOTH','CP_VALID_UNKNOWN'),
 'idle_valid_unknown_both':('IDLE_VALID_X_BOTH','CP_VALID_UNKNOWN'),
 'valid_drop':('VALID_DROP','CP_VALID_MISMATCH'),
 'metadata_flip':('META_FLIP','CP_META_MISMATCH'),
 'other_control_flip':('OTHER_FLIP','FULL_SHADOW_MISMATCH port=boot_pending'),
 'other_control_x':('OTHER_X','FULL_SHADOW_MISMATCH port=boot_pending'),
 'other_control_z':('OTHER_Z','FULL_SHADOW_MISMATCH port=boot_pending'),
 'short_reset':('SHORT_RESET','FULL_SHADOW_INCOMPLETE'),
 'no_stream':('NO_STREAM','CP_PROTOCOL_COVERAGE_MISSING'),
 'no_transfers':('NO_TRANSFERS','CP_PROTOCOL_COVERAGE_MISSING'),
 'no_stalls':('NO_STALLS','CP_PROTOCOL_COVERAGE_MISSING')}


def main():
    p=Path(sys.argv[1]).resolve();assert p.parent==BASE and p.name in ['shadow_cp_protocol_controls_v4','shadow_cp_protocol_controls_v5']
    partial=p.name.endswith('_v4');version='v4' if partial else 'v5'
    m=read(p/'manifest.json');assert not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts'/f'run_shadow_cp_protocol_controls_{version}.py')
    if partial:
        assert m['status']=='failed' and m['stage']=='edge_only_data_flip_simulate'
        assert set(m['cases'])==set(list(EXPECTED)[:5])
    else:
        assert m['status']=='observed' and m['stage']=='complete'
        assert set(m['cases'])==set(EXPECTED)
    variant=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4'
    parent=ROOT/'hardware/variants/stage_static_cp_shadow_clock_v2/shadow.sv'
    vm=read(variant/'manifest.json')
    assert m['checker_manifest_sha256']==sha(variant/'manifest.json')
    assert m['checker_sha256']==sha(variant/'shadow.sv')==vm['files']['shadow.sv']
    assert render(parent.read_text())==(variant/'shadow.sv').read_text()
    outcomes={};sources=set()
    for name,c in m['cases'].items():
        d=p/name;define,expected=EXPECTED[name]
        assert c['status']=='observed' or (partial and name=='edge_only_data_flip' and c['status']=='running')
        for file,h in c['inputs'].items():assert sha(d/file)==h
        assert sha(d/'shadow.sv')==m['checker_sha256']
        source=(d/'control.sv').read_text();sources.add(sha(d/'control.sv'))
        assert 'if(stream_valid&&cp_m_ready)word_index<=word_index+1;' in source
        assert 'wire stream_valid=(counter>=10&&word_index<5);' in source
        assert "(32'hd00d0000+word_index)" in source
        assert 'always @(posedge clk)if(cold)stream<=0;else stream<=stream+1;' in source
        if not partial:assert '#4.999;edge_fault=1;' in source
        commands=c['commands'];assert [v['stage'] for v in commands]==['compile','elaborate','simulate']
        compiler=commands[0]['argv'];macros=[compiler[i+1] for i,x in enumerate(compiler) if x=='-d']
        assert macros==['SHADOW_NETLIST_TOP=protocol_gate']+([define] if define else [])
        for command in commands:
            assert command['exit_code']==0
            assert sha(d/(command['stage']+'.stdout.log'))==command['stdout_sha256']
        log=(d/'simulate.stdout.log').read_text();fatal=re.findall(r'^Fatal:.*$',log,re.M)
        if expected is None:
            assert not fatal and '$finish called at time : 1202 ns' in log
            pattern=r'^FULL_SHADOW_PROTOCOL_PASS outputs=346 unconditional=345 qualified=cp_m_data checks=(\d+) reset_edges=(\d+) original_end=(\d+) last_checked=(\d+) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$'
            rows=re.findall(pattern,log,re.M);assert len(rows)==1
            values=list(map(int,rows[0]));assert values[:4]==[190,5,1000000,1201000]
            active,stall,transfers,edges,idle,diffs=values[4:]
            assert all(v>0 for v in values[4:]) and transfers==5 and idle==diffs
            if name=='matching':assert [active,stall,transfers,edges]==[30,16,5,10]
            if name=='ready_nba':assert [active,stall,transfers,edges]==[33,19,5,11]
            outcomes[name]=dict(verdict='match',active=active,stalled=stall,transfers=transfers,edges=edges,idle=idle,idle_differences=diffs)
        else:
            assert len(fatal)==1 and 'FULL_SHADOW_PROTOCOL_PASS' not in log
            if partial and name=='edge_only_data_flip':
                assert 'CP_DATA_MISMATCH phase=0 ready=1 time=411000' in fatal[0]
                verdict='corruption_detected_but_edge_control_not_isolated'
            else:
                assert expected in fatal[0],(name,fatal[0]);verdict='expected_rejection'
            if name in ['no_stream','no_transfers','no_stalls']:
                counts=re.search(r'active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+)',fatal[0]);assert counts
                active,stall,transfers,edges,idle=map(int,counts.groups())
                if name=='no_stream':assert active==stall==transfers==edges==0 and idle>0
                if name=='no_transfers':assert active>0 and stall>0 and transfers==0 and edges>0 and idle>0
                if name=='no_stalls':assert active>0 and stall==0 and transfers==5 and edges==5 and idle>0
            outcomes[name]=dict(verdict=verdict,fatal=fatal[0])
    assert len(sources)==1
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                outcomes=outcomes,complete_contract_controls_passed=not partial,planned_cases=17,
                completed_expected_cases=4 if partial else 17,checker_sha256=m['checker_sha256'],
                unconditional_outputs=345,valid_qualified_outputs=['cp_m_data'],
                clock_lead_ps=1,all_pin_strict_equivalence=False,full_system_functional_netlist_validated=False,
                scope='Bounded observer controls: two legal5-beat matches with idle X/0, stalls and NBA stimulus; negative corruption/unknown/control/frame/reset and non-vacuous coverage cases. Partial v4 preserves its failed phase-isolation expectation. No actual FPGA gate proof.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('CP_PROTOCOL_CONTROLS_AUDITED',version,len(outcomes),'complete',not partial)


if __name__=='__main__':main()
