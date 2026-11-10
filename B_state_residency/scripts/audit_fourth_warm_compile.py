"""Preserve a TB declaration-order compilation failure, not an RTL counterexample."""
from pathlib import Path
import json,runpy,sys
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='failed'and list(m['cases'])==['full']
commands=m['cases']['full']['commands'];assert len(commands)==1 and commands[0]['stage']=='compile'and commands[0]['exit_code']!=0
base=Path(m['parent_run']);bm=json.loads((base/'manifest.json').read_text())
assert sha(base/'source_bound_audit.json')==m['parent_audit_sha256']
for n,e in m['sources'].items():
 assert sha(p/'sources'/n)==e['sha256'],n
 if n not in ['runner.py','tb_query_fault.sv','fourth_warm_build.py','floor_probe.sv']:assert e['sha256']==bm['sources'][n]['sha256'],n
s=(p/'sources/tb_query_fault.sv').read_text()
assert s.index('g4_saved_path[x]=')<s.index('reg[31:0]g4_saved_path')
assert runpy.run_path(str(p/'sources/fourth_warm_build.py'))['make']()==s
log=(p/'full/compile.stdout.log').read_text()
assert "ERROR: [VRFC 10-3380] identifier 'g4_saved_path' is used before its declaration"in log
assert not(p/'full/natural_trace.txt').exists()and not(p/'full/simulate.log').exists()
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),compile_failure=True,
 reason='TB saved-state array declared after use under default_nettype none; no simulation ran',production_rtl_matches=base.name,
 scope='Compilation failure provenance only. No behavioral correctness or production RTL defect conclusion.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FOURTH_WARM_COMPILE_FAILURE_AUDITED')
