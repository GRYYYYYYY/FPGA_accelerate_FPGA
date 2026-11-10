from pathlib import Path
import json,sys
from audit_authority_query_synth import main as audit_full_system
from run_checkpoint_authority import ROOT,sha

def main():
 audit_full_system();p=Path(sys.argv[1]).resolve();a=json.loads((p/'source_bound_audit.json').read_text());assert a['facts']['directory_observers']==0
 a['parent_auditor_sha256']=sha(ROOT/'scripts/audit_authority_query_synth.py');a['auditor_sha256']=sha(Path(__file__));a['observer_excluded']=True;(p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n')
if __name__=='__main__':main()
