"""Audit actual three-slot q3 continuity, CPU numerical oracle, and physical DDR."""
from pathlib import Path
from collections import Counter
import json, runpy, struct, sys, zlib
from run_checkpoint_authority import ROOT, sha
from audit_route_fault_axi import replay
from audit_path_native_records import audit_native_records

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed' and len(m['cases'])==1
case=next(iter(m['cases']));c=m['cases'][case];d=p/case
assert c['status']=='observed'and len(c['commands'])==3 and all(x['exit_code']==0 for x in c['commands'])
for n,v in m['sources'].items():assert sha(p/'sources'/n)==v['sha256'],n
generated=runpy.run_path(str(p/'sources/path_capacity_build.py'))['make']()
for n,s in generated.items():assert (p/'sources'/n).read_text()==s,n
assert runpy.run_path(str(p/'sources/third_build_tb.py'))['make']()==(p/'sources/tb_query_fault.sv').read_text()
ref=p.parent/('owner_g3_retired_'+case+'_v3');rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
oldreport=json.loads((ROOT/'results/owner_g3_publish_20261027.json').read_text())
assert ra==oldreport['cases'][ref.name]and sha(ref/'manifest.json')==ra['manifest_sha256']
assert oldreport['restores'][ref.name]['audit_sha256']==sha(ref/'source_bound_audit.json')
for n,v in m['sources'].items():
 if n not in generated and n not in ['runner.py','path_capacity_build.py','third_build_tb.py','tb_query_fault.sv']:assert v['sha256']==rm['sources'][n]['sha256'],n
assert m['rtl']==rm['rtl']and m['binding_sha256']==rm['binding_sha256']and m['baseline_manifest_sha256']==rm['baseline_manifest_sha256']
for n,h in m['third_inputs'].items():assert sha(Path(n)/'source_bound_audit.json')==h
for key in ['scoreboards','next_scoreboards','third_scoreboards']:
 for n,h in m[key].items():assert sha(p/n)==h
allrows=[s.split()for s in(d/'natural_trace.txt').read_text().splitlines()]
cut=next(i for i,t in enumerate(allrows)if t[0]=='THIRD_BEGIN');before=allrows[:cut];rows=allrows[cut:]
oldrows=[s.split()for s in(ref/case/'natural_trace.txt').read_text().splitlines()]
for tag in ['P','O','C','Q','SEARCH','LIFECYCLE','RO','RB']:
 assert [t[2:]for t in before if t[0]==tag]==[t[2:]for t in oldrows if t[0]==tag],tag
assert not any(t[0]in ['I','Z','Z2']for t in allrows)
prefix_counts={}
for tag in ['graph','design','table','label','owner','cost','qstate','snapshot','copy','labelsnap','baseline','g3copy']:
 old=(ref/case/(tag+'_axi.txt')).read_bytes();new=(d/(tag+'_axi.txt')).read_bytes();assert new.startswith(old),tag
 if tag in ['snapshot','copy','labelsnap','g3copy']:assert new==old,tag
 prefix_counts[tag]=len(old.splitlines())
def by(tag):return[t for t in rows if t[0]==tag]
cpu=p.parent/'followup_iter2_third_plain_v1';cost=p.parent/'followup_iter2_third_cost_v1';oracle=p.parent/'followup_iter2_third_oracle_v1'
assert json.loads((cost/'source_bound_audit.json').read_text())['cost_packets']==302
assert json.loads((oracle/'source_bound_audit.json').read_text())['filtered_children']==565
cpurows=[s.split()for s in(cpu/'events.txt').read_text().splitlines()]
polls=[list(map(int,t[1:4]))for t in cpurows if t[0]=='P']
candidates=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(cpurows)and cpurows[i+1][0]=='W')]for i,t in enumerate(cpurows)if t[0]=='C']
costs=[(int(t[1]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[2:25])),sum(int(v,16)<<(32*i)for i,v in enumerate(t[25:])))for t in map(str.split,(cost/'cost_vectors.txt').read_text().splitlines())]
assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')]==polls
assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O')]==candidates
assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==costs
assert len(polls)==114 and len(candidates)==565 and len(costs)==302
assert len(by('Q'))==113 and [int(t[2])for t in by('Q')]==list(range(100,213))
assert by('THIRD_BEGIN')[0][2:]==['3','0','180328']
assert by('THIRD_PREPARED')[0][2:]==['3','3','180328']
assert by('LIFECYCLE')[0][2:]==['2','0','1','4','1','3','3']
assert by('THIRD_PASS')[0][2:]==['114','113','565','302','7','180329']
assert len(by('LIFECYCLE'))==1 and len(by('THIRD_PASS'))==1
path2=list(struct.unpack('<78I',(ref/case/'native_g3_path.bin').read_bytes()))+[0]*39
path3=path2[:78]+[1,3,26422,66893,151354,0x9abcdef0,0x12345678,990179,558358,265324]+[0]*29
crc=lambda w:zlib.crc32(struct.pack('<'+'I'*len(w),*w))
g3path=[int(t[3],16)for t in before if t[0]=='G3_PATH_WORD'];assert g3path==path2
for capture,want in [(0,path2),(1,path3)]:
 t=[t for t in by('THIRD_PATH_WORD')if int(t[2])==capture]
 assert [int(t[3])for t in t]==list(range(117))and[int(t[4],16)for t in t]==want
 t=[t for t in by('THIRD_PATH_DONE')if int(t[2])==capture];assert len(t)==1 and t[0][3:]==[f'{crc(want):08x}',str(3 if capture==0 else 7)]
assert [(int(t[1]),int(t[2],16))for t in by('THIRD_PATH_IMPORT')]==list(enumerate(path3))
qwords=[int(t[3],16)for t in by('QCM')]
assert qwords==[0x51435031,1,0x9abcdef0,0x12345678,3,1,5,0x57,180329,0]
assert len(by('QCP'))==1 and by('QCP')[0][2:]==['0',f'{crc(qwords):08x}','0','180329']
assert [t[2:]for t in before if t[0]=='JP']==[['7','17','17','4','0000000100000001'],['7','18','18','3','0000000100000002']]
assert not by('JP')and not by('BASELINE_TARGET_RESET')and not by('FI')
for n in ['owners.bin','g3.bin','pool.bin','snapshot.bin','cost.bin','design.bin']:assert sha(d/n)==sha(ref/case/n),n
binding=json.loads(Path(m['binding']).read_text());reg=binding['regions'];graph=ROOT/'results/graph_image_20261024'
initial=b''.join(Path(reg[k]['path']).read_bytes()for k in ['owners','owner_pool','owner_allocator'])
regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),
 ('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),
 ('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),
 ('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),
 ('snapshot',[(0x91fffff000,initial),(0xa000000000,d/'pool.bin'),(0xc000000000,d/'g3.bin')],None),('baseline',[(0xb000000000,Path(m['baseline_image'])/'baseline.bin')],None)]
memory={tag:replay(d/(tag+'_axi.txt'),regions,final)for tag,regions,final in regions}
assert all(v['error_read_beats']==0 and v['error_write_replies']==int(k=='owner')for k,v in memory.items())
suffix=(d/'owner_axi.txt').read_text().splitlines()[prefix_counts['owner']:];writes=[]
for t in map(str.split,suffix):
 if t[0]=='W':
  mask=int(t[2],16);lane=(mask&-mask).bit_length()-1;assert lane in [0,16,32,48]and mask==0xffff<<lane
  node=(int(t[1],16)-0x61fffff000+lane)//16;words=struct.unpack('<4I',((int(t[3],16)>>(8*lane))&((1<<128)-1)).to_bytes(16,'little'));writes.append((node,words))
assert [n for n,v in writes]==[990179,558358,265324]*2
for (node,words),count in zip(writes,[1,3,4,2,4,5]):
 with(d/'g3.bin').open('rb')as f:f.seek(node*16);expected=list(struct.unpack('<4I',f.read(16)))
 expected[1]=(expected[1]&0xffff0000)|count;assert list(words)==expected
misses={int(t[2])for t in allrows if t[0]=='BM'};pages={}
with(cpu/'search_final_nodes.u32').open('rb')as f:
 for node in misses:
  f.seek(node*44);u=struct.unpack('<11I',f.read(44));v=[u[k]for k in [0,1,3,4,5]]
  if node==151354:v[4]=0
  pg,slot=divmod(node,8);page=pages.setdefault(pg,bytearray(192));page[0]|=1<<slot;struct.pack_into('<5I',page,1+slot*20,*v)
expected=Counter(bytes(v)for v in pages.values());expected[bytes(192)]+=16384-len(pages)
data=(d/'labels.bin').read_bytes();assert len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expected
native=audit_native_records(allrows,d)
log=(d/'simulate.log').read_text();assert 'THIRD_QUERY_PASS polls=114 expands=113 candidates=565 costs=302'in log and '$finish called'in log and 'Fatal:'not in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),native_auditor_sha256=sha(ROOT/'scripts/audit_path_native_records.py'),case=case,
 path_slots=3,path_words=117,g3_source_path_crc=f'{crc(path2):08x}',final_path_crc=f'{crc(path3):08x}',final_query_crc=f'{crc(qwords):08x}',
 polls=114,expansions=113,candidates=565,cost_packets=302,final_sequence=180329,final_slot_mask=7,checkpoint=19,journal=3,
 final_labels=len(misses),logical_pages=len(pages),new_baseline_misses=len(by('BM')),axi_interfaces=12,physical_memory=memory,native_labels=native,
 owner_writes=memory['owner']['write_beats'],owner_sha256=sha(d/'owners.bin'),g3_owner_sha256=sha(d/'g3.bin'),final_cycle=int(by('THIRD_PASS')[0][1]),
 scope='Actual three-slot hierarchy and native117-word G2/G3 exports and q2 warm restore, CPU q3 continuity/real historical-path registration/ripup/query commit without DDR reload. G3 checkpoint source still saves only q1/q2; final three paths are exported after q3 but not jointly published. No q3 fault/G3 warm recovery, arbitrary reprice, persistence/authentication or board proof.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('THIRD_QUERY_AUDITED',case,len(misses),len(pages))
