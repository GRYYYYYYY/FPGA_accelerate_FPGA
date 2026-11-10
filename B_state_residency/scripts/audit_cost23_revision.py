from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inputs=ROOT/'results/cost23_inputs_20261025';im=json.loads((inputs/'manifest.json').read_text());ig=json.loads((inputs/'source_bound_audit.json').read_text());assert im['status']==ig['status']=='passed' and ig['manifest_sha256']==sha(inputs/'manifest.json') and ig['auditor_sha256']==sha(ROOT/'scripts/audit_cost23_inputs.py')
 records={};counts={};modules=None
 for name in ['candidate_cost23_pilot_20261025','candidate_cost23_full_20261025']:
  p=ROOT/'results'/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json') and a['auditor_sha256']==sha(ROOT/'scripts/audit_candidate_cost23.py')
  assert a['cost_input_auditor_sha256']==ig['auditor_sha256'] and a['trace_auditor_sha256']==sha(ROOT/'scripts/audit_postprev_trace.py')
  assert a['params_derive_sha256']==sha(ROOT/'hardware/variants/candidate_cost23_v1/derive_top.py') and a['cost_core_derive_sha256']==sha(ROOT/'hardware/variants/candidate_cost23_v1/derive_core.py')
  current={Path(n).name:item['sha256']for n,item in m['sources'].items()if Path(n).suffix in ['.v','.sv','.dat'] and not Path(n).name.startswith('tb_')}
  if modules is None:modules=current
  else:assert modules==current
  records[name]={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')};counts[name]=a['counts']
 for c in counts['candidate_cost23_full_20261025'].values():
  assert c['expansions']==c['params_expansions']==1216 and c['decisions']==3063 and c['actual_cost23_calls']==c['actual_geometry_calls']==713 and c['cost23_input_words_bitexact']==16399 and c['cost23_output_words_bitexact']==3565
  assert c['ordered_prefixes']==713 and c['nonempty_clear_before_prev']==66 and c['fresh_SLL_label_reads']==12 and c['all_label_backing_bytes_checked']==3145728
 p=ROOT/'results/cost23_branches_20261025';bm=json.loads((p/'manifest.json').read_text());ba=json.loads((p/'source_bound_audit.json').read_text());assert bm['status']==ba['status']=='passed' and ba['manifest_sha256']==sha(p/'manifest.json') and ba['auditor_sha256']==sha(ROOT/'scripts/audit_cost23_branches.py') and ba['cases']==5
 for n,h in bm['sources'].items():
  if not n.startswith('tb_'):assert h==modules[n]
 records['cost23_branches_20261025']={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')}
 r={'status':'passed','auditor_sha256':sha(Path(__file__)),'input_manifest_sha256':sha(inputs/'manifest.json'),'input_audit_sha256':sha(inputs/'source_bound_audit.json'),'gates':records,'identical_RTL_and_data_modules':len(modules),'counts':counts,'branch_gate':ba,'scope':'Actual internal cost23 production and original CPU bitexact5-word arithmetic on previous scripted real-graph prefix replay. Separate mocked-coordinate crossSLR/version/unsupported-profile gate. Cost label commits, OFFER/recursive search, actual landmark data, joined recovery, joint synthesis/platform/board remain unfinished.'}
 (ROOT/'results/cost23_revision_20261025.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
