"""Current full hierarchy: real iteration2 numerical search and owner lifecycle."""
from pathlib import Path
from collections import Counter
import sys,json,struct,runpy,mmap,tempfile
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and len(m['cases'])==1
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert m['rtl']==['incremental_owner_snapshot.sv','owner_snapshot_checkpoint_adapter.sv','label_snapshot_reader.sv','label_snapshot_checkpoint_adapter.sv']+bm['rtl'];assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
scan=runpy.run_path(str(p/'sources/scan_build.py'))
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in ['tb_query_fault.sv','recovery_coordinator.sv','runner.py','iter2_build_tb.py','warm_build.py','scan_build.py','label_snapshot_reader.sv','label_snapshot_checkpoint_adapter.sv','incremental_owner_snapshot.sv','owner_snapshot_checkpoint_adapter.sv','axi_file_memory.sv','query_residency_system.sv','search_residency_system.sv','residency_system.sv']+scan['FILES']:assert h['sha256']==bm['sources'][n]['sha256'],n
runner=(p/'sources/runner.py').read_text()
assert runner.count("shutil.copyfile(d/'owners.bin',d/'pool.bin')")==1 and 'iter2_continuous_prep_full_v1/full/owners.bin'not in runner
assert sha(p/'sources/owner_snapshot_checkpoint_adapter.sv')==sha(ROOT/'hardware/variants/owner_snapshot_writer_v1/owner_snapshot_checkpoint_adapter.sv')
assert sha(p/'sources/incremental_owner_snapshot.sv')==sha(ROOT/'hardware/variants/owner_snapshot_writer_v1/incremental_owner_snapshot.sv')
assert sha(p/'sources/axi_file_memory.sv')==sha(ROOT/'hardware/variants/iter2_runtime_owner_v1/axi_file_memory.sv')
agent=(base/'sources/axi_file_memory.sv').read_text().replace('READ_ONLY=0,MAX_BEATS=3','READ_ONLY=0,MAX_BEATS=3,SECONDARY_WRITABLE=0').replace('fd[1]=$fopen(path1,"rb")','fd[1]=$fopen(path1,SECONDARY_WRITABLE?"r+b":"rb")')
assert agent==(p/'sources/axi_file_memory.sv').read_text()
assert sha(p/'sources/recovery_coordinator.sv')==sha(p.parent/'multi_owner_capacity_fixed_v1/sources/recovery_coordinator.sv')
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));b['make'].__globals__['BASE']=ROOT/'hardware/variants/iter2_runtime_owner_v1/build_tb.py';b['make'].__globals__['HERE']=ROOT/'hardware/variants/label_frame_export_v1';assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
with tempfile.TemporaryDirectory()as tmp:
 scan['make'].__globals__['HERE']=Path(tmp);scan['make']()
 for n in scan['FILES']:assert (Path(tmp)/n).read_bytes()==(p/'sources'/n).read_bytes()
for n in ['label_snapshot_reader.sv','label_snapshot_checkpoint_adapter.sv']:
 assert sha(p/'sources'/n)==sha(ROOT/'hardware/variants/label_frame_export_v1'/n)
assert "(out/'warmimports.txt').open"not in runner
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
assert {int(t[2]):[(int(t[3],16)>>(32*i))&0xffffffff for i in range(5)]for t in by('I')}==imports
assert {int(t[2]):[(int(t[3],16)>>(32*i))&0xffffffff for i in range(5)]for t in by('Z')}==final
assert len(by('I'))==len(by('Z'))==822
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
assert (d/'snapshot.bin').read_bytes()==initial and (d/'pool.bin').read_bytes()==prepared_owner
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
# Native source-AW dirty tracking, actual source reads and target writes/readback.
assert by('RUNTIME_OWNER_START')[0][2:]==['4'] and by('RUNTIME_OWNER_COPIED')[0][2:]==['4','4']
assert len(by('RUNTIME_OWNER_START'))==len(by('RUNTIME_OWNER_ACCEPT'))==len(by('RUNTIME_OWNER_COPIED'))==1
assert int(by('PREP_CONTINUITY')[0][1])<int(by('RUNTIME_OWNER_START')[0][1])<int(by('RUNTIME_OWNER_COPIED')[0][1])<int(by('G2_CAPTURE')[0][1])<int(by('JP')[0][1])
copyrows=[t.split()for t in(d/'copy_axi.txt').read_text().splitlines()];assert len(copyrows)==24
candidate=bytearray(initial)
for i,node in enumerate([339193,558358,265324,990179]):
 off=(node//4)*64;part=copyrows[i*6:(i+1)*6];srcaddr=0x61fffff000+off;dstaddr=0xa000000000+off
 assert [t[0]for t in part]==['A','R','W','B','A','R']
 assert [int(part[j][1],16)for j in [0,1,2,4,5]]==[srcaddr,srcaddr,dstaddr,dstaddr,dstaddr]
 assert part[0][2]==part[4][2]=='1'and part[1][3]==part[5][3]=='0'and part[3]==['B','0']
 assert int(part[2][2],16)==2**64-1
 data=prepared_owner[off:off+64]
 assert int(part[1][2],16).to_bytes(64,'little')==int(part[2][3],16).to_bytes(64,'little')==int(part[5][2],16).to_bytes(64,'little')==data
 candidate[off:off+64]=data
assert candidate==prepared_owner and (d/'pool.bin').read_bytes()==candidate
# Hardware frame enumeration and actual DDR pages produce the warm stream.
source=native(oracle/'expected_label_reads.u32');source[204279][4]=0
all_replies=by('FRAME_SCAN_REPLY');all_requests=by('FRAME_SCAN_REQUEST')
assert len(by('LABEL_UNFLUSHED_BEGIN'))==len(by('LABEL_UNFLUSHED_REJECT'))==1 and by('LABEL_UNFLUSHED_REJECT')[0][2]=='3'
assert all_replies[0][2:]==['2','0','0000000','0']and all_requests[0][2]=='0'
replies=all_replies[1:];requests=all_requests[1:]
assert len(requests)==len(replies)==404 and [int(t[2])for t in requests]==list(range(404))
frame_pages={}
for frame,t in enumerate(replies[:-1]):
 assert t[2]=='0'and int(t[3])==frame and t[5]=='1';owner=int(t[4],16);assert owner>>21==13;frame_pages[frame]=owner&((1<<21)-1)
assert replies[-1][2:]==['6','403','0000000','0']
assert set(frame_pages.values())=={n//8 for n in source}and len(set(frame_pages.values()))==403
expected_pages={}
for n,v in source.items():
 page,slot=divmod(n,8);raw=expected_pages.setdefault(page,bytearray(192));raw[0]|=1<<slot;struct.pack_into('<5I',raw,1+20*slot,*v)
labelsnap=[t.split()for t in(d/'labelsnap_axi.txt').read_text().splitlines()];assert len(labelsnap)==2418
for i in range(1209):
 a,r=labelsnap[2*i:2*i+2];frame,chunk=divmod(i,3);addr=frame*192+chunk*64
 assert a[0]=='A'and int(a[1],16)==addr and a[2]=='1'and r[0]=='R'and int(r[1],16)==addr and r[3]=='0'
 assert int(r[2],16).to_bytes(64,'little')==bytes(expected_pages[frame_pages[frame]][chunk*64:(chunk+1)*64])
exported_records=[(int(t[2]),int(t[3],16))for t in by('LABEL_SNAPSHOT_RECORD')]
assert len(exported_records)==822 and len(dict(exported_records))==822
assert dict(exported_records)=={n:sum(w<<(32*i)for i,w in enumerate(v))for n,v in source.items()}
raw_stream=b''.join(struct.pack('<I',n)+v.to_bytes(20,'little')for n,v in exported_records)
import zlib
assert by('LABEL_SNAPSHOT_DONE')[0][2:]==['822','403',f'{zlib.crc32(raw_stream):08x}']
file_rows=[(int(t[0]),sum(int(w,16)<<(32*i)for i,w in enumerate(t[1:])))for t in map(str.split,(d/'runtime_labels.txt').read_text().splitlines())]
assert file_rows==exported_records
assert int(by('RUNTIME_OWNER_COPIED')[0][1])<int(by('LABEL_SNAPSHOT_BEGIN')[0][1])<int(by('LABEL_SNAPSHOT_DONE')[0][1])<int(by('G2_CAPTURE')[0][1])<int(by('JP')[0][1])
# Native three-way publication and real ledger/path export under lease.
import zlib
assert len(by('JP'))==1 and by('JP')[0][2]=='7'
assert len(by('ITER2_G2_PUBLISHED'))==1 and by('ITER2_G2_PUBLISHED')[0][2:]==['18','0','0000000100000002']
assert len(by('G2_CAPTURE'))==1 and by('G2_CAPTURE')[0][4]=='180327'
exports={}
for t in by('QCM'):
 batch=int(t[1]);exports.setdefault(batch,[]).append((int(t[2]),int(t[3],16),int(t[4])))
assert len(exports)==2
for batch,data in exports.items():
 assert [i for i,w,last in data]==list(range(10)) and [last for i,w,last in data]==[0]*9+[1]
 words=[w for i,w,last in data];assert words==[0x51435031,1,0x9abcdef0,0x12345678,2,1,3,0x4d,180327,0]
 assert zlib.crc32(struct.pack('<10I',*words))==int(by('G2_CAPTURE')[0][3],16)
assert [int(t[3],16)for t in by('QCS')]==words
path_exports=by('BPATH');assert len(path_exports)==156
native_path=[int(t[2],16)for t in path_exports[-78:]]
assert native_path[:10]==[1,3,26422,66893,204279,0x9abcdef0,0x12345678,339193,558358,265324] and all(v==0 for v in native_path[10:])
assert zlib.crc32(struct.pack('<78I',*native_path))==int(by('G2_CAPTURE')[0][2],16)
assert len(by('APQ'))==8 and len(by('APR'))==8
assert [t[5]for t in by('APR')]==['0000000100000001']*3+['0000000100000002']*5
assert [t[2:5]for t in by('APR')[-5:]]==[['1','0','0'],['0','1','1'],['0','1','2'],['0','3','2'],['0','4','1']]
# Independently replay second-query numerical oracle and preserve untouched labels.
warmrows=allrows[cut:];retry=next(i for i,t in enumerate(warmrows)if t[0]=='ITER2_RETRY');rows=warmrows[retry:]
assert not by('I') and len(by('LIFECYCLE'))==1
nextcost=p.parent/'followup_iter2_next_cost_v1'
nextrows=[t.split()for t in(nextcpu/'events.txt').read_text().splitlines()]
for phase in [warmrows[:retry],warmrows[retry:]]:
 saved_rows=rows;rows=phase
 assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==[list(map(int,t[1:4]))for t in nextrows if t[0]=='P']
 assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(nextrows)and nextrows[i+1][0]=='W')]for i,t in enumerate(nextrows)if t[0]=='C']
 nextcosts=[(int(t[1]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[2:25])),sum(int(v,16)<<(32*i)for i,v in enumerate(t[25:])))for t in map(str.split,(nextcost/'cost_vectors.txt').read_text().splitlines())]
 assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==nextcosts and len(nextcosts)==302
 assert len(by('Q'))==113 and len(by('P'))==114 and len(by('O'))==564
 rows=saved_rows
assert by('LIFECYCLE')[0][2:]==['1','0','1','4','1','3','3']
assert by('ITER2_PAIR_PASS')[0][2:]==['114','113','564','302']
assert [list(map(int,t[2:]))for t in by('RO')]==[[1,1,n]for n in [990179,558358,265324]]
assert [list(map(int,t[2:]))for t in by('RB')]==[[1,0,r,o]for r,o in [(2,2),(4,2),(5,1)]]
with(nextcpu/'search_final_nodes.u32').open('rb')as f:
 for node in final:
  f.seek(node*44);u=struct.unpack('<11I',f.read(44));final[node]=[u[0],u[1],u[3],u[4],u[5]]
final[67922][4]=0
assert {int(t[2]):[(int(t[3],16)>>(32*i))&0xffffffff for i in range(5)]for t in by('Z2')}==final and len(by('Z2'))==822
for n,h in m['next_scoreboards'].items():assert sha(p/n)==h
for dep in [nextcpu,nextcost,p.parent/'followup_iter2_next_oracle_v1']:
 assert json.loads((dep/'source_bound_audit.json').read_text())['status']=='passed'
assert sha(nextcost/'cost.bin')==reg['cost_history_prices_nets']['sha256']and sha(nextcost/'connections.bin')==reg['connections']['sha256']
# All populated and unused backing pages, including target cleanup.
pages={}
for n,v in final.items():
 page,slot=divmod(n,8);r=pages.setdefault(page,bytearray(192));r[0]|=1<<slot;struct.pack_into('<5I',r,1+slot*20,*v)
expected=Counter(bytes(x)for x in pages.values());expected[bytes(192)]+=16384-len(pages)
data=(d/'labels.bin').read_bytes();assert len(pages)==403 and len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expected
regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),('snapshot',[(0x91fffff000,initial),(0xa000000000,prepared_owner)],None)]
memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
assert all(x['error_read_beats']==0 and x['error_write_replies']==(1 if k=='owner'else 0)for k,x in memory.items())and memory['snapshot']['read_beats']==31 and memory['snapshot']['write_beats']==0
# Every physical owner write is exactly one of the three committed/ripped nodes.
actual=[]
for t in map(str.split,(d/'owner_axi.txt').read_text().splitlines()):
 if t[0]=='W':
  mask=int(t[2],16);lane=(mask&-mask).bit_length()-1;assert lane in [0,16,32,48]and mask==0xffff<<lane
  off=int(t[1],16)-0x61fffff000+lane;assert off%16==0;actual.append((off//16,(int(t[3],16)>>(8*lane))&((1<<128)-1)))
assert len(actual)==13 and [n for n,v in actual]==chain[1:-1]+[990179,558358,265324]+[990179,558358]*2+[990179,558358,265324]
for (n,v),(r,o)in zip(actual,[(1,1),(4,2),(5,1),(1,2),(3,2),(4,1),(2,2),(4,2),(1,2),(3,2),(2,2),(4,2),(5,1)]):
 old=list(struct.unpack_from('<4I',initial,n*16));old[0]=26423 if r else 0;old[1]=(o<<16)|r;assert v==sum(w<<(32*i)for i,w in enumerate(old))
# Real G2 two-key owner recovery plus 822 native label/path/query receipts.
rows=warmrows
assert len(by('FAILED_QUERY'))==len(by('FI'))==1 and by('FAILED_QUERY')[0][2:]==['5','7','5','0','1','2']
assert by('ITER2_OWNER_REPAIRED')[0][2:]==['2','2']
assert by('ITER2_WARM_COMPLETE')[0][2:]==['0','2','1','180327']
assert [t[2:]for t in by('SHARED_B')]==[['990179','0','1'],['558358','2','2']]
assert [t[2:]for t in by('WL')]==[['0','822','822']]
source=native(oracle/'expected_label_reads.u32');source[204279][4]=0
assert {int(t[0]):[int(x,16)for x in t[1:]]for t in map(str.split,(d/'runtime_labels.txt').read_text().splitlines())}==source

records=[(int(t[2]),int(t[3],16))for t in by('RELOAD')];assert records==exported_records
assert [(int(t[2]),int(t[3],16))for t in by('CHECK')]==records and len(records)==822
assert [int(t[3],16)for t in by('QCS')]==words
assert [t[2:]for t in by('WPR')]==[['0',f'{zlib.crc32(struct.pack("<78I",*native_path)):08x}']]
assert [t[2:]for t in by('WQR')]==[['0',f'{zlib.crc32(struct.pack("<10I",*words)):08x}']]
assert [int(t[3])for t in by('KA')]==[990179,558358]*2 and all(t[2]=='18' and t[4]=='26422'for t in by('KA'))
assert [t[2:]for t in by('AS_REPLY')]==[['0','1','2','0000000100000002'],['0','3','2','0000000100000002']]*2
assert [list(map(int,t[2:4]))for t in by('KO')]==[[0,990179],[2,990179],[0,558358],[2,558358],[0,990179],[0,558358]]
assert [list(map(int,t[2:]))for t in by('KR')]==[[0,2,2],[0,1,2],[0,4,2],[0,3,2],[0,1,2],[0,3,2]]
ts=[int(by(tag)[0][1])for tag in ['FAILED_QUERY','ITER2_OWNER_REPAIRED','WL','WPR','WQR','ITER2_WARM_COMPLETE','ITER2_RETRY','LIFECYCLE']];assert ts==sorted(ts)and len(set(ts))==len(ts)
log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and 'ITER2_PAIR_PASS polls=114 expands=113 candidates=564 costs=302'in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,polls=171,expands=170,candidates=849,costs=421,labels=822,logical_pages=403,owner_capacity=53734,committed_path=chain,historical_path=[67922,990179,558358,265324,66893],intermediate_owner_matches_next_cpu_prepared=True,retained_query_sequence=180328,physical_owner_record_writes=13,runtime_owner_lines=4,runtime_owner_read_beats=8,runtime_owner_write_beats=4,runtime_label_frames=403,runtime_label_records=822,runtime_label_read_beats=1209,runtime_label_crc=f'{zlib.crc32(raw_stream):08x}',source_context=[3,1,3],restored_context=[4,2,4],warm_labels_verified=822,repair_keys=2,repair_corrections=2,next_query_polls=114,next_query_expands=113,next_query_candidates=564,next_query_costs=302,published_checkpoint=18,published_generation=0x100000002,memory=memory,limits=['Initial CPU future read-closure preloads and historical path metadata remain external. Warm label source is generated by native authority directory scan and actual DDR reads; owner updates use native dirty-line copy into initial G1 clone. No general unknown-page initialization, persistent authenticated snapshot or board proof.','Only next-owner preparation complete. Native G2 CP18 publication, two-owner-B fault repair, 822 labels and native path/query restoration, then attempt4 retry of query180328. Fixed source price/history content.','Behavioral simulation, no synthesis or board performance claim.'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('RUNTIME_LABEL_SNAPSHOT_AUDITED',case,flush=True)
