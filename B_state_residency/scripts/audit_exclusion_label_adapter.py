"""Independently bind passing v2 regression and the same-test v1 counterexample."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def verify_inputs(out, m):
    assert sha(out / 'runner.py') == m['dependencies'][str(ROOT / 'scripts/run_exclusion_label_adapter_v2.py')]
    for name, spec in m['sources'].items():
        assert sha(out / 'sources' / name) == spec['sha256'] == sha(Path(spec['path'])), name
    for path, digest in m['dependencies'].items():
        assert sha(Path(path)) == digest, path

def main():
    out = ROOT / 'results/exclusion_label_adapter_v2_20261024'
    neg = ROOT / 'results/exclusion_label_samecycle_negative_20261024'
    m, n = read(out / 'manifest.json'), read(neg / 'manifest.json')
    assert m['status'] == 'passed' and n['status'] == 'failed'
    verify_inputs(out, m)
    verify_inputs(neg, n)
    assert set(m['cases']) == {'production32', 'exhaustion3'}
    expected = {
        'production32': 'EXCLUSION_LABEL_PASS matrix_reads=1024 cookie_errors=6 service_errors=30 abort_cases=8 checks=2250 native_reads=1049 blocked_cycles=11735',
        'exhaustion3': 'TOKEN_EXHAUSTION_PASS accepted=7 refused=1 invalid=1 checks=9',
    }
    for case, cm in m['cases'].items():
        assert cm['status'] == 'passed'
        assert [r['stage'] for r in cm['commands']] == ['compile', 'elaborate', 'simulate']
        assert all(r['exit_code'] == 0 for r in cm['commands'])
        compile_argv = cm['commands'][0]['argv']
        defines = ['--define', 'TOKEN_SMALL'] if case == 'exhaustion3' else []
        bin_dir = '/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/'
        assert compile_argv == [bin_dir + 'xvlog', '--sv'] + defines + [str(out / 'sources' / name) for name in m['sources']]
        assert cm['commands'][1]['argv'] == [bin_dir + 'xelab', 'tb_exclusion_label_adapter', '-s', 'labels', '--debug', 'typical', '--mt', '2']
        assert cm['commands'][2]['argv'] == [bin_dir + 'xsim', 'labels', '--tclbatch', 'run.tcl', '--log', 'simulate.log']
        for name, digest in cm['artifacts'].items():
            assert sha(out / case / name) == digest, (case, name)
        assert (out / case / 'run.tcl').read_text() == 'run 5ms\nquit\n'
        for name in ('compile.stdout.log', 'elaborate.stdout.log', 'simulate.stdout.log', 'simulate.log'):
            log = (out / case / name).read_text()
            assert not re.search(r'(^|\n)(ERROR:|Fatal:|Error:)', log), (case, name)
        log = (out / case / 'simulate.log').read_text()
        assert log.splitlines().count(expected[case]) == 1 and '$finish called' in log
        assert cm['result'] == expected[case]
    # Same enhanced testbench and exactly the same backend sources; only DUT differs.
    changed = [name for name in m['sources'] if m['sources'][name]['sha256'] != n['sources'][name]['sha256']]
    assert changed == ['exclusion_label_adapter.sv'], changed
    assert set(n['cases']) == {'production32'}
    assert all(r['exit_code'] == 0 for r in n['cases']['production32']['commands'])
    negative_log = (neg / 'production32/simulate.log').read_text()
    assert negative_log.count('Fatal: same-cycle abort invisible at successful reply acceptance') == 1
    assert 'Time: 462741 ns ' in negative_log and 'EXCLUSION_LABEL_PASS ' not in negative_log
    base = ROOT / 'results/sparse_records_20261024'
    bm = read(base / 'manifest.json')
    ba = read(base / 'source_bound_audit.json')
    assert ba['status'] == 'passed' and ba['manifest_sha256'] == sha(base / 'manifest.json')
    for name, digest in bm['cases']['candidate']['sources'].items():
        if not name.startswith('tb_'):
            assert m['sources'][name]['sha256'] == digest
    hls = ROOT / 'results/exclusion_hls_20261024'
    ha = read(hls / 'source_bound_audit.json')
    assert ha['status'] == 'passed' and ha['manifest_sha256'] == sha(hls / 'manifest.json')
    boundary = read(ROOT / 'results/exclusion_label_boundary_20261024/manifest.json')
    assert boundary['status'] == 'source_reviewed'
    for path, digest in boundary['files'].items():
        assert sha(ROOT / path) == digest
    # Bind the correction explanation and MCP entry script without changing frozen sources.
    extras = [ROOT / 'hardware/variants/exclusion_label_v2/REVISION.md',
              ROOT / 'hardware/scripts/verify_exclusion_label_adapter_v2.tcl']
    for path in extras:
        (out / path.name).write_bytes(path.read_bytes())
    (out / 'auditor.py').write_bytes(Path(__file__).read_bytes())
    result = {
        'status': 'passed', 'manifest_sha256': sha(out / 'manifest.json'),
        'auditor_sha256': sha(Path(__file__)),
        'negative_manifest_sha256': sha(neg / 'manifest.json'),
        'negative_log_sha256': sha(neg / 'production32/simulate.log'),
        'counterexample': 'v1 same-cycle abort invisible at 462741 ns; same enhanced test passes on v2',
        'results': expected, 'extra_sources': {str(p): sha(p) for p in extras},
        'scope': m['scope'],
    }
    (out / 'source_bound_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
