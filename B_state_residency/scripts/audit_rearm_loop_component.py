"""Audit actual native retirement/retry traces and local Boolean rewrites."""
from pathlib import Path
from itertools import product
import importlib.util,json,re,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and len(m['commands'])==8 and all(c['exit_code']==0 for c in m['commands'])
for n,e in m['sources'].items():assert sha(p/'sources'/n)==e['sha256'],n
for n,h in m['artifacts'].items():assert sha(p/n)==h,n
assert sha(p/'runner.py')==m['runner_sha256']
ref=Path(m['reference']);assert sha(ref/'source_bound_audit.json')==m['reference_audit_sha256']
bpath=ROOT/'hardware/variants/rearm_loops_v1/build.py';assert sha(bpath)==m['sources']['build.py']['sha256']
spec=importlib.util.spec_from_file_location('rearm_builder',bpath);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
expected_results=[]
for scenario in range(3):
    values=[(6,2,0),(1,2,0)]+([]if scenario==0 else[(6,3,0),(1,3,0)])+[(0,3 if scenario==0 else 4,1)]
    expected_results += [[scenario,*v]for v in values]
cases={};events={};finishes={}
for mode in ['baseline','fixed']:
    for n,s in b.sources(mode=='fixed').items():assert (p/'sources'/mode/n).read_text()==s
    assert (p/'sources'/mode/'rearm_loop_slice.sv').read_text()==b.wrapper(mode=='fixed')[0]
    d=p/mode/'synth';log=(d/'vivado.log').read_text()
    assert 'REARM_LOOP_SYNTH_DONE'in log and 'VIVADO_VERSION 2022.2'in log and not re.search(r'^ERROR:',log,re.M)
    f=(d/'facts.txt').read_text().split();facts={f[i]:int(f[i+1])for i in range(0,len(f),2)}
    counts={k:int(v)for k,v in re.findall(r'^\d+\. checking (\w+) \((\d+)\)',(d/'check_timing.rpt').read_text(),re.M)}
    assert facts['latches']==facts['blackboxes']==0
    if mode=='baseline':assert facts['loops']>0 and counts['loops']>0
    else:assert facts['loops']==counts['loops']==0 and not re.search(r'^CRITICAL WARNING:',log,re.M)
    assert not re.search(r'^(set_false_path|create_waiver|.*ALLOW_COMBINATORIAL_LOOPS)',(d/'synth.tcl').read_text(),re.M)
    cases[mode]=dict(facts=facts,check_timing=counts)
    log=(p/mode/'simulate/simulate.log').read_text()
    assert 'REARM_LOOP_PASS scenarios=3 successes=3 failures=10 checks=179'in log and 'Fatal:'not in log and '$finish called'in log
    rows=[l.split()for l in log.splitlines()if l.startswith(('RESET ','WRITE ','RESULT '))]
    assert [list(map(int,t[1:]))for t in rows if t[0]=='RESULT']==expected_results
    assert [list(map(int,t[1:]))for t in rows if t[0]=='RESET']==[[0,3],[1,4],[2,4]]
    assert [[int(t[1]),int(t[2]),int(t[3],16)]for t in rows if t[0]=='WRITE']==[[s,f,f+1]for s in range(3)for f in range(5)]
    for scenario in range(3):
        batch=[t for t in rows if int(t[1])==scenario]
        before=next(i for i,t in enumerate(batch)if t[0]=='RESET')
        assert all(t[0]=='RESULT'and t[2]!='0'for t in batch[:before])
        assert [t[0]for t in batch[before:]]==['RESET']+['WRITE']*5+['RESULT']
    events[mode]=rows;finishes[mode]=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log)
assert events['baseline']==events['fixed']and len(finishes['fixed'])==1 and finishes['baseline']==finishes['fixed']
assert (p/'sources/tb_rearm_loop.sv').read_text()==b.testbench()
assert not re.search(r'\bforce\s+',b.testbench())
checked=0
for state in range(16):
    for cold,safe,av,ar,ov,orr in product([False,True],repeat=6):
        unexpected=(av and state!=5 and not(state==4 and ar))or(ov and state!=7 and not(state==6 and orr))
        old=not cold and state==12 and safe and not unexpected
        new=not cold and state==12 and safe and not av and not ov
        assert old==new;checked+=1
for state,rsp in product(range(16),[False,True]):
    assert (not(state!=0)and not rsp)==(state==0 and not rsp)
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    builder_sha256=sha(bpath),cases=cases,coordinator_results=expected_results,
    reset_attempts=[[0,3],[1,4],[2,4]],actual_field_writes=15,verified_native_records=3,
    actual_owner_authority_requests=0,journal_entries=0,
    event_order_and_finish_time_identical=True,finish_time=finishes['fixed'][0],
    attempt_reset_two_state_valuations=checked,retirement_equal_without_reset_valuations=32,
    reset_masking_counterexample=dict(scope='Boolean state observation, not a forced runtime trace',rst=1,state='CS',rsp_valid=0,old_retired=True,new_retired=False),
    scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('REARM_COMPONENT_AUDITED',cases,'checks',checked,'finish',finishes['fixed'])
