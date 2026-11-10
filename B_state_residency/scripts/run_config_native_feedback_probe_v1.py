"""Observe the original controller only after the unique CP matrix is frozen."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
TARGET = BASE / 'config_native_feedback_probe_v1'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def identity(pid):
    try:
        return Path('/proc', str(pid), 'stat').read_text().split(') ', 1)[1].split()[19]
    except FileNotFoundError:
        return None


def matrix_evidence():
    owner = BASE / 'checkpoint_edit_matrix_queue_v1/manifest.json'
    q = json.loads(owner.read_text())
    assert q['status'] == 'observed' and q['stage'] == 'complete', 'Wait for existing CP matrix owner'
    assert identity(q['runner_pid']) != str(q['runner_start_ticks']), 'Wait for CP matrix owner exit'
    assert not q.get('active_process')
    report = ROOT / 'results/checkpoint_edit_matrix_20261030.json'
    r = json.loads(report.read_text())
    assert sha(report) == q['result_sha256']
    assert r['status'] == 'eight_cp_behavioral_cases_restored'
    assert r['total_case_file_comparisons'] == 216 and len(r['cases']) == 7
    assert r['cases'] == q['cases'] and r['anchor'] == q['anchor']
    freeze = ROOT / 'results/checkpoint_edit_matrix_sources_20261030'
    fm = json.loads((freeze / 'manifest.json').read_text())
    assert fm['status'] == 'frozen' and fm['cases'] == 8 and fm['case_file_comparisons'] == 216
    for name, entry in fm['files'].items():
        assert sha(freeze / name) == entry['sha256'] == sha(entry['source']), name
    return [owner, report, freeze / 'manifest.json']


def generic_evidence():
    p = BASE / 'config_publication_probe_v1'
    m = json.loads((p / 'manifest.json').read_text())
    assert m['status'] == 'observed' and m['stage'] == 'complete'
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    a = json.loads((p / 'source_bound_audit.json').read_text())
    receipt = ROOT / 'results/config_publication_probe_v1_restore_20261025.json'
    r = json.loads(receipt.read_text())
    assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
    assert a['manifest_sha256'] == sha(p / 'manifest.json')
    assert r['audit_sha256'] == sha(p / 'source_bound_audit.json')
    assert a['events'] == 17 and a['checks'] == 138 and a['x_and_z_publication_observed']
    report = ROOT / 'results/config_publication_probe_20261030.json'
    accepted = json.loads(report.read_text())
    assert accepted['status'] == 'original_rtl_publication_counterexamples_restored'
    assert accepted['audit'] == a and accepted['restoration'] == r
    freeze = ROOT / 'results/config_publication_probe_sources_20261030'
    fm = json.loads((freeze / 'manifest.json').read_text())
    assert fm['status'] == 'frozen'
    for name, entry in fm['files'].items():
        assert sha(freeze / name) == entry['sha256'] == sha(entry['source'])
    return [p / 'manifest.json', p / 'source_bound_audit.json', receipt, report, freeze / 'manifest.json']


def source_evidence():
    preparation = ROOT / 'results/config_native_feedback_testbench_preparation_20261030.json'
    p = json.loads(preparation.read_text())
    assert p['status'] == 'native_testbench_prepared_not_compiled_or_simulated'
    dut = Path(p['unmodified_dut']); tb = Path(p['testbench'])
    assert sha(dut) == p['unmodified_dut_sha256'] and sha(tb) == p['testbench_sha256']
    model = ROOT / 'results/config_native_feedback_20261030.json'
    a = json.loads(model.read_text())
    assert sha(model) == p['model_sha256'] and a['bound'][str(dut)] == sha(dut)
    assert a['status'] == 'native_feedback_four_value_projection_passed_not_rtl_equivalence'
    freeze = ROOT / 'results/config_native_feedback_sources_20261030'
    for name, entry in json.loads((freeze / 'manifest.json').read_text())['files'].items():
        assert sha(freeze / name) == entry['sha256'] == sha(entry['source'])
    return dut, tb, [preparation, model, freeze / 'manifest.json']


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == TARGET and not p.exists()
    gates = matrix_evidence() + generic_evidence()  # Both predecessors must be complete before creation.
    dut, tb, evidence = source_evidence()
    assert not os.environ.get('LD_PRELOAD'), 'Use the existing XSim runtime, not the Vivado route preload'
    for name in ['xvlog', 'xelab', 'xsim']:
        assert os.access(BIN / name, os.X_OK)
    files = gates + evidence + [dut, tb] + [ROOT / 'scripts' / name for name in [
        'run_config_native_feedback_probe_v1.py', 'audit_config_native_feedback_probe_v1.py',
        'freeze_config_native_feedback_probe_v1.py', 'archive_offer_result.py',
        'verify_search_retire_restore.py', 'restore_offer_result.py']]
    p.mkdir(); (p / 'bound').mkdir()
    bound = {}
    for i, source in enumerate(files):
        name = f'{i:02d}_{source.name}'
        shutil.copyfile(source, p / 'bound' / name)
        bound[name] = dict(source=str(source), sha256=sha(source))
        assert sha(p / 'bound' / name) == bound[name]['sha256']
    shutil.copyfile(dut, p / 'config_restore_controller.sv')
    shutil.copyfile(tb, p / 'tb_config_native_feedback_v1.sv')
    (p / 'run.tcl').write_text('run 100us\nquit\n')
    m = dict(status='running', stage='wait_memory', runner_pid=os.getpid(),
        runner_start_ticks=identity(os.getpid()), bound=bound, commands=[],
        dut_source=str(dut), dut_sha256=sha(dut), tb_source=str(tb), tb_sha256=sha(tb),
        runner_sha256=sha(__file__), predecessor_evidence_sha256={str(f): sha(f) for f in gates},
        run_tcl_sha256=sha(p / 'run.tcl'), runtime='XSim 2022.2; unchanged inherited environment',
        scope='Original CP controller with the exact native feedback muxes; 20 data/action cases after six-lane version advancement. No replacement RTL, full-system or timing claim.')

    def save():
        temp = p / 'manifest.pending.json'
        temp.write_text(json.dumps(m, indent=2, sort_keys=True) + '\n')
        temp.replace(p / 'manifest.json')

    def validate_bound():
        for name, entry in bound.items():
            assert sha(entry['source']) == entry['sha256'] == sha(p / 'bound' / name), name
        assert sha(p / 'config_restore_controller.sv') == m['dut_sha256']
        assert sha(p / 'tb_config_native_feedback_v1.sv') == m['tb_sha256']
        assert sha(p / 'run.tcl') == m['run_tcl_sha256']

    save()
    try:
        stable = None; deadline = time.monotonic() + 10800
        while True:
            now = time.monotonic(); cg = Path('/sys/fs/cgroup')
            current = int((cg / 'memory.current').read_text())
            limit = int((cg / 'memory.max').read_text())
            if current * 4 <= limit * 3:
                if stable is None:
                    stable = now
            else:
                stable = None
            seconds = 0 if stable is None else now - stable
            m['memory_admission'] = dict(current_bytes=current, limit_bytes=limit, stable_seconds=seconds)
            save()
            if seconds >= 60:
                break
            assert now < deadline, 'Memory admission observation expired; no solver launched'
            time.sleep(10)
        commands = [
            ('compile', [BIN / 'xvlog', '--sv', p / 'config_restore_controller.sv', p / 'tb_config_native_feedback_v1.sv']),
            ('elaborate', [BIN / 'xelab', 'tb_config_native_feedback_v1', '-s', 'config_native', '--debug', 'typical', '--mt', '2']),
            ('simulate', [BIN / 'xsim', 'config_native', '--tclbatch', 'run.tcl', '--log', 'simulate.log', '--testplusarg', 'events=' + str(p / 'events.txt')]),
        ]
        for stage, args in commands:
            validate_bound(); argv = list(map(str, args)); start = time.monotonic()
            m['stage'] = stage; save()
            with (p / (stage + '.stdout.log')).open('w') as log:
                child = subprocess.Popen(argv, cwd=p, stdout=log, stderr=subprocess.STDOUT)
                m['active_process'] = dict(pid=child.pid, start_ticks=identity(child.pid), argv=argv)
                save()
                try:
                    code = child.wait(timeout=600)
                except subprocess.TimeoutExpired:
                    m.update(status='observation_timeout', error='Preserve original child and inspect its identity; do not restart or kill it')
                    save()
                    raise
            m.pop('active_process', None)
            m['commands'].append(dict(stage=stage, argv=argv, pid=child.pid, exit_code=code,
                elapsed_s=time.monotonic() - start, log_sha256=sha(p / (stage + '.stdout.log'))))
            save()
            assert code == 0, stage
            print('CONFIG_NATIVE_FEEDBACK', stage, 'exit0', flush=True)
        log = (p / 'simulate.log').read_text()
        assert 'CONFIG_NATIVE_FEEDBACK_PASS' in log and '$finish called' in log
        assert 'Fatal:' not in log and 'ERROR:' not in log
        m['artifacts'] = {name: sha(p / name) for name in ['events.txt', 'simulate.log']}
        m.update(status='observed', stage='complete')
    except Exception as exc:
        if m['status'] != 'observation_timeout':
            m.update(status='failed', error=repr(exc))
        raise
    finally:
        save()
    print('CONFIG_NATIVE_FEEDBACK_OBSERVED', p)


if __name__ == '__main__':
    main()
