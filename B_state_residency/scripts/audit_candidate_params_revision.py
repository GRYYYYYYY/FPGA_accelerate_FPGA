from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inp=ROOT/'results/connection_state_inputs_20261025';im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text())
 assert ig['status']=='passed' and ig['manifest_sha256']==sha(inp/'manifest.json') and im['artifacts']['connections.bin']==sha(inp/'connections.bin')
 gates={};counts={};modules=None
 for name in ['candidate_params_pilot_20261025','candidate_params_full_20261025','candidate_params_delay_20261025']:
  p=ROOT/'results'/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
  assert m['status']==a['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json') and a['auditor_sha256']==sha(ROOT/'scripts/audit_candidate_params.py')
  assert a['trace_auditor_sha256']==sha(ROOT/'scripts/audit_postprev_trace.py') and a['params_derive_sha256']==sha(ROOT/'hardware/variants/candidate_params_v1/derive_top.py')
  current={Path(n).name:x['sha256']for n,x in m['sources'].items()if Path(n).suffix in ['.v','.sv','.dat'] and not Path(n).name.startswith('tb_')}
  if modules is None:modules=current
  else:assert modules==current
  gates[name]={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')};counts[name]=a['counts']
 for c in counts['candidate_params_full_20261025'].values():
  assert c['params_expansions']==c['expansions']==1216 and c['decisions']==3063 and c['params_AXI_R_words_checked']==19456
  assert c['ordered_prefixes']==713 and c['nonempty_clear_before_prev']==66 and c['fresh_SLL_label_reads']==12 and c['all_label_backing_bytes_checked']==3145728
 d=counts['candidate_params_delay_20261025']['pilot'];assert len(d['delayed_wait_cycles_skip_allow_empty'])==3 and all(x>0 for x in d['delayed_wait_cycles_skip_allow_empty'])
 result={'status':'passed','auditor_sha256':sha(Path(__file__)),'input_gate_sha256':sha(inp/'source_bound_audit.json'),'input_table_sha256':sha(inp/'connections.bin'),'gates':gates,'identical_RTL_and_data_modules':len(modules),'counts':counts,'scope':'Actual immutable initial State parameters joined once per expansion; complete/one-slot and deliberately delayed-AXI functional gates. Cost23 arithmetic/label commits/recursive search and joined fault/reload/synthesis/platform/board remain unfinished. No speedup claim.'}
 (ROOT/'results/candidate_params_revision_20261025.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
