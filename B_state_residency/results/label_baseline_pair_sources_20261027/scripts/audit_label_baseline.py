"""Independent all-node CPU mapping and actual AXI/response replay."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
 image=Path(m['image']);im=json.loads((image/'manifest.json').read_text());cpu=Path(im['source']);data=image/'baseline.bin'
 assert sha(image/'manifest.json')==m['image_manifest_sha256']
 assert sha(cpu)==im['source_sha256'] and sha(data)==im['baseline_sha256']
 assert json.loads((cpu.parent/'manifest.json').read_text())['artifacts']['initial_nodes.u32']==im['source_sha256']
 assert cpu.name=='initial_nodes.u32' and json.loads((cpu.parent/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(p/'vectors.txt')==m['vectors_sha256']
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
 # Audit every record against the original 44B CPU layout, not builder output logic.
 total=0
 with cpu.open('rb')as f,data.open('rb')as g:
  while True:
   raw=f.read(44*32768)
   if not raw:break
   packed=g.read(len(raw)//44*32);assert len(packed)==len(raw)//44*32
   for off,u in enumerate(struct.iter_unpack('<11I',raw)):
    v=struct.unpack_from('<8I',packed,off*32)
    assert v[:5]==(u[0],u[1],u[3],u[4],u[5]) and v[5:]==(0,0,0) and u[5]<=255
   total+=len(raw)//44
  assert g.read()==(bytes(32)if total%2 else b'')
 assert total==im['node_count']==9089009
 vectors=[(int(t[0]),int(t[1],16))for line in(p/'vectors.txt').read_text().splitlines()if(t:=line.split())]
 q=[t for line in(p/'trace.txt').read_text().splitlines()if(t:=line.split())and t[0]=='Q']
 assert len(q)==len(vectors)+6
 expected=[(0,0x300010003,5,0,0)]+[(n,0x300010003,0,v,1)for n,v in vectors]+[(total,0x300010003,1,0,0),(0,0x300010004,5,0,0),(0,0x300010003,0,dict(vectors)[0],1),(0,0x300010003,3,0,1),(0,0x300010003,4,0,1)]
 assert [(int(t[1]),int(t[2],16),int(t[3]),int(t[4],16),int(t[5]))for t in q]==expected
 addresses=[0xb000000000+(n//2)*64 for n,ep,s,v,reads in expected if reads]
 axi=[line.split()for line in(p/'baseline_axi.txt').read_text().splitlines()]
 a=[t for t in axi if t[0]=='A'];r=[t for t in axi if t[0]=='R']
 assert len(a)==len(r)==len(addresses) and len(axi)==len(a)*2
 with data.open('rb')as f:
  for i,(ar,rr,addr)in enumerate(zip(a,r,addresses)):
   assert ar==['A',f'{addr:016x}','1'] and int(rr[1],16)==addr
   f.seek(addr-0xb000000000);beat=f.read(64);assert int(rr[2],16)==int.from_bytes(beat,'little')
   assert int(rr[3])==(2 if i==len(r)-2 else 0)
 # Every vector is independently sourced from CPU, including requests outside old closure.
 with cpu.open('rb')as f:
  for n,v in vectors:
   f.seek(n*44);u=struct.unpack('<11I',f.read(44));assert v==sum(u[j]<<(32*k)for k,j in enumerate([0,1,3,4,5]))
 closure={int(line.split()[0])for line in(p.parent/'label_source_crc_full_v2/imports.txt').read_text().splitlines()}
 outside=set(n for n,v in vectors)-closure;assert len(outside)==m['tested_outside_closure'] and len(outside)>0
 log=(p/'simulate.log').read_text();assert 'LABEL_BASELINE_PASS'in log and 'Fatal:'not in log
 terminal=(p/'trace.txt').read_text().splitlines()[-1].split();assert terminal[0]=='PASS' and int(terminal[3])==len(r)
 result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),all_cpu_records_compared=total,baseline_bytes=data.stat().st_size,baseline_sha256=sha(data),tested_records=len(vectors),tested_outside_old_closure=len(outside),actual_axi_reads=len(r),read_error_responses=1,corrupt_padding_responses=1,checks=int(terminal[1]),held_cycles=int(terminal[2]),scope='Real immutable all-node baseline reader component only. No native miss integration, arbitrary price validity, authentication, cancellation, synthesis or board claim.')
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('LABEL_BASELINE_AUDITED',total,len(r))
if __name__=='__main__':main()
