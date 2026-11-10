"""Independent semantic/source binding for full real-route bounded frontier."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from profile_real import parse_log
from build_search_cost_router import generate

def main():
 out=ROOT/'results/search_cost_real_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 base=ROOT/'results/children_real_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert sha(base/'manifest.json')==m['baseline_manifest_sha256']
 assert sha(base/'source_bound_audit.json')==m['baseline_audit_sha256'] and json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(ROOT/'scripts/verify_search_cost_real.py')==m['runner_sha256']==sha(out/'verify_search_cost_real.py')
 assert sha(ROOT/'adapters/build_search_cost_router.py')==m['generator_sha256']==sha(out/'build_search_cost_router.py')
 for name,digest in m['sources'].items():assert sha(out/name)==digest
 generated=generate((base/'sources/trace.cpp').read_text(),(base/'sources/real_trace.hpp').read_text())
 assert (out/'sources/trace.cpp').read_text()==generated[0] and (out/'sources/real_trace.hpp').read_text()==generated[1]
 assert generated[0].count('\n')==(base/'sources/trace.cpp').read_text().count('\n')
 for p in (base/'sources').iterdir():
  if p.name not in ('trace.cpp','real_trace.hpp'):assert sha(out/'sources'/p.name)==bm['sources'][str(p.relative_to(base))]
 for p in (out/'include').rglob('*'):
  if p.is_file():assert sha(p)==bm['sources'][str(p.relative_to(out))]
 component=ROOT/'hardware/search'
 unit=ROOT/'results/search_cost_unit_20261024/manifest.json';u=json.loads(unit.read_text());assert u['status']=='passed' and sha(unit)==m['unit_gate_sha256']
 assert u['helper_sha256']==sha(component/'search_cost.hpp')
 for name,digest in u['artifacts'].items():assert sha(unit.parent/name)==digest
 for name in ['search_cost.hpp']:assert sha(out/'sources'/name)==sha(component/name)
 assert [step['stage'] for step in m['commands']]==['build','route'] and all(step['exit_code']==0 for step in m['commands'])
 assert m['commands'][0]['argv'][-3:]==[str(out/'sources/trace.cpp'),'-o',str(out/'router_search_cost')]
 assert m['commands'][1]['argv'][-3:]==[str(out/'router_search_cost'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out/'trace.result')]
 assert sha(out/'router_search_cost')==m['binary_sha256']
 metrics=parse_log((out/'trace.log').read_text());assert metrics==m['metrics'] and metrics['convergence']==bm['metrics']['convergence'] and metrics['pushes']==bm['metrics']['pushes']==130334832
 assert sha(out/'trace.result')==m['result_sha256']==bm['result_sha256']
 assert sha(out/'trace.accesses')==m['accesses_sha256']==bm['accesses_sha256']
 assert sha(out/'trace.jsonl')==m['metadata_sha256']==bm['metadata_sha256']
 assert m['attempts']==570286
 unit_audit=json.loads((unit.parent/'source_bound_audit.json').read_text());assert unit_audit['status']=='passed' and unit_audit['manifest_sha256']==sha(unit)
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'attempts':m['attempts'],'heap_pushes':metrics['pushes'],'all_attempt_metadata_byte_equal':True,'result_byte_equal':True,'captured_label_access_binary_equal':True,'helper_sha256':sha(component/'search_cost.hpp'),'unit_cases':262144,'scope':'Pure scalar floating cost decomposition verified in complete real CPU route with unchanged geometry/exclusion/children/frontier. All search metadata and captured label accesses match; access capture is sampled. No floating HLS or complete FPGA routing claim.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
