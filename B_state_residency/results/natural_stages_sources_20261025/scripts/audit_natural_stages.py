"""Natural closed-loop ordering, original costs, all backing bytes and labels."""
from pathlib import Path
from collections import Counter
import contextlib,hashlib,json,mmap,re,struct,sys
from audit_recursive_join import words,packed
from audit_natural_axi import replay
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 inp=Path(m['input']);im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());oracle=ROOT/'results/natural_query_oracle_v1';graph=ROOT/'results/graph_image_20261024';base=ROOT/'results/candidate_recursive_pilot_20261025';bm=json.loads((base/'manifest.json').read_text())
 assert ig['status']=='passed' and m['input_manifest_sha256']==sha(inp/'manifest.json')==ig['manifest_sha256'] and m['oracle_audit_sha256']==sha(oracle/'source_bound_audit.json') and m['graph_audit_sha256']==sha(graph/'source_bound_audit.json')
 for name,v in m['sources'].items():assert sha(out/'sources'/name)==v['sha256']
 same=0
 for name,v in m['sources'].items():
  if name in ['runner.py','tb_natural_stages.sv']:continue
  assert bm['sources'][name]['sha256']==v['sha256'];same+=1
 assert same>90 and m['base_manifest_sha256']==sha(base/'manifest.json') and m['base_audit_sha256']==sha(base/'source_bound_audit.json')
 for name,h in m['scoreboards'].items():assert sha(out/name)==h
 native=lambda p:{r[0]:list(r[1:])for r in struct.iter_unpack('<6I',p.read_bytes())}
 imports=native(oracle/'initial_label_imports.u32');final=native(oracle/'expected_label_reads.u32')
 for name,records in [('imports.txt',imports),('finals.txt',final)]:assert {int(t[0]):[int(w,16)for w in t[1:]]for t in map(str.split,(out/name).read_text().splitlines())}==records
 cpu=Path(im['base']);cpurows=[l.split()for l in(cpu/'events.txt').read_text().splitlines()];cpuE=[int(t[1])for t in cpurows if t[0]=='E'];cpuP=[[int(t[1]),int(t[2]),int(t[3])]for t in cpurows if t[0]=='P'];cpuO=[]
 for i,t in enumerate(cpurows):
  if t[0]=='C':cpuO.append([int(t[1]),int(t[2]),int(t[3]),int(i+1<len(cpurows)and cpurows[i+1][0]=='W')])
 assert [list(map(int,t.split()[:4]))for t in(out/'candidates.txt').read_text().splitlines()]==cpuO
 assert [list(map(int,t.split()))for t in(out/'polls.txt').read_text().splitlines()]==cpuP
 costs=[]
 for t in map(str.split,(inp/'cost_vectors.txt').read_text().splitlines()):costs.append((int(t[0]),int(t[1]),[int(w,16)for w in t[2:25]],[int(w,16)for w in t[25:]]))
 # Independent expected complete persistent design image: cache masks derive
 # from ordered CPU K versus original raw CSR, already independently filtered.
 expected=bytearray((inp/'design.bin').read_bytes());K={};parent=None
 for t in cpurows:
  if t[0]=='E':parent=int(t[1]);K[parent]=[]
  if t[0]=='K':assert int(t[1])==parent;K[parent].append(int(t[2]))
 with contextlib.ExitStack()as stack:
  def mm(p):f=stack.enter_context(p.open('rb'));return stack.enter_context(mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ))
  attrs=mm(graph/'nodes.rrt32');offsets=mm(graph/'offsets.u32le');edges=mm(graph/'edges.u32le');snap=mm(cpu/'search_final_nodes.u32')
  init=mm(cpu/'initial_nodes.u32');current={};created={};rawtotal=0
  def initial(i):return struct.unpack_from('<11I',init,i*44)
  def label(i):return current.get(i,initial(i)[:6])
  def iscreated(i):return created.get(i,initial(i)[9])
  def excluded(parent,child):
   d=struct.unpack_from('<iiBBhhhhhIii',attrs,child*32)
   if iscreated(child):
    prev=label(child)[3]
    if prev!=0xffffffff and label(child)[4]!=label(parent)[4] and prev==parent and d[3]&64:return False
   if d[3]&64:return True
   if d[3]&4 and not iscreated(child):return True
   if d[3]&2:return True # selected profile has no Laguna
   return bool(iscreated(child) and d[3]&32 and label(child)[3]!=parent)
  for t in cpurows:
   if t[0]=='E':
    parent=int(t[1]);lo,hi=struct.unpack_from('<2I',offsets,parent*4);raw=[struct.unpack_from('<I',edges,j*4)[0]for j in range(lo,hi)];mask=0;kept=[]
    for position,child in enumerate(raw):
     if excluded(parent,child):continue
     created[child]=1
     # CPU getOrCreate and actual CREATE are unconditional for each allowed
     # child, including already raw-created sinks. Store bit0 can be redundant.
     flags=struct.unpack_from('<I',expected,child*16)[0]|1;struct.pack_into('<I',expected,child*16,flags)
     if attrs[child*32+8]==17:continue
     mask|=1<<position;kept.append(child)
    assert kept==K[parent]
    flags=struct.unpack_from('<I',expected,parent*16)[0]|4;struct.pack_into('<4I',expected,parent*16,flags,len(raw),mask,0);rawtotal+=len(raw)
   elif t[0]=='W':
    node,prev,lb,up,visited,target=map(int,t[1:7]);old=label(node);current[node]=(lb,up,old[2],prev,visited,target)
  for node in final:
   actual_created=bool(attrs[node*32+9]&1 or struct.unpack_from('<I',expected,node*16)[0]&1)
   assert actual_created==bool(struct.unpack_from('<I',snap,node*44+36)[0])
  assert rawtotal==382
 expected_design_hash=hashlib.sha256(expected).hexdigest()
 expectedpages={}
 for node,v in final.items():
  page,slot=divmod(node,8);p=expectedpages.setdefault(page,bytearray(192));p[0]|=1<<slot;struct.pack_into('<5I',p,1+slot*20,*v)
 expectedcounter=Counter(bytes(p)for p in expectedpages.values());expectedcounter[bytes(192)]+=16384-len(expectedpages)
 counts={}
 for case,cm in m['cases'].items():
  d=out/case;assert cm['status']=='passed'and len(cm['commands'])==3 and all(c['exit_code']==0 for c in cm['commands'])
  assert ('PRESSURE'in cm['commands'][0]['argv'])==(case=='pressure')
  for name,h in cm['artifacts'].items():assert sha(d/name)==h,name
  log=(d/'simulate.log').read_text();assert cm['result']in log and '$finish called'in log and 'Fatal:'not in log
  c={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert [c[k]for k in ['outputs','commits','offers','expands','polls','visited','State_R']]==[271,171,171,72,73,271,72] and c['host_blocks']>0
  rows=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()];assert all(int(a[1])<=int(b[1])for a,b in zip(rows,rows[1:]))
  by=lambda tag:[t for t in rows if t[0]==tag]
  E,S,M,V,O,C,W,A,F,R,P,I,Q,FQ,FR=[by(t)for t in ['E','S','M','V','O','C','W','A','F','R','P','I','Q','FQ','FR']]
  assert [[int(t[2]),int(t[3])]for t in E]==[[100+i,n]for i,n in enumerate(cpuE)] and len(S)==72 and len(Q)==72
  assert [[int(t[2]),int(t[3],16),int(t[4])]for t in P]==cpuP
  assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in O]==cpuO
  assert [[int(t[3]),int(t[4])]for t in M]==[[r[0],r[1]]for r in cpuO]
  for i,(t,parent)in enumerate(zip(E,cpuE)):
   assert int(P[i][1])<int(t[1])<int(S[i][1])<int(Q[i][1])<int(P[i+1][1]);assert int(Q[i][2])==100+i
  assert sum(int(t[4])for t in Q)==271 and sum(int(t[5])for t in Q)==382 and sum(int(t[6])for t in Q)==1
  assert len(C)==171
  expectedW=[];expectedA=[]
  for t,(parent,node,packet,result)in zip(C,costs):
   assert int(t[2])==node and words(int(t[3],16),23)==packet and words(int(t[4],16),5)==result
   lab=imports[node].copy();lab[2]=parent
   for field,value in [(0,result[4]),(1,result[2]),(3,1)]:expectedW.append([node,field,value]);lab[field]=value;expectedA.append(packed(lab))
  assert [[int(t[2]),int(t[3]),int(t[4],16)]for t in W]==expectedW
  assert len(A)==513 and all(t[2:4]==['0','1']for t in A) and [int(t[4],16)for t in A]==expectedA
  for i in range(513):
   assert int(W[i][1])<int(A[i][1])
   if i<512:assert int(A[i][1])<int(W[i+1][1])
  for i,(parent,node,packet,result)in enumerate(costs):assert int(A[i*3+2][1])<int(F[i][1])<int(C[i][1])
  assert len(V)==271 and [int(t[2])for t in V]==[r[1]for r in cpuO] and all(t[3]=='0'for t in V)
  assert len(R)==len(I)==308 and {int(t[2]):words(int(t[3],16),5)for t in R}==final and {int(t[2]):words(int(t[3],16),5)for t in I}==imports
  assert max(int(t[1])for t in I)<int(P[0][1]) and min(int(t[1])for t in R)>int(P[-1][1])
  ops=Counter(int(t[2])for t in FQ);assert ops==Counter({0:1,1:172,2:73,5:1,4:1}) and len(FQ)==len(FR) and all(t[2]=='0'for t in FR)
  clear=next(t for t in FQ if t[2]=='5');assert int(clear[1])<int(W[-3][1])<int(A[-1][1])<int(F[-1][1])<int(P[-1][1])
  data=(d/'labels.bin').read_bytes();assert len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expectedcounter
  assert sha(d/'design.bin')==expected_design_hash
  # Complete byte transcripts; read-only graph regions need a single padded
  # tail because AXI transfers full lines, even though no selected query reads it.
  memory={}
  for tag,regions,ff in [
   ('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),
   ('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),
   ('label',[(0,bytes(3145728))],d/'labels.bin'),
   ('owner',[(0x61fffff000,(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes())],None),
   ('cost',[(0x71fffff000,inp/'cost.bin')],None),
   ('qstate',[(0x81fffff000,inp/'connections.bin')],None),
   ('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]:memory[tag]=replay(d/(tag+'_axi.txt'),regions,ff)
  assert memory['label']['read_transactions']==c['labels_R'] and memory['label']['write_replies']==c['labels_W'] and memory['qstate']['read_beats']==72
  counts[case]=dict(c,memory=memory,label_sha256=sha(d/'labels.bin'),populated_physical_pages=111,final_native_records=308)
 assert counts['pressure']['labels_R']>counts['full']['labels_R'] and counts['pressure']['labels_W']>counts['full']['labels_W']
 r=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),input_audit_sha256=sha(inp/'source_bound_audit.json'),unchanged_production_RTL_dat=same,expected_full_design_sha256=expected_design_hash,counts=counts,scope='Actual heap POLL drives the selected natural search; all original costs/ACKs/outputs/labels/physical pages/design and AXI byte transcripts checked. No path backtrace, occupancy commit, RTL integrated autonomous search controller or board performance claim.')
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
