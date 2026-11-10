"""Project frozen real field vectors onto the public memory-endpoint interface.
Transport records become independent expected AXI bytes, never DUT inputs.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
 src=ROOT/'results/rtl_page_controller_20261023/vectors/actual.txt'
 vm=src.parent/'vectors_manifest.json';parent=json.loads(vm.read_text())
 if sha(src)!=parent['files'][str(src)]:raise ValueError('Source vectors changed')
 host=out/'actual.txt';pages=out/'pages.hex'
 if host.exists() or pages.exists():raise FileExistsError('No overwrite')
 counts=Counter();owners={};peak=0;sequence=0;offsets=set()
 with src.open() as stream,host.open('w') as h,pages.open('w') as raw:
  it=iter(stream)
  for line in it:
   a=[int(x,16) for x in line.split()];op,slot,page,q,price,gen,tx,kind,present,off,field,value,payload,peer,empty,status,word,seen,dirty,outtx,draining=a
   if status!=0:raise ValueError('Actual source has unexpected failures')
   frame=0;page_index=0
   if op in (5,6):
    key=(price,q,page)
    if op==5 and key not in owners:owners[key]=len(owners)
    if key not in owners:raise ValueError('Refill without backing write')
    frame=owners[key];peak=max(peak,len(owners));page_index=sequence;sequence+=1
    bitmap=0;labels=[]
    for pos in range(64):
     b=[int(x,16) for x in next(it).split()]
     if b[0]!=(9 if op==5 else 7) or b[1:6]!=a[1:6] or b[6]!=outtx or b[7]!=(op==6) or b[9]!=pos or b[15]!=0:raise ValueError('Malformed transport projection')
     present,word=(b[17],b[16]) if op==5 else (b[8],b[12])
     if word>>136 or (not present and word):raise ValueError('Noncanonical transport payload')
     bitmap|=present<<pos;labels.append(word.to_bytes(20,'little'))
    done=[int(x,16) for x in next(it).split()]
    if done[0]!=8 or done[1:6]!=a[1:6] or done[6]!=outtx or done[7]!=(op==6) or done[15]!=0:raise ValueError('Missing source completion')
    blob=bitmap.to_bytes(8,'little')+b''.join(labels)+bytes(56)
    for i in range(0,1344,64):raw.write(format(int.from_bytes(blob[i:i+64],'little'),'0128x')+'\n')
    offsets.add((frame*21)%64)
   elif op in (7,8,9):raise ValueError('Orphan internal command')
   if op==11:owners.clear()
   row=(op,slot,page,q,price,gen,off,field,value,status,word if op not in (5,6) else 0,seen,dirty,outtx,draining,frame,page_index)
   # Transport temporaries above must not overwrite host response expectations.
   row=(op,slot,page,q,price,gen,off,field,value,status,a[16],a[17],a[18],outtx,draining,frame,page_index)
   h.write(' '.join(format(x,'x') for x in row)+'\n');counts[str(op)]+=1
 record=dict(status='passed',public_commands=sum(counts.values()),field_accesses=counts['2']+counts['3'],transfers=sequence,peak_reserved_owners=peak,alignment_offsets=len(offsets),counts=dict(counts),
  files={str(p.resolve()):sha(p) for p in (src,vm,host,pages,Path(__file__).resolve())})
 (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='files'},indent=2))
if __name__=='__main__':main()
