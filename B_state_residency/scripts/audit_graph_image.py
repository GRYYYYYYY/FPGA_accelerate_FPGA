"""Independent graph image/source audit, including full byte-for-byte RRT1 reconstruction."""
from pathlib import Path
import hashlib,json,re,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/graph_image_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed'
 assert sha(ROOT/'data/derived/logicnets_jscl.rrt')==m['input_sha256']
 provenance=ROOT/'data/derived/logicnets_jscl_provenance.json';assert sha(provenance)==m['provenance_sha256']
 assert json.loads(provenance.read_text())['output_sha256']==m['input_sha256']
 gate=ROOT/'results/frontier_real_20261024/source_bound_audit.json';assert sha(gate)==m['frontier_gate_sha256'] and json.loads(gate.read_text())['status']=='passed'
 baseline=ROOT/'results/real_trace_20261022T165136Z/manifest.json';bm=json.loads(baseline.read_text())
 fm=json.loads((ROOT/'results/frontier_real_20261024/manifest.json').read_text());assert sha(baseline)==fm['baseline_manifest_sha256']
 assert sha(out/'reference/trace.cpp')==bm['build']['trace']['source_sha256']
 assert sha(out/'export_graph_image.py')==m['runner_sha256']==sha(ROOT/'scripts/export_graph_image.py')
 assert sha(out/'verify_graph_image.cpp')==m['verifier_sha256']==sha(ROOT/'adapters/verify_graph_image.cpp')
 for name,digest in m['sources'].items():assert sha(out/name)==digest
 expected={'config_prefix.rrtbin','offsets.u32le','edges.u32le','nodes.rrt32','design_suffix.rrtbin'}
 assert set(m['artifacts'])==expected
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest
 assert [c['stage'] for c in m['commands']]==['build','verify'] and all(c['exit_code']==0 for c in m['commands'])
 assert sha(out/'verify_graph')==m['binary_sha256'] and sha(out/'verify.log')==m['verify_log_sha256']
 assert f"GRAPH_IMAGE_PASS nodes={m['nodes']} edges={m['edges']}" in (out/'verify.log').read_text()
 assert (out/'offsets.u32le').stat().st_size==4*(m['nodes']+1)
 assert (out/'nodes.rrt32').stat().st_size==32*m['nodes']
 assert (out/'edges.u32le').stat().st_size==4*m['edges']
 # Reassemble the ORIGINAL file bytes with implicit cc=next_offset-current_offset.
 h=hashlib.sha256();prefix=(out/'config_prefix.rrtbin').read_bytes();h.update(prefix)
 assert prefix[:4]==b'RRT1' and len(prefix)==m['node_section_start']
 with (out/'offsets.u32le').open('rb') as offsets,(out/'nodes.rrt32').open('rb') as attrs,(out/'edges.u32le').open('rb') as edges:
  current=struct.unpack('<I',offsets.read(4))[0];assert current==0
  for _ in range(m['nodes']):
   nxt=struct.unpack('<I',offsets.read(4))[0];assert current<=nxt<=m['edges']
   count=nxt-current;a=attrs.read(32);e=edges.read(count*4);assert len(a)==32 and len(e)==count*4
   h.update(a);h.update(struct.pack('<i',count));h.update(e);current=nxt
  assert current==m['edges'] and not offsets.read() and not attrs.read() and not edges.read()
 with (out/'design_suffix.rrtbin').open('rb') as suffix:
  for data in iter(lambda:suffix.read(1<<20),b''):h.update(data)
 assert h.hexdigest()==m['input_sha256']
 result={'status':'passed','manifest_sha256':sha(mp),'auditor_sha256':sha(Path(__file__)),'nodes':m['nodes'],'edges':m['edges'],'max_degree':m['max_degree'],'adjacency_bytes':4*(m['nodes']+1+m['edges']),'node_attribute_bytes':32*m['nodes'],'reconstructed_rrt_sha256':h.hexdigest(),'full_original_loader_comparison':True,'scope':'Complete raw ordered graph and static attributes, losslessly reversible RRT1 split. No live cost/state publication, hardware upload or filtered-adjacency claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
