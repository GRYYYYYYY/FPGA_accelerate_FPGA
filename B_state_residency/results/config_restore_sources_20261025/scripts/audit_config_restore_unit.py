from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(x['exit_code']==0 for x in m['commands'])
 assert sha(out/'sources/config_restore_controller.sv')==sha(ROOT/'hardware/variants/config_restore_v1/config_restore_controller.sv')
 rows=[r.split()for r in(out/'events.txt').read_text().splitlines()];replies=[list(map(int,r[1:]))for r in rows if r[0]=='R'];assert len(replies)==27 and [r[0]for r in replies]==[0,0]+list(range(1,26))
 ends=[i for i,r in enumerate(rows)if r[0]=='R'];start=0
 for end,response in zip(ends,replies):
  mode,status,sent,retired=response;want=1 if mode in [5,6,7,8]else 2 if mode in [10,11,21,22]else 3 if mode in [12,13,14,17]else 0;mask=0 if mode in [5,6,7,8]else 1 if mode in [10,12]else 63
  assert status==want and sent==retired==mask
  batch=rows[start:end];requests=[r for r in batch if r[0]=='C'];responses=[r for r in batch if r[0]=='B'];lanes=[i for i in range(6)if mask>>i&1]
  assert sorted(int(r[3])for r in requests)==sorted(int(r[3])for r in responses)==lanes
  for q in requests:
   r=next(r for r in responses if r[3]==q[3]);assert int(q[2])<int(r[2]);lane=int(q[3]);assert int(r[4])==(5 if mode==10 and lane==0 or mode==11 and lane==2 or mode==21 and lane==5 or mode==22 and lane==1 else 0)
   if lane>0:assert int(next(r for r in responses if r[3]=='0')[2])<int(q[2])
  start=end+1
 installs=[list(map(int,r[1:]))for r in rows if r[0]=='I'];assert len(installs)==37
 assert sum(s for mode,s in installs)==9 # 7 malformed descriptors plus stale checkpoint and rollback version.
 log=(out/'simulate.log').read_text();assert 'CONFIG_RESTORE_PASS checks=27 loads=37'in log and 'Fatal:'not in log and '$finish called'in log
 a=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),responses=27,loads=37,scope='Six independent registered configuration services: resident immutable descriptor, load/start identity and handoff, nonrollback versions, no duplicate accepts, errors, exposed request cancellation/timeout, independent replies and physical/logical drain. Real backends tested separately.')
 (out/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
if __name__=='__main__':main()
