from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(out,marker):
 m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();assert marker in log and 'Fatal:'not in log and '$finish called'in log
 return m
def main():
 p=Path(sys.argv[1]).resolve();bridge=Path(sys.argv[2]).resolve();verify(p,'TRANSACTION_FENCE_PASS checks=11');verify(bridge,'RETIRED_IDLE_PASS checks=5')
 assert sha(p/'sources/transaction_fence.sv')==sha(ROOT/'hardware/variants/transaction_fence_v1/transaction_fence.sv')
 assert sha(bridge/'sources/cost_center_memory_call.sv')==sha(ROOT/'hardware/variants/transaction_fence_join_v1/backend/cost_center_memory_call.sv')
 rows=[r.split()for r in(p/'events.txt').read_text().splitlines()];rr=[list(map(int,r[1:]))for r in rows if r[0]=='R']
 assert rr==[[0,0,0,1,0,0],[1,0,0,1,1,0],[2,0,0,0,0,0],[3,6,0,0,0,0],[4,0,0,1,0,1],[5,0,0,0,0,0],[6,6,1,0,0,0],[7,0,0,1,1,0],[8,0,0,1,1,0],[9,0,0,0,1,0],[10,0,0,1,1,0]]
 aa=[(int(r[1]),int(r[3]),int(r[4]),int(r[5],16))for r in rows if r[0]=='A'];assert aa==[(0,1,0,0x31),(1,9,0,0x42),(1,9,1,0x53),(4,1,2,0x75),(4,1,0,0x64),(7,1,0,0x86),(7,2,1,0x96),(8,1,0,0xa8),(8,2,1,0xb8),(9,1,1,0xc1),(10,1,0,0xd2),(10,2,1,0xe0)]
 pending={}
 for r in rows:
  if r[0]=='A':key=(int(r[1]),int(r[4]));assert key not in pending;pending[key]=int(r[2])
  if r[0]=='B':key=(int(r[1]),int(r[4]));assert key in pending and int(r[2])>pending.pop(key)
 assert not pending and [int(r[1])for r in rows if r[0]=='K']==[0,1,2,3,5,6,7]
 for out,scope in [(p,'Eleven registered-backend episodes incl essential continuation during quiesce, frontend parent reply retirement before native ACK, and host/nonhost continuation type: payload capture, reply routing/backpressure, route pending drain, callback parallelism, admin bootstrap, failed recovery, physical/logical quiescence and invalid callback refusal.'),(bridge,'Five assertions distinguish idle sticky fault from held reply and owned HLS RUN even after ap_idle rises; no arithmetic numerical equivalence claim.')]:
  a=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),scope=scope)
  (out/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
if __name__=='__main__':main()
