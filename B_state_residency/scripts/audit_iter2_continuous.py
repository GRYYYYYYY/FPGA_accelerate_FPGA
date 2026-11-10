"""Current full hierarchy: real iteration2 numerical search and owner lifecycle."""
from pathlib import Path
from collections import Counter
import sys,json,struct,runpy,mmap
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and len(m['cases'])==1
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert m['rtl']==bm['rtl'];assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in ['tb_query_fault.sv','recovery_coordinator.sv','runner.py','iter2_build_tb.py']:assert h['sha256']==bm['sources'][n]['sha256'],n
assert sha(p/'sources/recovery_coordinator.sv')==sha(p.parent/'multi_owner_capacity_fixed_v1/sources/recovery_coordinator.sv')
assert sha(p/'sources/iter2_build_tb.py')==sha(ROOT/'hardware/variants/iter2_continuous_v1/build_tb.py')
b=runpy.run_path(str(ROOT/'hardware/variants/iter2_continuous_v1/build_tb.py'));assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
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
rows=[t.split()for t in(d/'natural_trace.txt').read_text().splitlines()]
def by(tag):return[t for t in rows if t[0]==tag]
assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==polls
assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==cand
assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==[(n,a,b)for _,n,a,b in costs]
assert len(by('Q'))==170 and [int(t[2])for t in by('Q')]==list(range(100,270))
assert [sum(int(t[i])for t in by('Q'))for i in [3,4,5,6]]==[849,853,912,1]
assert {int(t[2]):[(int(t[3],16)>>(32*i))&0xffffffff for i in range(5)]for t in by('I')}==imports
assert {int(t[2]):[(int(t[3],16)>>(32*i))&0xffffffff for i in range(5)]for t in by('Z')}==final
assert len(by('I'))==len(by('Z'))==822
assert len(by('LIFECYCLE'))==1 and by('LIFECYCLE')[0][2:]==['0','0','1','4','1','3','3']
assert len(by('ITER2_CONTINUOUS_PREP_PASS'))==1
assert by('PREP_CONTINUITY')[0][2:]==['1','4','180327']
ro=by('RO');rb=by('RB')
assert [list(map(int,t[2:]))for t in ro]==[[0,1,n]for n in chain[1:-1]]+[[1,2,n]for n in [990179,558358,265324]]
assert [list(map(int,t[2:]))for t in rb]==[[0,0,1,1],[0,0,4,2],[0,0,5,1],[1,0,1,2],[1,0,3,2],[1,0,4,1]]
assert len(by('ITER2_FOREIGN'))==2 and all(t[2:]==['1','2']for t in by('ITER2_FOREIGN'))
expected_owner=bytearray(initial)
for node,refs,occ in [(339193,1,1),(990179,1,2)]:
 struct.pack_into('<II',expected_owner,node*16,26423,refs|(occ<<16))
assert (d/'owners.bin').read_bytes()==expected_owner
assert (d/'snapshot.bin').read_bytes()==initial and (d/'pool.bin').read_bytes()==initial
# Entire primary image against independently captured next CPU prepared-state.
nextcpu=p.parent/'followup_iter2_next_v1'
with (nextcpu/'initial_nodes.u32').open('rb')as f:
 state=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
 for node in range(9089009):
  net,refs,occ=struct.unpack_from('<III',state,node*44+24)
  n,r,head,pad=struct.unpack_from('<4I',expected_owner,node*16)
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
# All populated and unused backing pages, including target cleanup.
pages={}
for n,v in final.items():
 page,slot=divmod(n,8);r=pages.setdefault(page,bytearray(192));r[0]|=1<<slot;struct.pack_into('<5I',r,1+slot*20,*v)
expected=Counter(bytes(x)for x in pages.values());expected[bytes(192)]+=16384-len(pages)
data=(d/'labels.bin').read_bytes();assert len(pages)==403 and len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expected
regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),('snapshot',[(0x91fffff000,initial),(0xa000000000,initial)],None)]
memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
assert all(x['error_read_beats']==x['error_write_replies']==0 for x in memory.values())and memory['snapshot']['read_beats']==9 and memory['snapshot']['write_beats']==0
# Every physical owner write is exactly one of the three committed/ripped nodes.
actual=[]
for t in map(str.split,(d/'owner_axi.txt').read_text().splitlines()):
 if t[0]=='W':
  mask=int(t[2],16);lane=(mask&-mask).bit_length()-1;assert lane in [0,16,32,48]and mask==0xffff<<lane
  off=int(t[1],16)-0x61fffff000+lane;assert off%16==0;actual.append((off//16,(int(t[3],16)>>(8*lane))&((1<<128)-1)))
assert len(actual)==6 and [n for n,v in actual]==chain[1:-1]+[990179,558358,265324]
for (n,v),(r,o)in zip(actual,[(1,1),(4,2),(5,1),(1,2),(3,2),(4,1)]):
 old=list(struct.unpack_from('<4I',initial,n*16));old[0]=26423 if r else 0;old[1]=(o<<16)|r;assert v==sum(w<<(32*i)for i,w in enumerate(old))
log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and 'ITER2_CONTINUOUS_PREP_PASS'in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,polls=171,expands=170,candidates=849,costs=421,labels=822,logical_pages=403,owner_capacity=53734,committed_path=chain,historical_path=[67922,990179,558358,265324,66893],owner_image_matches_next_cpu_prepared=True,retained_query_sequence=180327,physical_owner_record_writes=6,memory=memory,limits=['Historical path metadata imported from observed original CPU trace through native PC lease; not a runtime path discovery mechanism.','Only next-owner preparation complete. Next source/target label preparation and query180328 execution, G2 publication and recovery pending.','Behavioral simulation, no synthesis or board performance claim.'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('ITER2_CONTINUOUS_PREP_AUDITED',case,flush=True)
