"""Verify frozen sources, generated gate, executed stages and terminal contract."""
from pathlib import Path
import sys,json,runpy,tempfile
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
for n,h in m['artifacts'].items():assert sha(p/n)==h,n
assert [x['stage']for x in m['commands']]==['compile','elaborate','simulate']and all(x['exit_code']==0 for x in m['commands'])
b=runpy.run_path(str(p/'sources/build.py'))
with tempfile.TemporaryDirectory()as d:
 b['make'].__globals__['HERE']=Path(d);b['make']();assert (Path(d)/'warm_restore_receipt_join.sv').read_bytes()==(p/'sources/warm_restore_receipt_join.sv').read_bytes()
s=(p/'simulate.log').read_text();assert 'WARM_RETRY_UNIT_PASS checks=35'in s and '$finish called'in s and 'Fatal:'not in s
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=35,scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('WARM_RETRY_UNIT_AUDITED')
