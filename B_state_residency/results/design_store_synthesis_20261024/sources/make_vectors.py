from pathlib import Path
import struct,random,json,sys

def generate(graph,out):
 offsets=(graph/'offsets.u32le').read_bytes();edges=(graph/'edges.u32le').read_bytes();n=len(offsets)//4-1
 def u32(b,i):return struct.unpack_from('<I',b,i*4)[0]
 selected=set(range(128))|set(range(n-128,n))|set(range(4095,n,4096))|set(random.Random(20261025).sample(range(n),2048))
 selected.add(834307) # verified real duplicate-edge node
 records={};claim=None;rows=[];writes=0;reads=0;hits=0;empty=0;wrong=0
 def issue(op,node,arg=0,owner=0):
  nonlocal claim,writes,reads,hits,empty,wrong
  status=0;reply=[0,0,0];ar=aw=0
  if op>6 or node>=n or (op==1 and arg>32)or(op not in(1,4)and arg):status=2
  elif op==1 and claim is not None:status=3
  elif (op==1 and not owner)or(op!=1 and owner!=(claim['owner']if claim else 0))or(op in(4,5)and(not claim or node!=claim['node']))or(op==6 and claim):status=4;wrong+=1
  elif op==4:
   if arg>=claim['count']or arg<=claim['last']:status=2
   else:claim['last']=arg;claim['mask']|=1<<arg;reply=[0,claim['count'],claim['mask']]
  else:
   ar=1;reads+=1;r=records.setdefault(node,[0,0,0]);reply=r.copy()
   if op==1:
    if r[0]&4:
     assert r[1]==arg;hits+=1
    else:claim={'owner':owner,'node':node,'count':arg,'mask':0,'last':-1}
   elif op in(2,3,6):
    bit={2:1,3:2,6:8}[op]
    if not(r[0]&bit):r[0]|=bit;aw=1;writes+=1
    reply=r.copy()
   elif op==5:
    assert not(r[0]&4);r[:]=[r[0]|4,claim['count'],claim['mask']];aw=1;writes+=1;reply=r.copy();empty+=not bool(claim['mask']);claim=None
  c=[1,claim['owner'],claim['node'],claim['count'],claim['mask']]if claim else [0]*5
  rows.append([op,node,arg,owner,status,*reply,*c,ar,aw])
 issue(0,n);issue(7,0);issue(1,0,33,1);issue(1,0,0,0);issue(4,0,0,0);issue(5,0)
 for seq,p in enumerate(sorted(selected),1):
  lo,hi=u32(offsets,p),u32(offsets,p+1);d=hi-lo;owner=seq
  if seq%37==0:issue(6,p)
  issue(0,p);issue(1,p,d,owner);issue(0,p,owner=owner+100000);issue(1,p,d,owner+1)
  for i in range(d):
   child=u32(edges,lo+i);issue(0,child,owner=owner)
   if (p+i)%3!=0:
    issue(2,child,owner=owner);issue(2,child,owner=owner)
    if (p+i)%5!=0:
     issue(4,p,i,owner)
     if i%7==0:issue(4,p,i,owner) # duplicate position rejected
  issue(4,p,d,owner);issue(6,p,owner=owner)
  if seq%17==0:issue(3,p,owner=owner)
  issue(5,p,owner=owner);issue(1,p,d,owner+1000000);issue(0,p)
 # Full mask width boundary on a node not previously claimed (synthetic degree32).
 p=next(x for x in range(n)if x not in selected);synthetic_parent=p
 issue(1,p,32,0xffffffff)
 for i in range(32):issue(4,p,i,0xffffffff)
 issue(2,p,owner=0xffffffff);issue(3,p,owner=0xffffffff);issue(5,p,owner=0xffffffff);issue(1,p,32,12)
 assert claim is None
 with (out/'vectors.txt').open('w')as f:
  for row in rows:f.write(' '.join(map(str,row))+'\n')
 size=((n*16+63)//64)*64
 with (out/'expected_memory.bin').open('wb')as f:
  f.truncate(size)
  for p,r in records.items():
   if any(r):f.seek(p*16);f.write(struct.pack('<4I',*r,0))
 info={'nodes':n,'backing_bytes':size,'real_parents':len(selected),'synthetic_degree32_parent':synthetic_parent,'commands':len(rows),'reads':reads,'writes':writes,'cache_hits':hits,'empty_published':empty,'owner_rejections':wrong,'records_touched':len(records)}
 (out/'coverage.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info))
if __name__=='__main__':generate(Path(sys.argv[1]),Path(sys.argv[2]))
