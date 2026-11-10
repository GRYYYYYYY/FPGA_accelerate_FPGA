"""Independent two-query protocol, transition, complete memory and AXI audit."""
from pathlib import Path
from collections import Counter
import json,hashlib,struct,mmap,contextlib,sys,re,importlib.util
from audit_natural_axi import replay
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def native(p):return {v[0]:list(v[1:])for v in struct.iter_unpack('<6I',p.read_bytes())}
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed';inp=Path(m['input']);oracle=Path('/tmp/B_state_residency_offer_20261025/continuous_oracle_v1');graph=ROOT/'results/graph_image_20261024';baseline=ROOT/'results/candidate_recursive_pilot_20261025';bm=json.loads((baseline/'manifest.json').read_text())
 for n,v in m['sources'].items():assert sha(out/'sources'/n)==v['sha256']
 same=0;derived=0
 bp=ROOT/'hardware/variants/transaction_fence_join_v1/build_backend.py';sp=importlib.util.spec_from_file_location('backend_builder',bp);backend=importlib.util.module_from_spec(sp);sp.loader.exec_module(backend);variants=backend.sources()
 extras={'route_commit_controller.sv':'route_commit_v1','route_commit_host_adapter.sv':'recovery_join_v1','axi_drain_watch.sv':'route_commit_join_drain_v2','transaction_fence.sv':'transaction_fence_static_v2','recovery_coordinator.sv':'recovery_coordinator_v1','config_restore_controller.sv':'config_restore_v1','label_restore_controller.sv':'label_restore_v1'}
 for n,v in m['sources'].items():
  p=out/'sources'/n
  if n in ['runner.py','tb_transaction_fence_normal.sv']:continue
  if p.name in variants:assert p.read_text()==variants[p.name];derived+=1
  elif p.name in extras:assert sha(p)==sha(ROOT/'hardware/variants'/extras[p.name]/p.name)
  else:assert v['sha256']==bm['sources'][n]['sha256'];same+=1
 assert (same,derived)==(96,13),(same,derived)
 assert sha(out/'sources/runner.py')==sha(ROOT/'scripts/run_transaction_fence_normal_rtl.py')
 builder=ROOT/'hardware/variants/transaction_fence_normal_v1/build_tb.py';sp=importlib.util.spec_from_file_location('builder',builder);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);assert mod.make().encode()==(out/'sources/tb_transaction_fence_normal.sv').read_bytes()
 for n,v in m['scoreboards'].items():assert sha(out/n)==v
 assert m['input_manifest_sha256']==sha(inp/'manifest.json') and m['oracle_audit_sha256']==sha(oracle/'source_bound_audit.json') and m['graph_audit_sha256']==sha(graph/'source_bound_audit.json')
 q1=ROOT/'results/natural_query_v2';q2=ROOT/'results/followup_q2_v1';c2=ROOT/'results/followup_q2_cost_v1';assert m['q2_audit_sha256']==sha(q2/'source_bound_audit.json') and m['q2_cost_audit_sha256']==sha(c2/'source_bound_audit.json')
 imports=native(oracle/'initial_label_imports.u32');final1=native(oracle/'expected_label_reads.u32');prepared=native(oracle/'prepared.u32');final=native(oracle/'final2.u32');assert len(imports)==328
 expected=bytearray((inp/'design.bin').read_bytes());cpuP=[];cpuO=[];costs=[];phases=[];expectedACK=[];expectedWrites=[];chain=[]
 with contextlib.ExitStack()as stack:
  def mm(p):return stack.enter_context(mmap.mmap(stack.enter_context(p.open('rb')).fileno(),0,access=mmap.ACCESS_READ))
  offsets=mm(graph/'offsets.u32le');edges=mm(graph/'edges.u32le');attrs=mm(graph/'nodes.rrt32')
  for phase,(cpu,costroot) in enumerate([(q1,inp),(q2,c2)]):
   snap=mm(cpu/'initial_nodes.u32');last=mm(cpu/'search_final_nodes.u32');current={};lines=[l.split()for l in(cpu/'events.txt').read_text().splitlines()];K={};parent=None
   for t in lines:
    if t[0]=='E':parent=int(t[1]);K[parent]=[]
    elif t[0]=='K':K[parent].append(int(t[2]))
   def label(i):return current.get(i,struct.unpack_from('<11I',snap,i*44)[:6])
   def created(i):return bool(attrs[i*32+9]&1 or expected[i*16]&1)
   def excluded(parent,child):
    flags=attrs[child*32+9];v=label(child)
    if created(child) and v[3]!=0xffffffff and v[4]!=label(parent)[4] and v[3]==parent and flags&64:return False
    if flags&64:return True
    if flags&4 and not created(child):return True
    if flags&2:return True
    return bool(created(child) and flags&32 and v[3]!=parent)
   for i,t in enumerate(lines):
    if t[0]=='P':cpuP.append([int(t[1]),int(t[2]),int(t[3])])
    if t[0]=='C':cpuO.append([int(t[1]),int(t[2]),int(t[3]),int(i+1<len(lines)and lines[i+1][0]=='W')])
    if t[0]=='E':
     parent=int(t[1]);lo,hi=struct.unpack_from('<II',offsets,parent*4);raw=struct.unpack_from('<'+'I'*(hi-lo),edges,lo*4);flags,count,mask,_=struct.unpack_from('<4I',expected,parent*16)
     if flags&4:assert [child for pos,child in enumerate(raw)if mask>>pos&1]==K[parent]
     else:
      mask=0;kept=[]
      for pos,child in enumerate(raw):
       if excluded(parent,child):continue
       expected[child*16]|=1
       if attrs[child*32+8]==17:continue
       mask|=1<<pos;kept.append(child)
      assert kept==K[parent];flags=struct.unpack_from('<I',expected,parent*16)[0]|4;struct.pack_into('<4I',expected,parent*16,flags,len(raw),mask,0)
    if t[0]=='W':
     child,prev,lb,up,seq,target=map(int,t[1:7]);old=label(child);current[child]=(lb,up,old[2],prev,seq,target)
   for t in map(str.split,(costroot/'cost_vectors.txt').read_text().splitlines()):
    parent,node=map(int,t[:2]);packet=list(map(lambda x:int(x,16),t[2:25]));result=list(map(lambda x:int(x,16),t[25:]));costs.append((node,packet,result));phases.append(phase)
    v=list(struct.unpack_from('<11I',snap,node*44));lab=[v[0],v[1],parent,v[4],v[5]]
    for field,value in [(0,result[4]),(1,result[2]),(3,phase+1)]:
     expectedWrites.append([node,field,value]);lab[field]=value;expectedACK.append(sum(x<<(32*j)for j,x in enumerate(lab)))
   records=[imports,prepared][phase];expectedrecords=[final1,final][phase]
   for node,record in records.items():
    v=struct.unpack_from('<11I',snap,node*44);assert record==[v[0],v[1],v[3],v[4],v[5]]
    v=struct.unpack_from('<11I',last,node*44);assert expectedrecords[node]==[v[0],v[1],v[3],v[4],v[5]]
  last=mm(q1/'search_final_nodes.u32');node=150697
  while node!=65185:
   prev=struct.unpack_from('<I',last,node*44+12)[0];assert prev!=0xffffffff and len(chain)<32;chain.append([node,prev]);node=prev
 # Independent source-snapshot q2 path and four expected owner images.
 q2chain=[]
 with (q2/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm2:
  node=128009
  while node!=65185:
   prev=struct.unpack_from('<I',mm2,node*44+12)[0];assert prev!=0xffffffff and len(q2chain)<32;q2chain.append([node,prev]);node=prev
 path1=[v[1]for v in chain[:-1]];path2=[v[1]for v in q2chain[:-1]];assert len(path1)==len(path2)==6
 original=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes();stage_images=[]
 for node in set(path1+path2):assert struct.unpack_from('<4I',original,node*16)==(0,0,0,0)
 for paths in [[path1],[path1,path2],[path2],[]]:
  image=bytearray(original)
  for pathnodes in paths:
   for node in pathnodes:
    key,packed,ptr,reserved=struct.unpack_from('<4I',image,node*16);assert key in [0,2718] and ptr==reserved==0
    refs=(packed&65535)+1;struct.pack_into('<4I',image,node*16,2718,refs|65536,0,0)
  stage_images.append(bytes(image))
 assert stage_images[0]==(ROOT/'results/warm_q2_codec_v1/owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes()
 q3=ROOT/'results/followup_q3_v1';q3gate=json.loads((q3/'source_bound_audit.json').read_text());assert q3gate['status']=='passed' and (q3/'initial_overflow.u32').stat().st_size==0
 with (q3/'initial_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm3:
  for node,v in enumerate(struct.iter_unpack('<11I',mm3)):
   assert struct.unpack_from('<4I',stage_images[1],node*16)==(0 if v[6]==0xffffffff else v[6]+1,v[7]|v[8]<<16,0,0),(node,'CPU post-q2 owners')
 pages={}
 for node,record in final.items():
  p,slot=divmod(node,8);data=pages.setdefault(p,bytearray(192));data[0]|=1<<slot;struct.pack_into('<5I',data,1+slot*20,*record)
 want=Counter(map(bytes,pages.values()));want[bytes(192)]+=16384-len(pages);counts={}
 for case,cm in m['cases'].items():
  d=out/case;assert cm['status']=='passed'and all(x['exit_code']==0 for x in cm['commands'])
  assert len(cm['commands'])==3 and ('PRESSURE' in cm['commands'][0]['argv'])==(case=='pressure')
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  c={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert [c[k]for k in ['outputs','commits','offers','expands','polls','visited','State_R']]==[447,293,293,114,116,447,114]
  log=(d/'simulate.log').read_text();assert cm['result']in log and '$finish called'in log and 'Fatal:'not in log
  rows=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()];by=lambda tag:[t for t in rows if t[0]==tag]
  assert all(int(a[1])<=int(b[1])for a,b in zip(rows,rows[1:]))
  assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==cpuP
  assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==cpuO
  assert len(by('C'))==len(costs)==293
  for t,(node,packet,result)in zip(by('C'),costs):assert int(t[2])==node and int(t[3],16)==sum(x<<(32*j)for j,x in enumerate(packet)) and int(t[4],16)==sum(x<<(32*j)for j,x in enumerate(result))
  assert [[int(t[2]),int(t[3]),int(t[4],16)]for t in by('W')]==expectedWrites
  assert len(by('A'))==879 and all(t[2:4]==['0','1']for t in by('A')) and [int(t[4],16)for t in by('A')]==expectedACK
  for phase,records in enumerate([final1,final]):assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in by('R')if int(t[4])==phase}==records
  assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in by('T')}==prepared
  assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in by('I')}==imports
  assert len(by('I'))==328 and max(int(t[1])for t in by('I'))<int(by('P')[0][1])
  assert int(by('P')[72][1])<int(by('RL')[0][1])<int(by('RC')[0][1])<int(by('T')[0][1])<int(by('T')[-1][1])<int(by('P')[73][1])
  expected_labels=[]
  for slot,(capture,route)in enumerate([(q1,chain),(q2,q2chain)]):
   with(capture/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as labels:
    for node in [route[0][0]]+[pair[1]for pair in route]:
     v=struct.unpack_from('<11I',labels,node*44);record=[v[0],v[1],v[3],v[4],v[5]];expected_labels.append([slot,node,sum(x<<(32*j)for j,x in enumerate(record))])
  assert [[int(t[2]),int(t[3])]for t in by('RL')]==[[v[0],v[1]]for v in expected_labels]
  assert [[int(t[2]),int(t[3]),int(t[4],16)]for t in by('RA')]==expected_labels
  assert [[int(v)for v in t[2:]]for t in by('RC')]==[[0,0,6,6],[0,1,6,6],[1,0,6,6],[1,1,6,6]]
  ro=[];rb=[];references=Counter()
  for slot,op,nodes in [(0,1,path1),(1,1,path2),(0,2,path1),(1,2,path2)]:
   for node in nodes:
    ro.append([slot,op,node]);references[node]+=1 if op==1 else -1;rb.append([slot,0,references[node],int(references[node]>0)])
  assert [[int(v)for v in t[2:]]for t in by('RO')]==ro
  assert [[int(v)for v in t[2:]]for t in by('RB')]==rb
  for i in range(24):assert int(by('RO')[i][1])<int(by('RB')[i][1])
  assert len(by('RL'))==len(by('RA'))==16 and len(by('RC'))==4
  assert int(by('P')[-1][1])<int(by('RL')[8][1])

  observed=[[int(v)for v in t[2:]]for t in by('SO')];expected_ops=[]
  for stage in range(4):
   for node in (path1 if stage==0 else path1+path2):
    refs=int(node in path1)if stage==0 else int(node in path1)+int(node in path2)if stage==1 else int(node in path2)if stage==2 else 0
    expected_ops.append([stage,0,node,refs,int(refs!=0)])
  assert observed==expected_ops
  assert [int(t[2])for t in by('ST')]==[0,1,2,3]
  ownerbuf=bytearray(original);writes=0
  for line in(d/'owner_axi.txt').read_text().splitlines():
   t=line.split()
   if t[0]=='W':
    off=int(t[1],16)-0x61fffff000;mask=int(t[2],16);data=int(t[3],16).to_bytes(64,'little')
    for j in range(64):
     if mask>>j&1:ownerbuf[off+j]=data[j]
   elif t[0]=='B':
    writes+=1
    if writes in [6,12,18,24]:assert bytes(ownerbuf)==stage_images[writes//6-1],('owner stage',writes)
  assert writes==24
  data=(d/'labels.bin').read_bytes();assert Counter(data[i:i+192]for i in range(0,len(data),192))==want
  assert (d/'design.bin').read_bytes()==expected
  assert (d/'owners.bin').read_bytes()==(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes()
  memory={}
  for tag,regions,ff in [('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('owner',[(0x61fffff000,(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes())],d/'owners.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],None),('qstate',[(0x81fffff000,inp/'connections.bin')],None),('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]:memory[tag]=replay(d/(tag+'_axi.txt'),regions,ff)
  assert memory['owner']['write_replies']==24 and memory['qstate']['read_beats']==114
  # Ownership ledger: every accepted frontend request reaches exactly one backend
  # with identical packed payload, and retires exactly once before the next primary.
  pending={};accepted=Counter();native_counts=Counter();retired=Counter();route_pending=False;normal_done=0
  for t in rows:
   tag=t[0]
   if tag=='FS':
    lane=int(t[2]);assert lane not in pending and not route_pending
    if pending:assert 11 in pending and lane in [10,13]
    pending[lane]=dict(payload=int(t[3],16),cycle=int(t[1]),sent=False);accepted[lane]+=1
   elif tag=='FD':
    lane=int(t[3]);assert lane in pending and not pending[lane]['sent']
    p=pending[lane];assert int(t[4],16)==p['payload'] and int(t[1])>p['cycle'] and int(t[2]) in [1,2,3]
    p['sent']=True;native_counts[lane]+=1
   elif tag=='FB':
    lane=int(t[3]);assert lane in pending and pending[lane]['sent'];del pending[lane];retired[lane]+=1
   elif tag=='FR' and len(t)==2:
    assert not pending and not route_pending;route_pending=True
   elif tag=='RC':assert route_pending;route_pending=False;normal_done+=1
   elif tag in ['FK','RESET','CQ','CP','CD','KA','KO','KR','LC','LL','LX','RELOAD','ABS','CHECK','LD','KD']:
    raise AssertionError(('unexpected recovery in normal fixture',t))
  assert not pending and not route_pending and accepted==native_counts==retired and normal_done==4
  assert accepted[11]==114 and accepted[12]==118 and accepted[14]==accepted[15]==1
  assert len(by('NF'))==1 and int(by('NF')[0][2])==10
  assert len(by('J'))==len(by('BF'))==24
  assert [[int(v)for v in t[2:]]for t in by('J')]==[[node,2717,op]for slot,op,node in ro]
  assert [[int(v)for v in t[2:]]for t in by('BF')]==[[op,node]for slot,op,node in ro]
  assert all(int(j[1])<int(b[1]) for j,b in zip(by('J'),by('BF')))
  assert all(memory[tag]['read_beats']>0 for tag in ['graph','design','label','owner','cost','qstate'])
  assert memory['table']['read_beats']==0  # Neither natural query exercises the table lookup branch.
  counts[case]=dict(frontend_accepted=dict(sorted(accepted.items())),backend_retired=dict(sorted(retired.items())),route_commands=normal_done,journal_unique_nodes=10,result=cm['result'],memory=memory,label_sha256=sha(d/'labels.bin'),design_sha256=sha(d/'design.bin'),owner_sha256=sha(d/'owners.bin'))
 result=dict(status='passed',q3_capture_audit_sha256=sha(q3/'source_bound_audit.json'),q2_chain=q2chain,shared_nodes=sorted(set(path1)&set(path2)),stage_owner_sha256=[hashlib.sha256(x).hexdigest()for x in stage_images],manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),unchanged_production_RTL_dat=same,derived_retired_idle_exports=derived,chain=chain,initial_union_records=328,final_pages=len(pages),counts=counts,scope='Unchanged static16-port fence, journal adapter and recovery components on actual seven AXI services; two natural queries trace/commit/ripup, full snapshots/AXI and CPU q3 owner confirmation. External TB search/prepare and CPU-known union remain; no real-service fault injection or price/epoch switching.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
