"""Independent exact event and evidence audit for the unchanged RTL observer."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def observation(events, log):
    assert 'Fatal:' not in log and 'ERROR:' not in log
    lines = events.splitlines()
    expected = []
    for mode, bit in enumerate(['0', '1', 'x', 'z', 'x', 'z', 'x']):
        if mode == 1:
            expected.append((f'REJECT mode={mode} bit=1 checkpoint=17', None))
        else:
            expected.append((f'STAGE mode={mode} bit={bit} active=0', None))
            if mode in [0, 2, 3]:
                expected.append((rf'PUBLISH mode={mode} cycle=(\d+) old=0 staged={bit}', 'cycle'))
                expected.append((f'RESULT mode={mode} bit={bit} checkpoint=18', None))
            else:
                expected.append((f'CLEAR mode={mode} bit=0 checkpoint=17', None))
    coverage = 'loads=14 captures=6 publications=3 clears=3 rejections=1 checks=138'
    expected.append(('COVERAGE ' + coverage, None))
    assert len(lines) == len(expected) == 17
    cycles = []
    for actual, (wanted, kind) in zip(lines, expected):
        if kind == 'cycle':
            match = re.fullmatch(wanted, actual)
            assert match, (actual, wanted)
            cycles.append(int(match[1]))
        else:
            assert actual == wanted, (actual, wanted)
    assert 0 < cycles[0] < cycles[1] < cycles[2] < 500
    assert re.findall(r'CONFIG_PUBLICATION_PROBE_PASS[^\r\n]*', log) == ['CONFIG_PUBLICATION_PROBE_PASS ' + coverage]
    finish = re.findall(r'\$finish called at time : ([0-9.]+) (ps|ns|us)', log)
    assert len(finish) == 1
    time_ns = float(finish[0][0]) * {'ps': 0.001, 'ns': 1, 'us': 1000}[finish[0][1]]
    assert 0 < time_ns < 5010
    return dict(loads=14, captures=6, publications=3, clears=3, rejections=1,
                checks=138, events=17, publication_cycles=cycles,
                finish_time=' '.join(finish[0]), x_and_z_publication_observed=True,
                abort_discard_attempt_reset_preserve_active=True)


def main():
    p = Path(sys.argv[1]).resolve()
    m = json.loads((p / 'manifest.json').read_text())
    assert m['status'] == 'observed' and m['stage'] == 'complete' and not m.get('active_process')
    proc = Path('/proc', str(m['runner_pid']), 'stat')
    if proc.exists():
        assert proc.read_text().split(') ', 1)[1].split()[19] != str(m['runner_start_ticks'])
    for name, entry in m['bound'].items():
        assert sha(entry['source']) == entry['sha256'] == sha(p / 'bound' / name), name
    assert sha(p / 'config_restore_controller.sv') == m['dut_sha256'] == sha(m['dut_source'])
    assert sha(p / 'tb_config_publication_probe_v1.sv') == m['tb_sha256'] == sha(m['tb_source'])
    prep = json.loads((ROOT / 'results/config_publication_probe_preparation_20261030.json').read_text())
    assert m['dut_sha256'] == prep['unmodified_dut_sha256'] and m['tb_sha256'] == prep['testbench_sha256']
    assert m['runner_sha256'] == sha(ROOT / 'scripts/run_config_publication_probe_v1.py')
    assert not re.search(r'\b(force|release)\s', (p / 'tb_config_publication_probe_v1.sv').read_text())
    for path, digest in m['matrix_evidence_sha256'].items():
        assert sha(path) == digest
    base = Path('/tmp/B_state_residency_offer_20261025')
    matrix_paths = [base / 'checkpoint_edit_matrix_queue_v1/manifest.json',
                    ROOT / 'results/checkpoint_edit_matrix_20261030.json',
                    ROOT / 'results/checkpoint_edit_matrix_sources_20261030/manifest.json']
    assert set(m['matrix_evidence_sha256']) == set(map(str, matrix_paths))
    owner, matrix, frozen = [json.loads(f.read_text()) for f in matrix_paths]
    assert owner['status'] == 'observed' and owner['stage'] == 'complete'
    assert owner['result_sha256'] == sha(matrix_paths[1])
    assert matrix['status'] == 'eight_cp_behavioral_cases_restored' and matrix['total_case_file_comparisons'] == 216
    assert frozen['status'] == 'frozen' and frozen['cases'] == 8 and frozen['case_file_comparisons'] == 216
    assert m['memory_admission']['stable_seconds'] >= 60
    assert m['memory_admission']['current_bytes'] * 4 <= m['memory_admission']['limit_bytes'] * 3
    assert (p / 'run.tcl').read_text() == 'run 10us\nquit\n'
    assert sha(p / 'run.tcl') == m['run_tcl_sha256']
    assert [c['stage'] for c in m['commands']] == ['compile', 'elaborate', 'simulate']
    binary = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
    expected_commands = [
        [binary / 'xvlog', '--sv', p / 'config_restore_controller.sv', p / 'tb_config_publication_probe_v1.sv'],
        [binary / 'xelab', 'tb_config_publication_probe_v1', '-s', 'config_pub', '--debug', 'typical', '--mt', '2'],
        [binary / 'xsim', 'config_pub', '--tclbatch', 'run.tcl', '--log', 'simulate.log', '--testplusarg', 'events=' + str(p / 'events.txt')],
    ]
    for command, expected_command in zip(m['commands'], expected_commands):
        assert command['argv'] == list(map(str, expected_command))
        assert command['exit_code'] == 0
        assert sha(p / (command['stage'] + '.stdout.log')) == command['log_sha256']
        assert not re.search(r'(^|\n)(?:ERROR:|FATAL_ERROR:)', (p / (command['stage'] + '.stdout.log')).read_text())
    assert '2022.2' in (p / 'elaborate.stdout.log').read_text()
    for name, digest in m['artifacts'].items():
        assert sha(p / name) == digest
    assert set(m['artifacts']) == {'events.txt', 'simulate.log'}
    result = observation((p / 'events.txt').read_text(), (p / 'simulate.log').read_text())
    result.update(status='passed', manifest_sha256=sha(p / 'manifest.json'),
        auditor_sha256=sha(__file__), dut_sha256=m['dut_sha256'], tb_sha256=m['tb_sha256'],
        events_sha256=sha(p / 'events.txt'), simulate_log_sha256=sha(p / 'simulate.log'),
        production_rtl_changed=False, replacement_equivalence=False, full_system_knownness_proven=False,
        scope=m['scope'])
    (p / 'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('CONFIG_PUBLICATION_PROBE_AUDITED', result['events'], result['finish_time'])


if __name__ == '__main__':
    main()
