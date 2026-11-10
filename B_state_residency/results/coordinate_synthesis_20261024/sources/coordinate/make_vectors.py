from pathlib import Path
import json,mmap,struct,sys
inp,graph,out=map(Path,sys.argv[1:]);cov=json.loads((inp/'coverage.json').read_text())
for name in ['synthetic','real']:
 d=out/name;d.mkdir();meta=cov[name];g=inp/name if name=='synthetic' else graph
 rows=(inp/name/'rows.bin').read_bytes();cols=(inp/name/'columns.bin').read_bytes();labels={};serial=0;counts={};ops={};lines=[]
 with (g/'nodes.rrt32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as data:
  def attrs(n):return data[n*32:n*32+32]
  def i16(a,o):return struct.unpack_from('<h',a,o)[0]
  def query(op,n,query=1,price=3,status=0):
   global serial
   serial+=1;a=bytes(32);y=slr=nx=pr=lp=rd=present=north=0
   if status==0:
    a=attrs(n)
    if op==2:nx,pr=struct.unpack_from('<ii',cols,i16(a,14)*8)
    elif op!=3:
     y=i16(a,16)
     if a[8]==5:
      rd=1;present=int(n in labels);lp=labels.get(n,{}).get(2,0)
      if lp!=0xffffffff and i16(attrs(lp),16)==y:y=i16(a,12)
     if op==1:slr,north=struct.unpack_from('<ii',rows,y*8)
   vals=[status,y,slr,nx,pr,lp,rd,present,north]
   lines.append(f'R {serial} {op} {n} {query} {price} '+' '.join(f'{v&0xffffffff:x}'for v in vals)+' '+a[::-1].hex())
   ops[op]=ops.get(op,0)+1;counts['queries']=serial
  def write(n,field,value):labels.setdefault(n,{})[field]=value&0xffffffff;lines.append(f'W {n} {field} {value&0xffffffff:x}')
  def control(op,q,p):
   lines.append(f'C {op} {q} {p}')
   if op==0:labels.clear()
  query(0,0,status=2);control(0,1,3)
  query(0,meta['nodes'],status=1);query(0,0,query=2,status=2);query(0,0,price=4,status=2)
  if not meta['columns']:query(2,0,status=1)
  if name=='synthetic':selected=list(range(64))*3
  else:
   selected=sorted(set([0,meta['nodes']-1]+list(range(0,meta['nodes'],65537))+[n for n in range(meta['nodes'])if data[n*32+8]==5]))
  for n in selected:
   query(0,n);a=attrs(n);lp=labels.get(n,{}).get(2,0);y=i16(a,16)
   if a[8]==5 and lp!=0xffffffff and i16(attrs(lp),16)==y:y=i16(a,12)
   if 0<=y<meta['rows']:query(1,n)
   if meta['columns']:query(2,n)
   if n%32==0:query(3,n)
  sll=[n for n in selected if attrs(n)[8]==5][:80]
  for j,n in enumerate(sll):
   write(n,2,0xffffffff if j%3==0 else 0 if j%3==1 else 5);query(0,n)
   if j%7==0:control(1,1,3);query(0,n)
  if name=='synthetic':
   write(5,2,0);write(1,2,5);query(0,5);query(0,1);query(1,1)
  control(1,1,3)
  for n in sll:query(0,n)
  control(2,1,3);control(0,2,4)
  for n in sll:query(0,n,query=2,price=4)
  control(2,2,4)
 (d/'vectors.txt').write_text('\n'.join(lines)+'\n');(d/'metadata.json').write_text(json.dumps(dict(meta,counts=counts,ops=ops),indent=2)+'\n')
