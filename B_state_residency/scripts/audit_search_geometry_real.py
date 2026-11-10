from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_search_geometry_router import generate
from profile_real import parse_log

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/search_geometry_real_v2_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 base=ROOT/'results/search_cost_exact_real_20261024';bm=read(base/'manifest.json')
 assert bm['status']=='passed' and sha(base/'manifest.json')==m['baseline_manifest_sha256']
 bg=read(base/'source_bound_audit.json');assert bg['status']=='passed' and bg['manifest_sha256']==sha(base/'manifest.json')
 assert sha(base/'source_bound_audit.json')==m['baseline_audit_sha256']
 assert sha(ROOT/'scripts/verify_search_geometry_real_v2.py')==m['runner_sha256']==sha(out/'verify_search_geometry_real_v2.py')
 assert sha(ROOT/'adapters/build_search_geometry_router.py')==m['generator_sha256']==sha(out/'build_search_geometry_router.py')
 for name,digest in m['sources'].items():assert sha(out/name)==digest,name
 source,header=generate((base/'sources/trace.cpp').read_text(),(base/'sources/real_trace.hpp').read_text())
 assert (out/'sources/trace.cpp').read_text()==source and (out/'sources/real_trace.hpp').read_text()==header
 assert source.count('\n')==(base/'sources/trace.cpp').read_text().count('\n')
 for p in (base/'sources').iterdir():
  if p.name not in ['trace.cpp','real_trace.hpp']:assert sha(out/'sources'/p.name)==sha(p)
 for p in (out/'include').rglob('*'):
  if p.is_file():assert sha(p)==sha(base/p.relative_to(out))
 assert sha(out/'sources/geometry.hpp')==sha(ROOT/'hardware/hls/search_geometry/v1/geometry.hpp')
 assert sha(out/'sources/search_geometry_checked.hpp')==sha(ROOT/'hardware/search/search_geometry_checked.hpp')
 unit=ROOT/'results/search_geometry_unit_v3_20261024';ug=read(unit/'source_bound_audit.json')
 assert ug['status']=='passed' and sha(unit/'manifest.json')==ug['manifest_sha256']==m['unit_gate_sha256']
 assert sha(out/'sources/geometry.hpp')==sha(unit/'sources/geometry.hpp')
 assert [c['stage']for c in m['commands']]==['build','route'] and all(c['exit_code']==0 for c in m['commands'])
 assert sha(out/'router_search_geometry')==m['binary_sha256']
 metrics=parse_log((out/'trace.log').read_text());assert metrics==m['metrics'] and metrics['convergence']==bm['metrics']['convergence'] and metrics['pushes']==130334832
 for name,key in [('trace.result','result_sha256'),('trace.accesses','accesses_sha256'),('trace.jsonl','metadata_sha256')]:assert sha(out/name)==m[key]==bm[key]
 assert m['attempts']==570286
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'geometry_helper_sha256':sha(out/'sources/geometry.hpp'),'unit_gate_sha256':sha(unit/'source_bound_audit.json'),'attempts':570286,'pushes':130334832,'whole_result_equal':True,'all_metadata_equal':True,'sampled_label_access_binary_equal':True,'scope':'Checked scalar geometry integrated with exact binary32 CPU route, unchanged coordinate/SLR/label access order. CrossSLR/recursive cases still require synthetic evidence; no FPGA whole-router or speed claim.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
