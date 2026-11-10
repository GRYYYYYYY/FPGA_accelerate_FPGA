"""Require literal full trace/cycle/DDR equality to the independently audited case."""
from pathlib import Path
import json,re,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and len(m['cases'])==1
case=next(iter(m['cases']));d=p/case;c=m['cases'][case]
assert c['status']=='observed'and len(c['commands'])==3 and all(x['exit_code']==0 for x in c['commands'])
ref=Path(m['capture_loop_reference']);rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
assert sha(ref/'source_bound_audit.json')==m['capture_loop_reference_audit_sha256']
receipt=ROOT/'results'/f'{ref.name}_restore_20261025.json';rr=json.loads(receipt.read_text())
assert rr['status']=='passed'and rr['audit_byte_identical']and rr['audit_sha256']==sha(ref/'source_bound_audit.json')
component=Path(m['capture_loop_component']);cm=json.loads((component/'manifest.json').read_text());ca=json.loads((component/'source_bound_audit.json').read_text())
assert ca['status']=='passed'and ca['manifest_sha256']==sha(component/'manifest.json')
assert sha(component/'source_bound_audit.json')==m['capture_loop_component_audit_sha256']
assert m['rtl']==rm['rtl']and m['binding_sha256']==rm['binding_sha256']==sha(Path(m['binding']))
changed=['recursive/recursive_candidate_controller.sv','capture/expansion_capture.sv']
assert set(m['sources'])==set(rm['sources'])
for n,e in m['sources'].items():
    assert sha(p/'sources'/n)==e['sha256'],n
    if n in changed:
        assert e['sha256']==cm['sources']['fixed/'+Path(n).name]['sha256']
        assert rm['sources'][n]['sha256']==cm['sources']['baseline/'+Path(n).name]['sha256']
    elif n!='runner.py':assert e['sha256']==rm['sources'][n]['sha256'],n
assert sha(p/'sources/runner.py')==sha(ROOT/'scripts/run_capture_loop_system.py')
for old,new in zip(rm['cases'][case]['commands'],c['commands']):
    assert new['stage']==old['stage']and new['argv']==[x.replace(str(ref),str(p))for x in old['argv']]
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    assert m[key]==rm[key]
    for n,h in m[key].items():assert sha(p/n)==h
files=sorted(f.name for f in(ref/case).iterdir()if f.is_file()and f.suffix in ['.txt','.bin','.dat'])
assert {f.name for f in d.iterdir()if f.is_file()and f.suffix in ['.txt','.bin','.dat']}==set(files)
assert len([n for n in files if n.endswith('_axi.txt')])==12
assert all(n in files for n in ['natural_trace.txt','owners.bin','labels.bin','runtime_g4_labels.txt','restore_seed_trace.txt'])
comparisons={}
for name in files:
    actual=sha(d/name);expected=sha(ref/case/name)
    assert actual==expected,(name,'literal bytes differ; do not normalize away events or cycles')
    comparisons[name]=dict(bytes=(d/name).stat().st_size,sha256=actual)
log=(d/'simulate.log').read_text();oldlog=(ref/case/'simulate.log').read_text()
assert 'Fatal:'not in log and '$finish called'in log
finish=re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',log)
assert len(finish)==1 and finish==re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)',oldlog)
markers=[l for l in log.splitlines()if any(tag in l for tag in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS'])]
assert markers==[l for l in oldlog.splitlines()if any(tag in l for tag in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS'])]
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    reference_audit_sha256=sha(ref/'source_bound_audit.json'),reference_restore_receipt_sha256=sha(receipt),
    component_audit_sha256=sha(component/'source_bound_audit.json'),modified_production_sources=changed,
    exact_comparisons=comparisons,finish_time=finish[0],markers=markers,
    inherited_numerical_scope='Exact literal native cycles, all12 AXI traces, stream images and final DDR equal the restored independently audited reference; its CPU/oracle and byte replay conclusions apply to these identical observed artifacts. No trace rewriting or relaxed comparison.',
    scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('CAPTURE_LOOP_SYSTEM_AUDITED',p.name,len(comparisons),finish[0])
