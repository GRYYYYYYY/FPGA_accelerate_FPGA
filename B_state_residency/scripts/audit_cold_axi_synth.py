from pathlib import Path
import json,sys,re
from collections import Counter
from audit_authority_query_synth import main as full_audit
from run_checkpoint_authority import ROOT,sha

def main():
 full_audit();p=Path(sys.argv[1]).resolve();a=json.loads((p/'source_bound_audit.json').read_text());assert a['facts']['directory_observers']==0
 log=(p/'vivado.log').read_text();a['warnings']=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M)))
 gate_warnings=[l for l in log.splitlines()if l.startswith('WARNING: [Synth 8-7129]')and 'in module boot_restore_gate 'in l]
 assert len(gate_warnings)==6*2432+2432+(2432-36)==19420 and all(re.search(r'Port sp\[[0-9]+\]',l)for l in gate_warnings)
 a['gate_unused_sp_warnings']=len(gate_warnings)
 net=(p/'synth.v').read_text();assert 'module boot_restore_gate'in net and 'host_reply_owned_reg'in net
 a['boot_gate_and_host_ownership_retained']=True
 a['parent_auditor_sha256']=sha(ROOT/'scripts/audit_authority_query_synth.py');a['auditor_sha256']=sha(Path(__file__));a['observer_excluded']=True
 ref=Path(sys.argv[2]).resolve();assert sha(p/'sources/query_residency_system.sv')==sha(ref/'sources/query_residency_system.sv')and sha(p/'sources/boot_restore_gate.sv')==sha(ref/'sources/boot_restore_gate.sv')
 (p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n')
if __name__=='__main__':main()
