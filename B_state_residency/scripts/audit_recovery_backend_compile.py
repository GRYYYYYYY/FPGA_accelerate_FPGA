"""Preserve the monitor declaration-order failure without claiming RTL execution."""
from pathlib import Path
import json,sys
from run_checkpoint_authority import ROOT,sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='failed' and len(m['cases'])==1
case=next(iter(m['cases']));c=m['cases'][case];d=p/case
assert len(c['commands'])==1 and c['commands'][0]['stage']=='compile'and c['commands'][0]['exit_code']!=0
for n,e in m['sources'].items():assert sha(p/'sources'/n)==e['sha256'],n
assert sha(p/'sources/runner.py')==sha(ROOT/'scripts/run_recovery_backend_system.py')
v=ROOT/'hardware/variants/recovery_backend_loops_v1'
assert sha(v/'build.py')==m['recovery_backend_evidence']['builder_sha256']
for n,h in m['recovery_backend_evidence']['candidate_sha256'].items():assert sha(v/'fixed'/n)==sha(p/'sources'/n)==h
assert sha(v/'tb_query_fault.sv')==sha(p/'sources/tb_query_fault.sv')
log=(d/'compile.stdout.log').read_text()
assert "ERROR: [VRFC 10-3380] identifier 'exclusive_checks' is used before its declaration"in log
assert not(d/'simulate.log').exists()and not(d/'elaborate.stdout.log').exists()
s=(p/'sources/tb_query_fault.sv').read_text()
assert s.index('if(exclusive_checks==0')<s.index('integer exclusive_checks=0')
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    compile_log_sha256=sha(d/'compile.stdout.log'),audit_kind='source-bound compile-failure evidence only',
    simulated=False,error='VRFC 10-3380',scope='Verification counter declaration after first use. No elaboration or simulation; not a DUT protocol counterexample. V2 moves only TB declarations.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print('RECOVERY_BACKEND_COMPILE_FAILURE_PRESERVED')
