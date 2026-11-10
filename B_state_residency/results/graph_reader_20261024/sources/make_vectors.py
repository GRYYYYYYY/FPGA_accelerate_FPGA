"""Independent little-endian file oracle; every real 4KiB CSR offset boundary plus strata."""
from pathlib import Path
import mmap,struct,random,json,sys
BASES=(0x00000001fffff000,0x00000010fffff000,0x00000020fffff000)
def vectors(graph,output):
 files=[(graph/n).open('rb') for n in ('offsets.u32le','edges.u32le','nodes.rrt32')]
 off,edge,attr=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)for f in files]
 n=len(attr)//32;e=len(edge)//4
 def u32(buf,p):return struct.unpack_from('<I',buf,p*4)[0]
 selected=set(range(128))|set(range(n-128,n))|set(range(1023,n-1,1024))
 selected.update(random.Random(20261024).sample(range(n),1024))
 degrees={};duplicate=None
 for p in range(n):
  a,b=u32(off,p),u32(off,p+1);d=b-a
  if d not in degrees:degrees[d]=p;selected.add(p)
  if duplicate is None and d>1:
   children=struct.unpack_from('<'+'I'*d,edge,a*4)
   if len(set(children))<d:duplicate=p;selected.add(p)
 counts={'nodes':n,'edges':e,'sampled_nodes':len(selected),'degree_representatives':degrees,'duplicate_parent':duplicate,'queries':0,'axi_beats':0,'meta':0,'child':0,'invalid_child_index':0,'csr_page_boundaries':len(range(1023,n-1,1024))}
 with output.open('w')as out:
  for p in sorted(selected):
   a,b=u32(off,p),u32(off,p+1);d=b-a
   for op,index in [(0,0)]+[(1,i)for i in range(d+1)]:
    bad=op==1 and index==d;target=u32(edge,a+index)if op and not bad else p
    addresses=[(BASES[0]+p*4)&~63]
    if p%16==15:addresses.append((BASES[0]+(p+1)*4)&~63)
    if not bad:
     if op:addresses.append((BASES[1]+(a+index)*4)&~63)
     addresses.append((BASES[2]+target*32)&~63)
    raw=int.from_bytes(attr[target*32:target*32+32],'little')if not bad else 0
    out.write(f'{op} {p} {index} {2 if bad else 0} {0 if bad else target} {0 if bad else a} {0 if bad else d} {raw:064x} {len(addresses)} '+ ' '.join(f'{x:016x}'for x in addresses+[0]*(4-len(addresses)))+'\n')
    counts['queries']+=1;counts['axi_beats']+=len(addresses);counts['invalid_child_index'if bad else 'child'if op else 'meta']+=1
 for m in (off,edge,attr):m.close()
 for f in files:f.close()
 return counts
if __name__=='__main__':
 result=vectors(Path(sys.argv[1]),Path(sys.argv[2]));Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
