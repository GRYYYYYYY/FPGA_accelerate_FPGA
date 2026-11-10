"""Extract source-bound SLR/Laguna tables, retain explicit zero-vs-dense counterexample."""
from pathlib import Path
import hashlib,json,mmap,struct
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/coordinate_inputs_20261024';out.mkdir();graph=ROOT/'results/graph_image_20261024'
 gm=json.loads((graph/'manifest.json').read_text());gg=json.loads((graph/'source_bound_audit.json').read_text())
 assert gg['status']=='passed' and gg['manifest_sha256']==sha(graph/'manifest.json')
 p=graph/'config_prefix.rrtbin';assert sha(p)==gm['artifacts'][p.name]
 data=p.read_bytes();assert data[:4]==b'RRT1';pos=68
 rows=struct.unpack_from('<i',data,pos)[0];pos+=4;slr=list(struct.unpack_from('<'+str(rows)+'i',data,pos));pos+=rows*4
 has=struct.unpack_from('<i',data,pos)[0];pos+=4;cols=0;nx=[];pr=[];north=[0]*rows
 if has:
  cols=struct.unpack_from('<i',data,pos)[0];pos+=4
  nx=list(struct.unpack_from('<'+str(cols)+'i',data,pos));pos+=4*cols
  pr=list(struct.unpack_from('<'+str(cols)+'i',data,pos));pos+=4*cols
  north=list(data[pos:pos+rows]);pos+=rows
 nodes=struct.unpack_from('<i',data,pos)[0];pos+=4;assert pos==len(data) and nodes==gm['nodes']
 def write_tables(d,slr,north,nx,pr):
  d.mkdir();(d/'rows.bin').write_bytes(b''.join(struct.pack('<ii',a,b)for a,b in zip(slr,north)))
  (d/'columns.bin').write_bytes(b''.join(struct.pack('<ii',a,b)for a,b in zip(nx,pr)))
 write_tables(out/'real',slr,north,nx,pr)
 counts={};sll=[]
 with (graph/'nodes.rrt32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
  for n in range(nodes):
   t=mm[n*32+8];counts[t]=counts.get(t,0)+1
   if t==5:sll.append(n)
 # Complete small CSR image. Several SLLs deliberately point to node zero and
 # to another SLL; resolving a predecessor recursively would be incorrect.
 syn=out/'synthetic';ys=[i//32 for i in range(128)];norths=[int(i%32<16)for i in range(128)]
 nxs=[16 if i<=16 else 48 if i<=48 else 2147483647 for i in range(64)]
 prs=[-2147483648 if i<16 else 16 if i<48 else 48 for i in range(64)]
 write_tables(syn,ys,norths,nxs,prs)
 attrs=[]
 for n in range(64):
  typ=5 if n%4==1 else 12;bx=n%64;by=(n*3)%64;ex=bx;ey=by+32
  if n==0:ey=70;by=38
  if n==1:by=10;ey=70
  if n==5:by=20;ey=70
  attrs.append(struct.pack('<iiBBhhhhhIii',n%9,n,typ,1,bx,by,ex,ey,1,0x3f800000,n,-1))
 (syn/'nodes.rrt32').write_bytes(b''.join(attrs));(syn/'offsets.u32le').write_bytes(bytes(65*4));(syn/'edges.u32le').write_bytes(b'')
 summary={'real':{'nodes':nodes,'edges':gm['edges'],'rows':rows,'columns':cols,'has_laguna':has,'types':counts,'sll_nodes':len(sll)},'synthetic':{'nodes':64,'edges':0,'rows':128,'columns':64,'has_laguna':1},'semantic_counterexample':{'child':1,'child_begin_y':10,'child_static_end_y':70,'node_zero_static_end_y':70,'dense_uncreated_prev':-1,'dense_end_y':70,'paged_absent_prev':0,'paged_end_y':10,'meaning':'Do not reinterpret absent zero prev as -1; full dense equivalence is not proven by paged endpoint tests.'}}
 (out/'coverage.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'runner.py').write_bytes(Path(__file__).read_bytes())
 m={'status':'prepared','graph_manifest_sha256':sha(graph/'manifest.json'),'graph_audit_sha256':sha(graph/'source_bound_audit.json'),'prefix_sha256':sha(p),'runner_sha256':sha(Path(__file__)),'artifacts':{str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()}}
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
