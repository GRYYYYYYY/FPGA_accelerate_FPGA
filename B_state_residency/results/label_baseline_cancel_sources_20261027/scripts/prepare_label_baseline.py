"""Convert every prepared CPU node, without a future read list, to immutable label records."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir()
 assert source.stat().st_size%44==0
 n=source.stat().st_size//44;assert 0<n<=1<<24
 target=out/'baseline.bin'
 with source.open('rb')as f,target.open('wb')as g:
  while True:
   block=f.read(44*32768)
   if not block:break
   dst=bytearray()
   for u in struct.iter_unpack('<11I',block):
    assert u[5]<=255
    dst+=struct.pack('<8I',u[0],u[1],u[3],u[4],u[5],0,0,0)
   g.write(dst)
  if n%2:g.write(bytes(32))
 m=dict(status='prepared',source=str(source),source_sha256=sha(source),node_count=n,stride=32,baseline_bytes=target.stat().st_size,baseline_sha256=sha(target),builder_sha256=sha(Path(__file__)),mapping=[0,1,3,4,5],padding='three zero u32; last unused odd half zero',scope='All CPU prepared nodes, no future closure or read-list input; immutable initial baseline only.')
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m))
if __name__=='__main__':main()
