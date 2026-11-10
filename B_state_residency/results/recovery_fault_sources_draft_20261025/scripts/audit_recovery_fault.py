"""Independent real recovery-fault audit: CPU prefix, complete AXI bytes, journal/gates."""
from pathlib import Path
from collections import Counter
import json,struct,sys,importlib.util
from run_recovery_fault import ROOT,sha
from audit_route_fault_axi import replay

def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());partial='--partial' in sys.argv[2:]
 assert m['status']=='observed' or partial
 base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert sha(base/'manifest.json')==m['base_manifest_sha256'] and sha(base/'source_bound_audit.json')==m['base_audit_sha256']
 production=0
 for n,v in m['sources'].items():
  assert sha(out/'sources'/n)==v['sha256'],n
  if n not in ['runner.py','build_tb.py','tb_recovery_fault.sv']:
   assert v['sha256']==bm['sources'][n]['sha256'];production+=1
 assert production==122
 p=out/'sources/build_tb.py';sp=importlib.util.spec_from_file_location('recovery_fault_tb',p);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);b.ROOT=ROOT;b.BASE=base/'sources';assert b.make()==(out/'sources/tb_recovery_fault.sv').read_text()
 inp=Path(json.loads((ROOT/'results/query_lifecycle_join_v2/manifest.json').read_text())['input']);graph=ROOT/'results/graph_image_20261024';cpu=ROOT/'results/natural_query_v2';oracle=Path('/tmp/B_state_residency_offer_20261025/continuous_oracle_v1')
 imports={r[0]:list(r[1:])for r in struct.iter_unpack('<6I',(oracle/'initial_label_imports.u32').read_bytes())};order=list(imports)
 ct=[l.split() for l in(cpu/'events.txt').read_text().splitlines()]
 polls=[[int(x) for x in t[1:4]]for t in ct if t[0]=='P']
 candidates=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(ct)and ct[i+1][0]=='W')]for i,t in enumerate(ct)if t[0]=='C']
 costs=[(int(t[1]),sum(int(v,16)<<(32*j)for j,v in enumerate(t[2:25])),sum(int(v,16)<<(32*j)for j,v in enumerate(t[25:])))for t in map(str.split,(inp/'cost_vectors.txt').read_text().splitlines())]
 initial=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes();dirty=bytearray(initial);struct.pack_into('<4I',dirty,1411724*16,2718,65537,0,0)
 if not partial:assert set(m['cases'])==set(m['expected_cases'])
 report={}
 for name,cm in m['cases'].items():
  if partial and cm['status']!='observed':continue
  assert cm['status']=='observed' and cm['outcome']=='fail_closed',(name,cm.get('outcome'))
  d=out/name;fc=cm['recovery_fault'];assert cm['faultcase']==5
  for n,h in cm['artifacts'].items():assert sha(d/n)==h,(name,n)
  log=(d/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish called' in log and 'outcome=fail_closed' in log
  ts=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()]
  def by(tag):return [t for t in ts if t[0]==tag]
  for tag in ['FI','FAILED_QUERY','FK','RESET','RFI','RF_DONE','RF_HELD','RF_CLOSED']:assert len(by(tag))==1,(name,tag)
  assert not by('RETRY')and not by('LIFECYCLE')and not by('RF_STALLED')and not by('KD')
  cycles=[int(by(tag)[0][1])for tag in ['FI','FAILED_QUERY','FK','RESET','RFI','RF_DONE','RF_HELD','RF_CLOSED']];assert cycles==sorted(set(cycles))
  fi,rfi,done=by('FI')[0],by('RFI')[0],by('RF_DONE')[0]
  assert by('FAILED_QUERY')[0][5:]==['0','0','1']
  assert fi[2:]==['5','6','4'] and int(rfi[2])==fc and int(done[2])==fc and int(done[3])!=0 and int(done[5])==1
  assert int(by('RF_HELD')[0][1])-int(done[1])>=9 and int(by('RF_CLOSED')[0][1])-int(by('RF_HELD')[0][1])>=32
  # Reasserted recovery remains an unaccepted RECSEND(8) offer; sticky
  # coordinator fault keeps ready low. It must not create another FK/reset.
  assert by('RF_CLOSED')[0][2:]==['1','8']
  state=dict(t.split('=')for t in rfi[3:]);assert int(state['ctl'])==(7 if fc<=2 else 9)
  if fc<=2:assert int(state['owner_op'])==(0 if fc==1 else 2)
  else:assert int(state['label'])=={3:7,4:2,5:10}[fc]
  if fc==4:assert state['checkpoint']=='1'
  assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==polls
  assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==candidates
  assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==costs
  assert len(by('Q'))==72 and by('SEARCH')[0][2:]==['0','0','73','72','271']
  assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in by('I')}==imports
  assert [list(map(int,t[2:]))for t in by('J')]==[[1411724,2717,1]]
  assert [[int(t[3]),int(t[4])]for t in by('RO')]==[[1,1411724]]
  # No new host operation was admitted after the recovery acquired ownership.
  assert not [t for t in by('FS')if int(t[1])>int(by('FK')[0][1])]
  # Every recovery callback issued through the fence has a matching native reply.
  pending={};commands=Counter();returns=Counter()
  for t in ts:
   if int(t[1])<=int(by('RESET')[0][1]):continue
   if t[0]=='FD':
    assert t[2]=='9';lane=int(t[3]);assert lane not in pending;pending[lane]=int(t[1]);commands[lane]+=1
   elif t[0]=='FB':
    lane=int(t[3]);assert lane in pending and int(t[1])>pending.pop(lane);returns[lane]+=1
  assert not pending and commands==returns
  regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('owner',[(0x61fffff000,initial)],d/'owners.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],None),('qstate',[(0x81fffff000,inp/'connections.bin')],None),('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]
  mem={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
  for tag,v in mem.items():
   er=int(fc==1 and tag=='owner')+int(fc==5 and tag=='label');eb=int(tag=='owner')+int(fc==2 and tag=='owner')+int(fc in [3,4]and tag=='label')
   assert (v['error_read_beats'],v['error_write_replies'])==(er,eb),(name,tag,v)
  assert sha(d/'cost.bin')==sha(inp/'cost.bin')
  assert (d/'owners.bin').read_bytes()==(dirty if fc==1 else initial)
  assert mem['owner']['write_replies']==(1 if fc==1 else 2)
  assert int(done[4])==(0 if fc<=2 else 1)
  # Label stream and native writes are a prefix of the actual initial snapshot.
  reloads=by('RELOAD');assert [int(t[2])for t in reloads]==order[:len(reloads)]
  for t in reloads:assert int(t[3],16)==sum(v<<(32*j)for j,v in enumerate(imports[int(t[2])]))
  writes=[t for t in by('LL')if t[2]=='1'];expected=[(n,f,v)for n in order for f,v in enumerate(imports[n])]
  assert [(int(t[3]),int(t[4]),int(t[5],16))for t in writes]==expected[:len(writes)]
  checks=by('CHECK');good=[t for t in by('LX')if t[2]=='0']
  for t in checks:
   # A failed verification read is still recorded; only successful payloads
   # are certified by the paired native reply status below.
   match=[x for x in by('LX')if x[1]==t[1]];assert len(match)==1
   if match[0][2]=='0':assert int(t[3],16)==sum(v<<(32*j)for j,v in enumerate(imports[int(t[2])]))
  if fc<=2:assert not by('AUTH')and not by('LL')and not reloads
  else:
   assert by('AUTH')[0][2]=='1'
   assert len(by('LL'))==len(by('LX'))
   if fc in [4,5]:assert len(reloads)==328 and len(writes)==1640 and int(done[6])==328
  report[name]={'outcome':'fail_closed','second_fault_state':state,'native_error_status':int(done[3]),'confirmed_corrections':int(done[4]),'journal_count':int(done[5]),'snapshot_written':int(done[6]),'snapshot_verified':int(done[7]),'callback_transactions':dict(commands),'owner_sha256':sha(d/'owners.bin'),'memory':mem}
  print(name,'fail_closed audited',flush=True)
 result={'status':'partial'if partial else'passed','meaning':'Failure handling passed; recovery intentionally remains blocked, not successful restoration or automatic retry.','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'replay_sha256':sha(ROOT/'scripts/audit_route_fault_axi.py'),'unchanged_inherited_RTL_dat':production,'outcomes':dict(Counter(v['outcome']for v in report.values())),'cases':report,'scope':'One original owner B fault and one recovery AXI fault per case; all physical bytes replayed and actual callback retirement checked. Known q1 authority/snapshot only. No complete checkpoint, no recovery retry, no board claim.'}
 (out/('partial_audit.json'if partial else'source_bound_audit.json')).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
