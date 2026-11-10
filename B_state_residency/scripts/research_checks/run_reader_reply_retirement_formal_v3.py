"""Run one prepared active generation persistence proof, preserving live children."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shadow_terminal_receipt_v1 import record_child_exit, record_exception

BASE = Path('/tmp/B_state_residency_offer_20261025')
ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def identity(pid):
    return Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()[19]


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == BASE / 'ka_reader_reply_retirement_formal_v3'
    m = json.loads((p / 'manifest.json').read_text())
    assert m['status'] == 'prepared' and not m['commands']
    assert sha(p / 'kernel.json') == m['kernel_json_sha256']
    assert sha(p / 'harness.sv') == m['harness_sha256']
    assert sha(p / 'memory_control.sv') == m['memory_control_sha256']
    assert sha(p / 'memory_binding.json') == m['memory_binding_sha256']
    assert sha(Path(m['original_core'])) == m['original_core_sha256']
    for name, e in m['sources'].items():
        assert sha(Path(e['source'])) == e['sha256']
    helper = ROOT / 'scripts/shadow_terminal_receipt_v1.py'
    calibration = ROOT / 'results/shadow_terminal_receipt_v1_calibration_20261031.json'
    assert json.loads(calibration.read_text())['helper_sha256'] == sha(helper)
    m.update(status='running', runner_pid=os.getpid(),
             runner_start_ticks=identity(os.getpid()), runner_sha256=sha(Path(__file__)),
             terminal_helper_sha256=sha(helper), calibration_sha256=sha(calibration))

    def save():
        pending = p / 'manifest.pending.json'
        pending.write_text(json.dumps(m, indent=2) + '\n')
        pending.replace(p / 'manifest.json')

    env = os.environ.copy()
    tools = BASE / 'ka_formal_packages_v1'
    env['PYTHONPATH'] = str(tools)
    env['XDG_CACHE_HOME'] = str(BASE / 'ka_formal_cache_v1')
    env['PATH'] = str(tools / 'bin') + ':' + env['PATH']
    (p / 'prepare.ys').write_text(
        'read_json kernel.json\nread_verilog -formal -sv memory_control.sv harness.sv\n'
        'prep -top ka_reader_reply_retirement_formal\nasync2sync\n'
        'chformal -lower\ndffunmap\nwrite_smt2 -wires design.smt2\n')
    yosys = [sys.executable, str(tools / 'bin/yowasp-yosys'), '-s', 'prepare.ys']
    smt = [sys.executable, str(tools / 'bin/yowasp-yosys-smtbmc'), '-s', 'z3']
    jobs = [('prepare', yosys),
            ('bmc', smt + ['-t', '10', '--dump-vcd', 'bmc_failure.vcd', 'design.smt2']),
            ('induction', smt + ['-i', '-t', '10', '--dump-vcd', 'induction_failure.vcd', 'design.smt2']),
            ('cover', smt + ['-c', '-t', '20', '--dump-vcd', 'cover%.vcd', 'design.smt2'])]
    child = None
    save()
    try:
        for stage, argv in jobs:
            m['stage'] = stage
            start = time.monotonic()
            with (p / (stage + '.log')).open('w') as log:
                child = subprocess.Popen(argv, cwd=p, env=env, stdout=log,
                                         stderr=subprocess.STDOUT)
                m['active_process'] = dict(stage=stage, pid=child.pid,
                                          start_ticks=identity(child.pid), argv=argv)
                save()
                code = child.wait()
            record_child_exit(m, code)
            text = (p / (stage + '.log')).read_text()
            m['commands'].append(dict(stage=stage, argv=argv, exit_code=code,
                                      elapsed_s=time.monotonic() - start,
                                      log_sha256=sha(p / (stage + '.log'))))
            save()
            assert code == 0, (stage, text[-2000:])
            if stage == 'prepare':
                assert 'implicitly declared' not in text and 'used but has no driver' not in text
            else:
                assert 'Status: PASSED' in text, (stage, text[-2000:])
            print(stage, 'observed', text[-700:], flush=True)
        m.update(status='observed', stage='complete')
    except BaseException as error:
        record_exception(m, error, child)
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
