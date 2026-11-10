"""Bind verbatim original arithmetic, candidate extraction, fixture and executed UBSan gate."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'));sys.path.insert(0,str(ROOT/'scripts'))
from build_search_cost_router import generate
from verify_search_cost_unit import extract

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_cost_unit_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 base=ROOT/'results/children_real_20261024';p=base/'sources/trace.cpp';assert sha(p)==m['original_source_sha256']
 assert sha(base/'source_bound_audit.json')==m['baseline_gate_sha256'] and json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 original=ROOT.parent/'_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp'
 assert extract(original.read_text())==extract(p.read_text())
 gen,_=generate(p.read_text(),'#include <fstream>')
 assert (out/'original_cost.inc').read_text()==extract(p.read_text()) and (out/'candidate_cost.inc').read_text()==extract(gen)
 for name,folder,key in [('search_cost.hpp','hardware/search','helper_sha256'),('build_search_cost_router.py','adapters','generator_sha256'),('verify_search_cost_unit.py','scripts','runner_sha256')]:assert sha(ROOT/folder/name)==sha(out/name)==m[key]
 assert sha(ROOT/'hardware/search/test_search_cost.cpp')==sha(out/'test_search_cost.cpp')
 for name,d in m['artifacts'].items():assert sha(out/name)==d
 assert all(c['exit_code']==0 for c in m['commands']) and '-fsanitize=undefined' in m['commands'][0]['argv'] and '-ffp-contract=off' in m['commands'][0]['argv']
 log=(out/'verify.log').read_text();assert log.strip()==m['result']
 counts=dict((k,int(v)) for k,v in re.findall(r'(\w+)=(\d+)',log));assert counts==dict(cases=262144,nan=741,inf=373,cross=131072,alt=131072,reverse_y=131072,hot=65536)
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'oracle':'Verbatim original getNodeCost/getNodeCostSearch/evaluateCostAndPush, including original integer geometry; helper candidate differs only scalar floating arithmetic. Exact bits including NaN payloads, call label access order, prev and push flags compared. UBSan clean on fixture.','limits':'No HLS FP proof, no exhaustive IEEE coverage. Geometry fixture uses defined bounded integers and valid Laguna columns; original sentinel INT_MAX+detour overflow case not exercised or repaired.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
