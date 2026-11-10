"""Preserve actual false TB assertion, tied to the independently audited correction."""
from pathlib import Path
import json
import runpy
import sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
ref=p.parent/'fourth_system_full_v2';rm=json.loads((ref/'manifest.json').read_text())
ra=json.loads((ref/'source_bound_audit.json').read_text())
assert m['status']=='failed' and rm['status']=='observed' and ra['status']=='passed'
assert ra['manifest_sha256']==sha(ref/'manifest.json') and ra['auditor_sha256']==sha(ROOT/'scripts/audit_fourth_system.py')
assert len(m['cases']['full']['commands'])==3 and all(c['exit_code']==0 for c in m['cases']['full']['commands'])
for n,e in m['sources'].items():
    assert sha(p/'sources'/n)==e['sha256'],n
    if n not in ['tb_query_fault.sv','fourth_build.py']:assert e['sha256']==rm['sources'][n]['sha256'],n
tb=(p/'sources/tb_query_fault.sv').read_text();fixed=(ref/'sources/tb_query_fault.sv').read_text()
assert tb.count('!=190328')==2 and tb.replace('!=190328','!=180329')==fixed
assert runpy.run_path(str(p/'sources/fourth_build.py'))['make']()==tb
old=(p/'full/natural_trace.txt').read_bytes();new=(ref/'full/natural_trace.txt').read_bytes()
assert new.startswith(old)
rows=[t.split()for t in old.decode().splitlines()]
assert rows[-1]==['QCP','6','0','327d3916','0','180329']
query=[int(t[3],16)for t in rows if t[0]=='QCM'and t[1]=='6']
assert query==[0x51435031,1,0x9abcdef0,0x12345678,4,1,6,0x58,180329,0]
assert not any(t[0]=='G4_PUBLISHED'for t in rows)
log=(p/'full/simulate.log').read_text()
assert log.count('Fatal:')==1 and 'Fatal: G4 query/bundle identity'in log and 'THIRD_WARM_PASS'in log
counts={}
for tag in ['graph','design','table','label','owner','cost','qstate','snapshot','copy','labelsnap','baseline','g3copy']:
    a=(p/'full'/(tag+'_axi.txt')).read_bytes();b=(ref/'full'/(tag+'_axi.txt')).read_bytes()
    assert b.startswith(a),tag;counts[tag]=len(a.splitlines())
assert sha(p/'full/owners.bin')==sha(p/'full/g3.bin')==sha(p/'full/pool.bin')==ra['owner_sha256']
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),corrected_reference_audit_sha256=sha(ref/'source_bound_audit.json'),
            development_failure=True,failure='Generated TB assertion expected190328 although native G4 query correctly exported180329',changed_assertions=2,
            full_native_prefix_byte_identical=True,axi_prefix_lines=counts,
            scope='Evidence of test-generator assertion error only, not a production RTL counterexample or successful full G4/q4 run. Corrected native/physical prefix independently audited in full_v2.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FOURTH_DEVELOPMENT_AUDITED')
