"""Check native contract behavior and default-mode compatibility independently."""
from pathlib import Path
import importlib.util, json, re, sys
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve()
m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'
assert sha(p/'runner.py')==m['runner_sha256']==sha(ROOT/'scripts/run_recovery_backend_native.py')
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
for n,h in m['artifacts'].items():assert sha(p/n)==h,n
assert sha(Path(m['template_path']))==m['sources']['template.sv']
v=ROOT/'hardware/variants/recovery_backend_loops_v1'
assert sha(v/'build.py')==m['builder_sha256']
spec=importlib.util.spec_from_file_location('backend_builder',v/'build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
assert (p/'sources/baseline.sv').read_text()==b.sources(False)['recovery_coordinator.sv']
assert (p/'sources/fixed.sv').read_text()==b.sources(True)['recovery_coordinator.sv']
assert set(m['cases'])=={mode+'_'+str(e) for mode in ['baseline','default','exclusive']for e in range(3)}
observed={}
for name,c in m['cases'].items():
    d=p/name
    assert c['status']=='observed' and sha(d/'tb.sv')==c['tb_sha256']
    assert [x['stage']for x in c['commands']]==['compile','elaborate','simulate']
    assert all(x['exit_code']==0 for x in c['commands'])
    violated=c['mode']=='exclusive' and c['early']!=0
    status=6 if violated else 3
    tb=(p/'sources/tb_template.sv').read_text().replace('EARLY',str(c['early'])).replace('EXPECTED_STATUS',str(status))
    tb=tb.replace('PARAMS','#(.EXCLUSIVE_BACKEND_RESPONSES(1))'if c['mode']=='exclusive'else '')
    assert (d/'tb.sv').read_text()==tb
    assert not re.search(r'\b(force|release)\s',tb)
    log=(d/'simulate.log').read_text()
    assert 'Fatal:'not in log
    verdict=re.findall(r'BACKEND_CONTRACT_PASS status=(\d+) refusals=(\d+) gets=(\d+) authority=(\d+) journal=(\d+)',log)
    expected=[status,0,int(c['early']==2),1,1]if violated else [3,2,2,2,1]
    assert len(verdict)==1 and list(map(int,verdict[0]))==expected,(name,verdict)
    finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log)
    assert len(finish)==1
    events=[line for line in log.splitlines()if line.startswith('EVENT ')]
    parsed=[re.fullmatch(r'EVENT (\d+) (A_REQUEST|A_REPLY|O_REQUEST|O_REPLY) (\d+)(?: (\d+))?',line)for line in events]
    assert all(parsed)
    for tag,count in [('A_REQUEST',expected[3]),('A_REPLY',expected[3]),('O_REQUEST',expected[1]+expected[2]),('O_REPLY',expected[1]+expected[2])]:
        assert sum(x.group(2)==tag for x in parsed)==count,(name,tag)
    # The one-key authority cookie changes on the bounded repair pass.
    areqs=[(int(x.group(3)),int(x.group(4)))for x in parsed if x.group(2)=='A_REQUEST']
    assert areqs==[(208292,0x1001)]+([]if violated else [(208292,0x40001001)])
    oreqs=[(int(x.group(3)),int(x.group(4)))for x in parsed if x.group(2)=='O_REQUEST']
    expected_ops=([0]if c['early']==2 else [])if violated else [0,1,0,1]
    assert oreqs==[(op,0x1001+i)for i,op in enumerate(expected_ops)]
    observed[name]=dict(status=status,refusals=expected[1],gets=expected[2],authority=expected[3],journal=1,
        finish=finish[0],events=events)
for early in range(3):
    assert observed['baseline_'+str(early)]==observed['default_'+str(early)]
assert observed['baseline_0']==observed['exclusive_0']
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    builder_sha256=m['builder_sha256'],cases=observed,case_count=9,
    default_compatibility_cases=3,exclusive_legal_cases=1,exclusive_contract_violation_cases=2,
    scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('RECOVERY_BACKEND_NATIVE_AUDITED cases=9 default_comparisons=3 exclusive_legal=1 contract_violations=2')
