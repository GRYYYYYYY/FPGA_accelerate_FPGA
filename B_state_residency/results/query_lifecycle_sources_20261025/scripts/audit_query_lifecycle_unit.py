from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'and len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 for n,h in m['sources'].items():
  assert sha(out/'sources'/n)==h==sha(ROOT/('scripts'if n.startswith('run_')else'hardware/variants/query_lifecycle_v1')/n)
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 log=(out/'simulate.log').read_text();assert 'QUERY_LIFECYCLE_PASS checks=28'in log and 'Fatal:'not in log and '$finish called'in log
 rows=[l.split()for l in(out/'events.txt').read_text().splitlines()];done=[list(map(int,t[1:]))for t in rows if t[0]=='DONE']
 modes=[0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,0,21,0,22,23,25,26]
 assert len(done)==len(modes)==28
 expected_status={0:0,1:1,2:1,3:2,4:2,5:3,6:4,7:4,8:4,9:5,10:5,11:5,12:6,13:6,14:7,15:8,16:7,17:7,18:7,19:0,21:1,22:1,23:7,25:0,26:1}
 for i,(d,mode)in enumerate(zip(done,modes),1):
  assert d[:3]==[i,mode,expected_status[mode]],d
  committed=mode in [0,11,12,13,18,19,25];assert d[3]==int(committed)
  ios=[t for t in rows if t[0]=='IO'and int(t[1])==i];search=[t for t in rows if t[0]=='SEARCH'and int(t[1])==i];route=[t for t in rows if t[0]=='ROUTE'and int(t[1])==i]
  wanted_ios=7 if mode in [0,13,19,25]else 0 if mode in [1,2,21,22,26]else 1 if mode in [3,4,14,15,23]else 3 if mode==5 else 6 if mode==12 else 5
  assert len(ios)==wanted_ios
  assert len(search)==int(mode in [0,6,7,8,9,10,11,12,13,16,17,18,19,25])
  assert len(route)==int(mode in [0,9,10,11,12,13,18,19,25])
  source,sink,seq=(11,21,8)if i==2 else(10,10,7)if mode==25 else(10,20,7)
  expected=[(8,source<<1),(8,1|(sink<<1)|(1<<33)|(4<<65)),(8,1|(source<<1)),(8,1|(source<<1)|(1<<65)),(8,1|(source<<1)|(seq<<33)|(3<<65)),(8,1|(sink<<1)|(4<<65)),(6,1|(1<<2)|(3<<4)|(3<<8))]
  assert [(int(t[3]),int(t[4],16))for t in ios]==expected[:wanted_ios]
  if route:
   packet=int(route[0][2],16);assert packet&1==0 and packet>>34&0xffffffff==source and packet>>66&0xffffffff==sink and packet>>130&0xffffffff==seq
   assert packet>>2&0xffffffff==100+i
  if d[2]==0:assert d[4:8]==[4,1,0 if mode==25 else 6,0 if mode==25 else 6]
  if mode in [9,11]:assert d[7]==(2 if mode==9 else 5) # report confirmed acknowledgements even on failed commit
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=done,scope='28 model scenarios: two-command target isolation, immutable descriptors, source checks, label/search/route/cleanup failures, bounds, held requests/response, abort during offered search or route, drain, strict sequence, external label edits, zero-interior path. rsp_committed records status0+matching native cookie even if contradictory ack counts later fail; it is not success by itself. Real lifecycle faults/recovery not exercised here.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','cases':len(done)}))
if __name__=='__main__':main()
