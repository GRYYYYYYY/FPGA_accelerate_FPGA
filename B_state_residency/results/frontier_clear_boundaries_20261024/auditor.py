"""Check service fail-stop tests against frozen integrated RTL and the normal gate."""
from pathlib import Path
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/frontier_clear_boundaries_20261024';normal=ROOT/'results/frontier_service_v3_20261024'
 api=runpy.run_path(str(ROOT/'scripts/audit_frontier_service.py'));m=api['verify_sources'](out)
 ng=json.loads((normal/'source_bound_audit.json').read_text());assert ng['status']=='passed' and ng['manifest_sha256']==sha(normal/'manifest.json')
 for name in ['frontier_hls_call.sv','frontier_service.sv']:
  assert sha(out/'sources'/name)==sha(normal/'sources'/name)
 log=(out/'frontier_service_fault.log').read_text();assert 'FRONTIER_SERVICE_FAULT_PASS cases=7 recovered_empty=1' in log and 'Fatal:' not in log and '$finish called' in log
 pending=None;tags=[];resets=boots=responses=0;faulted=False
 for line in (out/'fault_transactions.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='RESET':pending=None;faulted=False;resets+=1
  elif v[0]=='BOOT':boots+=1;assert not faulted
  elif v[0]=='Q':assert not faulted and pending is None;pending=v[1:]
  elif v[0]=='R':
   assert not faulted and pending is not None
   op=int(pending[0],16);assert op in (0,1,2)
   expected=1 if op==2 else 0
   assert list(map(lambda s:int(s,16),v[1:5]))==[expected,0,0,1 if op==1 else 0]
   assert v[5:]==pending[3:];pending=None;responses+=1
  elif v[0]=='FAULT':
   tag,active,size,initialized=map(int,v[1:]);assert tag==len(tags)
   assert (active,size,initialized)==((0,0,0) if tag==0 else ((1,1,1) if tag==6 else (1,0,1)))
   assert (pending is None) if tag==0 else (int(pending[0],16)==(5 if tag==6 else 1))
   tags.append(tag);faulted=True
  else:raise AssertionError(v)
 assert tags==list(range(7)) and resets==boots==7 and responses==10 and pending is None
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'normal_gate_sha256':sha(normal/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'fault_cases':['boot_idle_timeout','missing_completion_timeout','bad_status','bad_size','bad_nonpoll_payload','abort_inflight','bad_clear_size'],'cold_recoveries':7,'normal_responses':10,'scope':'Stop admission without committing mirrored size on timeout/bad HLS reply/abort; coordinated reset plus boot CLEAR recovers. Failed physical heap writes are not rolled back.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
