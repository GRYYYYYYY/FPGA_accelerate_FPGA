"""Audit all-port read-only replay of failed v4 without changing its checker."""
from pathlib import Path
import json,re,sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_static_cp_shadow_failure_probe_v2'
    ref=BASE/'stage_static_cp_shadow_system_v4'
    m=read(p/'manifest.json');rm=read(ref/'manifest.json')
    assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/probe_stage_static_cp_shadow_failure_v2.py')
    assert rm['status']=='failed' and m['reference_manifest_sha256']==sha(ref/'manifest.json')
    assert m['command']==[a.replace(str(ref),str(p)) for a in rm['cases']['full']['commands'][-1]['argv']]
    assert sha(p/'full/run.tcl')==m['tcl_sha256']
    schema=ROOT/'results/stage_static_cp_port_schema_20261030.json'
    assert sha(schema)==m['schema_sha256']
    ports=read(schema)['ports'];outputs=[e['name'] for e in ports if e['direction']=='output'];inputs=[e['name'] for e in ports if e['direction']=='input']
    extra=['armed','reset_edges','checks','cp_active_checks','cp_stall_checks','cp_transfer_checks','cp_edge_checks','cp_idle_observations','cp_idle_differences']
    expected=[prefix+n for n in outputs for prefix in ['actual_','expected_']]+['drive_'+n for n in inputs]+extra
    assert m['objects']==expected and len(expected)==918 and len(outputs)==346 and len(inputs)==217
    for name,h in m['snapshot_sha256'].items():assert sha(p/'full/xsim.dir/iter2'/name)==sha(ref/'full/xsim.dir/iter2'/name)==h
    text=(p/'full/simulate.log').read_text();assert sha(p/'full/simulate.log')==m['log_sha256']
    failure='Fatal: FULL_SHADOW_MISMATCH port=k_a_net time=256000 actual=00000000 expected=xxxxxxxx'
    assert re.findall(r'^Fatal:.*$',text,re.M)==[failure]
    assert '$finish called at time : 255999 ps' in text
    rows=re.findall(r'^SHADOW_PROBE (before_255ns|after_256ns) (\w+) (\S+)$',text,re.M)
    assert len(rows)==1836
    values={label:{name:value.lower() for lab,name,value in rows if lab==label} for label in ['before_255ns','after_256ns']}
    inventory={}
    for label,v in values.items():
        assert len(v)==918 and set(v)==set(expected)
        for n in ['actual_k_a_valid','expected_k_a_valid','actual_cp_m_valid','expected_cp_m_valid','drive_cp_m_ready','drive_k_cold_rst']:
            assert v[n]=='0',(label,n,v[n])
        assert v['actual_k_a_net']=='00000000' and v['expected_k_a_net']=='xxxxxxxx'
        assert v['armed']=='1' and v['reset_edges']=='00000005'
        assert v['cp_transfer_checks']=='00000000'
        inventory[label]=dict(differences={n:dict(actual=v['actual_'+n],expected=v['expected_'+n]) for n in outputs if v['actual_'+n]!=v['expected_'+n]},
            unknown_actual=[n for n in outputs if re.search('[xz]',v['actual_'+n])],
            unknown_expected=[n for n in outputs if re.search('[xz]',v['expected_'+n])])
    assert values['before_255ns']['checks']=='00000000' and values['after_256ns']['checks']=='00000001'
    a=m['memory_admission'];assert a['stable_seconds']>=60 and a['current_bytes']*4<=a['limit_bytes']*3
    result=dict(status='passed',audit_kind='Read-only failed v4 snapshot inventory; not functional acceptance',
        manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),observations=values,
        output_inventory=inventory,first_failure=failure,first_failure_ps=255999,
        all_output_ports_observed=346,all_input_ports_observed=217,snapshot_and_checker_unchanged=True,
        same_failure_reproduced=True,authority_request_valid_zero_at_failure=True,no_cp_export_transfer_at_failure=True,
        full_system_functional_netlist_validated=False,scope='All ports observed at two timestamps in the exact copied failed snapshot. k_a_valid and cp_m_valid are0. This is not permission to mask other outputs, not active-transfer correctness, full protocol/formal equivalence, timing or board proof.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('V4_FAILURE_ALL_PORT_PROBE_AUDITED',[(k,len(v['differences'])) for k,v in inventory.items()])


if __name__=='__main__':main()
