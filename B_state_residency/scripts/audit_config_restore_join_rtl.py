from pathlib import Path
from collections import Counter
import json,hashlib,struct,mmap,re,sys,importlib.util
from audit_route_fault_axi import replay
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed';base=ROOT/'results/route_join_rtl_v1';bm=json.loads((base/'manifest.json').read_text());inp=Path(m['input']);graph=ROOT/'results/graph_image_20261024';cpu=ROOT/'results/natural_query_v2'
 assert m['base_audit_sha256']==sha(base/'source_bound_audit.json') and m['capture_audit_sha256']==sha(cpu/'source_bound_audit.json')
 same=0
 for n,h in m['sources'].items():
  assert sha(out/'sources'/n)==h
  if n not in ['runner.py','tb_config_restore_join.sv','route_commit_host_adapter.sv','axi_drain_watch.sv','recovery_coordinator.sv','label_restore_controller.sv','config_restore_controller.sv']:assert bm['sources'][n]['sha256']==h;same+=1
 assert same==110
 assert sha(out/'sources/runner.py')==sha(ROOT/'scripts/run_config_restore_join_rtl.py')
 assert sha(out/'sources/route_commit_host_adapter.sv')==sha(ROOT/'hardware/variants/recovery_join_v1/route_commit_host_adapter.sv')
 assert sha(out/'sources/axi_drain_watch.sv')==sha(ROOT/'hardware/variants/route_commit_join_drain_v2/axi_drain_watch.sv')
 builder=ROOT/'hardware/variants/config_restore_join_v1/build_tb.py';sp=importlib.util.spec_from_file_location('builder',builder);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);assert mod.make().encode()==(out/'sources/tb_config_restore_join.sv').read_bytes()
 config_unit=ROOT/'results/config_restore_unit_v2';assert json.loads((config_unit/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(out/'sources/config_restore_controller.sv')==sha(config_unit/'sources/config_restore_controller.sv')==sha(ROOT/'hardware/variants/config_restore_v1/config_restore_controller.sv')
 assert sha(out/'sources/label_restore_controller.sv')==sha(ROOT/'hardware/variants/label_restore_v1/label_restore_controller.sv')
 unit=ROOT/'results/label_restore_unit_v2';assert json.loads((unit/'source_bound_audit.json').read_text())['status']=='passed';assert sha(out/'sources/label_restore_controller.sv')==sha(unit/'sources/label_restore_controller.sv')
 assert sha(out/'sources/recovery_coordinator.sv')==sha(ROOT/'hardware/variants/recovery_coordinator_v1/recovery_coordinator.sv')
 assert sha(out/'sources/recovery_coordinator.sv')==json.loads((ROOT/'results/recovery_coordinator_unit_v4/manifest.json').read_text())['sources']['recovery_coordinator.sv']
 assert sha(out/'imports.txt')==m['imports_sha256'];records={int(t[0]):[int(x,16)for x in t[1:]]for t in map(str.split,(out/'imports.txt').read_text().splitlines())};assert len(records)==328
 with(cpu/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as snap:
  for n,r in records.items():v=struct.unpack_from('<11I',snap,n*44);assert r==[v[0],v[1],v[3],v[4],v[5]]
  chain=[];n=150697
  while n!=0xffffffff:chain.append(n);assert len(chain)<=8;n=struct.unpack_from('<I',snap,n*44+12)[0]
 q2=ROOT/'results/followup_q2_v1'
 assert m['authority_after_audit_sha256']==sha(q2/'source_bound_audit.json')
 authority=[]
 with(cpu/'initial_nodes.u32').open('rb')as f,(q2/'initial_nodes.u32').open('rb')as g,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as before,mmap.mmap(g.fileno(),0,access=mmap.ACCESS_READ)as after:
  for n in chain[1:-1]:
   a=struct.unpack_from('<11I',before,n*44);b=struct.unpack_from('<11I',after,n*44)
   authority.append(f'{n} 2717 {a[7]if a[6]==2717 else 0} {a[8]} {b[7]if b[6]==2717 else 0} {b[8]}\n')
 assert (out/'authority.txt').read_text()==''.join(authority) and sha(out/'authority.txt')==m['authority_sha256']
 pages={}
 for n,r in records.items():p,s=divmod(n,8);b=pages.setdefault(p,bytearray(192));b[0]|=1<<s;struct.pack_into('<5I',b,1+20*s,*r)
 expected=Counter(map(bytes,pages.values()));expected[bytes(192)]+=16384-len(pages)
 owner_initial=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes();owner_one=bytearray(owner_initial);assert struct.unpack_from('<4I',owner_initial,chain[1]*16)==(0,0,0,0);struct.pack_into('<4I',owner_one,chain[1]*16,2718,65537,0,0)
 assert len(m['commands'])==4 and all(c['exit_code']==0 for c in m['commands'])
 assert set(m['cases'])=={f'{mode}_{case}'for mode in ['full','pressure']for case in range(1,6)};counts={}
 for name,cm in m['cases'].items():
  d=out/name;case=cm['fault_case'];assert cm['status']=='passed' and len(cm['commands'])==1 and cm['commands'][0]['exit_code']==0
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and '$finish called'in log
  rows=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()];by=lambda t:[r for r in rows if r[0]==t]
  c={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert c['case']==case and c['epoch']==2 and c['version']==4 and c['journal']==0 and c['repairs']==int(case in [1,3,4])
  fc=list(map(int,by('FC')[0][2:]));assert fc[:3]==[case,4 if case==2 else 6 if case in [3,4]else 5,int(case in [3,4])]
  if case==2:assert int(by('RA')[0][1])<int(by('FI')[-1][1])<int(by('FC')[0][1]),'native reply vs physical drain barrier'
  assert len(by('FC'))==1 and len(by('FI'))>=1 and int(by('FI')[0][1])<int(by('FC')[0][1]);assert len(by('I'))==328
  assert {int(r[2]):[(int(r[3],16)>>(32*j))&0xffffffff for j in range(5)]for r in by('I')}==records
  labels=[int(r[3])for r in by('RL')];assert labels==(chain[:1]if case==2 else chain)+chain
  assert [list(map(int,t[2:]))for t in by('RO')]==([[0,1,chain[1]]]if case!=2 else[])+[[0,1,n]for n in chain[1:-1]]
  normal_nodes=([chain[1]]if case!=2 else[])+chain[1:-1]
  assert [list(map(int,t[2:]))for t in by('J')]==[[n,2717,1]for n in normal_nodes]
  assert [list(map(int,t[2:]))for t in by('BF')]==[[1,n]for n in normal_nodes]
  assert len(by('J'))==len(by('BF'))==len(by('RO'))
  for j,b,o in zip(by('J'),by('BF'),by('RO')):assert int(j[1])==int(o[1])<int(b[1])
  assert list(map(int,by('RESET')[0][2:]))==[int(case!=2)]
  assert [int(t[2])for t in by('KC')]==[17,18]
  assert list(map(int,by('KD')[0][2:]))==[0,c['repairs']]
  assert int(by('CHECK')[-1][1])<int(by('KD')[0][1])<int(by('RECOVERED')[0][1])<int(by('KC')[-1][1])
  assert [list(map(int,t[2:]))for t in by('KA')]==([]if case==2 else[[17,chain[1],2717,0xc0010001],[17,chain[1],2717,0x40010001]])
  assert len(by('RESET'))==len(by('AUTH'))==len(by('ABS'))==len(by('RECOVERED'))==1
  assert int(by('FC')[0][1])<int(by('RESET')[0][1])<int(by('AUTH')[0][1])<int(by('ABS')[0][1])<int(by('RELOAD')[0][1])<int(by('CHECK')[-1][1])<int(by('RECOVERED')[0][1])
  assert len(by('KO'))==len(by('KR'))
  observed=[]
  for index,(q,r)in enumerate(zip(by('KO'),by('KR'))):
   assert int(q[1])<int(r[1]) and int(q[4])==0xc0010001+index
   assert int(r[2])==0
   observed.append([int(q[2]),int(q[3]),int(r[3]),int(r[4])])
  if by('KA'):assert int(by('RESET')[0][1])<int(by('KA')[0][1])<int(by('KO')[0][1]) and int(by('KR')[-1][1])<int(by('AUTH')[0][1])

  expected_repair=[]if case==2 else([[0,chain[1],1,1],[2,chain[1],0,0],[0,chain[1],0,0]]if case in [1,3,4]else[[0,chain[1],0,0],[0,chain[1],0,0]])
  assert observed==expected_repair
  assert int(by('AUTH')[0][2])==c['repairs']
  assert [int(t[2])for t in by('LC')]==[0,1]
  assert len(by('LD'))==1 and list(map(int,by('LD')[0][2:]))==[0,328,328]
  assert [list(map(int,t[2:]))for t in by('CL')]==[[17,0],[18,0]]
  assert len(by('CD'))==1 and list(map(int,by('CD')[0][2:]))==[0,63,63]
  cq=by('CQ');cp=by('CP');assert len(cq)==len(cp)==6 and {int(t[2])for t in cq}=={int(t[2])for t in cp}==set(range(6))
  wanted_config=[
   [0x81fffff000,0x123456789abcdef0,180326,9089009,27960,1],
   [0x1fffff000,0x10fffff000,0x20fffff000,9089009,40469536],
   [0x31fffff000,9089009],
   [0x41fffff000,0x51fffff000,311,0],
   [0x61fffff000,0x61fffff000+145424192,0x61fffff000+145424192,9089009,0],
   [0x71fffff000,0x71fffff000+36356096,0x71fffff000+36357120,0x123456789abcdef0,9089009,27960,4]]
  widths=[[64,64,32,32,32,32],[64,64,64,32,32],[64,32],[64,64,32,32],[64,64,64,32,32],[64,64,64,64,32,32,32]]
  for q in cq:
   lane=int(q[2]);bits=int(q[3],16);want=0;off=0
   for value,width in zip(wanted_config[lane],widths[lane]):want|=value<<off;off+=width
   assert bits==want
   r=next(t for t in cp if t[2]==q[2]);assert int(r[3])==0 and int(q[1])<int(r[1])<int(by('CD')[0][1])
   if lane>0:assert int(next(t for t in cp if t[2]=='0')[1])<int(q[1])
  assert int(by('CL')[0][1])<int(by('FC')[0][1])<int(by('RESET')[0][1])<int(cq[0][1])
  assert int(by('CD')[0][1])<int(by('AUTH')[0][1]) and int(by('KC')[-1][1])<int(by('CL')[-1][1])

  ll=by('LL');lx=by('LX');assert len(ll)==len(lx)==1+328*5+328
  assert [list(map(int,t[2:5]))for t in ll]==[[0,150697,0]]+[[1,n,f]for n in records for f in range(5)]+[[0,n,0]for n in records]
  assert [int(t[5],16)for t in ll[1:1+328*5]]==[v for r in records.values()for v in r]
  for q,r in zip(ll,lx):assert int(q[1])<int(r[1]) and int(r[2])==0
  assert int(lx[0][3])==0
  for r,(n,want)in zip(lx[1+328*5:],records.items()):assert int(r[3])==1 and [(int(r[4],16)>>(32*j))&0xffffffff for j in range(5)]==want
  assert int(by('AUTH')[0][1])<=int(by('LC')[0][1])<int(ll[0][1])<int(by('RELOAD')[0][1]) # Empty journal: TB marker may share the first hardware control cycle.
  assert int(ll[328*5][1])<int(by('LC')[1][1])<int(ll[1+328*5][1])
  assert int(by('CHECK')[-1][1])<int(by('LD')[0][1])<int(by('KD')[0][1])

  for tag in ['RELOAD','CHECK']:
   assert len(by(tag))==328 and {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in by(tag)}==records
  assert list(map(int,by('RECOVERED')[0][2:]))==[0,6,6]

  want=bytearray(owner_initial)
  for n in chain[1:-1]:assert struct.unpack_from('<4I',want,n*16)==(0,0,0,0);struct.pack_into('<4I',want,n*16,2718,65537,0,0)
  assert (d/'owners.bin').read_bytes()==bytes(want)==(ROOT/'results/warm_q2_codec_v1/owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes()
  assert sha(d/'design.bin')==sha(inp/'design.bin') and sha(d/'cost.bin')==sha(inp/'cost.bin')
  b=(d/'labels.bin').read_bytes();assert Counter(b[i:i+192]for i in range(0,len(b),192))==expected
  memory={}
  for tag,regions,final in [('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('owner',[(0x61fffff000,owner_initial)],d/'owners.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],None),('qstate',[(0x81fffff000,inp/'connections.bin')],None),('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]:memory[tag]=replay(d/(tag+'_axi.txt'),regions,final)
  for tag,v in memory.items():
   assert v['error_write_replies']==int(tag=='owner'and case==1)
   if tag=='label'and case==2:assert 1<=v['error_read_beats']<=3 and v['error_read_beats']==fc[5]
   else:assert v['error_read_beats']==int(tag=='owner'and case==5)
  assert memory['owner']['write_replies']==(8 if case in [1,3,4]else 6) and memory['owner']['read_beats']==(20 if case in [1,3,4]else 17 if case==5 else 12)
  assert all(memory[t]['read_beats']==memory[t]['write_beats']==0 for t in ['graph','design','cost','qstate','table'])
  counts[name]=dict(c,fault_modified_nodes=[chain[1]]if case in [1,3,4]else[],memory=memory,owner_sha256=sha(d/'owners.bin'),label_sha256=sha(d/'labels.bin'))
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),error_replayer_sha256=sha(ROOT/'scripts/audit_route_fault_axi.py'),unchanged_RTL_dat=110,label_unit_audit_sha256=sha(unit/'source_bound_audit.json'),config_unit_audit_sha256=sha(config_unit/'source_bound_audit.json'),cases=counts,scope='Ten actual faults, same-instance post-drain coordinated reset retaining physical backing, owner journal GET/DEC repair against empty-initial-node authority, fresh epoch absent probe and 328 authoritative label reload, successful full path recommit. Synthesizable coordinator and registered-before-forward journal survive target reset and drive actual owner repair; Synthesizable label service performs OPEN/absent probe/stream load/CHECKPOINT/readback; Resident hardware descriptor and six-lane configuration with direct start/done/fault join; TB CPU authority and snapshot producer remain. Trusted checkpoint advances after recommit. Not durable power-loss recovery, autonomous full checkpoint, or unknown working set; no search rerun.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
