from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inp=ROOT/'results/commit_inputs_20261025';im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());assert im['status']==ig['status']=='passed' and ig['manifest_sha256']==sha(inp/'manifest.json') and ig['auditor_sha256']==sha(ROOT/'scripts/audit_commit_inputs.py')
 assert ig['packets']==702 and ig['visited_reuse_skips_from_prior_commits']==13 and ig['parent_upstream_from_prior_commits']==12 and ig['final_nonzero_label_records']==436
 modules=None;records={};counts={}
 for name in ['candidate_commit_pilot_20261025','candidate_commit_full_20261025']:
  p=ROOT/'results'/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json') and a['auditor_sha256']==sha(ROOT/'scripts/audit_candidate_commit_v2.py')
  assert a['trace_auditor_sha256']==sha(ROOT/'scripts/audit_commit_trace.py') and a['cost_input_auditor_sha256']==ig['auditor_sha256'] and a['params_derive_sha256']==sha(ROOT/'hardware/variants/candidate_commit_v2/derive_top.py') and a['cost_core_derive_sha256']==sha(ROOT/'hardware/variants/candidate_commit_v1/derive_core.py')
  current={Path(n).name:item['sha256']for n,item in m['sources'].items()if Path(n).suffix in ['.v','.sv','.dat'] and not Path(n).name.startswith('tb_')}
  if modules is None:modules=current
  else:assert modules==current
  records[name]={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')};counts[name]=a['counts']
 for c in counts['candidate_commit_full_20261025'].values():
  assert c['expansions']==c['params_expansions']==1216 and c['decisions']==3066 and c['early']==65
  assert c['actual_cost23_calls']==c['cost_label_commits']==c['actual_geometry_calls']==702 and c['cost23_input_words_bitexact']==16146 and c['cost23_output_words_bitexact']==3510 and c['ordered_label_ACKs']==2106
  assert c['final_label_records_read_after_checkpoint']==436 and c['final_label_words_checked']==2180 and c['all_label_backing_bytes_checked']==3145728 and c['fresh_SLL_label_reads']==12
 p=ROOT/'results/cost_label_commit_unit_20261025';um=json.loads((p/'manifest.json').read_text());ua=json.loads((p/'source_bound_audit.json').read_text());assert um['status']==ua['status']=='passed' and ua['manifest_sha256']==sha(p/'manifest.json') and ua['auditor_sha256']==sha(ROOT/'scripts/audit_cost_label_commit.py') and ua['cases']==13
 assert um['sources']['cost_label_commit.sv']['sha256']==modules['cost_label_commit.sv']
 records['cost_label_commit_unit_20261025']={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')}
 p=ROOT/'results/commit_bad_cost_guard_20261025';gm=json.loads((p/'manifest.json').read_text());ga=json.loads((p/'source_bound_audit.json').read_text());assert gm['status']==ga['status']=='passed' and ga['manifest_sha256']==sha(p/'manifest.json') and ga['auditor_sha256']==sha(ROOT/'scripts/audit_commit_bad_cost.py') and ga['cases']==2 and ga['cost_label_requests_accepted']==0
 for n,h in gm['sources'].items():
  if Path(n).suffix in ['.v','.sv','.dat'] and not Path(n).name.startswith('tb_'):assert h==modules[Path(n).name]
 records['commit_bad_cost_guard_20261025']={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')}
 r={'status':'passed','auditor_sha256':sha(Path(__file__)),'input_manifest_sha256':sha(inp/'manifest.json'),'input_audit_sha256':sha(inp/'source_bound_audit.json'),'gates':records,'identical_RTL_and_data_modules':len(modules),'counts':counts,'component_boundaries':ua,'bad_cost_guard':ga,'scope':'Stateful cost-label commit and changed CPU decisions; complete/single-slot actual native/AXI regression with final post-checkpoint label readback. Separate mocked-native partial commit/drain/identity failure cases. No cost OFFER, immediate recursive scheduler, full route, combined nonzero-owner, actual landmark/crossSLR joined, coordinated recovery, joint synthesis/platform/board proof.'}
 (ROOT/'results/commit_revision_20261025.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
