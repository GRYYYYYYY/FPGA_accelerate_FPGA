"""Independent snapshot/event/heap replay; not an RTL or cost recomputation proof."""
from pathlib import Path
import hashlib,json,mmap,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
 for n,v in m['sources'].items():assert sha(p/'sources'/n)==v,n
 for n,v in m['artifacts'].items():assert sha(p/n)==v,n
 s=(p/'sources/router.cpp').read_text()
 for a,b in reversed(json.loads((p/'sources/changes.json').read_text())):assert s.count(b)==1;s=s.replace(b,a,1)
 assert s.encode()==(p/'sources/original.cpp').read_bytes()
 assert sha(p/'sources/original.cpp')==json.loads((ROOT/'build/real_trace/build.json').read_text())['original']['source_sha256']
 assert sha(p/'router.result')==m['reference_result_sha256']==sha(Path(m['reference_result']))
 state={line.split()[0]:list(map(int,line.split()[1:])) for line in (p/'state.txt').read_text().splitlines()}
 assert state['sequence']==[1] and state['conn_index']==[89391] and state['source']==[41486] and state['sink']==[41981]
 assert state['heap']==[8,1] and state['landmark']==[0] and state['cross']==[0,0]
 n=state['nodes'][0];assert (p/'initial_nodes.u32').stat().st_size==(p/'search_final_nodes.u32').stat().st_size==n*44
 assert (p/'prices.u32').stat().st_size==1024
 def heapfile(name):
  b=(p/name).read_bytes();assert len(b)%8==0
  return list(struct.iter_unpack('<II',b))
 h=heapfile('initial_heap.u32');assert len(h)==1 and h[0]==(0,state['source'][0]);D=state['heap'][0]
 def f(x):return struct.unpack('<f',struct.pack('<I',x))[0]
 def offer(key,node):
  k=len(h);h.append((key,node))
  while k>0:
   parent=(k-1)//D
   if f(h[parent][0])<=f(key):break
   h[k]=h[parent];k=parent
  h[k]=(key,node)
 def poll():
  result=h[0];last=h.pop()
  if h:
   k=0
   while k*D+1<len(h):
    first=k*D+1;best=first
    for j in range(first+1,min(first+D,len(h))):
     if f(h[j][0])<f(h[best][0]):best=j
    if f(last[0])<=f(h[best][0]):break
    h[k]=h[best];k=best
   h[k]=last
  return result
 counts={k:0 for k in ['E','K','C','W','P','END']};updates={};created_changed=0;changed_labels=0;clear_count=0
 with(p/'initial_nodes.u32').open('rb')as a,(p/'search_final_nodes.u32').open('rb')as b:
  ia=mmap.mmap(a.fileno(),0,access=mmap.ACCESS_READ);fa=mmap.mmap(b.fileno(),0,access=mmap.ACCESS_READ)
  def initial(i):assert 0<=i<n;return struct.unpack_from('<11I',ia,i*44)
  def current(i):return updates.get(i,initial(i)[:6])
  parent=None;kids=[];pos=0
  for line in (p/'events.txt').read_text().splitlines():
   tag,*v=line.split();v=list(map(int,v));assert tag in counts;counts[tag]+=1
   if tag=='E':
    parent,nk,q=v;assert q==len(h);kids=[];pos=0
   elif tag=='K':assert v[0]==parent;kids.append(v[1]);assert len(kids)<=nk
   elif tag=='C':
    par,child,position,lb,up,prev,visited,target,typ,created=v
    assert par==parent and len(kids)==nk and position==pos and kids[position]==child;pos+=1
    d=current(child);assert (lb,up,prev&0xffffffff,visited,target)==(d[0],d[1],d[3],d[4],d[5]);assert created==1
   elif tag=='W':
    child,prev,lb,up,visited,target,la,q=v;assert la==0 and prev==parent and child==kids[pos-1]
    assert visited==1 and target==current(child)[5]
    if q!=len(h):assert target==1 and q==0;h.clear();clear_count+=1
    old=current(child);updates[child]=(lb,up,old[2],prev&0xffffffff,visited,target);offer(lb,child)
   elif tag=='P':
    node,key,q=v;assert poll()==(key,node) and len(h)==q
   elif tag=='END':assert v==[counts['P'],1,0,len(h)]
  assert counts['END']==1 and counts['E']==81 and counts['P']==82 and counts['W']==178
  assert h==heapfile('search_final_heap.u32')
  # Fast block equality, then every differing node: persistent hist/owner/occupancy
  # must remain identical; only created/type can differ through child construction.
  stride=44*16384
  for start in range(0,n*44,stride):
   aa=ia[start:start+stride];bb=fa[start:start+stride]
   if aa==bb:continue
   for off in range(0,len(aa),44):
    x=aa[off:off+44];y=bb[off:off+44]
    if x==y:continue
    node=(start+off)//44;u=struct.unpack('<11I',x);v=struct.unpack('<11I',y)
    assert v[:6]==current(node),(node,'label');assert u[2]==v[2] and u[6:9]==v[6:9],(node,'persistent state')
    assert u[9]<=v[9]<=1
    created_changed+=u[9]!=v[9];changed_labels+=u[:6]!=v[:6]
  for node,d in updates.items():assert struct.unpack_from('<6I',fa,node*44)==d
  ia.close();fa.close()
 audit=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),source_recovered_byte_identical=True,nodes=n,state=state,event_counts=counts,updated_nodes=len(updates),changed_label_nodes=changed_labels,created_transitions=created_changed,heap_clear_count=clear_count,full_snapshot_rows_verified=n,scope='Full-route byte identity, natural prepared snapshot, per-candidate label chronology, original 8-ary heap replay and full-node persistent state preservation. Cost values observed, not independently recomputed; child filtering/type construction not independently replayed; no RTL replay.')
 (p/'source_bound_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
