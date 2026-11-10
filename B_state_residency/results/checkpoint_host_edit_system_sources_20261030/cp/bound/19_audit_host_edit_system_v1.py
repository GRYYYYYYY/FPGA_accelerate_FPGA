"""Independently audit the full run, raw host-edit suffix and paired outputs."""
from pathlib import Path
from decimal import Decimal
import json
import re
import sys
from host_edit_system_common_v1 import (ROOT, BASE, REFERENCE, TARGETS, CHANGED,
    sha, read, identity, predecessors, sources, restored)
from check_host_edit_trace_v1 import check


def audit(p):
    m = read(p/'manifest.json'); mode = m['mode']; assert p == TARGETS[mode]
    assert m['status'] == 'observed' and m['stage'] == 'complete' and not m.get('active_process')
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert m['runtime'] == dict(LD_PRELOAD=None, simulator='XSim 2022.2')
    assert m['predecessors'] == predecessors(mode)
    rm, ra, tb, original, _ = sources()
    assert m['host_edit_original'] == str(REFERENCE)
    assert m['runner_sha256'] == sha(ROOT/'scripts/run_host_edit_system_v1.py')
    assert list(m['cases']) == ['pressure'] and m['cases']['pressure']['status'] == 'observed'
    assert m['rtl'] == rm['rtl'] and set(m['sources']) == set(rm['sources'])
    assert m['binding_sha256'] == rm['binding_sha256'] == sha(m['binding'])
    for name, entry in m['bound'].items():
        assert sha(p/'bound'/name) == entry['sha256'] == sha(entry['source']), name
    bound_sources = {entry['source'] for entry in m['bound'].values()}
    for name in ['host_edit_system_common_v1.py','run_host_edit_system_v1.py',
                 'audit_host_edit_system_v1.py','freeze_host_edit_system_v1.py','check_host_edit_trace_v1.py']:
        assert str(ROOT/'scripts'/name) in bound_sources
    for n, entry in m['sources'].items():
        assert sha(p/'sources'/n) == entry['sha256'], n
        if n == 'tb_query_fault.sv':
            assert entry['sha256'] == sha(tb)
        elif n == 'runner.py':
            assert entry['sha256'] == sha(ROOT/'scripts/run_host_edit_system_v1.py')
        elif mode == 'baseline' and n in CHANGED:
            assert entry['sha256'] == original['baseline']['sources'][n]
        else:
            assert entry['sha256'] == rm['sources'][n]['sha256'], n
    assert len(original[mode]['rtl']) == 133
    for n in original[mode]['rtl']:
        assert sha(p/'sources'/n) == original[mode]['sources'][n]
    for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
        assert m[key] == rm[key]
        for n, digest in m[key].items():
            assert sha(p/n) == digest
    d = p/'pressure'; reference = REFERENCE/'pressure'
    assert sha(d/'run.tcl') == m['run_tcl_sha256'] == sha(reference/'run.tcl')
    commands = m['cases']['pressure']['commands']
    assert [c['stage'] for c in commands] == ['compile','elaborate','simulate']
    for old, new in zip(rm['cases']['pressure']['commands'],commands):
        assert new['exit_code'] == 0 and new['stage'] == old['stage']
        assert new['argv'] == [a.replace(str(REFERENCE),str(p)) for a in old['argv']]
        assert new['start_ticks'] is not None and identity(new['pid']) != str(new['start_ticks'])
        assert sha(d/(new['stage']+'.stdout.log')) == new['stdout_sha256']
        if new['stage'] in ['elaborate','simulate']:
            assert '2022.2' in (d/(new['stage']+'.stdout.log')).read_text()
        else:
            assert '[VRFC ' in (d/(new['stage']+'.stdout.log')).read_text()
    admission = m['memory_admission']
    assert admission['stable_seconds'] >= 60 and admission['current_bytes']*4 <= admission['limit_bytes']*3
    log, oldlog = (d/'simulate.log').read_text(), (reference/'simulate.log').read_text()
    assert 'Fatal:' not in log and 'ERROR:' not in log
    finish = re.findall(r'\$finish called at time : ([0-9.]+) ns',log)
    old_finish = re.findall(r'\$finish called at time : ([0-9.]+) ns',oldlog)
    assert len(finish) == len(old_finish) == 1
    semantic = check((d/'natural_trace.txt').read_text(),log,(reference/'natural_trace.txt').read_text())
    assert Decimal(finish[0]) == Decimal(old_finish[0]) + semantic['extension_cycles']*10
    markers = [line for line in log.splitlines() if line.startswith(('THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS'))]
    assert markers == [line for line in oldlog.splitlines() if line.startswith(('THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_WARM_PASS'))]
    assert log.splitlines().count('ITER2_CONTINUOUS_PREP_PASS') == 1
    patterns = {
        'backend_exclusion':('BACKEND_EXCLUSION_PASS',['cycles','authority','owner']),
        'capture_retirement':('CAPTURE_RETIREMENT_PASS',['cycles','nonzero','replies']),
        'query_interface_exclusion':('QUERY_INTERFACE_EXCLUSION_PASS',['cycles','service_req','service_rsp','search_req','search_rsp','route_req','route_rsp']),
        'checkpoint_edit_exclusion':('CHECKPOINT_EDIT_EXCLUSION_PASS',['cycles','safe','edit','busy','requests','replies','imports','exports']),
    }
    coverage = {}
    for key, (tag, columns) in patterns.items():
        pattern = '^'+tag+' '+ ' '.join(name+r'=(\d+)' for name in columns)+'$'
        rows = re.findall(pattern,log,re.M); assert len(rows) == 1
        values = list(map(int,rows[0])); assert all(v > 0 for v in values)
        coverage[key] = dict(zip(columns,values))
    assert len({v['cycles'] for v in coverage.values()}) == 1
    qi = coverage['query_interface_exclusion']
    for name in ['service','search','route']:
        assert qi[name+'_req'] == qi[name+'_rsp']
    assert coverage['checkpoint_edit_exclusion']['requests'] == coverage['checkpoint_edit_exclusion']['replies'] == 15
    files = sorted(ra['exact_comparisons']); assert len(files) == 27
    actual_files = {f.name for f in d.iterdir() if f.is_file() and f.suffix in ['.txt','.bin','.dat']}
    assert actual_files == set(files) and sum(name.endswith('_axi.txt') for name in files) == 12
    outputs = {name:dict(bytes=(d/name).stat().st_size,sha256=sha(d/name)) for name in files}
    comparisons = {}
    baseline_audit = None
    if mode == 'cp':
        bp = TARGETS['baseline']; bm, ba, _ = restored(bp)
        assert ba['host_edit'] == semantic and ba['finish_time'] == finish[0]+' ns'
        assert ba['coverage'] == coverage and bm['rtl'] == m['rtl']
        for n in original['cp']['rtl']:
            assert (sha(bp/'sources'/n) != sha(p/'sources'/n)) == (n in CHANGED)
        assert sha(bp/'sources/tb_query_fault.sv') == sha(p/'sources/tb_query_fault.sv')
        for name, entry in outputs.items():
            assert entry == ba['outputs'][name]
            assert (bp/'pressure'/name).stat().st_size == entry['bytes'] and sha(bp/'pressure'/name) == entry['sha256'], name
            comparisons[name] = entry
        baseline_audit = sha(bp/'source_bound_audit.json')
    result = dict(status='passed',mode=mode,manifest_sha256=sha(p/'manifest.json'),
        auditor_sha256=sha(Path(__file__)),parser_sha256=sha(ROOT/'scripts/check_host_edit_trace_v1.py'),
        original_audit_sha256=sha(REFERENCE/'source_bound_audit.json'),baseline_audit_sha256=baseline_audit,
        host_edit=semantic,coverage=coverage,outputs=outputs,exact_comparisons=comparisons,
        production_sources=133,finish_time=finish[0]+' ns',markers=markers,predecessors=m['predecessors'],
        timing_qualified=False,board_acceptance=False,
        scope='Actual real host edit with independently checked suffix, original trace prefix, complete source/command bindings and held/atomic runtime monitors. Baseline is an observed reference; CP additionally requires27 complete byte/cycle matches. This auditor alone is not archive/actual-restore acceptance.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('HOST_EDIT_SYSTEM_AUDITED',mode,len(outputs),'outputs',len(comparisons),'exact pair comparisons')


if __name__ == '__main__':
    audit(Path(sys.argv[1]).resolve())
