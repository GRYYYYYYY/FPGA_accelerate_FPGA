"""Independent source, event, compatibility and explicit overlap checks."""
from pathlib import Path
import importlib.util
import json
import re
import sys
from run_checkpoint_authority import ROOT, sha
from host_edit_system_common_v1 import BASE,identity

p = Path(sys.argv[1]).resolve()
m = json.loads((p/'manifest.json').read_text())
assert p==BASE/'stage_static_cp_units_v2'
assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_units_v2.py')
for name, entry in m['bound'].items():
    assert sha(entry['source']) == sha(p/name) == entry['sha256']
assert sha(p/'labels.txt') == m['labels_sha256']
v = ROOT/'hardware/variants/stage_static_cp_v1'
vm = json.loads((v/'manifest.json').read_text())
spec = importlib.util.spec_from_file_location('route_label_tb', ROOT/'hardware/variants/stage_static_cp_units_v1/build_tb.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
expected = [(mode, suite) for mode in ['baseline', 'default', 'factored']
            for suite in ['route', 'checkpoint', 'checkpoint32', 'generic_overlap']]
assert [(c['mode'], c['suite']) for c in m['cases']] == expected
results = {}
for c in m['cases']:
    mode, suite = c['mode'], c['suite']
    name = f'{mode}_{suite}'
    d = p/name
    assert c['status'] == 'passed'
    assert sha(d/'route_commit_controller.sv') == c['rtl_sha256'] == vm['baseline_sha256' if mode == 'baseline' else 'fixed_sha256']
    tb, marker = b.build(ROOT, mode, suite)
    assert (d/'tb.sv').read_text() == tb and sha(d/'tb.sv') == c['tb_sha256']
    assert not re.search(r'\b(force|release)\s', tb)
    assert [x['stage'] for x in c['commands']] == ['compile', 'elaborate', 'simulate']
    for command in c['commands']:
        assert command['exit_code'] == 0
        assert sha(d/(command['stage']+'.stdout.log')) == command['log_sha256']
    assert '--O0' in c['commands'][1]['argv']
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
        value = 0
        assert lines == [['OVERLAP', '1', str(value), str(value)]]
        assert f'ROUTE_STAGE_OVERLAP_PASS specialized={value} unexpected={value}' in log
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
        result['route_checks'] = want
    bank_path=d/'bank_events.txt'
    assert sha(bank_path)==c['bank_trace_sha256']
    bank=[line.split()for line in bank_path.read_text().splitlines()]
    capacity=32 if suite=='checkpoint32'else 8
    previous={};last_cycle=0;known=0
    for line in bank:
        assert len(line)==5 and line[0]=='BANK'
        cycle,slot,word=map(int,line[1:4]);value=line[4].lower()
        assert cycle>=last_cycle and 0<=slot<2 and 0<=word<capacity
        assert re.fullmatch(r'[0-9a-fxz]{8}',value)
        key=(slot,word)
        assert key not in previous or previous[key]!=value
        previous[key]=value;last_cycle=cycle
        known+=int(not re.search('[xz]',value))
    assert len(previous)==2*capacity
    if suite!='generic_overlap':assert known>0
    result.update(bank_trace_sha256=sha(bank_path),bank_events=len(bank),known_bank_events=known)
    stage_path=d/'stage_events.txt'
    assert sha(stage_path)==c['stage_trace_sha256']
    rows=[line.split() for line in stage_path.read_text().splitlines()]
    seen={};last_cycle=0;known=0
    for row in rows:
        assert len(row)==4 and row[0]=='STAGE'
        cycle,word=map(int,row[1:3]);value=row[3].lower()
        assert cycle>=last_cycle and 0<=word<2*(capacity+7)
        assert re.fullmatch(r'[0-9a-fxz]{8}',value)
        assert word not in seen or seen[word]!=value
        seen[word]=value;last_cycle=cycle
        known+=int(not re.search('[xz]',value))
    assert len(seen)==2*(capacity+7)
    coverage=re.findall(r'ROUTE_STAGE_BANK_PASS checked=(\d+) captures=(\d+) imports=(\d+)',log)
    assert len(coverage)==1
    checked,captures,imports=map(int,coverage[0]);assert checked>0
    if suite in ['checkpoint','checkpoint32']:
        assert known>0 and captures>0 and imports>0
    else:
        assert known==captures==imports==0
    result.update(stage_trace_sha256=sha(stage_path),stage_events=len(rows),known_stage_events=known,
                  stage_checked_cycles=checked,stage_captures=captures,stage_imports=imports)
    results[name] = result
for suite in ['route', 'checkpoint', 'checkpoint32', 'generic_overlap']:
    assert results[f'baseline_{suite}'] == results[f'default_{suite}']
    assert results[f'baseline_{suite}'] == results[f'factored_{suite}']
result = dict(status='passed', manifest_sha256=sha(p/'manifest.json'),
              auditor_sha256=sha(Path(__file__)), cases=results, exact_trace_comparisons=8,
              generic_overlap_preserved=True,
              scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print('ROUTE_STAGE_UNITS_AUDITED', len(results), 'cases, eight exact comparisons including full bank events')
