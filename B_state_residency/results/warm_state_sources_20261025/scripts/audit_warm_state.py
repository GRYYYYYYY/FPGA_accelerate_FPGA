"""Independently decode every image row, linked owner and warm CSR mask."""
from pathlib import Path
import sys,json,struct,mmap,contextlib,hashlib

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed';base=Path(m['base']);graph=Path(m['graph']);template=Path(m['template']);layout=json.loads((out/'layout.json').read_text());n=layout['nodes']
 assert sha(base/'source_bound_audit.json')==m['base_audit_sha256']
 for p,d in m['inputs'].items():assert sha(Path(p))==d
 for p,d in m['artifacts'].items():assert sha(out/p)==d
 for p,d in m['sources'].items():assert sha(out/'sources'/p)==d
 expected={};data=(base/'initial_caches.u32').read_bytes();pos=0
 while pos<len(data):
  node,count=struct.unpack_from('<II',data,pos);pos+=8;assert node not in expected;expected[node]=data[pos:pos+count*4];pos+=count*4
 owners={}
 for node,net,refs in struct.iter_unpack('<III',(base/'initial_overflow.u32').read_bytes()):
  entries=owners.setdefault(node,{});assert net not in entries;entries[net]=refs
 seen=set();cachehits=empty=0
 with contextlib.ExitStack() as stack:
  def mm(p):return stack.enter_context(mmap.mmap(stack.enter_context(p.open('rb')).fileno(),0,access=mmap.ACCESS_READ))
  snap=mm(base/'initial_nodes.u32');design=mm(out/'design.bin');primary=mm(out/'owners.bin');labels=mm(out/'initial_labels.native160');history=mm(out/'history.bin');attrs=mm(graph/'nodes.rrt32');off=mm(graph/'offsets.u32le');edges=mm(graph/'edges.u32le');sinks=mm(template/'design.bin')
  pool=(out/'owner_pool.bin').read_bytes();capacity=layout['owner_pool_capacity'];assert len(pool)==(capacity*16+63)//64*64
  assert (out/'owner_allocator.bin').read_bytes()==struct.pack('<4I',capacity,0,capacity,0)+bytes(48)
  assert len(snap)==44*n and len(labels)==20*n and len(design)==len(primary)==(16*n+63)//64*64 and len(history)==(4*n+63)//64*64
  for node,v in enumerate(struct.iter_unpack('<11I',snap)):
   flags,count,mask,reserved=struct.unpack_from('<4I',design,node*16);assert reserved==0 and flags&~13==0
   assert bool(flags&1)==bool(v[9] and not attrs[node*32+9]&1) and flags&8==sinks[node*16]&8
   assert v[10]==attrs[node*32+8]
   if flags&4:
    assert node in expected;start,end=struct.unpack_from('<II',off,node*4);assert count==end-start and count<=32 and mask>>count==0
    decoded=b''.join(edges[(start+i)*4:(start+i+1)*4] for i in range(count) if mask&(1<<i));assert decoded==expected[node],node;cachehits+=1;empty+=len(decoded)==0
   else:assert node not in expected and count==mask==0
   key,packed,ptr,rsv=struct.unpack_from('<4I',primary,node*16);assert rsv==0
   assert key==(0 if v[6]==0xffffffff else v[6]+1) and packed&65535==v[7] and packed>>16==v[8]
   decoded={}
   while ptr:
    assert 1<=ptr<=capacity and ptr not in seen;seen.add(ptr)
    net,refs,nxt,reserved=struct.unpack_from('<4I',pool,(ptr-1)*16)
    assert reserved==0 and net!=key and net>0 and net-1 not in decoded and 0<refs<=65535
    decoded[net-1]=refs;ptr=nxt
   assert decoded==owners.get(node,{}) and v[8]==bool(key)+len(decoded)
   assert struct.unpack_from('<5I',labels,node*20)==(v[0],v[1],v[3],v[4],v[5])
   assert struct.unpack_from('<I',history,node*4)[0]==v[2]
  assert len(seen)==capacity and cachehits==layout['cache_parents']==len(expected) and empty==layout['empty_cached_parents']
  assert not any(pool[capacity*16:]) and not any(design[n*16:]) and not any(primary[n*16:]) and not any(history[n*4:])
 assert (out/'prices.u32').read_bytes()==(base/'prices.u32').read_bytes()
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),rows_verified=n,overflow_entries_verified=capacity,warm_parents_verified=cachehits,empty_cached_parents=empty,scope='Independent full-image decoding against real prepared CPU snapshots and original ordered CSR. No RTL replay or unknown-page initialization proof.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
