"""Audit bounded immutable-snapshot runtime diagnostic, not design acceptance."""
from pathlib import Path
import json,re,sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_static_cp_shadow_runtime_probe_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/probe_stage_static_cp_shadow_runtime_v1.py')
    parent=read(p/'parent_manifest_at_start.json')
    assert sha(p/'parent_manifest_at_start.json')==m['parent_snapshot_sha256']==m['reference_manifest_sha256']
    assert parent['status'] in ['running','observation_timeout'] and parent['stage']=='simulate'
    assert parent['mode']=='full_netlist_shadow_three_payload_contracts' and parent['parameters']['SLOTS']==32
    ref=BASE/'stage_static_cp_shadow_system_v5'
    assert m['command']==[a.replace(str(ref),str(p)) for a in parent['active_process']['argv']]+['--maxdeltaid','10000']
    assert m['max_requested_time_ns']==1000 and m['max_delta_iterations']==10000
    assert sha(p/'full/run.tcl')==m['tcl_sha256']
    for n,h in m['snapshot_sha256'].items():assert sha(p/'full/xsim.dir/iter2'/n)==sha(ref/'full/xsim.dir/iter2'/n)==h
    text=(p/'full/simulate.log').read_text();assert sha(p/'full/simulate.log')==m['log_sha256'] and sha(p/'full/stdout.log')==m['stdout_sha256']
    assert 'Fatal:' not in text and 'ERROR:' not in text and 'FULL_SHADOW_PROTOCOL_PASS' not in text
    steps=re.findall(r'^RUNTIME_PROBE_STEP (\d+) actual_time \{([^}]+)\} catch_code (\d+) message \{\}$',text,re.M)
    assert len(steps)==100
    def ps(value):
        match=re.fullmatch(r'(\d+) (ps|ns|us)',value);assert match,value
        return int(match[1])*{'ps':1,'ns':1000,'us':1000000}[match[2]]
    for i,(step,t,code) in enumerate(steps,1):assert int(step)==i and ps(t)==i*10000 and code=='0'
    cycles=re.findall(r'^RUNTIME_PROBE_CYCLES ([0-9a-f]+)$',text,re.M);assert len(cycles)==100
    assert [int(x,16) for x in cycles]==list(range(1,101))
    rows=re.findall(r'^RUNTIME_PROBE_VALUE (\w+) ([0-9a-f]+)$',text,re.M);assert len(rows)==600
    for n in ['cp_transfer_checks','ka_transfer_checks','pw_transfer_checks']:
        assert len([v for k,v in rows if k==n])==100 and all(int(v,16)==0 for k,v in rows if k==n)
    final={n:int(v,16) for n,v in rows[-6:]};assert final==dict(armed=1,reset_edges=5,checks=149,cp_transfer_checks=0,ka_transfer_checks=0,pw_transfer_checks=0)
    trace=(p/'full/natural_trace.txt').read_bytes();gold=BASE/'stage_static_cp_host_full_static_v1/full/natural_trace.txt'
    with gold.open('rb') as f:assert f.read(len(trace))==trace
    a=m['memory_admission'];assert a['stable_seconds']>=60 and a['current_bytes']*4<=a['limit_bytes']*3
    result=dict(status='passed',audit_kind='Bounded runtime diagnostic provenance, not functional acceptance',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),same_compiled_snapshot=True,source_or_checker_modified=False,original_solver_restarted=False,delta_limit=10000,delta_limit_reached=False,completed_steps=100,reached_time_ps=1000000,final_observer_counters=final,rtl_trace_reference_prefix_bytes=len(trace),full_system_functional_netlist_validated=False,scope='Exact v5 compiled snapshot advanced100 successive10ns steps to1us with official delta limit, no errors and149 comparisons. No CP/KA/PW transfers occurred in this early window. Does not prove full fixture, later scheduling, whole-run speed or absence of future delta loops; original full job remains authoritative.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('BOUNDED_RUNTIME_DIAGNOSTIC_AUDITED_1US_NO_DELTA_LIMIT')


if __name__=='__main__':main()
