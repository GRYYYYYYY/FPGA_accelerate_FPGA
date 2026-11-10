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
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
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
assert len(by('ITER2_CONTEXT'))==1 and by('ITER2_CONTEXT')[0][2:]==['180327','3','1','3']
assert len(by('ITER2_SEQUENCE_REJECT'))==1 and by('ITER2_SEQUENCE_REJECT')[0][2:]==['1','0','180327']
assert len(by('ITER2_LIFECYCLE_PASS'))==1 and by('ITER2_LIFECYCLE_PASS')[0][2:]==['171','170','849','421']
ro=by('RO');rb=by('RB');assert [list(map(int,t[2:]))for t in ro]==[[0,op,n]for op in [1,2]for n in chain[1:-1]]
assert [list(map(int,t[2:]))for t in rb]==[[0,0,r,o]for r,o in [(1,1),(4,2),(5,1),(0,0),(3,2),(4,1)]]
assert len(by('ITER2_FOREIGN'))==2 and all(t[2:]==['1','2']for t in by('ITER2_FOREIGN'))
assert [list(map(int,t[2:]))for t in by('SO')]==[[s,0,n,r,o]for s,data in [(0,[(339193,1,1),(558358,4,2),(265324,5,1)]),(1,[(339193,0,0),(558358,3,2),(265324,4,1)])]for n,r,o in data]
assert [t[2:]for t in by('APQ')]==[['208292','6632','0000000100000001','1'],['208292','17601','0000000100000001','2'],['558358','23916','0000000100000001','3']]
assert [t[2:]for t in by('APR')]==[['0',str(r),'2','0000000100000001',str(i+1)]for i,r in enumerate([1,2,1])]
assert max(int(t[1])for t in by('APR'))<int(by('P')[0][1])<int(ro[0][1])<int(by('LIFECYCLE')[0][1])<int(by('Z')[0][1])<int(ro[3][1])<int(by('ITER2_SEQUENCE_REJECT')[0][1])
assert (d/'owners.bin').read_bytes()==initial and (d/'snapshot.bin').read_bytes()==initial and (d/'pool.bin').read_bytes()==initial
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
assert len(actual)==6 and [n for n,v in actual]==chain[1:-1]*2
for (n,v),(r,o)in zip(actual,[(1,1),(4,2),(5,1),(0,0),(3,2),(4,1)]):
 old=list(struct.unpack_from('<4I',initial,n*16));old[0]=26423 if r else 0;old[1]=(o<<16)|r;assert v==sum(w<<(32*i)for i,w in enumerate(old))
log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and 'ITER2_LIFECYCLE_PASS polls=171 expands=170 candidates=849 costs=421'in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,full_sequence=180327,storage_context=[3,1,3],polls=171,expands=170,candidates=849,costs=421,labels=822,logical_pages=403,owner_capacity=53734,path=chain,foreign_net=23916,foreign_refs_preserved=1,owner_image_restored_exact=True,physical_owner_record_writes=6,duplicate_sequence_rejected=True,memory=memory,limits=['CPU conservative future read-closure preloads822 labels; no arbitrary unknown-page initialization or whole-cache rebuild proof.','Native full query/search/backtrace/commit/ripup and generation1 snapshot reads; G2 publication and full warm fault recovery with this dataset still pending.','Label restore service still512 records:822-record warm restoration needs an explicit capacity change. No board performance claim.'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('ITER2_LIFECYCLE_AUDITED',case,flush=True)
