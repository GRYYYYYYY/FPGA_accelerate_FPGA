from pathlib import Path
import json,sys
from run_checkpoint_authority import sha
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();fixed=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
a=(p/'sources/checkpoint_authority_rotator.sv').read_text();b=(fixed/'sources/checkpoint_authority_rotator.sv').read_text();assert a.count('(!cfg_stage&&configured)')==1 and a.replace('(!cfg_stage&&configured)','(!cfg_stage&&(bound_generation!=0))')==b
assert sha(p/'sources/tb_rotate.sv')==sha(fixed/'sources/tb_rotate.sv')
for n in ['old','warm']:assert sha(p/(n+'.bin'))==m[n+'_sha256']==sha(fixed/(n+'.bin'))
log=(p/'simulate.log').read_text();assert log.count('Fatal:')==1 and 'native cfg status active=0000000100000001'in log and 'AUTHORITY_ROTATE_PASS'not in log
ts=[l.split()for l in(p/'events.txt').read_text().splitlines()];assert ts[-5][0]=='L'and ts[-5][3:]==['3','1']and ts[-4][0]=='F'and ts[-4][2:5]==['3','1','0000000100000002']
assert ts[-3][0]=='C'and ts[-3][2]=='0'and ts[-3][4:6]==['0000000100000001','17'];assert ts[-2][0]=='K'and ts[-2][3:]==['0000000100000001','17'];assert ts[-1][0]=='L'and ts[-1][3:]==['0','0']
assert len([t for t in ts if t[0]=='P'])==1
physical=replay(p/'snapshot_axi.txt',[(0x1000000000,p/'old.bin'),(0x2000000000,p/'warm.bin')]);assert physical['error_read_beats']==1 and physical['write_beats']==0
r={'status':'passed','meaning':'Expected pre-fix namespace rollback after canceled rearm; not a successful run.','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'fixed_manifest_sha256':sha(fixed/'manifest.json'),'sole_change':'initial-bind guard uses retained nonzero bound_generation rather than service configured flag','physical':physical,'observed_rollback':['0x100000002','0x100000001']}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('pre-fix identity rollback counterexample audited')
