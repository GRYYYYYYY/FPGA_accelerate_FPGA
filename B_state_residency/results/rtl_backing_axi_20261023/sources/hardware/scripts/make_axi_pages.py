"""Freeze two directed and 62 actual scratch pages in the existing 1344B codec."""
from pathlib import Path
import json,struct,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.scratch_page_values import ScratchLabel,ScratchPageCodec

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
 capture=ROOT/'results/real_field_values_20261023T024250Z';manifest=json.loads((capture/'manifest.json').read_text())
 paths=[capture/'trace.values',capture/'trace.queries.jsonl']
 for p in paths:
  if sha(p)!=manifest['artifacts'][str(p)]:raise ValueError('Capture changed')
 pages=[{}, {0:ScratchLabel(0x7fc12345,0x80000000,-1,0x7fffffff,255),63:ScratchLabel()}];selected=[]
 with paths[0].open('rb') as f:
  for line in paths[1].read_text().splitlines():
   row=json.loads(line)
   if row['count']>100000:continue
   f.seek(row['byte_offset']);raw=f.read(row['count']*20);words={}
   for node,source,bits,field,write,reserved,hist in struct.iter_unpack('<IIIBBHI',raw):
    old=words.get(node,0);width=8 if field==4 else 32;shift=32*field
    if write:words[node]=(old&~(((1<<width)-1)<<shift))|(bits<<shift)
    elif ((old>>shift)&((1<<width)-1))!=bits:raise ValueError('Actual read mismatch')
   mapped={}
   for node,word in words.items():
    mapped.setdefault(node>>6,{})[node&63]=ScratchLabel(*struct.unpack('<IIiiB3x',word.to_bytes(20,'little')))
   for page,values in sorted(mapped.items()):
    if len(pages)==64:break
    pages.append(values);selected.append(dict(attempt=row['attempt'],page=page,nodes=len(values)))
   if len(pages)==64:break
 if len(pages)!=64:raise ValueError('Insufficient real fixture pages')
 codec=ScratchPageCodec(6);encoded=[codec.encode(p) for p in pages]
 if any(codec.decode(raw)!=p for raw,p in zip(encoded,pages)):raise ValueError('Codec mismatch')
 rawpath=out/'pages.bin';hexpath=out/'pages.hex'
 if rawpath.exists() or hexpath.exists():raise ValueError('Never overwrite frozen fixtures')
 rawpath.write_bytes(b''.join(encoded));hexpath.write_text(''.join(f'{int.from_bytes(raw[i:i+64],"little"):0128x}\n' for raw in encoded for i in range(0,1344,64)))
 inputs=paths+[Path(__file__).resolve(),ROOT/'src/scratch_page_values.py',rawpath,hexpath]
 record=dict(status='passed',pages=64,directed_pages=2,actual_pages=62,stride=1344,beats=21,selected=selected,files={str(p):sha(p) for p in inputs})
 (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ('files','selected')},indent=2))
if __name__=='__main__':main()
