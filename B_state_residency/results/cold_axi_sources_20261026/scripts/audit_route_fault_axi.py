"""Replay all bytes and actual 4KiB-split 192B page bursts (base zero)."""
from pathlib import Path
from collections import Counter
def replay(path,regions,final=None):
 buffers=[bytearray(p.read_bytes())if isinstance(p,Path)else bytearray(p)for _,p in regions];pending=[];reads=writes=bs=requests=0;label=path.name=='label_axi.txt';nextread=nextwrite=None;waddresses=[];lengths=Counter();wlengths=Counter();error_r=error_b=0
 def expected_length(address):return min((192-address%192)//64,(4096-address%4096)//64)
 for line in path.read_text().splitlines():
  t=line.split()
  if t[0]=='A':
   assert not pending;requests+=1;address=int(t[1],16);length=int(t[2]);assert 1<=length<=3 and address%4096+64*length<=4096;lengths[length]+=1
   if label:
    assert (nextread is None and address%192==0)or address==nextread
    assert length==expected_length(address)
    end=address+64*length;nextread=end if end%192 else None
   pending=[address+64*i for i in range(length)]
  elif t[0]=='B':
   assert t in [['B','0'],['B','2']];error_b+=t[1]=='2';bs+=1;assert 1<=len(waddresses)<=3
   if label:
    start=waddresses[0];assert (nextwrite is None and start%192==0)or start==nextwrite
    assert len(waddresses)==expected_length(start) and waddresses==[start+64*i for i in range(len(waddresses))]
    end=start+64*len(waddresses);nextwrite=end if end%192 else None
   else:assert len(waddresses)==1
   wlengths[len(waddresses)]+=1;waddresses=[]
  else:
   address=int(t[1],16);choices=[(i,address-base)for i,(base,_)in enumerate(regions)if base<=address<base+len(buffers[i])];assert len(choices)==1
   idx,offset=choices[0];assert offset%64==0 and offset+64<=len(buffers[idx]);buf=buffers[idx]
   if t[0]=='R':
    assert pending and pending.pop(0)==address and t[3]in ['0','2'];error_r+=t[3]=='2';assert int(t[2],16).to_bytes(64,'little')==buf[offset:offset+64];reads+=1
   else:
    assert t[0]=='W' and final is not None;mask=int(t[2],16)
    assert mask==2**64-1 if label else mask in [0xffff<<(16*i)for i in range(4)]
    data=int(t[3],16).to_bytes(64,'little')
    for j in range(64):
     if mask>>j&1:buf[offset+j]=data[j]
    writes+=1;waddresses.append(address)
 assert not pending and not waddresses and (nextread is None or error_r>0) and nextwrite is None
 if final is None:assert not writes and not bs
 else:assert len(buffers)==1 and bytes(buffers[0])==final.read_bytes()
 if label:assert (reads%3==0 or error_r>0) and writes%3==0
 return dict(error_read_beats=error_r,error_write_replies=error_b,read_transactions=requests,read_beats=reads,write_beats=writes,write_replies=bs,read_burst_lengths=dict(lengths),write_burst_lengths=dict(wlengths),logical_192B_reads=reads//3 if label else None,logical_192B_writes=writes//3 if label else None,bytes_checked=sum(map(len,buffers)))
