"""Independent source/transaction checks for the twelve query interface cases."""
from pathlib import Path
import importlib.util
import json
import re
import sys
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'
v=ROOT/'hardware/variants/query_native_exclusion_v1'
for name,digest,original in [
 ('run_query_native_exclusion.py',m['runner_sha256'],ROOT/'scripts/run_query_native_exclusion.py'),
 ('build_tb.py',m['builder_sha256'],v/'build_tb.py'),
 ('manifest.json',m['variant_manifest_sha256'],v/'manifest.json'),
 ('tb_query_lifecycle.sv',m['parent_tb_sha256'],ROOT/'hardware/variants/query_lifecycle_v1/tb_query_lifecycle.sv')]:
    assert sha(p/'tools'/name)==digest==sha(original),name
vm=json.loads((v/'manifest.json').read_text())
spec=importlib.util.spec_from_file_location('query_tb',v/'build_tb.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
assert [(c['mode'],c['early']) for c in m['cases']]==[(mode,e)for mode in ['baseline','default','exclusive']for e in range(4)]
normal_statuses=[0,0,1,1,2,2,3,4,4,4,5,5,5,6,6,7,8,7,7,7,0,0,1,0,1,7,0,1]
observed={}
for c in m['cases']:
    mode,early=c['mode'],c['early'];name=f'{mode}_{early}';d=p/name
    assert c['status']=='passed'
    assert sha(d/'query_lifecycle.sv')==c['rtl_sha256']==vm['sources']['query_lifecycle.sv']['baseline'if mode=='baseline'else 'candidate']
    tb=(d/'tb.sv').read_text()
    assert sha(d/'tb.sv')==c['tb_sha256'] and tb==b.build(ROOT,mode,early)
    assert not re.search(r'\b(force|release)\s',tb)
    assert [x['stage']for x in c['commands']]==['compile','elaborate','simulate']
    for command in c['commands']:
        assert command['exit_code']==0
        assert sha(d/(command['stage']+'.stdout.log'))==command['log_sha256']
    log=(d/'simulate.log').read_text()
    assert sha(d/'simulate.log')==c['simulate_log_sha256']
    assert 'Fatal:'not in log and 'ERROR:'not in log
    expected=1 if early else 28
    assert re.findall(r'QUERY_LIFECYCLE_PASS checks=(\d+)',log)==[str(expected)]
    finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log);assert len(finish)==1
    events=(d/'events.txt').read_text();assert sha(d/'events.txt')==c['events_sha256']
    done=[list(map(int,l.split()[1:]))for l in events.splitlines()if l.startswith('DONE ')]
    assert len(done)==expected and all(len(x)==11 for x in done)
    assert [x[0]for x in done]==list(range(1,expected+1))
    assert [x[2]for x in done]==([7 if mode=='exclusive'else 0]if early else normal_statuses)
    monitor=re.findall(r'^MONITOR (\d+) (\d+)$',events,re.M)
    assert len(monitor)==1 and int(monitor[0][0])>0 and int(monitor[0][1])==int(bool(early))
    injections=re.findall(r'^EARLY (\d+) (\d+)$',events,re.M)
    assert len(injections)==int(bool(early))
    if early:
        assert int(injections[0][0])==early
        assert done[0][3]==int(mode!='exclusive' or early==3)
    observed[name]=dict(done=done,finish=finish[0],events_sha256=c['events_sha256'],observed_cycles=int(monitor[0][0]),injections=len(injections))
for early in range(4):assert observed[f'baseline_{early}']==observed[f'default_{early}']
assert observed['baseline_0']==observed['exclusive_0']
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=observed,
            scope='Twelve modeled-backend native controller tests with exact default and legal event/finish comparisons. No complete-system, X/Z formal or timing claim.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('QUERY_NATIVE_EXCLUSION_AUDITED cases=12')
