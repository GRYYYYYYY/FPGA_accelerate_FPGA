from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 groups=['candidate_cost_state_full_20261025','candidate_cost_updates_20261025','candidate_cost_default_20261025'];gates={};common=None;reference=None
 for name in groups:
  p=ROOT/'results'/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json')
  current={n:s['sha256']for n,s in m['sources'].items()if n.endswith(('.sv','.v'))and not Path(n).name.startswith('tb_')}
  for n,d in current.items():assert sha(p/'sources'/n)==d
  if reference is None:reference=current
  else:assert reference==current
  gates[name]={'manifest_sha256':sha(p/'manifest.json'),'audit_sha256':sha(p/'source_bound_audit.json')}
 assert len(reference)==55 # Includes the shared AXI file-memory model.
 rtl={n:d for n,d in reference.items()if Path(n).name!='axi_file_memory.sv'};assert len(rtl)==54
 result={'status':'passed','gates':gates,'rtl_sha256':rtl,'shared_rtl_files_including_model':55,'synthesis_rtl_files':54,'controller_sha256':rtl['candidate/candidate_controller.sv'],'scope':'Same tested candidate-cost-state RTL across normal/pressure/default function and selected update/identity/AXI boundary cases; no joined synthesis, in-session fault recovery or cost-packet/arithmetic/search proof.'}
 target=Path(sys.argv[1]).resolve();assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rtl_sha256'},indent=2))
if __name__=='__main__':main()
