"""Verify both frozen C++ frontier implementations and source lineage."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from build_frontier_reference import generate

def main():
 out=ROOT/'results/frontier_cpp_verified_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 assert sha(ROOT/'scripts/verify_frontier_cpp.py')==m['runner_sha256']
 assert sha(ROOT/'adapters/build_frontier_reference.py')==m['reference_generator_sha256']
 for name,digest in m['sources'].items():assert sha(out/name)==digest
 golden=generate((ROOT/'results/frontier_real_20261024/original_trace.cpp').read_text())
 assert (out/'frame_based/frontier_reference.hpp').read_text()==golden==(out/'rearchitect/v1/tb/frontier_reference.hpp').read_text()
 assert (out/'frame_based/testbench.cpp').read_bytes()==(out/'rearchitect/v1/tb/testbench.cpp').read_bytes()
 for case in ['reference','candidate']:
  row=m['cases'][case];assert row['status']=='passed' and all(s['exit_code']==0 for s in row['commands'])
  assert [s['stage'] for s in row['commands']]==['build','verify']
  assert sha(out/(case+'_test'))==row['binary_sha256']
  assert sha(out/(case+'.log'))==row['log_sha256']
  assert 'FRONTIER_TEST_PASS capacity=65536 checks=135228 comparisons=1000169' in (out/(case+'.log')).read_text()
 component=ROOT/'hardware/hls/frontier/rearchitect/v1/src'
 for name in ['kernel_hls.cpp','frontier_api.hpp','frontier_bounded.hpp']:assert sha(component/name)==sha(out/'rearchitect/v1/src'/name)
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'capacity':65536,'command_checks_per_implementation':135228,'comparator_pairs_per_implementation':1000169,'helper_sha256':sha(component/'frontier_bounded.hpp'),'scope':'Independent native-float golden vs fixed-capacity integer-bit HLS-ready C++ behavior; RTL proof still separate.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
