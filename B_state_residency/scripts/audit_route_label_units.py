"""Independent source, event, compatibility and explicit overlap checks."""
from pathlib import Path
import importlib.util
import json
import re
import sys
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p/'manifest.json').read_text())
assert m['status'] == 'observed'
for name, digest in m['bound'].items():
    assert sha(ROOT/name) == sha(p/'tools'/name) == digest
assert sha(p/'labels.txt') == m['labels_sha256']
v = ROOT/'hardware/variants/route_label_exclusion_v1'
vm = json.loads((v/'manifest.json').read_text())
spec = importlib.util.spec_from_file_location('route_label_tb', v/'build_tb.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
expected = [(mode, suite) for mode in ['baseline', 'default', 'exclusive']
            for suite in ['route', 'checkpoint', 'native_checkpoint', 'generic_overlap']]
assert [(c['mode'], c['suite']) for c in m['cases']] == expected
results = {}
for c in m['cases']:
    mode, suite = c['mode'], c['suite']
    name = f'{mode}_{suite}'
    d = p/name
    assert c['status'] == 'passed'
    assert sha(d/'route_commit_controller.sv') == c['rtl_sha256'] == vm['sources']['route_commit_controller.sv']['baseline' if mode == 'baseline' else 'fixed']
    tb, marker = b.build(ROOT, mode, suite)
    assert (d/'tb.sv').read_text() == tb and sha(d/'tb.sv') == c['tb_sha256']
    assert not re.search(r'\b(force|release)\s', tb)
    assert [x['stage'] for x in c['commands']] == ['compile', 'elaborate', 'simulate']
    for command in c['commands']:
        assert command['exit_code'] == 0
        assert sha(d/(command['stage']+'.stdout.log')) == command['log_sha256']
    log = (d/'simulate.log').read_text()
    assert sha(d/'simulate.log') == c['simulate_log_sha256']
    assert marker in log and 'Fatal:' not in log and 'ERROR:' not in log
    finish = re.findall(r'\$finish called at time : ([0-9.]+ [a-z]+)', log)
    assert len(finish) == 1
    trace = (d/'events.txt').read_text()
    assert sha(d/'events.txt') == c['trace_sha256']
    lines = [line.split() for line in trace.splitlines()]
    result = dict(trace_sha256=sha(d/'events.txt'), finish_time=finish[0])
    if suite == 'generic_overlap':
        value = 1 if mode == 'exclusive' else 0
        assert lines == [['OVERLAP', '1', str(value), str(value)]]
        assert f'ROUTE_LABEL_OVERLAP_PASS specialized={value} unexpected={value}' in log
        result['unexpected'] = value
    else:
        route = [line for line in lines if line[0] == 'R']
        want = 25 if suite == 'route' else 31
        assert len(route) == want
        if suite == 'route':
            assert re.findall(r'ROUTE_COMMIT_PASS checks=(\d+)', log) == ['25']
        else:
            assert re.findall(r'ROUTE_CHECKPOINT_PASS checks=(\d+) cp=(\d+)', log) == [('31', '27')]
            assert len([line for line in lines if line[0] == 'CPR']) == 27
        if suite == 'native_checkpoint':
            coverage = [line for line in lines if line[0] == 'NATIVE_LABEL']
            assert len(coverage) == 1
            requests, replies = map(int, coverage[0][1:])
            assert requests == replies and requests > 0
            result['native_label'] = dict(requests=requests, replies=replies)
        result['route_checks'] = want
    results[name] = result
for suite in ['route', 'checkpoint', 'native_checkpoint', 'generic_overlap']:
    assert results[f'baseline_{suite}'] == results[f'default_{suite}']
    if suite != 'generic_overlap':
        assert results[f'baseline_{suite}'] == results[f'exclusive_{suite}']
result = dict(status='passed', manifest_sha256=sha(p/'manifest.json'),
              auditor_sha256=sha(Path(__file__)), cases=results, exact_trace_comparisons=7,
              generic_overlap_specialization_counterexample=True,
              scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print('ROUTE_LABEL_UNITS_AUDITED', len(results), 'cases, seven exact comparisons')
