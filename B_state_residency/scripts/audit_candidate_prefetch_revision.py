"""Join only explicitly completed cases; do not relabel an interrupted batch PASS."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 full=ROOT/'results/candidate_prefetch_full_20261025';pressure=ROOT/'results/candidate_prefetch_pressure_20261025';unit=ROOT/'results/cost_inputs_prefetch_boundaries_v2_20261025'
 paths=[full/'completed_full_audit.json',pressure/'source_bound_audit.json',unit/'source_bound_audit.json'];gates=[]
 for p in paths:
  a=json.loads(p.read_text());assert a['status']=='passed' and a['manifest_sha256']==sha(p.parent/'manifest.json');gates.append(a)
 assert gates[0]['selected_completed_case']=='full' and gates[1]['selected_completed_case'] is None
 fm=json.loads((full/'manifest.json').read_text());pm=json.loads((pressure/'manifest.json').read_text());assert fm['status']=='failed' and fm['cases']['full']['status']=='passed' and pm['status']=='passed'
 assert 'Disk quota exceeded' in fm['error']
 left={Path(n).name:s['sha256'] for n,s in fm['sources'].items() if n!='runner.py'}
 right={Path(n).name:s['sha256'] for n,s in pm['sources'].items() if n!='runner.py'}
 assert left==right and left['cost_inputs_prefetch.sv']==gates[2]['controller_sha256']
 for a,case in [(gates[0],'full'),(gates[1],'pressure')]:
  c=a['counts'][case];assert (c['expansions'],c['decisions'],c['early'],c['prefetch_calls'])==(1212,3022,60,785)
 result={'status':'passed','auditor_sha256':sha(Path(__file__)),'gates':{str(p):sha(p) for p in paths},'same_sources_excluding_runner':len(left),
 'scope':'Explicit completed full case + separately completed single-slot pressure case + standalone selector boundaries; interrupted original batch remains failed.',
 'real_prefetch_coverage':'785 allowed candidates per case, all actual occupancy0/refs0/index0; history and net data from real AXI backing. Nonzero occupancy/reference boundaries are standalone mocks, not live occupied candidate proof.',
 'not_verified':['Post-prev geometry and actual center operand binding','Full cost23 input production and label commit','Joined failure drain/recovery','Default directory and new synthesis/platform/board']}
 out=Path(sys.argv[1]);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
