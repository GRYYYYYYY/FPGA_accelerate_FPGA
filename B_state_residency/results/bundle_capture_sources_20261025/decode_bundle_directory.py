"""Reconstruct authoritative directory only from actual accepted protocol events."""
from pathlib import Path
import struct

def decode(path,labels,query,price):
 owners=[];leases={};tx_used=False;last_tx=0;pending=None;resets=0;commands=0;headers=0;last_cycle=-1
 for line in Path(path).read_text().splitlines():
  t=line.split();tag=t[0]
  if tag=='H':headers+=1;continue
  cycle=int(t[1]);assert cycle>=last_cycle;last_cycle=cycle
  if tag=='RESET':assert pending is None;owners=[];leases={};tx_used=False;last_tx=0;resets+=1;continue
  if tag=='C':
   assert pending is None;pending=(cycle,int(t[2]),int(t[3]),int(t[4]),int(t[5],16),int(t[6]),int(t[7]));commands+=1;continue
  assert tag=='R'and pending is not None
  cc,op,owner,frame,cookie,success,fence=pending;assert cycle>cc;status,rf,pub,allocated=int(t[2]),int(t[3]),int(t[4]),int(t[5]);mask=int(t[6],16);fault=int(t[7]);expected=0;want_frame=want_pub=0;slot=cookie&31;kind=(cookie>>64)&1;owner_cookie=(cookie>>5)&((1<<27)-1);tx=(cookie>>48)&65535
  if op in [0,5]:
   found=next((i for i,x in enumerate(owners)if x[0]==owner),None)
   if found is None:
    if op==5:expected=6
    else:want_frame=len(owners);owners.append([owner,False])
   else:want_frame=found;want_pub=int(owners[found][1])
  elif op==1:
   if cookie>>65:expected=3
   elif frame>=len(owners):expected=1
   elif slot in leases or any(x['frame']==frame for x in leases.values()):expected=2
   elif tx_used and tx<=last_tx:expected=5
   elif owners[frame][0]!=owner_cookie:expected=1
   elif kind and not owners[frame][1]:expected=6
   else:
    leases[slot]={'frame':frame,'cookie':cookie,'phase':0};tx_used=True;last_tx=tx;want_frame=frame;want_pub=kind
    if not kind:owners[frame][1]=False
  elif op in [2,3]:
   l=leases.get(slot);match=l is not None and l['frame']==frame and l['cookie']==cookie
   if not match or(op==2 and l['phase']!=0):expected=1
   elif op==3 and l['phase']!=1:expected=6
   elif op==2:
    l['phase']=1 if success else 2
    if not success:expected=7
    else:
     want_frame=frame;want_pub=1
     if not kind:owners[frame][1]=True
   else:del leases[slot];want_frame=frame;want_pub=1
  elif op in [4,6]:
   if leases or not fence:expected=2
   else:
    tx_used=False;last_tx=0
    if op==4:owners=[]
  else:expected=3
  assert status==expected,(cycle,op,status,expected)
  assert (rf,pub,allocated)==(want_frame,want_pub,len(owners)),(cycle,op,(rf,pub,allocated),(want_frame,want_pub,len(owners)))
  assert mask==sum(1<<s for s in leases)and fault==int(any(x['phase']==2 for x in leases.values()))
  pending=None
 assert headers==1 and pending is None and not leases and resets>=2 and owners and all(x[1]for x in owners)
 data=Path(labels).read_bytes();assert len(data)%192==0 and len(owners)<=len(data)//192;records={};mapping=[]
 for frame,(owner,published)in enumerate(owners):
  page=owner&((1<<21)-1);q=(owner>>21)&3;p=(owner>>23)&15;assert (q,p)==(query,price)
  block=data[frame*192:(frame+1)*192];assert block[161:]==bytes(31)
  mapping.append({'frame':frame,'owner':owner,'page':page,'query':q,'price':p,'published':published})
  for offset in range(8):
   if block[0]>>offset&1:
    node=page*8+offset;assert node not in records;records[node]=list(struct.unpack_from('<5I',block,1+offset*20))
 return {'allocated':len(owners),'owners':mapping,'tx_used':tx_used,'last_tx':last_tx,'live_leases':0,'protocol_commands':commands,'resets':resets,'physical_frames':len(data)//192},records
if __name__=='__main__':
 import sys,json
 d,r=decode(sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]));print(json.dumps({'frames':d['allocated'],'records':len(r),'commands':d['protocol_commands'],'last_tx':d['last_tx']}))
