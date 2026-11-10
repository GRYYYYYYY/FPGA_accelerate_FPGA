from pathlib import Path
import json,sys
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
expected=['1100','0100','1100']+['0100']*3+['0110']+['0010']*3+['0010']+['0010']*4+['0110']+['0110']*4+['1100','0101','1100','0001']
rows=[t.split()for t in(p/'guard_trace.txt').read_text().splitlines()];assert rows[:-1]==[['CHECK',str(i+1),v]for i,v in enumerate(expected)]and rows[-1]==['PASS','24']
log=(p/'simulate.log').read_text();assert 'BASELINE_GUARD_UNIT_PASS 24'in log and 'Fatal:'not in log
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=24,scope='Observer request ownership and physical AR/R drain, configuration offer, held AR/R, physical-complete but held logical reply, unexpected response and stray R fail closed. No root recovery proof.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('BASELINE_GUARD_UNIT_AUDITED')
