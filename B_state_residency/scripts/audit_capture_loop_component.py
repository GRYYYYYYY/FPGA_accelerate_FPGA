"""Independent structural, event-order and local Boolean-contract checks."""
from pathlib import Path
from itertools import product
import hashlib,importlib.util,json,re,sys
from run_checkpoint_authority import ROOT,sha

def traversal():
    expected=[];summaries=[]
    for scenario in range(5):
        seen=set();counter=100;early=False;calls=decisions=depth=0
        def kids(node):
            if scenario==4:return []
            if scenario==3:return [node+1]if node<8 else[]
            if node==0:return [1,2]
            if node==1:return [3]if scenario==1 else[2]
            if scenario==1 and node==3:return [2]
            return []
        def expand(parent,level,cookie):
            nonlocal counter,early,calls,decisions,depth
            calls+=1;depth=max(depth,level);expected.append(f'E {scenario} {cookie} {parent}')
            for node in kids(parent):
                if early:break
                expected.append(f'M {scenario} {cookie} {parent} {node}')
                old=int(node in seen);expected.append(f'R {scenario} {parent} {node} {old}')
                if old:action=0
                elif scenario==2 and node==2:action=1;early=True
                else:action=2 if scenario==3 or parent==0 or(scenario==1 and node==3)else 1
                expected.append(f'O {scenario} {cookie} {parent} {node} {action}');decisions+=1
                if action:seen.add(node)
                if action==2:counter+=1;expand(node,level+1,counter)
        expand(0,1,100)
        summaries.append(f'CASE {scenario} PASS decisions={decisions} expansions={calls} depth={depth} early={int(early)}')
    return expected,summaries

def pop_equivalence():
    # Exhaust all two-state valuations of the relevant inputs. Enumerate the
    # old implicit feedback equation rather than substituting candidate logic.
    checked=0
    for valid,ready,offered,fault,idle,eligible,done_base in product([False,True],repeat=7):
        begin_valid=valid and idle and not ready and not offered
        qual=fault or not valid or offered
        old=[]
        for pop in [False,True]:
            begin_ready=eligible and not pop
            push=begin_valid and begin_ready;done=done_base and not push
            result=done and idle and qual
            if pop==(result and ready):
                old.append((begin_ready and idle and not ready and not offered,push,result,pop and done and not begin_valid))
        assert len(old)==1
        pop=ready and idle and qual;begin_ready=eligible and not pop
        push=begin_valid and begin_ready;done=done_base and not push;result=done and idle and qual
        new=(begin_ready and idle and not ready and not offered,push,result,pop and done and not begin_valid)
        assert old[0]==new
        checked+=1
    return checked

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and len(m['commands'])==20 and all(x['exit_code']==0 for x in m['commands'])
for n,e in m['sources'].items():assert sha(p/'sources'/n)==e['sha256'],n
for n,h in m['artifacts'].items():assert sha(p/n)==h,n
assert sha(p/'runner.py')==m['runner_sha256']
ref=Path(m['reference']);assert sha(ref/'source_bound_audit.json')==m['reference_audit_sha256']
builder=ROOT/'hardware/variants/capture_loops_v1/build.py'
assert sha(builder)==m['sources']['build.py']['sha256']
spec=importlib.util.spec_from_file_location('capture_loop_builder',builder);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
for mode in ['baseline','fixed']:
    for n,s in b.sources(mode=='fixed').items():assert (p/'sources'/mode/n).read_text()==s
assert (p/'sources/capture_loop_slice.sv').read_text()==b.wrapper()
assert (p/'sources/tb_root_offer.sv').read_text()==b.ready_test()
assert (p/'sources/baseline/children_frames.sv').read_bytes()==(p/'sources/fixed/children_frames.sv').read_bytes()
expected,summaries=traversal();cases={};events={};finishes={}
for mode in ['baseline','fixed']:
    d=p/mode/'synth';log=(d/'vivado.log').read_text()
    assert 'VIVADO_VERSION 2022.2'in log and 'CAPTURE_LOOP_SYNTH_DONE'in log
    assert not re.search(r'^ERROR:',log,re.M)
    facts=(d/'facts.txt').read_text().split();facts={facts[i]:int(facts[i+1])for i in range(0,len(facts),2)}
    assert facts['latches']==facts['blackboxes']==0 and facts['port_bits']>0
    counts={k:int(v)for k,v in re.findall(r'^\d+\. checking (\w+) \((\d+)\)',(d/'check_timing.rpt').read_text(),re.M)}
    if mode=='baseline':assert facts['loops']>0 and counts['loops']>0
    else:
        assert facts['loops']==counts['loops']==0
        assert not re.search(r'^CRITICAL WARNING:',log,re.M)
    assert not re.search(r'^(set_false_path|create_waiver|.*ALLOW_COMBINATORIAL_LOOPS)',(d/'synth.tcl').read_text(),re.M)
    cases[mode]=dict(facts=facts,check_timing=counts)
    events[mode]={};finishes[mode]={}
    for test in ['controller','retire','offer']:
        text=(p/mode/test/'simulate.log').read_text()
        assert 'Fatal:'not in text and 'Error:'not in text and '$finish called'in text
        finishes[mode][test]=re.findall(r'\$finish called at time : (.+)',text)
        assert len(finishes[mode][test])==1
        if test=='controller':
            rows=[l for l in text.splitlines()if l.startswith(('E ','M ','R ','O '))]
            assert [l for l in rows if int(l.split()[1])<5]==expected
            for scenario in [5,6]:
                terminal=[l for l in rows if int(l.split()[1])==scenario]
                assert [l[0]for l in terminal]==['E','M','R','O']
                assert terminal[-1].split()[-3:]==['0','1','2']
            assert [l for l in text.splitlines()if l.startswith('CASE ')]==summaries
            assert [l for l in text.splitlines()if l.startswith('STOP ')]==['STOP 5 PASS status=4 decisions=1 expansions=1','STOP 6 PASS status=4 decisions=1 expansions=1']
            events[mode][test]=rows
        elif test=='retire':
            rows=[l for l in text.splitlines()if l.startswith(('ITEM ','RESULT ','ERROR_RETIRED '))]
            assert rows==['ITEM 10 1','ITEM 20 3','RESULT 20 1','ITEM 10 2','RESULT 10 2']+[f'ERROR_RETIRED {x}'for x in [30,50,40,60,70,80,90,100,120]]
            events[mode][test]=rows
        else:
            accepts=[l for l in text.splitlines()if l.startswith('ACCEPT ')]
            if mode=='baseline':assert not accepts and 'ROOT_OFFER_BASELINE_BLOCKED cycles=16'in text
            else:assert accepts==['ACCEPT 1 201']and 'ROOT_OFFER_FIXED_PASS checks=18 accepted=1'in text
for test in ['controller','retire']:
    assert events['baseline'][test]==events['fixed'][test]
    assert finishes['baseline'][test]==finishes['fixed'][test]
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    builder_sha256=sha(builder),cases=cases,recursive_events=len(events['fixed']['controller']),
    capture_events=len(events['fixed']['retire']),existing_event_order_and_finish_times_identical=True,
    local_pop_two_state_equivalence_valuations=pop_equivalence(),finish_times=finishes,
    valid_dependent_receiver=dict(baseline_no_progress_cycles=16,candidate_acceptances=1,candidate_checks=18,invalid_rejected_locally=True),
    scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('CAPTURE_COMPONENT_AUDITED',result)
