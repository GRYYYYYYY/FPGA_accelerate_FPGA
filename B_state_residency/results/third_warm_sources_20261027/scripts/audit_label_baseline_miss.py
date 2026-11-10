from pathlib import Path
import sys,json,struct,runpy,collections
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
image=Path(m['image']);im=json.loads((image/'manifest.json').read_text());assert sha(image/'manifest.json')==m['image_manifest_sha256'];assert sha(image/'baseline.bin')==im['baseline_sha256']
cpu=Path(im['source']);assert sha(cpu)==im['source_sha256'];assert sha(p/'vectors.txt')==m['vectors_sha256']
b=runpy.run_path(str(p/'sources/build.py'));b['make'].__globals__['BASE']=ROOT/'hardware/variants/label_frame_export_v1/expansion_20261024/pager/pager/resident_page_manager.sv';assert b['make']()==(p/'sources/resident_page_manager.sv').read_text()
b=runpy.run_path(str(p/'sources/build_tb.py'));b['make'].__globals__['HERE']=ROOT/'hardware/variants/label_baseline_miss_v1';assert b['make']()==(p/'sources/tb_miss.sv').read_text()
def initial(n):
 with cpu.open('rb')as f:f.seek(n*44);u=struct.unpack('<11I',f.read(44))
 return list(u[j]for j in [0,1,3,4,5])
def value(v):return sum(u<<(32*i)for i,u in enumerate(v))
def packed(records):
 d=bytearray(192)
 for off,v in records.items():d[0]|=1<<off;struct.pack_into('<5I',d,1+off*20,*v)
 return bytes(d)
lines=[line.split()for line in(p/'trace.txt').read_text().splitlines()]
slots={};back={};dirty={};pending=None;wbs=[];rfs=[];writes=[];misses=[];bases=[];ios=[];clients=[];native_reads=0
for t in lines:
 if t[0]=='N':
  assert pending is None
  op,slot,page,off,field=map(int,t[1:6]);val=int(t[6],16);status=0;present=0;payload=0
  if op==1:assert slot not in slots;slots[slot]=(page,{});dirty[slot]=False
  elif op in [2,3]:
   assert slots[slot][0]==page;rec=slots[slot][1]
   if op==3:
    v=list(rec.get(off,[0]*5));v[field]=val;assert v[4]<=255;rec[off]=v;dirty[slot]=True;writes.append((page*8+off,field,val))
   else:native_reads+=1
   present=int(off in rec);payload=value(rec[off])if present else 0
  elif op==5:
   assert slots[slot][0]==page;back[page]={o:list(v)for o,v in slots[slot][1].items()};wbs.append(packed(back[page]));dirty[slot]=False
  elif op==4:
   assert not dirty[slot] and slots[slot][0]==page;del slots[slot];del dirty[slot]
  elif op==6:
   assert slots[slot][0]==page
   if page not in back:status=8
   else:slots[slot]=(page,{o:list(v)for o,v in back[page].items()});rfs.append(packed(back[page]))
  else:assert op in [0,12]
  pending=(status,present,payload)
 elif t[0]=='R':assert pending==(int(t[1]),int(t[2]),int(t[3],16));pending=None
 elif t[0]=='MISS':misses.append((int(t[1]),int(t[2],16)))
 elif t[0]=='BASE':bases.append((int(t[1]),int(t[2]),int(t[3],16)))
 elif t[0]=='IO':ios.append((int(t[1]),int(t[2]),int(t[3]),int(t[4],16),int(t[5]),int(t[6],16)))
 elif t[0]=='CLIENT':clients.append((int(t[1]),int(t[2],16)))
assert pending is None
assert misses==[(n,0x300010003)for n in [0,1,8,16]]
assert bases==[(n,0,value(initial(n)))for n in [0,1,8]]+[(16,0,value(initial(16)))if m['drain_fault']else(16,3,0)]
expected_writes=[(n,f,v)for n in [0,1]for f,v in enumerate(initial(n))]+[(1,3,180327)]+[(8,f,v)for f,v in enumerate(initial(8))]
assert writes==expected_writes
v1=initial(1);v1[3]=180327
assert ios==[(0,0,2,0,0,value(initial(0))),(1,1,3,180327,0,value(v1)),(1,0,2,0,0,value(v1)),(0,0,2,0,0,value(initial(0))),(1,0,2,0,0,value(v1)),(16,0,2,0,10,0)]
assert clients==[(8,value(initial(8)))]*2
assert len(wbs)==2 and len(rfs)>=2
# Replay every physical page beat against byte memory and native independent record snapshots.
physical=bytearray(3072);wbeats=[];rbeats=[];acount=bcount=0
for t in [s.split()for s in(p/'pages_axi.txt').read_text().splitlines()]:
 if t[0]=='W':
  addr=int(t[1],16);assert int(t[2],16)==(1<<64)-1;v=int(t[3],16).to_bytes(64,'little');physical[addr:addr+64]=v;wbeats.append(v)
 elif t[0]=='R':
  addr=int(t[1],16);v=int(t[2],16).to_bytes(64,'little');assert v==physical[addr:addr+64] and t[3]=='0';rbeats.append(v)
 elif t[0]=='A':assert t[2]=='3';acount+=1
 elif t[0]=='B':assert t[1]=='0';bcount+=1
 else:assert False,t
assert b''.join(wbeats)==b''.join(wbs);assert b''.join(rbeats)==b''.join(rfs);assert acount==len(rfs)and bcount==len(wbs);assert physical==(p/'pages.bin').read_bytes()
# Baseline bytes are actual independent file-agent responses, not TB expected values.
a=[s.split()for s in(p/'baseline_axi.txt').read_text().splitlines()];assert len(a)==8
with(image/'baseline.bin').open('rb')as f:
 for i,n in enumerate([0,1,8,16]):
  addr=0xb000000000+(n//2)*64;assert a[i*2]==['A',f'{addr:016x}','1'];t=a[i*2+1];assert t[0]=='R'and int(t[1],16)==addr
  f.seek((n//2)*64);assert int(t[2],16)==int.from_bytes(f.read(64),'little');assert int(t[3])==(2 if i==3 and not m['drain_fault']else 0)
log=(p/'simulate.log').read_text();assert 'BASELINE_MISS_PASS'in log and 'Fatal:'not in log
assert lines[-1][0]=='PASS'and lines[-1][2]=='4'
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),single=m['single'],drain_fault=m['drain_fault'],checks=int(lines[-1][1]),baseline_misses=4,seeded_records=3,field_writes=len(writes),native_reads=native_reads,page_writebacks=len(wbs),page_refills=len(rfs),physical_page_bytes_checked=len(physical),baseline_read_beats=4,first_write_preserves_other_fields=True,read_seed_survives_writeback_refill=True,client_read_seed_survives_writeback_refill=True,post_open_epoch_pin_changed=True,scope='Actual manager/native endpoint plus baseline/page AXI; final baseline error or native-fault deferred drain closes business. Fixed initial context only. Not full query, warm recovery, arbitrary cancellation, authentication or board proof.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('BASELINE_MISS_AUDITED',p.name)
