"""Select real owner queries; golden refs come from original CPU snapshots."""
from pathlib import Path
import json,struct,mmap,heapq,random,sys,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def prepare(codec,out,checkpoint,generation):
 codec=Path(codec).resolve();out=Path(out).resolve();out.mkdir();m=json.loads((codec/'manifest.json').read_text());a=json.loads((codec/'source_bound_audit.json').read_text());assert a['status']=='passed'and a['manifest_sha256']==sha(codec/'manifest.json')
 cpu=Path(m['base']);layout=json.loads((codec/'layout.json').read_text());nodes=layout['nodes'];capacity=layout['owner_pool_capacity'];nets=27960
 occupied=[];multi=[];top=[]
 with(codec/'owners.bin').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
  for node,(key,packed,head,reserved)in enumerate(struct.iter_unpack('<4I',mm[:nodes*16])):
   if key:
    if len(occupied)<32:occupied.append(node)
    occ=packed>>16;refs=packed&65535
    if occ>1 and len(multi)<32:multi.append(node)
    if len(top)<8:heapq.heappush(top,(occ,refs,node))
    else:heapq.heappushpop(top,(occ,refs,node))
 chosen=set(range(16))|set(range(nodes-4,nodes))|set(occupied)|set(multi)|{x[2]for x in top}|set(random.Random(9417).sample(range(nodes),96))|{1411724,3919432,2988027,1431200,554512,263946,1231788,726313,1279818,1431195,208292}
 overflow={}
 for node,net,refs in struct.iter_unpack('<III',(cpu/'initial_overflow.u32').read_bytes()):
  if node in chosen:overflow.setdefault(node,{})[net]=refs
 vectors=[];metadata=[];D=0x123456789abcdef0
 with(cpu/'initial_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
  for node in sorted(chosen):
   row=struct.unpack_from('<11I',mm,node*44);owners=dict(overflow.get(node,{}))
   if row[6]!=0xffffffff:owners[row[6]]=row[7]
   assert len(owners)==row[8]
   targets=set(owners)
   foreign=0
   while foreign in targets:foreign+=1
   targets.add(foreign)
   if not owners:targets.add(2717)
   for net in sorted(targets):
    assert net<nets
    k=len(overflow.get(node,{}));reads=2+k*(k+1)//2
    vectors.append((node,net,D,checkpoint,generation,0,owners.get(net,0),row[8],reads))
   metadata.append({'node':node,'owners':owners,'occupancy':row[8]})
 # Rejections cannot touch the physical snapshot or expose a previous response.
 anchor=next(n for n in sorted(chosen)if any(x['node']==n and x['owners']for x in metadata))
 for d,cp,g,node,net,status in [(D^1,checkpoint,generation,anchor,2717,1),(D,checkpoint+1,generation,anchor,2717,1),(D,checkpoint,generation+1,anchor,2717,1),(D,checkpoint,generation^(1<<32),anchor,2717,1),(D,checkpoint,generation,nodes,2717,2),(D,checkpoint,generation,anchor,nets,2)]:vectors.append((node,net,d,cp,g,status,0,0,0))
 lines=[]
 for i,(node,net,d,cp,g,status,refs,occ,reads)in enumerate(vectors):lines.append(f'{i} {node} {net} {d:016x} {cp} {g:016x} {status} {refs} {occ} {reads}\n')
 (out/'vectors.txt').write_text(''.join(lines));(out/'selected_owners.json').write_text(json.dumps(metadata,indent=2)+'\n')
 for src,dst in [('owners.bin','primary.bin'),('owner_pool.bin','pool.bin'),('owner_allocator.bin','allocator.bin')]:shutil.copyfile(codec/src,out/dst)
 primary_bytes=(nodes*16+63)//64*64;pool_bytes=(capacity*16+63)//64*64
 result={'codec':str(codec),'cpu':str(cpu),'codec_audit_sha256':sha(codec/'source_bound_audit.json'),'cpu_audit_sha256':sha(cpu/'source_bound_audit.json'),'nodes':nodes,'nets':nets,'capacity':capacity,'checkpoint':checkpoint,'generation':generation,'design':D,'primary_base':0x91fffff000,'pool_base':0x91fffff000+primary_bytes,'allocator_base':0x91fffff000+primary_bytes+pool_bytes,'primary_bytes':primary_bytes,'pool_bytes':pool_bytes,'selected_nodes':len(chosen),'vectors':len(vectors),'occupied_queries':sum(v[7]>0 for v in vectors),'overflow_queries':sum(v[6]>0 and v[1]in overflow.get(v[0],{})for v in vectors),'artifacts':{p.name:sha(p)for p in out.iterdir()if p.is_file()},'preparer_sha256':sha(Path(__file__))}
 (out/'fixture.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(prepare(sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4],0))))
