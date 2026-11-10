"""Measure actual native operations inside the independently audited G3 label restore."""
from pathlib import Path
from collections import Counter
import json
from run_checkpoint_authority import ROOT, sha

base = Path('/tmp/B_state_residency_offer_20261025')
cases = {}
for case in ['full', 'pressure']:
    p = base / ('third_warm_' + case + '_v2')
    audit = json.loads((p/'source_bound_audit.json').read_text())
    assert audit['status'] == 'passed' and audit['manifest_sha256'] == sha(p/'manifest.json')
    assert audit['auditor_sha256'] == sha(ROOT/'scripts/audit_third_warm_system.py')
    rows = [line.split() for line in (p/case/'natural_trace.txt').read_text().splitlines()]
    start = next(i for i, t in enumerate(rows) if t[0] == 'THIRD_WARM_OWNER')
    end = next(i for i, t in enumerate(rows) if t[0] == 'THIRD_WARM_LABELS')
    part = rows[start:end]
    counts = Counter(int(t[2]) for t in part if t[0] == 'NB')
    durations = Counter()
    completed = Counter()
    pending = None
    for t in part:
        if t[0] == 'NB':
            assert pending is None
            pending = (int(t[1]), int(t[2]))
        elif t[0] == 'NR':
            assert pending is not None
            cycle, op = pending
            durations[op] += int(t[1]) - cycle
            completed[op] += 1
            pending = None
    assert pending is None and completed == counts
    restore_writes = len([t for t in part if t[0] == 'LL' and t[2] == '1'])
    misses = len([t for t in part if t[0] == 'BM'])
    assert restore_writes == 781*5 and counts[3] == 2*restore_writes and misses == 781
    phase_cycles = int(rows[end][1]) - int(rows[start][1])
    assert phase_cycles == audit['behavioral_cycles']['label_phase']
    cases[case] = dict(audit_sha256=sha(p/'source_bound_audit.json'),
        trace_sha256=sha(p/case/'natural_trace.txt'), label_phase_cycles=phase_cycles,
        fault_to_release_cycles=audit['behavioral_cycles']['fault_to_release'],
        restored_records=781, baseline_misses=misses, recovery_field_writes=restore_writes,
        native_field_writes=counts[3], other_native_field_writes=counts[3]-restore_writes,
        native_operations={str(op): dict(count=counts[op], accepted_to_response_cycles=durations[op]) for op in sorted(counts)},
        non_native_service_cycles=phase_cycles-sum(durations.values()))
result = dict(status='measured', analyzer_sha256=sha(Path(__file__)), cases=cases,
    scope='Behavioral phase-cycle and actual native transaction accounting only. Extra baseline initialization is a candidate for investigation; no optimization, board-time or speedup claim. Native service durations do not attribute the remaining queue/control cycles to a specific module.')
(ROOT/'results/third_warm_phases_20261027.json').write_text(json.dumps(result, indent=2)+'\n')
print('THIRD_WARM_PHASES_MEASURED', {k: v['label_phase_cycles'] for k, v in cases.items()})
