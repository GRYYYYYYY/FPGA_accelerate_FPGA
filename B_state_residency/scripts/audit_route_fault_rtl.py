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
  if n not in ['runner.py','tb_route_fault.sv','route_commit_host_adapter.sv','axi_drain_watch.sv']:assert bm['sources'][n]['sha256']==h;same+=1
 assert same==110
 assert sha(out/'sources/route_commit_host_adapter.sv')==sha(ROOT/'hardware/variants/route_commit_join_drain_v2/route_commit_host_adapter.sv')
 assert sha(out/'sources/axi_drain_watch.sv')==sha(ROOT/'hardware/variants/route_commit_join_drain_v2/axi_drain_watch.sv')
 builder=ROOT/'hardware/variants/route_fault_v1/build_tb.py';sp=importlib.util.spec_from_file_location('builder',builder);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);assert mod.make().encode()==(out/'sources/tb_route_fault.sv').read_bytes()
 assert sha(out/'imports.txt')==m['imports_sha256'];records={int(t[0]):[int(x,16)for x in t[1:]]for t in map(str.split,(out/'imports.txt').read_text().splitlines())};assert len(records)==328
 with(cpu/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as snap:
  for n,r in records.items():v=struct.unpack_from('<11I',snap,n*44);assert r==[v[0],v[1],v[3],v[4],v[5]]
  chain=[];n=150697
  while n!=0xffffffff:chain.append(n);assert len(chain)<=8;n=struct.unpack_from('<I',snap,n*44+12)[0]
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
  c={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert c['case']==case and c['status']==(4 if case==2 else 6 if case in [3,4]else 5) and c['acked']==int(case in [3,4])
  if case==2:assert int(by('RA')[0][1])<int(by('FI')[-1][1])<int(by('FC')[0][1]),'native reply vs physical drain barrier'
  assert len(by('FC'))==1 and len(by('FI'))>=1 and int(by('FI')[0][1])<int(by('FC')[0][1]);assert len(by('I'))==328
  assert {int(r[2]):[(int(r[3],16)>>(32*j))&0xffffffff for j in range(5)]for r in by('I')}==records
  labels=[int(r[3])for r in by('RL')];assert labels==(chain[:1]if case==2 else chain)
  assert len(by('RO'))==int(case!=2)
  if by('RO'):assert list(map(int,by('RO')[0][2:]))==[0,1,chain[1]]
  want=bytes(owner_one)if case in [1,3,4]else owner_initial;assert (d/'owners.bin').read_bytes()==want
  assert sha(d/'design.bin')==sha(inp/'design.bin') and sha(d/'cost.bin')==sha(inp/'cost.bin')
  b=(d/'labels.bin').read_bytes();assert Counter(b[i:i+192]for i in range(0,len(b),192))==expected
  memory={}
  for tag,regions,final in [('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('owner',[(0x61fffff000,owner_initial)],d/'owners.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],None),('qstate',[(0x81fffff000,inp/'connections.bin')],None),('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]:memory[tag]=replay(d/(tag+'_axi.txt'),regions,final)
  for tag,v in memory.items():
   assert v['error_write_replies']==int(tag=='owner'and case==1)
   if tag=='label'and case==2:assert 1<=v['error_read_beats']<=3 and v['error_read_beats']==c['label_R']
   else:assert v['error_read_beats']==int(tag=='owner'and case==5)
  assert memory['owner']['write_replies']==c['owner_B']==int(case in [1,3,4]) and memory['owner']['read_beats']==c['owner_R']
  assert all(memory[t]['read_beats']==memory[t]['write_beats']==0 for t in ['graph','design','cost','qstate','table'])
  counts[name]=dict(c,physical_modified_nodes=[chain[1]]if case in [1,3,4]else[],memory=memory,owner_sha256=sha(d/'owners.bin'),label_sha256=sha(d/'labels.bin'))
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),error_replayer_sha256=sha(ROOT/'scripts/audit_route_fault_axi.py'),unchanged_RTL_dat=110,cases=counts,scope='Ten actual pager/owner AXI faults/late cancel/version-input drift from restored CPU q1 final labels. New physical AXI drain observer/gated completion; native-error-before-last-R timing checked. Exact physical bytes/errored transaction statuses/drain/fence after response checked; B error may already write. No automatic rollback/recovery/reset or search rerun.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
