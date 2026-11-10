"""Encode real prepared-state design/owner/label images for existing service layouts."""
from pathlib import Path
import sys,json,struct,mmap,hashlib,contextlib,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 base=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir();src=out/'sources';src.mkdir();shutil.copyfile(__file__,src/Path(__file__).name)
 audit=json.loads((base/'source_bound_audit.json').read_text());assert audit['status']=='passed'
 graph=ROOT/'results/graph_image_20261024';template=ROOT/'results/natural_query_inputs_v1';n=audit['nodes'];assert n==json.loads((graph/'source_bound_audit.json').read_text())['nodes']
 caches={};b=(base/'initial_caches.u32').read_bytes();off=0
 while off<len(b):
  node,count=struct.unpack_from('<II',b,off);off+=8;assert node not in caches;caches[node]=struct.unpack_from('<'+'I'*count,b,off);off+=count*4
 overflow={}
 for node,net,refs in struct.iter_unpack('<III',(base/'initial_overflow.u32').read_bytes()):overflow.setdefault(node,[]).append((net,refs))
 pool=[];cached=0;empty=0
 with contextlib.ExitStack() as st:
  def mm(p):return st.enter_context(mmap.mmap(st.enter_context(p.open('rb')).fileno(),0,access=mmap.ACCESS_READ))
  snapshot=mm(base/'initial_nodes.u32');attrs=mm(graph/'nodes.rrt32');offsets=mm(graph/'offsets.u32le');edges=mm(graph/'edges.u32le');sinks=mm(template/'design.bin')
  d=st.enter_context((out/'design.bin').open('wb'));o=st.enter_context((out/'owners.bin').open('wb'));l=st.enter_context((out/'initial_labels.native160').open('wb'));h=st.enter_context((out/'history.bin').open('wb'))
  for node,v in enumerate(struct.iter_unpack('<11I',snapshot)):
   rawcreated=bool(attrs[node*32+9]&1);assert v[9]>=rawcreated and v[10]==attrs[node*32+8],(node,'unrepresentable mutable type')
   flags=int(v[9] and not rawcreated)|(sinks[node*16]&8);count=mask=0
   if node in caches:
    begin,end=struct.unpack_from('<II',offsets,node*4);count=end-begin;assert count<=32
    raw=struct.unpack_from('<'+'I'*count,edges,begin*4);j=0
    for pos,child in enumerate(raw):
     if j<len(caches[node]) and child==caches[node][j]:mask|=1<<pos;j+=1
    assert j==len(caches[node]),(node,'cache is not CSR ordered subsequence')
    flags|=4;cached+=1;empty+=not caches[node]
   d.write(struct.pack('<4I',flags,count,mask,0))
   extra=sorted(overflow.get(node,[]));assert len({net for net,refs in extra})==len(extra)
   assert v[7]<=65535 and v[8]<=65535 and v[8]==int(v[6]!=0xffffffff)+len(extra)
   assert (v[6]==0xffffffff)==(v[7]==0)
   head=len(pool)+1 if extra else 0
   for j,(net,refs) in enumerate(extra):
    assert net!=v[6] and 0<refs<=65535
    pool.append((net+1,refs,len(pool)+2 if j+1<len(extra) else 0,0))
   o.write(struct.pack('<4I',0 if v[6]==0xffffffff else v[6]+1,v[7]|v[8]<<16,head,0))
   l.write(struct.pack('<5I',v[0],v[1],v[3],v[4],v[5]));h.write(struct.pack('<I',v[2]))
  d.write(bytes((-n*16)%64));o.write(bytes((-n*16)%64));h.write(bytes((-n*4)%64))
 with (out/'owner_pool.bin').open('wb') as f:
  for record in pool:f.write(struct.pack('<4I',*record))
  f.write(bytes((-len(pool)*16)%64))
 (out/'owner_allocator.bin').write_bytes(struct.pack('<4I',len(pool),0,len(pool),0)+bytes(48))
 shutil.copyfile(base/'prices.u32',out/'prices.u32')
 layout=dict(nodes=n,owner_pool_capacity=len(pool),cache_parents=cached,empty_cached_parents=empty,label_format='native160 import, not paged backing',scope='Prepared-state persistent subset: design/owners/history/labels/prices. Does not include State/geometry/cost table or unknown-page initializer.')
 (out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
 m=dict(status='passed',base=str(base),base_audit_sha256=sha(base/'source_bound_audit.json'),graph=str(graph),template=str(template),inputs={str(p):sha(p) for p in [base/'initial_nodes.u32',base/'initial_caches.u32',base/'initial_overflow.u32',graph/'nodes.rrt32',graph/'offsets.u32le',graph/'edges.u32le',template/'design.bin']},sources={'encode_warm_state.py':sha(src/'encode_warm_state.py')},artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()})
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('WARM_STATE_ENCODE_PASSED',out)
if __name__=='__main__':main()
