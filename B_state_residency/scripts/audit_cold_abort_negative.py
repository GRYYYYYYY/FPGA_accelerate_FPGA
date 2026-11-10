"""Preserve the expected pre-fix full-system held-completion counterexample."""
from pathlib import Path
import sys,json
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();fixed=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
old=(p/'sources/query_residency_system.sv').read_text();new=(fixed/'sources/query_residency_system.sv').read_text();assert old.count('.work_rst(rst),')==1 and old.replace('.work_rst(rst),','.work_rst(rst||abort),')==new
assert sha(p/'sources/tb_cold_boot.sv')==sha(fixed/'sources/tb_cold_boot.sv')
log=(p/'full/simulate.log').read_text();assert log.count('Fatal:')==1 and 'Fatal: abort did not mask held boot completion'in log and 'COLD_BOOT_PASS'not in log
ts=[l.split()for l in(p/'full/natural_trace.txt').read_text().splitlines()];stages=[t for t in ts if t[0]=='BOOT_STAGE'];assert [t[1]for t in stages]==['labels_written','labels_verified','imports']and stages[-1][3]=='1f'
cp=[t for t in ts if t[0]=='QCP'];assert len(cp)==1 and cp[0][2]=='0'
r={'status':'passed','meaning':'Expected pre-fix failure reproduced, not a successful restore run.','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'fixed_run':str(fixed),'fixed_manifest_sha256':sha(fixed/'manifest.json'),'testbench_sha256':sha(p/'sources/tb_cold_boot.sv'),'failure':'abort did not mask held boot completion','native_receipts_before_abort':'1f','scope':'One-line root connection is the sole RTL difference; same full-system stimulus reaches the held successful boot reply.'}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('expected pre-fix failure audited')
