"""Resolve dependency source hashes through audited manifests where sources are indirect."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items=[('ka_lease_temporal_boundary_v1_review_20261101.json','ka_as_lease_staging_boundary_formal_v1'),('ka_publication_discard_lease_unit_v1_review_20261101.json',None),('ka_ap_ownership_busy_formal_v1_review_20261031.json','ka_ap_ownership_busy_formal_v2'),('ka_as_no_ap_owned_formal_v1_review_20261031.json','ka_as_no_ap_owned_formal_v1')];rows=[]
for name,root in items:
 report=R/'results'/name;d=json.loads(report.read_text());matches={}
 for src in ['query_residency_system.sv','recovery_coordinator.sv','checkpoint_publish_barrier.sv']:
  hashes={h for f,h in d['file_sha256'].items() if f.endswith('/'+src)}
  if hashes:assert hashes=={sha(S/src)};matches[src]=next(iter(hashes))
 if root:
  path=B/root/'manifest.json';assert sha(path)==d['file_sha256'][root+'/manifest.json'];m=json.loads(path.read_text());assert m['status']=='observed'
  for src,e in m['sources'].items():assert sha(Path(e['source']))==e['sha256']
  matches.update({src:e['sha256'] for src,e in m['sources'].items()})
 assert matches['query_residency_system.sv']==sha(S/'query_residency_system.sv')
 rows.append({'report':name,'sha256':sha(report),'source_sha256':matches,'accepted_manifest':root})
out=R/'results/ka_as_history_phase_exclusion_source_binding_supplement_20261101.json';assert not out.exists();out.write_text(json.dumps({'status':'phase_review_dependency_source_hashes_match_actual_full_sources','dependencies':rows,'initial_review_note':'An initial direct-file suffix lookup rejected the AP review because sources are bound through its audited manifest; this reviewer resolves and checks the accepted v2 manifest instead. No proof or source was changed.','reviewer_sha256':sha(Path(__file__)),'phase_review_sha256':sha(R/'results/ka_as_history_phase_exclusion_review_20261101.json'),'full_system_functional_netlist_validated':False,'physical_gate_open':False},indent=2)+'\n');print('Verified four dependencies against actual source hashes')
