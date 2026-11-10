from pathlib import Path
import hashlib,json,mmap,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();dep=ROOT/'results/access_fabric_inputs_20261024';m=json.loads((dep/'manifest.json').read_text());assert m['status']=='passed'
 integrated=ROOT/'results/access_owner_v3_20261024';gate=json.loads((integrated/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(integrated/'manifest.json')
 result={'status':'running','source_manifest_sha256':sha(dep/'manifest.json'),'integrated_gate_sha256':sha(integrated/'source_bound_audit.json'),'cases':{}}
 for case,fixture in [('synthetic','synthetic'),('real','real'),('pressure','synthetic')]:
  meta=m['cases'][fixture];attrs_path=Path(meta['graph'])/'nodes.rrt32';contexts={int(r[0]):r for r in map(str.split,(dep/fixture/'contexts.txt').read_text().splitlines())};starts={}
  for line in (dep/fixture/'vectors.txt').open():
   r=line.split();x=[int(v,16)for v in r[2:22]]
   if x[0]==0:starts[int(r[1])]=x[6:]
  ids=[cid for cid in starts if case!='pressure'or cid%19==0]
  # A child progresses from alive to dead at most once in this design run.
  ids.sort(key=lambda cid:(int(contexts[cid][2]),bool(starts[cid][1]&2),cid))
  marked=set();rows=[]
  with attrs_path.open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as attrs:
   for cid in ids:
    r=contexts[cid];parent,child,sink=map(int,r[1:4]);expected=starts[cid];dead=bool(expected[1]&2)
    assert dead or child not in marked
    if dead:marked.add(child)
    def u32(n,o):return struct.unpack_from('<I',attrs,n*32+o)[0]
    def i16(n,o):return struct.unpack_from('<h',attrs,n*32+o)[0]&0xffffffff
    flags=(expected[1]&0x11d)|(2 if dead else 0)|(32 if attrs[parent*32+9]&2 else 0)|(64 if attrs[child*32+9]&2 else 0)|(128 if attrs[child*32+9]&128 else 0)
    oracle=[expected[0],flags,attrs[child*32+8],attrs[parent*32+8],attrs[sink*32+8],i16(child,14),u32(child,0),u32(sink,0),i16(sink,10),i16(sink,12)]+expected[10:]
    assert oracle==expected,(case,cid,oracle,expected)
    descriptor=[expected[0],expected[1]&0x11d]+expected[10:]
    rows.append(' '.join([str(cid),str(parent),str(child),str(sink),str(int(dead))]+[f'{v:08x}'for v in descriptor]+[f'{sum(v<<(32*i)for i,v in enumerate(expected)):0112x}']))
  d=out/case;d.mkdir();(d/'commands.txt').write_text('\n'.join(rows)+'\n');result['cases'][case]={**meta,'fixture':fixture,'ordered_case_ids':ids,'commands_sha256':sha(d/'commands.txt'),'dead_nodes':len(marked),'count':len(ids),'attrs_sha256':sha(attrs_path)}
 result['status']='passed';(out/'generator.py').write_bytes(Path(__file__).read_bytes());result['generator_sha256']=sha(Path(__file__));(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('METADATA_INPUTS_PASS synthetic=11664 real=512 pressure=614 original_config14_equal=1 monotonic_dead_order=1')
if __name__=='__main__':main()
