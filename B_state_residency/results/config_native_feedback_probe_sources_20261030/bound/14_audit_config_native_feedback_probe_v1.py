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
    for bit in ['0', '1', 'x', 'z']:
        for action in range(5):
            version = 4 if action == 0 else 3
            checkpoint = 18 if action == 0 else 17
            expected.append(f'NATIVE data={bit} action={action} raw_version={version} active_version=4 checkpoint={checkpoint}')
    assert len(lines) == 21 and lines[:20] == expected
    fixed = 'loads=60 recoveries=20 captures=20 publications=4 clears=16 blocked_overwrites=20 configuration_requests=120 alias_checks=40'
    coverage = re.fullmatch(r'COVERAGE ' + fixed + r' prepared_checks=(\d+) checks=689', lines[-1])
    assert coverage and int(coverage[1]) > 0
    expected_pass = 'CONFIG_NATIVE_FEEDBACK_PASS cases=20 ' + lines[-1].removeprefix('COVERAGE ')
    assert re.findall(r'CONFIG_NATIVE_FEEDBACK_PASS[^\r\n]*', log) == [expected_pass]
    finish = re.findall(r'\$finish called at time : ([0-9.]+) (ps|ns|us)', log)
    assert len(finish) == 1
    time_ns = float(finish[0][0]) * {'ps': 0.001, 'ns': 1, 'us': 1000}[finish[0][1]]
    assert 0 < time_ns < 30010
    return dict(cases=20, loads=60, recoveries=20, captures=20, publications=4, clears=16,
                blocked_overwrites=20, configuration_requests=120, alias_checks=40,
                prepared_checks=int(coverage[1]), checks=689, events=21,
                finish_time=' '.join(finish[0]), native_feedback_with_xz_observed=True,
                raw_version_publish_vs_cancel_observed=True,
                abort_discard_attempt_reset_and_collision_observed=True)


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
    assert sha(p / 'tb_config_native_feedback_v1.sv') == m['tb_sha256'] == sha(m['tb_source'])
    prep = json.loads((ROOT / 'results/config_native_feedback_testbench_preparation_20261030.json').read_text())
    assert m['dut_sha256'] == prep['unmodified_dut_sha256'] and m['tb_sha256'] == prep['testbench_sha256']
    assert m['runner_sha256'] == sha(ROOT / 'scripts/run_config_native_feedback_probe_v1.py')
    assert not re.search(r'\b(force|release)\s', (p / 'tb_config_native_feedback_v1.sv').read_text())
    for path, digest in m['predecessor_evidence_sha256'].items():
        assert sha(path) == digest
    base = Path('/tmp/B_state_residency_offer_20261025')
    matrix_paths = [base / 'checkpoint_edit_matrix_queue_v1/manifest.json',
                    ROOT / 'results/checkpoint_edit_matrix_20261030.json',
                    ROOT / 'results/checkpoint_edit_matrix_sources_20261030/manifest.json']
    generic = base / 'config_publication_probe_v1'
    generic_paths = [generic / 'manifest.json', generic / 'source_bound_audit.json',
                     ROOT / 'results/config_publication_probe_v1_restore_20261025.json',
                     ROOT / 'results/config_publication_probe_20261030.json',
                     ROOT / 'results/config_publication_probe_sources_20261030/manifest.json']
    assert set(m['predecessor_evidence_sha256']) == set(map(str, matrix_paths + generic_paths))
    gm, ga, gr, gp, gf = [json.loads(f.read_text()) for f in generic_paths]
    assert gm['status'] == 'observed' and gm['stage'] == 'complete'
    assert ga['status'] == gr['status'] == 'passed' and gr['audit_byte_identical']
    assert ga['manifest_sha256'] == sha(generic_paths[0]) and gr['audit_sha256'] == sha(generic_paths[1])
    assert ga['events'] == 17 and ga['checks'] == 138 and ga['x_and_z_publication_observed']
    assert gp['status'] == 'original_rtl_publication_counterexamples_restored' and gp['audit'] == ga and gp['restoration'] == gr
    assert gf['status'] == 'frozen'
    owner, matrix, frozen = [json.loads(f.read_text()) for f in matrix_paths]
    assert owner['status'] == 'observed' and owner['stage'] == 'complete'
    assert owner['result_sha256'] == sha(matrix_paths[1])
    assert matrix['status'] == 'eight_cp_behavioral_cases_restored' and matrix['total_case_file_comparisons'] == 216
    assert frozen['status'] == 'frozen' and frozen['cases'] == 8 and frozen['case_file_comparisons'] == 216
    assert m['memory_admission']['stable_seconds'] >= 60
    assert m['memory_admission']['current_bytes'] * 4 <= m['memory_admission']['limit_bytes'] * 3
    assert (p / 'run.tcl').read_text() == 'run 100us\nquit\n'
    assert sha(p / 'run.tcl') == m['run_tcl_sha256']
    assert [c['stage'] for c in m['commands']] == ['compile', 'elaborate', 'simulate']
    binary = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
    expected_commands = [
        [binary / 'xvlog', '--sv', p / 'config_restore_controller.sv', p / 'tb_config_native_feedback_v1.sv'],
        [binary / 'xelab', 'tb_config_native_feedback_v1', '-s', 'config_native', '--debug', 'typical', '--mt', '2'],
        [binary / 'xsim', 'config_native', '--tclbatch', 'run.tcl', '--log', 'simulate.log', '--testplusarg', 'events=' + str(p / 'events.txt')],
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
    print('CONFIG_NATIVE_FEEDBACK_AUDITED', result['events'], result['finish_time'])


if __name__ == '__main__':
    main()
