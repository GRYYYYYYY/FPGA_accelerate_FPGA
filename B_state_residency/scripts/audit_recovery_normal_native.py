"""Bind NORMAL-gate native regression to original source and exact native events."""
from pathlib import Path
import hashlib, importlib.util, json, re, sys
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p / 'manifest.json').read_text())
assert m['status'] == 'observed' and len(m['commands']) == 3
assert [x['stage'] for x in m['commands']] == ['compile', 'elaborate', 'simulate']
assert all(x['exit_code'] == 0 for x in m['commands'])
for n, h in m['sources'].items():
    assert sha(p / 'sources' / n) == h, n
for n, h in m['artifacts'].items():
    assert sha(p / n) == h, n
assert sha(p / 'runner.py') == m['runner_sha256'] == sha(ROOT / 'scripts/run_recovery_normal_native_v2.py')
ref = Path(m['reference'])
rm = json.loads((ref / 'manifest.json').read_text())
ra = json.loads((ref / 'source_bound_audit.json').read_text())
receipt = ROOT / 'results/rearm_loops_component_v2_restore_20261025.json'
rr = json.loads(receipt.read_text())
assert ra['status'] == rr['status'] == 'passed'
assert ra['manifest_sha256'] == sha(ref / 'manifest.json')
assert sha(ref / 'source_bound_audit.json') == m['reference_audit_sha256'] == rr['audit_sha256']
assert rr['audit_byte_identical'] and sha(receipt) == m['reference_restore_sha256']
builder = ROOT / 'hardware/variants/recovery_normal_loops_v2/build.py'
assert sha(builder) == m['sources']['build.py']
spec = importlib.util.spec_from_file_location('normal_builder', builder)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
assert (ref / 'sources/fixed/recovery_coordinator.sv').read_text() == b.source(False)
assert (p / 'sources/recovery_coordinator.sv').read_text() == b.source(True)
for n in ['label_restore_controller.sv', 'rearm_loop_slice.sv']:
    assert m['sources'][n] == rm['sources']['fixed/' + n]['sha256'] == sha(ref / 'sources/fixed' / n)
assert m['sources']['tb_rearm_loop.sv'] == rm['sources']['tb_rearm_loop.sv']['sha256'] == sha(ref / 'sources/tb_rearm_loop.sv')
proof = json.loads((p / 'sources/identity.json').read_text())
assert m['sources']['identity.json'] == sha(ROOT / 'results/recovery_normal_identity_20261027.json')
assert proof['status'] == 'normal_admission_boolean_identity_not_rtl_validation' and proof['valuations'] == 65536
assert proof['analyzer_sha256'] == sha(ROOT / 'scripts/analyze_recovery_normal_identity.py')
assert proof['source_sha256'] == sha(ref / 'sources/fixed/recovery_coordinator.sv')
log = (p / 'simulate/simulate.log').read_text()
oldlog = (ref / 'fixed/simulate/simulate.log').read_text()
assert 'Fatal:' not in log and '$finish called' in log
marker = 'REARM_LOOP_PASS scenarios=3 successes=3 failures=10 checks=179'
assert marker in log and marker in oldlog
def events(text):
    return [line for line in text.splitlines() if line.startswith(('RESET ', 'WRITE ', 'RESULT '))]
trace, previous = events(log), events(oldlog)
assert trace == previous and len(trace) == 31
finish = re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)', log)
assert finish == re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)', oldlog) == ['3836 ns']
assert len([s for s in trace if s.startswith('WRITE ')]) == 15
assert len([s for s in trace if s.startswith('RESET ')]) == 3
assert len([s for s in trace if s.startswith('RESULT ')]) == 13
result = dict(status='passed', manifest_sha256=sha(p / 'manifest.json'),
    auditor_sha256=sha(Path(__file__)), builder_sha256=sha(builder),
    reference_audit_sha256=sha(ref / 'source_bound_audit.json'), reference_restore_sha256=sha(receipt),
    native_trace_identical=True, trace=trace,
    trace_sha256=hashlib.sha256(('\n'.join(trace)+'\n').encode()).hexdigest(),
    finish_time=finish[0], checks=179, scenarios=3, successful_retries=3,
    failed_or_rejected_results=10, actual_field_writes=15, verified_records=3,
    journal_entries=0, owner_authority_requests=0, boolean_valuations=proof['valuations'],
    scope=m['scope'])
(p / 'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('RECOVERY_NORMAL_NATIVE_AUDITED', len(trace), 'events', finish[0])
