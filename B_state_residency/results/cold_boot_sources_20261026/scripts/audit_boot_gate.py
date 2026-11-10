"""Check frozen component sources, command results and assertion completion."""
from pathlib import Path
import sys,json
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
assert [x['stage']for x in m['commands']]==['compile','elaborate','simulate'] and all(x['exit_code']==0 for x in m['commands'])
log=(p/'simulate.stdout.log').read_text();assert 'BOOT_GATE_PASS checks=31'in log and 'Fatal:'not in log
result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'checks':31,'simulation_log_sha256':sha(p/'simulate.stdout.log'),'scope':'Native receipt gate component test with driven provider and transaction signals, distinct from full-system cold restore.'}
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('31 component assertions audited')
