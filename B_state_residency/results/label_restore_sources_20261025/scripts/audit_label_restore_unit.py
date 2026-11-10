from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(x['exit_code']==0 for x in m['commands'])
 assert sha(out/'sources/label_restore_controller.sv')==sha(ROOT/'hardware/variants/label_restore_v1/label_restore_controller.sv')
 rows=[l.split()for l in(out/'events.txt').read_text().splitlines()];replies=[list(map(int,r[1:]))for r in rows if r[0]=='R'];assert len(replies)==30
 expected={i:0 if i in [0,21,25]else 1 if i<=5 or i in [23,24]else 2 if i in [6,16]else 3 if i==7 else 4 if i in [8,15,20]else 5 if i in [9,10,11,12]else 6 if i in [13,14]else 7 for i in range(29)}
 assert [r[0]for r in replies]==[0,0]+list(range(1,29))
 for mode,status,written,verified,controls,writes,reads in replies:
  assert status==expected[mode]
  if status==0:assert written==verified==3 and controls in [2,4] and writes==controls//2*15 and reads==controls//2*4
  if 1<=mode<=5 or mode in [23,24]:assert controls==0 and writes==reads==0
 # Independent request reconstruction of each successful episode, including reuse.
 for mode in [0,21,25]:
  ls=[[int(r[3]),int(r[4]),int(r[5]),int(r[6],16)]for r in rows if r[0]=='L'and int(r[1])==mode]
  episode=[[0,2,0,0]]+[[1,n+2,f,[5+n,6,7,8,9][f]]for n in range(3)for f in range(5)]+[[0,n+2,0,0]for n in range(3)]
  # l_value on reads is deliberately don't-care; compare read semantic fields.
  for a in ls:
   if a[0]==0:a[3]=0
  assert ls==episode*(2 if mode==0 else 1)
 log=(out/'simulate.log').read_text();assert 'LABEL_RESTORE_PASS checks=30'in log and 'Fatal:'not in log and '$finish called'in log
 a=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),responses=30,scope='Registered control/labels unit: metadata, stream boundaries, absent probe, writes, checkpoint, readback, backpressure, reuse, held failures, cancellation and timeout drain; no real AXI claim.')
 (out/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
if __name__=='__main__':main()
