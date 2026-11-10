"""Bind the two full-design observational censuses and their controls."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 controls=BASE/'natural_census_controls_v1/source_bound_audit.json'
 assert json.loads(controls.read_text())['status']=='passed'
 rows=[]
 for dataset,name in [('logicnets_jscl','natural_census_v1'),('vtr_mcml','natural_mcml_census_v1')]:
  p=BASE/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
  assert m['status']==a['status']=='passed'
  assert a['manifest_sha256']==sha(p/'manifest.json')
  assert a['controls_audit_sha256']==sha(controls)
  assert sha(p/'router.result')==m['reference_result_sha256']==m['artifacts']['router.result']
  assert a['source_recovered_byte_identical']
  rows.append(dict(dataset=dataset,root=str(p),manifest_sha256=sha(p/'manifest.json'),audit_sha256=sha(p/'source_bound_audit.json'),binary_sha256=m['artifacts']['router'],totals=a['totals'],max_depth_histogram=a['max_depth_histogram'],state_profiles=a['state_profiles'],first_snapshot_candidate=a['small_real_query_candidates'][0]))
 assert rows[0]['binary_sha256']==rows[1]['binary_sha256']
 out=dict(status='passed',controls_audit_sha256=sha(controls),datasets=rows,totals={k:sum(r['totals'][k] for r in rows) for k in rows[0]['totals']},scope='Full original serial searches, observational census with byte-identical final routes. No natural state snapshots or RTL replay and no speedup measurement.')
 dest=ROOT/'results/natural_recursion_census_20261025.json'
 dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['totals']))
if __name__=='__main__':main()
