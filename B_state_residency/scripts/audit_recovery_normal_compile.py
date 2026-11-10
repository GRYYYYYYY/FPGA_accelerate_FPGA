"""Preserve a source declaration-order compilation failure, not a runtime result."""
from pathlib import Path
import json, sys
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p / 'manifest.json').read_text())
assert m['status'] == 'failed' and len(m['commands']) == 1
c = m['commands'][0]
assert c['stage'] == 'compile' and c['exit_code'] != 0
for n, h in m['sources'].items():
    assert sha(p / 'sources' / n) == h
for n, h in m['artifacts'].items():
    assert sha(p / n) == h
assert sha(p / 'runner.py') == m['runner_sha256']
log = (p / 'simulate/compile.stdout.log').read_text()
assert "ERROR: [VRFC 10-3380] identifier 'timeout' is used before its declaration" in log
assert not (p / 'simulate/simulate.log').exists()
source = (p / 'sources/recovery_coordinator.sv').read_text()
assert source.index('wire normal_fault=') < source.index('wire timeout=')
variant = ROOT / 'hardware/variants/recovery_normal_loops_v1'
assert sha(variant / 'fixed/recovery_coordinator.sv') == m['sources']['recovery_coordinator.sv']
assert sha(variant / 'build.py') == m['sources']['build.py']
ref = Path(m['reference'])
ra = json.loads((ref / 'source_bound_audit.json').read_text())
assert ra['status'] == 'passed' and ra['manifest_sha256'] == sha(ref / 'manifest.json')
assert sha(ref / 'source_bound_audit.json') == m['reference_audit_sha256']
for n in ['label_restore_controller.sv', 'rearm_loop_slice.sv']:
    assert sha(ref / 'sources/fixed' / n) == m['sources'][n]
assert sha(ref / 'sources/tb_rearm_loop.sv') == m['sources']['tb_rearm_loop.sv']
result = dict(status='passed', manifest_sha256=sha(p / 'manifest.json'),
    auditor_sha256=sha(Path(__file__)), audit_kind='source-bound compile-failure evidence only',
    error_code='VRFC 10-3380', simulated=False,
    scope='Initial candidate referenced timeout before its declaration; no elaboration or runtime occurred. This audit does not accept the candidate RTL or establish a protocol counterexample.')
(p / 'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('RECOVERY_NORMAL_COMPILE_FAILURE_PRESERVED')
