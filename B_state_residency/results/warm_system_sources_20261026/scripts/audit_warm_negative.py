from pathlib import Path
import sys,json
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
if '--context'in sys.argv:
 positive=p.parent/'warm_join_context_v1';old=(p/'sources/warm_restore_receipt_join.sv').read_text();new=(positive/'sources/warm_restore_receipt_join.sv').read_text();assert old.replace('((owner_repaired||state==DONE)&&!context_ok)','((ld||state==DONE)&&!context_ok)').replace('&&owner_repaired&&context_ok&&!ls;','&&owner_repaired&&!ls;')==new
 assert (p/'sources/tb_join_context.sv').read_bytes()==(positive/'sources/tb_join_context.sv').read_bytes();log=(p/'simulate.log').read_text();rows=[x.split()for x in(p/'native.txt').read_text().splitlines()];assert 'Fatal: check 9 scenario=0 state=3 receipts=000'in log and 'Time: 140 ns'in log and 'WARM_RECEIPT_JOIN_PASS'not in log
 assert any(r[0]=='I'and r[7:]==['1','0','18']for r in rows)and not any(r[0]=='L'for r in rows);reason='Owner-repaired preceding label initialization wrongly required active target context, quarantining before native label control could create it.'
else:
 assert '--handshake'in sys.argv;log=(p/'full_5/simulate.log').read_text();rows=[x.split()for x in(p/'full_5/natural_trace.txt').read_text().splitlines()];assert 'Fatal: warm repair binding'in log and 'WARM_RESTORE_OBSERVED'not in log
 assert len([r for r in rows if r[0]=='WARM_FAULT_START'])==1 and [r[2:]for r in rows if r[0]=='WA']==[['0','0']]
 assert not any(r[0]=='WL'for r in rows);reason='Frontend recover-ready coincides with backend acceptance; pre-edge attempt register remained0, so actual native recovery accepted without arming warm join.'
r=dict(status='passed',expected_failure=True,manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),reason=reason,scope='Source-bound observed negative, not an AXI correctness or successful-recovery claim.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='passed',expected_failure=True)))
