"""Source-bound recovery retry unit checks, preserving original regressions."""
from pathlib import Path
import json,sys,importlib.util
from run_recovery_retry import ROOT,sha

def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 bench=ROOT/'hardware/variants/recovery_retry_v1';b=load(bench/'build.py','retry_build');u=load(bench/'build_units.py','retry_units')
 config='config_restore_controller.sv'in m['sources'];rtl='config_restore_controller.sv'if config else'recovery_coordinator.sv';tb='tb_config_restore.sv'if config else'tb_recovery_coordinator.sv'
 assert (out/'sources'/rtl).read_text()==b.make()[rtl]
 assert (out/'sources'/tb).read_text()==(u.config()if config else u.coordinator())
 log=(out/'simulate.log').read_text();assert '$finish called'in log and 'Fatal:'not in log
 rows=[t.split()for t in(out/'events.txt').read_text().splitlines()];R=[list(map(int,t[1:]))for t in rows if t[0]=='R']
 if config:
  expected=[]
  for mode in [0,0]+list(range(1,26)):
   status=1 if mode in [5,6,7,8]else 2 if mode in [10,11,21,22]else 3 if mode in [12,13,14,17]else 0
   mask=0 if mode in [5,6,7,8]else 1 if mode in [10,12]else 63
   expected.append([mode,status,mask,mask])
  expected += [[11,2,63,63],[0,0,63,63],[0,1,0,0],[0,0,63,63],[12,0,63,63]]
  assert R==expected and 'CONFIG_RESTORE_PASS checks=32 loads=39'in log
  ends=[i for i,t in enumerate(rows)if t[0]=='R'];start=0
  for end,r in zip(ends,R):
   batch=rows[start:end];cs=[t for t in batch if t[0]=='C'];bs=[t for t in batch if t[0]=='B'];lanes=[i for i in range(6)if r[2]>>i&1]
   assert sorted(int(t[3])for t in cs)==sorted(int(t[3])for t in bs)==lanes
   for c in cs:
    reply=next(t for t in bs if t[3]==c[3]);assert int(reply[2])>int(c[2])
    if c[3]!='0':assert int(next(t for t in bs if t[3]=='0')[2])<int(c[2])
   start=end+1
  assert len([t for t in rows if t[0]=='I'])==39
 else:
  expected=[[0,0,5,0],[0,0,1,0],[1,2,0,4],[2,2,0,4],[3,2,0,4],[4,4,5,4],[5,3,0,4],[6,3,0,4],[7,3,1,4],[0,6,0,4],[0,6,0,4],[10,6,1,4],[11,6,0,4],[12,6,0,4],[13,6,5,4]]+[[14,1,0,0]]*5+[[14,0,0,0],[15,5,0,4],[16,0,3,0],[17,0,6,0],[18,6,0,0],[19,2,0,4],[21,0,0,0],[22,4,1,1]]
  expected += [[5,3,0,4]]+[[5,1,0,4]]*5+[[0,0,5,0],[7,3,1,4],[0,0,4,0],[13,6,5,4],[0,0,0,0]]
  assert R==expected and 'RECOVERY_COORDINATOR_PASS checks=39'in log
  assert [t for t in rows if t[0]=='SOFT']==[['SOFT','0','4','5']]*3
  for t in rows:
   if t[0]=='AD':assert int(t[2],16)==0x12345678+(int(t[1])==19) and int(t[3],16)==int(t[4],16)==0x12345678
  # Independently count actual physical INC/DEC on successful retry episodes.
  softs=[i for i,t in enumerate(rows)if t[0]=='SOFT']
  for pos,wanted in zip(softs,[5,4,0]):
   end=next(i for i in range(pos+1,len(rows))if rows[i][0]=='R');ops=[t for t in rows[pos:end]if t[0]=='O' and t[3]!='0'];assert len(ops)==wanted
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),builder_sha256=sha(bench/'build.py'),unit_builder_sha256=sha(bench/'build_units.py'),responses=len(R),scope='Registered service models; original cases retained. Explicit retry preserves authority/journal/config descriptor. Fresh version/query, held replies, physical/logical drain, unexpected authority reply and physical partial repair checked. No real AXI or synthesis claim.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
