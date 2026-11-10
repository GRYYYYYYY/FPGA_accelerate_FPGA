"""Native label replay extended only with the explicit G4 target context7/1/7.
Reads original full logs without manufacturing a compatibility transcript.
"""
import struct

def audit_native_records(allrows,d):
    slots={};dirty={};back={};pending=None;native_write_pages=[];native_read_pages=[];native_fields=0
    last_reset=False
    for t in allrows:
     if t[0]=='BASELINE_TARGET_RESET':
      assert pending is None
      if not last_reset:slots={};dirty={};back={}
      last_reset=True
      continue
     last_reset=False
     if t[0]=='NB':
      assert pending is None
      op,sl,pg,gen,off,fi=map(int,t[2:8]);val=int(t[8],16);qid,pr=map(int,t[9:11]);status=present=payload=0
      assert(qid,pr)in [(1,3),(2,4),(3,5),(0,6),(1,7)]
      if op==1:
       assert sl not in slots and gen>0;slots[sl]=(pg,gen,{});dirty[sl]=False
      elif op in [2,3,4,5,6]:
       assert sl in slots and slots[sl][:2]==(pg,gen);records=slots[sl][2]
       if op in [2,3]:
        if op==3:
         assert 0<=fi<=4;v=list(records.get(off,[0]*5));v[fi]=val;assert v[4]<=255;records[off]=v;dirty[sl]=True;native_fields+=1
        present=int(off in records);payload=sum(v<<(32*i)for i,v in enumerate(records[off]))if present else 0
       elif op==4:
        assert not dirty[sl];del slots[sl];del dirty[sl]
       elif op==5:
        back[pg]={o:list(v)for o,v in records.items()};dirty[sl]=False
        packed=bytearray(192)
        for o,v in records.items():packed[0]|=1<<o;struct.pack_into('<5I',packed,1+o*20,*v)
        native_write_pages.append(bytes(packed))
       else:
        if pg not in back:status=8
        else:
         slots[sl]=(pg,gen,{o:list(v)for o,v in back[pg].items()});packed=bytearray(192)
         for o,v in back[pg].items():packed[0]|=1<<o;struct.pack_into('<5I',packed,1+o*20,*v)
         native_read_pages.append(bytes(packed))
      else:assert op in [0,12]
      pending=(status,present,payload)
     elif t[0]=='NR':assert pending==(int(t[2]),int(t[3]),int(t[4],16));pending=None
    assert pending is None
    wbeats=[];rbeats=[]
    for t in map(str.split,(d/'label_axi.txt').read_text().splitlines()):
     if t[0]=='W':assert int(t[2],16)==(1<<64)-1;wbeats.append(int(t[3],16).to_bytes(64,'little'))
     elif t[0]=='R':assert t[3]=='0';rbeats.append(int(t[2],16).to_bytes(64,'little'))
    assert b''.join(wbeats)==b''.join(native_write_pages)
    assert b''.join(rbeats)==b''.join(native_read_pages)
    return dict(native_fields=native_fields,write_pages=len(native_write_pages),read_pages=len(native_read_pages))
