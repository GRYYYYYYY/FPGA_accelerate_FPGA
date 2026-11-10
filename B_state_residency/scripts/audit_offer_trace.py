"""Independent semantic journal and observed handshake ordering for the prefix pipeline."""
from pathlib import Path
import json
from collections import defaultdict

def check_case(d,inp,limit):
 im=json.loads((inp/'manifest.json').read_text());rows=[tuple(map(int,s.split()))for s in(inp/'post_vectors.txt').read_text().splitlines()]
 rows=[r for r in rows if not limit or r[0]<=limit];oracle={(r[0],r[1]):r for r in rows};assert len(oracle)==len(rows)
 graph=(inp/'graph_attrs.rrt32').read_bytes();cost=(inp/'cost.bin').read_bytes();no=im['cost_layout']['nets_offset']
 cost_values={}
 for line in(inp/'cost_vectors.txt').read_text().splitlines():
  t=line.split();cost_values[tuple(map(int,t[:2]))]=[int(w,16)for w in t[2:]]
 commits={};labels={};present=set();child_payload={};parent_payload={};parent_present={};center_inputs={};parent=net=cookie=seq=0
 def packed(v):return sum((w&0xffffffff)<<(32*i)for i,w in enumerate(v))
 for line in(inp/'vectors.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='Q'and int(t[1])==0:labels={};present=set()
  elif t[0]=='L':
   n,f,v=map(int,t[1:]);labels.setdefault(n,[0]*5)[f]=v&0xffffffff;present.add(n)
  elif t[0]=='E':cookie,parent=map(int,t[1:3])
  elif t[0]=='D':net=int(t[3]);seq=int(t[4])
  elif t[0]=='A'and int(t[4])!=0:
   ordinal,child=map(int,t[1:3]);key=(cookie,ordinal);label=labels.setdefault(child,[0]*5);label[2]=parent;present.add(child)
   if key not in oracle:continue
   r=oracle[key];child_payload[key]=packed(label);parent_payload[key]=packed(labels.get(parent,[0]*5));parent_present[key]=int(parent in present)
   centers=int.from_bytes(cost[no+net*16:no+net*16+8],'little');center_inputs[key]=(centers<<64)|(r[5]<<32)|r[4]
   c=cost_values[key];stages=[]
   for field,value in [(0,c[27]),(1,c[25]),(3,seq)]:
    label[field]=value;stages.append((field,value,packed(label)))
   commits[key]=(seq,stages)

 observed=[]
 for line in(d/'post_observed.txt').read_text().splitlines():
  t=line.split();assert len(t)==10 and t[0]=='X';observed.append(tuple(map(int,t[1:5]))+tuple(int(w,16)for w in t[5:9])+(int(t[9]),))
 expected=[r[:8]+(int(graph[r[3]*32+8]==5),)for r in rows];assert observed==expected
 queue_owner={}
 for line in(d/'queue_calls.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='Q':queue_owner[int(t[1])]=int(t[8])
 events=defaultdict(list);pending=None;heap=0;owner=None;clears={};seed_count=0;hq=[];hp=[]
 for line in(d/'post_order.txt').read_text().splitlines():
  t=line.split();kind=t[0];cycle=int(t[1])
  if kind in ['HQ','HP']:
   (hq if kind=='HQ'else hp).append(tuple(map(int,t[1:])));continue
  if kind=='FQ':
   assert pending is None;op,cookie,before,q,p,exp=map(int,t[2:]);assert before==heap
   if op==0:assert owner is None;size=0
   else:
    assert owner==(q,p)
    if op==1:
     size=heap+1
     if queue_owner[cycle]==2:seed_count+=1
     else:assert queue_owner[cycle]==3
    elif op==2:size=max(0,heap-1)
    elif op==3:size=heap
    elif op in [4,5]:size=0
    else:raise AssertionError('unexpected Frontier op')
   if op==5:assert (exp,cookie)in oracle and oracle[(exp,cookie)][9]==1 and heap>=3
   pending=(op,cookie,q,p,exp,size,1 if op==2 and heap==0 else 0);continue
  if kind=='FR':
   assert pending is not None;op,cookie,q,p,exp,size,expected_status=pending;status,rc,rs,rq,rp=map(int,t[2:]);assert (status,rc,rs,rq,rp)==(expected_status,cookie,size,q,p)
   heap=size
   if op==0:owner=(q,p)
   if op==4:owner=None
   if op==5:clears[(exp,cookie)]=cycle
   pending=None;continue
  key=(int(t[2]),int(t[3]));assert key in oracle,(kind,key);events[key].append(t)
 assert pending is None and owner is None and heap==0 and hq==hp and len(hq)>1
 sll=0
 for key,r in oracle.items():
  es=events[key];is_sll=graph[r[3]*32+8]==5
  kinds=['LQ','LR','LQ','LR','CQ','GQ','GR']+(['YQ','YR','GQ','GR']if is_sll else [])+['CR','AQ','AR']
  assert [t[0]for t in es]==kinds,(key,[t[0]for t in es]);assert all(int(a[1])<int(b[1])for a,b in zip(es,es[1:])),key
  w,wa,rd,ra=es[:4]
  assert tuple(map(int,w[4:]))==(1,r[3],2,r[2],3)
  assert tuple(map(int,wa[4:6]))==(0,1)and int(wa[6],16)==child_payload[key]and int(wa[7])==4
  assert tuple(map(int,rd[4:]))==(0,r[2],1,0,5)
  assert int(ra[4])==0 and int(ra[5])==parent_present[key]and int(ra[6],16)==parent_payload[key]and int(ra[7])==6
  if r[9]:assert key in clears and clears[key]<int(w[1])
  else:assert key not in clears
  cq=es[4];assert int(cq[4])==r[3]
  gqs=[t for t in es if t[0]=='GQ'];grs=[t for t in es if t[0]=='GR'];nodes=[r[3],r[2]]if is_sll else[r[3]]
  assert [int(t[4])for t in gqs]==nodes
  for t,n in zip(grs,nodes):assert int(t[4])==n and int(t[5])==0 and int(t[6],16)==int.from_bytes(graph[n*32:n*32+32],'little')
  if is_sll:
   sll+=1;yq=next(t for t in es if t[0]=='YQ');yr=next(t for t in es if t[0]=='YR')
   assert tuple(map(int,yq[4:]))==(r[3],2)and tuple(map(int,yr[4:6]))==(0,1)and int(yr[6],16)==child_payload[key]
  cr,aq,ar=es[-3:];assert tuple(map(int,cr[4:8]))==(0,r[5],int(is_sll),r[2]if is_sll else 0)
  assert int(cr[8],16)==int.from_bytes(graph[r[3]*32:r[3]*32+32],'little')
  assert int(aq[4],16)==center_inputs[key]and int(ar[4],16)==r[7]<<32 and int(ar[5])==0
 assert len(clears)==sum(r[9]for r in rows)and seed_count==3*len(clears)
 # All three new native writes are serialized after the actual cost result.
 cost_done={}
 for line in(d/'cost23_order.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='CR':cost_done[tuple(map(int,t[2:4]))]=int(t[1])
 cevents=defaultdict(list)
 for line in(d/'commit_order.txt').read_text().splitlines():
  t=line.split();key=tuple(map(int,t[2:4]));assert key in commits;cevents[key].append(t)
 assert set(cevents)==set(oracle)
 for key,es in cevents.items():
  assert [t[0]for t in es]==['I','W','A','W','A','W','A','O'] and cost_done[key]<int(es[0][1])
  assert all(int(a[1])<int(b[1])for a,b in zip(es,es[1:]))
  r=oracle[key];seq,stages=commits[key];i=es[0]
  assert tuple(map(int,i[4:7]))==(r[2],r[3],seq) and [int(w,16)for w in i[7:9]]==[cost_values[key][25],cost_values[key][27]]
  for step,(w,a,stage)in enumerate(zip(es[1:7:2],es[2:7:2],stages)):
   f,v,payload=stage
   assert tuple(map(int,w[4:6]))==(r[3],f) and int(w[6],16)==v and int(w[7])==step
   assert tuple(map(int,a[4:6]))==(0,1) and int(a[6],16)==payload and int(a[7])==step
 seen=[]
 for line in(d/'commit_observed.txt').read_text().splitlines():
  t=line.split();assert len(t)==6 and t[0]=='T';key=tuple(map(int,t[1:3]));assert int(t[3])==oracle[key][3] and int(t[4])==commits[key][0] and int(t[5],16)==commits[key][1][-1][2];seen.append(key)
 assert seen==list(oracle)
 final=[]
 for line in(d/'final_observed.txt').read_text().splitlines():
  t=line.split();assert len(t)==3 and t[0]=='F';final.append((int(t[1]),int(t[2],16)))
 if not limit:
  expected_final=[]
  for line in(inp/'final_labels.txt').read_text().splitlines():
   t=line.split();expected_final.append((int(t[0]),packed([int(w,16)for w in t[1:]])))
  assert final==expected_final
 else:assert final==[]
 assert f"COST_LABEL_COMMIT_PASS calls={len(oracle)} final_reads={len(final)}"in(d/'simulate.log').read_text()
 # Cost OFFER is later than the final visited ACK, and earlier than output retirement.
 actions={};cost_keys={};cookie=0
 for line in(inp/'vectors.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='E':cookie=int(t[1])
  elif t[0]=='A' and int(t[4])==1 and (not limit or cookie<=limit):actions[(cookie,int(t[1]))]=int(t[2])
 oe=defaultdict(list)
 for line in(d/'offer_order.txt').read_text().splitlines():
  t=line.split();key=tuple(map(int,t[2:4]));assert key in actions;oe[key].append(t)
 assert set(oe)==set(actions)
 for key,es in oe.items():
  assert [t[0]for t in es]==['I','FQ','FR','O'] and int(cevents[key][-2][1])<int(es[0][1])
  assert all(int(a[1])<int(b[1])for a,b in zip(es,es[1:]))
  i,q,a,o=es;expected=cost_values[key][27]
  assert int(i[4],16)==int(q[4],16)==expected and int(i[5])==int(q[5])==actions[key]
  assert int(a[4])==0 and int(a[5])==int(i[6])+1 and int(q[6])==int(a[6]) and int(q[7],16)==int(a[7],16)==0x123456789abcdef0
 observed_offer=[]
 for line in(d/'offer_observed.txt').read_text().splitlines():
  t=line.split();assert t[0]=='V' and len(t)==7;key=tuple(map(int,t[1:3]));assert key in actions and int(t[3],16)==cost_values[key][27] and int(t[4])==actions[key] and int(t[6])==int(t[5])+1;observed_offer.append(key)
 assert observed_offer==list(actions)
 # Check every physical label read/write and all untouched backing bytes.
 memory=bytearray((d/'labels.bin').stat().st_size);reads=writes=0
 for line in(d/'label_axi.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='A':continue
  if t[0]=='B':assert t[1]=='0';continue
  address=int(t[1],16);assert 0<=address<=len(memory)-64
  if t[0]=='R':assert t[3]=='0'and int(t[2],16).to_bytes(64,'little')==memory[address:address+64];reads+=1
  else:
   assert t[0]=='W';strobe=int(t[2],16);data=int(t[3],16).to_bytes(64,'little')
   for i in range(64):
    if strobe>>i&1:memory[address+i]=data[i]
   writes+=1
 assert bytes(memory)==(d/'labels.bin').read_bytes()
 return {'ordered_prefixes':len(rows),'nonempty_clear_before_prev':len(clears),'fresh_SLL_label_reads':sll,'actual_center_calls':len(rows),'seed_offers':seed_count,'label_R_beats_checked':reads,'label_W_beats_checked':writes,'all_label_backing_bytes_checked':len(memory),'external_internal_control_handshakes':len(hq),'cost_label_commits':len(commits),'ordered_label_ACKs':3*len(commits),'final_label_records_read_after_checkpoint':len(final),'final_label_words_checked':5*len(final),'actual_cost_offers':len(actions)}
