"""Lossless RRT1 graph layout split, independently checked by original Router loader."""
from pathlib import Path
import hashlib,json,mmap,os,shutil,struct,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=Path(sys.argv[1]).resolve();out.mkdir()
 input_path=ROOT/'data/derived/vtr_mcml.rrt';provenance=ROOT/'data/derived/vtr_mcml_provenance.json'
 prov=json.loads(provenance.read_text());assert prov['status']=='exported' and sha(input_path)==prov['output_sha256']
 source=ROOT/'results/frontier_real_20261024';gate=source/'source_bound_audit.json';assert json.loads(gate.read_text())['status']=='passed'
 m={'status':'exporting','pid':os.getpid(),'input_sha256':sha(input_path),'provenance_sha256':sha(provenance),'frontier_gate_sha256':sha(gate),'runner_sha256':sha(Path(__file__)),'commands':[],'scope':'Lossless raw graph and attributes, not filtered adjacency, live occupancy/history snapshot, device upload or hardware graph expansion.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 try:
  with input_path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
   assert data[:4]==b'RRT1';position=4+16*4
   def i32():
    nonlocal position
    value=struct.unpack_from('<i',data,position)[0];position+=4;return value
   rows=i32();assert 0<rows<10000000;position+=4*rows
   laguna=i32();assert laguna in (0,1)
   if laguna:
    cols=i32();assert 0<cols<10000000;position+=8*cols+rows
   nodes=i32();assert nodes>0
   (out/'config_prefix.rrtbin').write_bytes(data[:position]);node_start=position
   edges=0;max_degree=0;reserved_flag16=0
   with (out/'offsets.u32le').open('wb',buffering=1<<20) as offsets,(out/'edges.u32le').open('wb',buffering=1<<20) as adjacency,(out/'nodes.rrt32').open('wb',buffering=1<<20) as attrs:
    offsets.write(struct.pack('<I',0))
    for node in range(nodes):
     assert position+36<=len(data)
     prefix=data[position:position+32];count=struct.unpack_from('<i',data,position+32)[0];position+=36
     assert 0<=count and position+4*count<=len(data)
     children=data[position:position+4*count];position+=4*count
     assert all(0<=child<nodes for (child,) in struct.iter_unpack('<i',children))
     attrs.write(prefix);adjacency.write(children);edges+=count;assert edges<=0xffffffff
     offsets.write(struct.pack('<I',edges));max_degree=max(max_degree,count);reserved_flag16+=bool(prefix[9]&16)
   assert position<len(data)
   (out/'design_suffix.rrtbin').write_bytes(data[position:])
   m.update(nodes=nodes,edges=edges,max_degree=max_degree,reserved_flag16_nodes=reserved_flag16,node_section_start=node_start,node_section_end=position,rrt_bytes=len(data))
  # Frozen original baseline source and includes; main only renamed in verifier TU.
  frozen=out/'reference';frozen.mkdir()
  (frozen/'trace.cpp').write_bytes((source/'original_trace.cpp').read_bytes())
  for name in ['real_trace.hpp','real_router_hooks.inc']:(frozen/name).write_bytes((source/('original_'+name)).read_bytes())
  (frozen/'real_profile.hpp').write_bytes((source/'sources/real_profile.hpp').read_bytes())
  shutil.copytree(source/'include',frozen/'include')
  verifier=ROOT/'adapters/verify_graph_image.cpp';(out/verifier.name).write_bytes(verifier.read_bytes())
  m['sources']={str(p.relative_to(out)):sha(p) for p in frozen.rglob('*') if p.is_file()};m['verifier_sha256']=sha(verifier)
  m['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix not in ('.json','.py','.cpp')}
  build=['g++','-std=c++17','-O2','-fno-fast-math','-pthread','-I'+str(frozen),'-I'+str(frozen/'include'),str(out/verifier.name),'-o',str(out/'verify_graph')]
  for stage,argv in [('build',build),('verify',[str(out/'verify_graph'),str(input_path),str(out),str(nodes),str(edges)])]:
   m['status']=stage;m['commands'].append({'stage':stage,'argv':argv});save()
   with (out/(stage+'.log')).open('w') as log:
    proc=subprocess.Popen(argv,cwd=out,stdout=log,stderr=subprocess.STDOUT,env={k:v for k,v in os.environ.items()if k not in ['LD_LIBRARY_PATH','LD_PRELOAD']});m['commands'][-1]['pid']=proc.pid;save();code=proc.wait();m['commands'][-1]['exit_code']=code;save();assert code==0
  assert f'GRAPH_IMAGE_PASS nodes={nodes} edges={edges}' in (out/'verify.log').read_text()
  m.update(status='passed',binary_sha256=sha(out/'verify_graph'),verify_log_sha256=sha(out/'verify.log'));save();print('GRAPH_IMAGE_EXPORT_PASS',nodes,edges,flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
