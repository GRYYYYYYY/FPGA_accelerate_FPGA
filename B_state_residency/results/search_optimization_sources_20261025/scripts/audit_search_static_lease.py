"""Bind frozen search model tests to command/response events and current RTL."""
from pathlib import Path
import hashlib,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());lease='search_host_fence.sv'in m['sources']
 assert m['status']=='passed' and len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 for n,h in m['sources'].items():
  assert sha(out/'sources'/n)==h
  current=ROOT/('scripts'if n.startswith('run_')else'hardware/variants/search_static_v2'if n=='search_host_fence.sv'else'hardware/variants/search_scheduler_v1')/n
  assert sha(current)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 if lease:
  p=ROOT/'hardware/variants/search_scheduler_v1/build_lease_unit.py';sp=importlib.util.spec_from_file_location('builder',p);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
  assert b.make().encode()==(out/'sources/tb_search_lease.sv').read_bytes()
 log=(out/'simulate.log').read_text();assert 'SEARCH_SCHEDULER_PASS checks=20'in log and '$finish called'in log and 'Fatal:'not in log
 rows=[l.split()for l in(out/'events.txt').read_text().splitlines()]
 expected=[(0,0,2,1,1),(0,0,2,1,1),(1,4,0,0,0),(2,3,0,0,0),(3,4,0,0,0),(4,5,1,0,0),(5,5,1,0,0),(6,6,1,0,0),(7,7,1,1,1),(8,7,2,1,1),(9,8,0,0,0),(10,10,0,0,0),(11,0,1,0,0),(12,2,1,1,1),(13,8,0,0,0),(14,1,0,0,0),(15,9,1,1,1),(16,4,0,0,0),(17,0,2,1,1),(0,0,2,1,1)]
 done=[list(map(int,t[1:]))for t in rows if t[0]=='DONE'];assert len(done)==20
 lane_sequences=[]
 for i,(d,e)in enumerate(zip(done,expected),1):
  assert d[:6]==[i,*e],(d,e)
  mode=e[0];rr=[t for t in rows if t[0]=='REQ' and int(t[1])==i];lanes=list(map(lambda t:int(t[3]),rr))
  wanted=[12,12,8,11,12,8,6]if mode in [0,8]else[12]if mode in [1,9,10,13,16]else[12,12]if mode in [2,3]else[12,12,8]if mode in [4,5,6]else[12,12,8,11]if mode in [7,12,15]else[12,12,8,6]if mode==11 else[]if mode==14 else[12,12,8,11,12,8,12,6]
  assert lanes==wanted,(i,lanes,wanted);assert d[-1]==len(rr)+(7 if i==2 else 0)
  for t in rr:
   lane=int(t[3]);v=int(t[4],16)
   if lane==11:assert v>>64&0xffffffff==10 and v>>160&0xffffffff==20 and v>>224&0xffffffff==7 and v>>416==3
   if lane==12 and v&0xffffffff==1:assert v>>32&0xffffffff==0 and v>>64&0xffffffff==10 and v>>128&0xffffffff==3
  lane_sequences.append(lanes)
 assert [t for t in rows if t[0]=='RECOVERY']==([['RECOVERY','11']]if lease else[])
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=done,service_lanes=lane_sequences,lease_composition=lease,scope='20 model scenarios, including same-instance reuse, immutable descriptors, errors/bounds/cancel/timeout/drain and held replies. Lease variant also contends all16 host lanes+route and delays recovery until cancelled search completion is consumed. Model backend only; no real-service search fault/recovery or liveness with permanently stalled backend.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','cases':len(done),'lease':lease}))
if __name__=='__main__':main()
