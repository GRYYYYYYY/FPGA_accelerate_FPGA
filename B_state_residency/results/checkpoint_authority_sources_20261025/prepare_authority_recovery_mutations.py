from pathlib import Path
import json,mmap,struct

def prepare(case):
 case=Path(case);f=json.loads((case/'fixture.json').read_text());codec=Path(f['codec']);cpu=Path(f['cpu']);n=f['nodes'];chosen={};used=set()
 with(codec/'owners.bin').open('rb')as fp,mmap.mmap(fp.fileno(),0,access=mmap.ACCESS_READ)as mm:
  for node,(net,packed,head,rsv)in enumerate(struct.iter_unpack('<4I',mm[:n*16])):
   refs=packed&65535;occ=packed>>16
   if net==0 and 'empty'not in chosen:chosen['empty']=(node,2717,1);used.add(node)
   elif net and refs<65535 and node not in used:
    if 'inc'not in chosen:chosen['inc']=(node,net-1,1);used.add(node)
    elif refs>1 and 'dec'not in chosen:chosen['dec']=(node,net-1,2);used.add(node)
    elif occ>1 and refs==1 and 'promote'not in chosen:chosen['promote']=(node,net-1,2);used.add(node)
   if len(chosen)==4:break
  if 'dec'not in chosen:
   for node,(net,packed,head,rsv)in enumerate(struct.iter_unpack('<4I',mm[:n*16])):
    if net and node not in used:chosen['dec']=(node,net-1,2);used.add(node);break
  if f['capacity']:
   for node,net,refs in struct.iter_unpack('<III',(cpu/'initial_overflow.u32').read_bytes()):
    if node not in used and refs<65535:chosen['overflow']=(node,net,1);used.add(node);break
 assert {'empty','inc','dec'}<=chosen.keys()
 if f['capacity']:assert {'promote','overflow'}<=chosen.keys()
 order=[chosen[k]for k in ['inc','dec','promote','overflow','empty']if k in chosen]
 extra={}
 for node,net,refs in struct.iter_unpack('<III',(cpu/'initial_overflow.u32').read_bytes()):
  if node in used:extra.setdefault(node,{})[net]=refs
 records=[]
 with(cpu/'initial_nodes.u32').open('rb')as fp,mmap.mmap(fp.fileno(),0,access=mmap.ACCESS_READ)as mm:
  for node,net,op in order:
   row=struct.unpack_from('<11I',mm,node*44);owners=dict(extra.get(node,{}))
   if row[6]!=0xffffffff:owners[row[6]]=row[7]
   old=owners.get(net,0);now=old+(1 if op==1 else -1);assert 0<=now<=65535
   occ=len(owners);after=occ+int(old==0 and op==1)-int(old==1 and op==2)
   records.append({'node':node,'net':net,'op':op,'before_refs':old,'before_occupancy':occ,'after_refs':now,'after_occupancy':after})
 with(case/'mutations.txt').open('w')as fp:
  for i,r in enumerate(records):fp.write(f"{i} {r['node']} {r['net']} {r['op']} {r['before_refs']} {r['before_occupancy']} {r['after_refs']} {r['after_occupancy']}\n")
 with(case/'live.bin').open('wb')as dst:
  for name in ['primary.bin','pool.bin','allocator.bin']:
   with(case/name).open('rb')as src:
    for b in iter(lambda:src.read(1<<20),b''):dst.write(b)
 return records
