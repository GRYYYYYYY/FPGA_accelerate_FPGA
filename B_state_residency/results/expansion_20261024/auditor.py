"""Independent semantic event replay and complete byte-memory transcript audit."""
from pathlib import Path
import hashlib,json,struct,mmap,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/expansion_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 for path,digest in m['gates'].items():assert sha(Path(path))==digest
 oracle=Path(m['oracle']);graph=Path(m['graph']);og=read(oracle/'source_bound_audit.json');assert og['status']=='passed'and og['manifest_sha256']==sha(oracle/'manifest.json')
 gm=read(graph/'manifest.json')
 handles=[(graph/n).open('rb')for n in ['offsets.u32le','edges.u32le','nodes.rrt32']];off,adj,attrs=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)for f in handles]
 def word(buf,index):return struct.unpack_from('<I',buf,index*4)[0]
 sinks=set(map(int,(oracle/'sink_nodes.txt').read_text().split()));initial=(oracle/'initial_design.bin').read_bytes();fixture=(oracle/'vectors.txt').read_text().splitlines();cases={}
 for name,cm in m['cases'].items():
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  assert cm['initial_design_sha256']==sha(oracle/'initial_design.bin')
  d=out/name
  for file,digest in cm['artifacts'].items():assert sha(d/file)==digest
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  counts={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
  labels={};created=set();dead=set();cache={};generation=0;expansions=children=hits=svc_count=0;state=bytearray(initial);i=0
  with (d/'output.txt').open()as transcript:
   def expect(s):
    line=transcript.readline().strip();assert line==s,(name,i,line,s)
   while i<len(fixture)and(not cm['limit']or expansions<cm['limit']):
    row=fixture[i].split();i+=1
    if row[0]=='Q':
     expect(' '.join(row));op,q,price=map(int,row[1:]);
     if op==0:labels={}
    elif row[0]=='L':
     expect(' '.join(row));node,field,value=map(int,row[1:]);labels[node,field]=value
    else:
     assert row[0]=='E';cookie,parent,prune,laguna,hit,degree,mask,nchildren=map(int,row[1:]);start,end=word(off,parent),word(off,parent+1);assert end-start==degree and degree<=32
     is_hit=parent in cache;assert is_hit==bool(hit);hits+=is_hit;expansions+=1
     if not is_hit:
      generation+=1;keep=0;alive=False
      def service(pos,phase,node,value=0,aux=0):
       nonlocal svc_count
       expect(f'S {generation} {parent} {pos} {phase} {node}');expect(f'T {generation} {parent} {pos} {phase} {node} {value} {aux}');svc_count+=1
      for pos in range(degree):
       child=word(adj,start+pos);typ=attrs[child*32+8];flags=attrs[child*32+9]
       structural=bool(flags&64 or child in dead or typ==17 or (1<=typ<=4 and child not in sinks))
       service(pos,0,parent,child,int(structural));alive|=bool(prune and not structural)
       exists=bool(flags&1 or child in created);prev=labels.get((child,2),0);visited=labels.get((child,3),0);parent_visited=labels.get((parent,3),0)
       existing=exists and prev!=0xffffffff and visited!=parent_visited and prev==parent and bool(flags&64)
       excluded=False if existing else bool(flags&64 or ((flags&4)and not exists and(not laguna or not flags&8))or(not laguna and flags&2)or(exists and flags&32 and prev!=parent))
       service(pos,1,child,int(excluded))
       if excluded:continue
       created.add(child);fl,=struct.unpack_from('<I',state,child*16);struct.pack_into('<I',state,child*16,fl|1);service(pos,2,child)
       service(pos,3,child,int(typ==17),int(child in dead))
       if typ==17 or(prune and child in dead):continue
       keep|=1<<pos;service(pos,4,child)
      if prune and not alive:
       typ=attrs[parent*32+8];flags=attrs[parent*32+9];can_dead=parent not in sinks and not 1<=typ<=4 and not flags&0x8e
       service(degree,5,parent,int(can_dead))
       if can_dead:
        dead.add(parent);fl,=struct.unpack_from('<I',state,parent*16);struct.pack_into('<I',state,parent*16,fl|2);service(degree,6,parent)
      cache[parent]=keep;fl,=struct.unpack_from('<I',state,parent*16);struct.pack_into('<4I',state,parent*16,fl|4,degree,keep,0);service(degree,7,parent)
     assert cache[parent]==mask and mask.bit_count()==nchildren
     for pos in range(degree):
      if mask>>pos&1:
       node=word(adj,start+pos);assert fixture[i]==f'C {pos} {node}';i+=1
       expect(f'C {cookie} {pos} {node} {int.from_bytes(attrs[node*32:(node+1)*32],"little"):064x}');children+=1
     expect(f'E {cookie} {parent} {hit} {mask} {nchildren}')
   assert transcript.read()==''
  assert (counts['expansions'],counts['hits'],counts['children'],counts['builds'],counts['services'])==(expansions,hits,children,generation,svc_count)
  assert counts['host_blocks']>0 and sha(d/'design.bin')==hashlib.sha256(state).hexdigest()
  if not cm['limit']:assert sha(d/'design.bin')==sha(oracle/'expected_design.bin')and counts['native_reads']>0 and counts['checkpoints']>=2
  # Raw graph beats: compare all bytes, including the zero-padded final line.
  bases=[0x1fffff000,0x10fffff000,0x20fffff000];buffers=[off,adj,attrs];pending=[];nreads=0
  for line in (d/'graph_axi.txt').read_text().splitlines():
   parts=line.split();address=int(parts[1],16)
   if parts[0]=='A':assert not pending and int(parts[2])==1;pending=[address];nreads+=1
   else:
    assert parts[0]=='R'and pending==[address]and int(parts[3])==0;pending=[]
    choices=[(base,buf)for base,buf in zip(bases,buffers)if base<=address<base+((len(buf)+63)//64)*64];assert len(choices)==1
    base,buf=choices[0];offset=address-base;assert offset%64==0
    assert int(parts[2],16)==int.from_bytes(buf[offset:offset+64].ljust(64,b'\0'),'little')
  assert not pending and nreads==counts['graph_reads']
  # Byte-addressed replay proves no hidden writes to neighbours or untouched backing.
  for kind,base,start_mem,final_file in [('design',0x31fffff000,initial,'design.bin'),('label',0,bytes(49152),'labels.bin')]:
   backing=bytearray(start_mem);pending=[];reads=writes=bs=0
   for line in (d/(kind+'_axi.txt')).read_text().splitlines():
    p=line.split()
    if p[0]=='A':
     assert not pending;address=int(p[1],16);length=int(p[2]);assert 1<=length<=(1 if kind=='design'else 3)
     pending=[address+64*j for j in range(length)];reads+=1
    elif p[0]=='R':
     address=int(p[1],16);assert pending.pop(0)==address and int(p[3])==0;offset=address-base
     assert offset%64==0 and 0<=offset<=len(backing)-64
     assert int(p[2],16)==int.from_bytes(backing[offset:offset+64],'little')
    elif p[0]=='W':
     address=int(p[1],16);strb=int(p[2],16);data=int(p[3],16).to_bytes(64,'little');offset=address-base
     assert offset%64==0 and 0<=offset<=len(backing)-64
     if kind=='design':assert strb in [65535<<(16*j)for j in range(4)]
     else:assert strb==2**64-1
     for j in range(64):
      if strb>>j&1:backing[offset+j]=data[j]
     writes+=1
    else:assert p==['B','0'];bs+=1
   assert not pending and reads==counts[kind+'_reads']and bs==counts[kind+'_writes']and(writes==bs if kind=='design'else bs<=writes<=3*bs)
   assert hashlib.sha256(backing).hexdigest()==sha(d/final_file)
  cases[name]={**counts,'created_delta_nodes':len(created),'dead_nodes':len(dead),'design_sha256':sha(d/'design.bin')}
 for b in buffers:b.close()
 for f in handles:f.close()
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':cases,'scope':m['scope'],'limitations':['Default synthesized FRAMES163840 is larger than functional FRAMES256.','Selected real expansions with scripted query contexts, not full routing replay.','No frontend integration error-injection or actual counter exhaustion gate yet.','No distance/cost/frontier/backtrace/commit/platform/board integration.']}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
