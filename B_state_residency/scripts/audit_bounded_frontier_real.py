"""Independent semantic/source binding for full real-route bounded frontier."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from profile_real import parse_log
from build_bounded_frontier_router import generate

def main():
 out=ROOT/'results/bounded_frontier_real_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 base=ROOT/'results/frontier_real_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert sha(base/'manifest.json')==m['frontier_profile_manifest_sha256']
 assert sha(base/'source_bound_audit.json')==m['frontier_profile_audit_sha256'] and json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(ROOT/'scripts/verify_bounded_frontier_real.py')==m['runner_sha256']==sha(out/'verify_bounded_frontier_real.py')
 assert sha(ROOT/'adapters/build_bounded_frontier_router.py')==m['generator_sha256']==sha(out/'build_bounded_frontier_router.py')
 for name,digest in m['sources'].items():assert sha(out/name)==digest
 generated=generate((base/'sources/trace.cpp').read_text(),(base/'sources/real_trace.hpp').read_text())
 assert (out/'sources/trace.cpp').read_text()==generated[0] and (out/'sources/real_trace.hpp').read_text()==generated[1]
 assert generated[0].count('\n')==(base/'sources/trace.cpp').read_text().count('\n')
 for p in (base/'sources').iterdir():
  if p.name not in ('trace.cpp','real_trace.hpp'):assert sha(out/'sources'/p.name)==bm['sources'][str(p.relative_to(base))]
 for p in (out/'include').rglob('*'):
  if p.is_file():assert sha(p)==bm['sources'][str(p.relative_to(out))]
 component=ROOT/'hardware/hls/frontier/rearchitect/v1/src'
 for name in ['frontier_api.hpp','frontier_bounded.hpp']:assert sha(out/'sources'/name)==sha(component/name)
 assert [step['stage'] for step in m['commands']]==['build','route'] and all(step['exit_code']==0 for step in m['commands'])
 assert m['commands'][0]['argv'][-3:]==[str(out/'sources/trace.cpp'),'-o',str(out/'router_bounded_frontier')]
 assert m['commands'][1]['argv'][-3:]==[str(out/'router_bounded_frontier'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out/'trace.result')]
 assert sha(out/'router_bounded_frontier')==m['binary_sha256']
 metrics=parse_log((out/'trace.log').read_text());assert metrics==m['metrics'] and metrics['convergence']==bm['metrics']['convergence'] and metrics['pushes']==bm['metrics']['pushes']==130334832
 assert sha(out/'trace.result')==m['result_sha256']==bm['result_sha256']
 assert sha(out/'trace.accesses')==m['accesses_sha256']==bm['accesses_sha256']
 assert sha(out/'trace.jsonl')==m['metadata_sha256']==bm['metadata_sha256']
 assert m['attempts']==570286
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'attempts':m['attempts'],'heap_pushes':metrics['pushes'],'all_attempt_metadata_byte_equal':True,'result_byte_equal':True,'captured_label_access_binary_equal':True,'helper_sha256':sha(component/'frontier_bounded.hpp'),'capacity':65536,'scope':'Same bounded helper used by HLS compute, verified in complete real CPU route. Captured label accesses remain sampled as in original trace; no complete FPGA routing or hardware throughput claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
