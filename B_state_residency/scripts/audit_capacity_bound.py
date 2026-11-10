from pathlib import Path
import sys,json,runpy
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
for n,h in m['artifacts'].items():assert sha(p/n)==h,n
b=runpy.run_path(str(p/'sources/build.py'));assert b['make']()==(p/'sources/recovery_coordinator.sv').read_text()
assert [x['stage']for x in m['commands']]==['compile','elaborate','simulate']and all(x['exit_code']==0 for x in m['commands'])
s=(p/'simulate.log').read_text();assert 'CAPACITY_BOUND_PASS refusals=2 gets=2 authority=2 journal=1'in s and '$finish called'in s and 'Fatal:'not in s
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),refusals=2,extra_repair_passes=1,failure_status=3,journal_retained=1,scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('CAPACITY_BOUND_AUDITED')
