"""Independent two-attempt recovery audit: frozen fault prefix, full CPU and AXI."""
from pathlib import Path
from collections import Counter
import json,struct,sys,importlib.util
from run_recovery_retry import ROOT,sha
from audit_route_fault_axi import replay

def module(p,name):
 sp=importlib.util.spec_from_file_location(name,p);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);return b

def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());partial='--partial'in sys.argv[2:]
 assert m['status']=='observed' or partial
 base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());ba=json.loads((base/'source_bound_audit.json').read_text())
 assert ba['status']=='passed' and sha(base/'manifest.json')==m['base_manifest_sha256'] and sha(base/'source_bound_audit.json')==m['base_audit_sha256']
 b=module(out/'sources/build.py','retry_rtl');b.BASE=base/'sources';derived=b.make()
 tb=module(out/'sources/build_tb.py','retry_tb');tb.ROOT=ROOT;tb.BASE=base/'sources';tb.SUCCESS=ROOT/'results/search_fault_retire_matrix_v6/sources/tb_query_fault.sv'
 assert tb.make()==(out/'sources/tb_recovery_retry.sv').read_text()
 production=0
 for n,v in m['sources'].items():
  assert sha(out/'sources'/n)==v['sha256'],n
  if n in derived:assert (out/'sources'/n).read_text()==derived[n]
  elif n not in ['runner.py','build_tb.py','build.py','tb_recovery_retry.sv']:
   assert v['sha256']==bm['sources'][n]['sha256'];production+=1
 assert production==119 and len(derived)==3
 inp=Path(json.loads((ROOT/'results/query_lifecycle_join_v2/manifest.json').read_text())['input']);graph=ROOT/'results/graph_image_20261024';cpu=ROOT/'results/natural_query_v2';oracle=Path('/tmp/B_state_residency_offer_20261025/continuous_oracle_v1')
 imports={r[0]:list(r[1:])for r in struct.iter_unpack('<6I',(oracle/'initial_label_imports.u32').read_bytes())};order=list(imports)
 final={r[0]:list(r[1:])for r in struct.iter_unpack('<6I',(oracle/'expected_label_reads.u32').read_bytes())};final[150697][4]=0
 ct=[l.split()for l in(cpu/'events.txt').read_text().splitlines()]
 polls=[[int(x)for x in t[1:4]]for t in ct if t[0]=='P']
 candidates=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(ct)and ct[i+1][0]=='W')]for i,t in enumerate(ct)if t[0]=='C']
 costs=[(int(t[1]),int(''.join(reversed(t[2:25])),16),int(''.join(reversed(t[25:])),16))for t in map(str.split,(inp/'cost_vectors.txt').read_text().splitlines())]
 initial=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes();expected=bytearray(initial);interiors=[1411724,3919432,2988027,1431200,554512,263946]
 for node in interiors:struct.pack_into('<4I',expected,node*16,2718,65537,0,0)
 if not partial:assert set(m['cases'])==set(m['expected_cases'])
 report={}
 for name,cm in m['cases'].items():
  if partial and cm['status']!='observed':continue
  assert cm['status']=='observed' and cm['outcome']=='recovered_retry',(name,cm)
  d=out/name;fc=cm['recovery_fault'];old=base/name
  for n,h in cm['artifacts'].items():assert sha(d/n)==h,(name,n)
  log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log
  ts=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()]
  def by(tag):return [t for t in ts if t[0]==tag]
  for tag in ['FI','FAILED_QUERY','RFI','RF_DONE','RF_HELD','RF_CLOSED','SOFT','KD','RETRY','LD','LIFECYCLE']:assert len(by(tag))==1,(name,tag)
  assert len(by('FK'))==len(by('RESET'))==2 and not by('RF_STALLED')and not by('STALLED')
  seq=[int(t[1])for t in [by('FI')[0],by('FAILED_QUERY')[0],by('FK')[0],by('RESET')[0],by('RFI')[0],by('RF_DONE')[0],by('RF_HELD')[0],by('RF_CLOSED')[0],by('FK')[1],by('SOFT')[0],by('RESET')[1],by('LD')[0],by('KD')[0],by('RETRY')[0],by('LIFECYCLE')[0]]];assert seq==sorted(set(seq)),name
  assert by('SOFT')[0][2:]==['1','3','5'] and by('RETRY')[0][2:]==['3','5']
  assert all(t[2:]==['1']for t in by('RESET'))
  assert by('RF_CLOSED')[0][2:]==['1','6'] and by('KD')[0][2:]==['0',str(int(fc==1))] and by('LD')[0][2:]==['0','328','328']
  # Match every first-attempt semantic event and every AXI byte to the already
  # independently audited fail-closed baseline. Cycle positions are not assumed.
  oldts=[l.split()for l in(old/'natural_trace.txt').read_text().splitlines()];first=[t for t in ts if int(t[1])<=int(by('RF_HELD')[0][1])]
  oldfirst=[t for t in oldts if int(t[1])<=int(next(t for t in oldts if t[0]=='RF_HELD')[1])]
  assert [[t[0]]+t[2:]for t in first]==[[t[0]]+t[2:]for t in oldfirst],(name,'first fault prefix')
  cut=int(by('RETRY')[0][1]);retry=[t for t in ts if int(t[1])>=cut]
  def rb(tag):return[t for t in retry if t[0]==tag]
  for part in [first,retry]:
   pb=lambda tag:[t for t in part if t[0]==tag]
   assert [[int(t[2]),int(t[3],16),int(t[4])]for t in pb('P')]==polls
   assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in pb('O')]==candidates
   assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in pb('C')]==costs
   assert len(pb('Q'))==72 and pb('SEARCH')[0][2:]==['0','0','73','72','271']
  assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in rb('Z')}==final
  assert [int(t[3])for t in rb('J')]==[2717]*6 and [int(t[2])for t in rb('J')]==interiors
  assert [[int(t[3]),int(t[4])]for t in rb('RO')]==[[1,n]for n in interiors]
  # Second stream is a complete replay; partial old stream is never continued.
  second=[t for t in ts if int(by('SOFT')[0][1])<int(t[1])<cut]
  sb=lambda tag:[t for t in second if t[0]==tag]
  assert [int(t[2])for t in sb('RELOAD')]==order
  for tag in ['RELOAD','CHECK']:
   assert len(sb(tag))==328
   for t in sb(tag):assert int(t[3],16)==sum(v<<(32*j)for j,v in enumerate(imports[int(t[2])]))
  writes=[t for t in sb('LL')if t[2]=='1'];assert [(int(t[3]),int(t[4]),int(t[5],16))for t in writes]==[(n,f,v)for n in order for f,v in enumerate(imports[n])]
  assert len(sb('LL'))==len(sb('LX')) and all(t[2]=='0'for t in sb('LX'))
  # Pair every recovery callback after both resets, no outstanding operation at
  # first completion or at second publication.
  pending={};commands=Counter()
  for t in ts:
   cycle=int(t[1])
   if cycle<=int(by('RESET')[0][1])or cycle>=cut:continue
   if t[0]=='FD':
    assert t[2]=='9';lane=int(t[3]);assert lane not in pending;pending[lane]=cycle;commands[lane]+=1
   elif t[0]=='FB':lane=int(t[3]);assert lane in pending and cycle>pending.pop(lane)
   elif t[0]in ['RF_DONE','SOFT','KD']:assert not pending
  assert not pending
  assert not [t for t in by('FS')if int(by('FK')[0][1])<int(t[1])<cut]
  regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('owner',[(0x61fffff000,initial)],d/'owners.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],None),('qstate',[(0x81fffff000,inp/'connections.bin')],None),('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]
  mem={}
  for tag,rr,ff in regions:
   assert (d/(tag+'_axi.txt')).read_bytes().startswith((old/(tag+'_axi.txt')).read_bytes()),(name,tag,'byte prefix')
   mem[tag]=replay(d/(tag+'_axi.txt'),rr,ff)
   assert (mem[tag]['error_read_beats'],mem[tag]['error_write_replies'])==(int(fc==1 and tag=='owner')+int(fc==5 and tag=='label'),int(tag=='owner')+int(fc==2 and tag=='owner')+int(fc in[3,4]and tag=='label'))
  assert (d/'owners.bin').read_bytes()==expected and sha(d/'cost.bin')==sha(inp/'cost.bin')
  assert mem['owner']['write_replies']==8
  # After the old failed attempt, owner writes are one needed DEC (GET fault
  # case only) followed by exactly six new INCs. Validate full 64-byte beats.
  suffix=(d/'owner_axi.txt').read_text()[len((old/'owner_axi.txt').read_text()):]
  ws=[t.split()for t in suffix.splitlines()if t.startswith('W ')]
  wants=([1411724]if fc==1 else[])+interiors;assert len(ws)==len(wants)
  for i,(t,node)in enumerate(zip(ws,wants)):
   off=(node*16)%64;assert int(t[1],16)==0x61fffff000+(node*16)//64*64 and int(t[2],16)==0xffff<<off
   row=int(t[3],16).to_bytes(64,'little')[off:off+16]
   assert row==(bytes(16)if fc==1 and i==0 else struct.pack('<4I',2718,65537,0,0))
  report[name]=dict(outcome='recovered_retry',first_attempt_error=int(by('RF_DONE')[0][3]),first_confirmed_corrections=int(by('RF_DONE')[0][4]),retry_confirmed_corrections=int(fc==1),journal_preserved=1,soft_resets=1,snapshot_written=328,snapshot_verified=328,retry_polls=73,retry_expands=72,retry_candidates=271,retry_costs=171,callbacks=dict(commands),owner_sha256=sha(d/'owners.bin'),memory=mem)
  print(name,'recovered_retry audited',flush=True)
 result=dict(status='partial'if partial else'passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),replay_sha256=sha(ROOT/'scripts/audit_route_fault_axi.py'),unchanged_RTL_dat=production,modified_RTL=sorted(derived),outcomes=dict(Counter(v['outcome']for v in report.values())),cases=report,scope='Explicit second command under fresh version/query and snapshot cookie. Two real AXI faults, full CPU replay and seven physical memory traces. Known initial 328 labels/q1 six-row authority; no full checkpoint, automatic retry, real price changes or board speedup.')
 (out/('partial_audit.json'if partial else'source_bound_audit.json')).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
