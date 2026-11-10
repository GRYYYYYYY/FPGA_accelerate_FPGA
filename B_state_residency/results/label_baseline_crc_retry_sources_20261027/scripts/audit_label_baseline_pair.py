"""Current full hierarchy: real iteration2 numerical search and owner lifecycle."""
from pathlib import Path
from collections import Counter
import sys,json,struct,runpy,mmap
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and len(m['cases'])==1
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert m['rtl']==['label_baseline_reader.sv']+bm['rtl'];assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in ['tb_query_fault.sv','recovery_coordinator.sv','runner.py','iter2_build_tb.py','baseline_build.py','label_baseline_reader.sv']+[x[0]for x in runpy.run_path(str(ROOT/'hardware/variants/label_baseline_system_v1/build.py'))['CHAIN']]+['expansion_20261024/pager/pager/resident_page_manager.sv']:assert h['sha256']==bm['sources'][n]['sha256'],n
assert sha(p/'sources/recovery_coordinator.sv')==sha(p.parent/'multi_owner_capacity_fixed_v1/sources/recovery_coordinator.sv')
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));b['make'].__globals__['PAIR']=ROOT/'hardware/variants/iter2_pair_v1/build_tb.py';assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
builder=runpy.run_path(str(p/'sources/baseline_build.py'));builder['make'].__globals__['ROOT']=ROOT;derived=builder['make']()
for n,t in derived.items():assert t==(p/'sources'/n).read_text(),n
for n,child in builder['CHAIN']:assert sha(builder['BASE']/n)==bm['sources'][n]['sha256']
assert sha(p/'sources/expansion_20261024/pager/pager/resident_page_manager.sv')==sha(p.parent/'label_baseline_miss_full_v3/sources/resident_page_manager.sv')
assert sha(p/'sources/label_baseline_reader.sv')==sha(ROOT/'hardware/variants/label_baseline_v1/label_baseline_reader.sv')
image=Path(m['baseline_image']);im=json.loads((image/'manifest.json').read_text());assert sha(image/'manifest.json')==m['baseline_manifest_sha256'];assert sha(image/'baseline.bin')==im['baseline_sha256'];assert sha(Path(im['source']))==im['source_sha256']
bind=json.loads(Path(m['binding']).read_text());assert sha(Path(m['binding']))==m['binding_sha256']and bind['status']=='passed'
for q,h in bind['audits'].items():assert sha(Path(q)/'source_bound_audit.json')==h
for r in bind['regions'].values():assert sha(Path(r['path']))==r['sha256']
for n,h in m['scoreboards'].items():assert sha(p/n)==h
reg=bind['regions'];cpu=Path(bind['base']);oracle=p.parent/'followup_iter2_oracle_v1';cost=p.parent/'followup_iter2_cost_v1';graph=ROOT/'results/graph_image_20261024'
def native(q):return {n:list(v)for n,*v in struct.iter_unpack('<6I',q.read_bytes())}
imports=native(oracle/'initial_label_imports.u32');final=native(oracle/'expected_label_reads.u32');assert len(imports)==len(final)==822
final[204279][4]=0
for n,expect in [('imports.txt',imports),('finals.txt',native(oracle/'expected_label_reads.u32'))]:assert {int(t[0]):[int(x,16)for x in t[1:]]for t in map(str.split,(p/n).read_text().splitlines())}==expect
cpurows=[t.split()for t in(cpu/'events.txt').read_text().splitlines()];polls=[list(map(int,t[1:4]))for t in cpurows if t[0]=='P'];cand=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(cpurows)and cpurows[i+1][0]=='W')]for i,t in enumerate(cpurows)if t[0]=='C'];expands=[int(t[1])for t in cpurows if t[0]=='E']
assert len(polls)==171 and len(cand)==849 and len(expands)==170
costs=[(int(t[0]),int(t[1]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[2:25])),sum(int(v,16)<<(32*i)for i,v in enumerate(t[25:])))for t in map(str.split,(cost/'cost_vectors.txt').read_text().splitlines())];assert len(costs)==421
initial=b''.join(Path(reg[k]['path']).read_bytes()for k in ['owners','owner_pool','owner_allocator']);assert len(initial)==146284032
# Actual CPU previous pointers determine the path; no injected path entries.
chain=[204279]
with(cpu/'search_final_nodes.u32').open('rb')as f:
 while chain[-1]!=66893:
  f.seek(chain[-1]*44+12);n=struct.unpack('<I',f.read(4))[0];assert n!=0xffffffff and len(chain)<32;chain.append(n)
assert chain[1:-1]==[339193,558358,265324]
case=next(iter(m['cases']));c=m['cases'][case];assert c['status']=='observed'and len(c['commands'])==3 and all(x['exit_code']==0 for x in c['commands']);d=p/case
allrows=[t.split()for t in(d/'natural_trace.txt').read_text().splitlines()]
cut=next(i for i,t in enumerate(allrows)if t[0]=='ITER2_NEXT_BEGIN');rows=allrows[:cut]
def by(tag):return[t for t in rows if t[0]==tag]
assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==polls
assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==cand
assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==[(n,a,b)for _,n,a,b in costs]
assert len(by('Q'))==170 and [int(t[2])for t in by('Q')]==list(range(100,270))
assert [sum(int(t[i])for t in by('Q'))for i in [3,4,5,6]]==[849,853,912,1]
assert not by('I') and len(by('BASELINE_NO_PRELOAD'))==1
assert not by('Z')
assert not [t for t in allrows if t[0]in ['I','Z','Z2']]
assert len(by('LIFECYCLE'))==1 and by('LIFECYCLE')[0][2:]==['0','0','1','4','1','3','3']
assert len([t for t in allrows if t[0]=='ITER2_PAIR_PASS'])==1
assert by('PREP_CONTINUITY')[0][2:]==['1','4','180327']
ro=by('RO');rb=by('RB')
assert [list(map(int,t[2:]))for t in ro]==[[0,1,n]for n in chain[1:-1]]+[[1,2,n]for n in [990179,558358,265324]]
assert [list(map(int,t[2:]))for t in rb]==[[0,0,1,1],[0,0,4,2],[0,0,5,1],[1,0,1,2],[1,0,3,2],[1,0,4,1]]
assert len(by('ITER2_FOREIGN'))==2 and all(t[2:]==['1','2']for t in by('ITER2_FOREIGN'))
expected_owner=bytearray(initial)
for node,refs,occ in [(339193,1,1),(990179,1,2)]:
 struct.pack_into('<II',expected_owner,node*16,26423,refs|(occ<<16))
prepared_owner=bytes(expected_owner)
struct.pack_into('<II',expected_owner,990179*16,26423,2|(2<<16))
struct.pack_into('<II',expected_owner,558358*16,26423,4|(2<<16))
struct.pack_into('<II',expected_owner,265324*16,26423,5|(1<<16))
assert (d/'owners.bin').read_bytes()==expected_owner
assert (d/'snapshot.bin').read_bytes()==initial and (d/'pool.bin').read_bytes()==initial
# Entire primary image against independently captured next CPU prepared-state.
nextcpu=p.parent/'followup_iter2_next_v1'
with (nextcpu/'initial_nodes.u32').open('rb')as f:
 state=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
 for node in range(9089009):
  net,refs,occ=struct.unpack_from('<III',state,node*44+24)
  n,r,head,pad=struct.unpack_from('<4I',prepared_owner,node*16)
  assert (n,r)==(0 if net==0xffffffff else net+1,refs|(occ<<16)),node
assert sha(nextcpu/'initial_overflow.u32')==sha(cpu/'initial_overflow.u32')
# Import preserves real exported slot0 and binds the observed CPU historical path to slot1.
trace_root=p.parent/'followup_iter2_prepare_trace_v1'
trace_audit=json.loads((trace_root/'prepare_trace_audit.json').read_text())
assert trace_audit['status']=='passed' and trace_audit['trace_sha256']==sha(trace_root/'prepare_ripup.txt')
assert trace_audit['capture_audit_sha256']==sha(trace_root/'source_bound_audit.json')
assert trace_audit['path_sink_to_source']==[67922,990179,558358,265324,66893]
words=[int(t[2],16)for t in by('PREP_PATH_IMPORT')]
assert len(words)==78 and words[:10]==[1,3,26422,66893,204279,0x9abcdef0,0x12345678,339193,558358,265324]
assert words[39:49]==[1,3,26422,66893,67922,0x9abcdef0,0x12345678,990179,558358,265324]
assert all(v==0 for v in words[10:39]+words[49:])
assert sha(d/'cost.bin')==reg['cost_history_prices_nets']['sha256']and sha(d/'design.bin')==reg['design']['sha256']
# Independently replay second-query numerical oracle and preserve untouched labels.
rows=allrows[cut:]
assert not by('I') and len(by('LIFECYCLE'))==1
nextcost=p.parent/'followup_iter2_next_cost_v1'
nextrows=[t.split()for t in(nextcpu/'events.txt').read_text().splitlines()]
assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==[list(map(int,t[1:4]))for t in nextrows if t[0]=='P']
assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(nextrows)and nextrows[i+1][0]=='W')]for i,t in enumerate(nextrows)if t[0]=='C']
nextcosts=[(int(t[1]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[2:25])),sum(int(v,16)<<(32*i)for i,v in enumerate(t[25:])))for t in map(str.split,(nextcost/'cost_vectors.txt').read_text().splitlines())]
assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==nextcosts and len(nextcosts)==302
assert len(by('Q'))==113 and len(by('P'))==114 and len(by('O'))==564
assert by('LIFECYCLE')[0][2:]==['1','0','1','4','1','3','3']
assert by('ITER2_PAIR_PASS')[0][2:]==['114','113','564','302']
assert [list(map(int,t[2:]))for t in by('RO')]==[[1,1,n]for n in [990179,558358,265324]]
assert [list(map(int,t[2:]))for t in by('RB')]==[[1,0,r,o]for r,o in [(2,2),(4,2),(5,1)]]
with(nextcpu/'search_final_nodes.u32').open('rb')as f:
 for node in final:
  f.seek(node*44);u=struct.unpack('<11I',f.read(44));final[node]=[u[0],u[1],u[3],u[4],u[5]]
final[67922][4]=0
assert not by('Z2')
for n,h in m['next_scoreboards'].items():assert sha(p/n)==h
for dep in [nextcpu,nextcost,p.parent/'followup_iter2_next_oracle_v1']:
 assert json.loads((dep/'source_bound_audit.json').read_text())['status']=='passed'
assert sha(nextcost/'cost.bin')==reg['cost_history_prices_nets']['sha256']and sha(nextcost/'connections.bin')==reg['connections']['sha256']
# Actual demand-loaded record set, never a CPU future list or host final read scan.
misses=[int(t[2])for t in allrows if t[0]=='BM'];assert misses and len(set(misses))==len(misses)
assert set(misses)<=set(imports)
first_misses=[int(t[2])for t in allrows[:cut]if t[0]=='BM'];next_misses=[int(t[2])for t in allrows[cut:]if t[0]=='BM']
assert len(first_misses)==777 and next_misses==[648770,125130,84955,84114]
simargv=m['cases'][case]['commands'][-1]['argv'];assert not any(x.startswith('imports=')for x in simargv)
assert all(t[3]=='0000000300010003'for t in allrows if t[0]=='BM')
responses=[t for t in allrows if t[0]=='BR'];assert [int(t[2])for t in responses]==misses
with Path(im['source']).open('rb')as f:
 for n,t in zip(misses,responses):
  f.seek(n*44);u=struct.unpack('<11I',f.read(44));assert t[3]=='0'and int(t[4],16)==sum(u[j]<<(32*i)for i,j in enumerate([0,1,3,4,5]))
actual_final={}
with(nextcpu/'search_final_nodes.u32').open('rb')as f:
 for n in misses:
  f.seek(n*44);u=struct.unpack('<11I',f.read(44));actual_final[n]=[u[j]for j in [0,1,3,4,5]]
actual_final[67922][4]=0
pages={}
for n,v in actual_final.items():
 page,slot=divmod(n,8);r=pages.setdefault(page,bytearray(192));r[0]|=1<<slot;struct.pack_into('<5I',r,1+slot*20,*v)
expected=Counter(bytes(x)for x in pages.values());expected[bytes(192)]+=16384-len(pages)
data=(d/'labels.bin').read_bytes();assert len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expected
assert any(t[0]=='BASELINE_PAIR_DONE'for t in allrows)
# Real baseline AXI reads and every byte are replayed independently.
baseline_axi=replay(d/'baseline_axi.txt',[(0xb000000000,image/'baseline.bin')],None)
assert baseline_axi['read_transactions']==baseline_axi['read_beats']==len(misses)and baseline_axi['write_beats']==0 and baseline_axi['error_read_beats']==0
# Replay native field updates, sparse present bits, binding and writeback/refill.
slots={};dirty={};back={};pending=None;native_write_pages=[];native_read_pages=[];native_fields=0
for t in allrows:
 if t[0]=='NB':
  assert pending is None
  op,sl,pg,gen,off,fi=map(int,t[2:8]);val=int(t[8],16);qid,pr=map(int,t[9:11]);status=present=payload=0
  assert qid==1 and pr==3
  if op==1:
   assert sl not in slots and gen>0;slots[sl]=(pg,gen,{});dirty[sl]=False
  elif op in [2,3,4,5,6]:
   assert sl in slots and slots[sl][:2]==(pg,gen);records=slots[sl][2]
   if op in [2,3]:
    if op==3:
     assert 0<=fi<=4;v=list(records.get(off,[0]*5));v[fi]=val;assert v[4]<=255;records[off]=v;dirty[sl]=True;native_fields+=1
    present=int(off in records);payload=sum(v<<(32*i)for i,v in enumerate(records[off]))if present else 0
   elif op==4:
    assert not dirty[sl];del slots[sl];del dirty[sl]
   elif op==5:
    back[pg]={o:list(v)for o,v in records.items()};dirty[sl]=False
    packed=bytearray(192)
    for o,v in records.items():packed[0]|=1<<o;struct.pack_into('<5I',packed,1+o*20,*v)
    native_write_pages.append(bytes(packed))
   else:
    if pg not in back:status=8
    else:
     slots[sl]=(pg,gen,{o:list(v)for o,v in back[pg].items()});packed=bytearray(192)
     for o,v in back[pg].items():packed[0]|=1<<o;struct.pack_into('<5I',packed,1+o*20,*v)
     native_read_pages.append(bytes(packed))
  else:assert op in [0,12]
  pending=(status,present,payload)
 elif t[0]=='NR':assert pending==(int(t[2]),int(t[3]),int(t[4],16));pending=None
assert pending is None
wbeats=[];rbeats=[]
for t in map(str.split,(d/'label_axi.txt').read_text().splitlines()):
 if t[0]=='W':assert int(t[2],16)==(1<<64)-1;wbeats.append(int(t[3],16).to_bytes(64,'little'))
 elif t[0]=='R':assert t[3]=='0';rbeats.append(int(t[2],16).to_bytes(64,'little'))
assert b''.join(wbeats)==b''.join(native_write_pages)
assert b''.join(rbeats)==b''.join(native_read_pages)
# Every baseline response must be consumed before its five seed writes and no other request can interleave.
seed_count=0
for i,t in enumerate(allrows):
 if t[0]=='BR':
  n=int(t[2]);payload=int(t[4],16);after=[z for z in allrows[i+1:]if z[0]=='NB'][:5]
  assert len(after)==5
  for fi,z in enumerate(after):
   assert int(z[2])==3 and int(z[4])*8+int(z[6])==n and int(z[7])==fi and int(z[8],16)==(payload>>(32*fi))&0xffffffff
  seed_count+=1
assert seed_count==len(misses)


regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),('snapshot',[(0x91fffff000,initial),(0xa000000000,initial)],None)]
memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
assert all(x['error_read_beats']==x['error_write_replies']==0 for x in memory.values())and memory['snapshot']['read_beats']==9 and memory['snapshot']['write_beats']==0
# Every physical owner write is exactly one of the three committed/ripped nodes.
actual=[]
for t in map(str.split,(d/'owner_axi.txt').read_text().splitlines()):
 if t[0]=='W':
  mask=int(t[2],16);lane=(mask&-mask).bit_length()-1;assert lane in [0,16,32,48]and mask==0xffff<<lane
  off=int(t[1],16)-0x61fffff000+lane;assert off%16==0;actual.append((off//16,(int(t[3],16)>>(8*lane))&((1<<128)-1)))
assert len(actual)==9 and [n for n,v in actual]==chain[1:-1]+[990179,558358,265324]*2
for (n,v),(r,o)in zip(actual,[(1,1),(4,2),(5,1),(1,2),(3,2),(4,1),(2,2),(4,2),(5,1)]):
 old=list(struct.unpack_from('<4I',initial,n*16));old[0]=26423 if r else 0;old[1]=(o<<16)|r;assert v==sum(w<<(32*i)for i,w in enumerate(old))
log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and 'ITER2_PAIR_PASS polls=114 expands=113 candidates=564 costs=302'in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,polls=171,expands=170,candidates=849,costs=421,labels=len(misses),logical_pages=len(pages),initial_label_imports=0,first_query_baseline_records=len(first_misses),second_query_new_baseline_records=len(next_misses),old_closure_unloaded_records=len(set(imports)-set(misses)),baseline_read_beats=len(misses),baseline_memory=baseline_axi,native_field_writes=native_fields,native_page_writebacks=len(native_write_pages),native_page_refills=len(native_read_pages),owner_capacity=53734,committed_path=chain,historical_path=[67922,990179,558358,265324,66893],intermediate_owner_matches_next_cpu_prepared=True,retained_query_sequence=180328,physical_owner_record_writes=9,next_query_polls=114,next_query_expands=113,next_query_candidates=564,next_query_costs=302,memory=memory,limits=['Historical path metadata imported from observed original CPU trace through native PC lease; not a runtime path discovery mechanism.','Two natural queries use demand loading from immutable full-node CPU baseline, no initial future label imports or between-query final host scans. G2 runtime snapshot publication and warm recovery of the enabled path remain pending.','Behavioral simulation, no synthesis or board performance claim.'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('BASELINE_PAIR_AUDITED',case,flush=True)
