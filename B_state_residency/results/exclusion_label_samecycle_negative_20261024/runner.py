"""Freeze sources and run resident endpoint integration and token exhaustion."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    src = out / 'sources'
    src.mkdir()
    baseline = ROOT / 'results/sparse_records_20261024'
    bm = json.loads((baseline / 'manifest.json').read_text())
    assert bm['status'] == 'passed'
    paths = []
    for name, digest in bm['cases']['candidate']['sources'].items():
        if name.startswith('tb_'):
            continue
        p = baseline / 'candidate/sources' / name
        assert sha(p) == digest
        paths.append(p)
    variant = ROOT / 'hardware/variants/exclusion_label_v2'
    dut = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else variant / 'exclusion_label_adapter.sv'
    paths += [dut, variant / 'tb_exclusion_label_adapter.sv']
    dependencies = [baseline / 'manifest.json', baseline / 'source_bound_audit.json', ROOT / 'results/exclusion_label_boundary_20261024/manifest.json',
                    ROOT / 'results/exclusion_hls_20261024/source_bound_audit.json', variant / 'CONTRACT.md', Path(__file__)]
    m = {'status': 'running', 'pid': os.getpid(), 'sources': {}, 'dependencies': {}, 'cases': {},
         'scope': 'Resident sparse_records endpoint RTL plus logical-label bridge. No HLS call collector, automatic pager, AXI traffic, full search, timing or board proof.'}
    def save():
        tmp = out / 'manifest.tmp'
        tmp.write_text(json.dumps(m, indent=2) + '\n')
        tmp.replace(out / 'manifest.json')
    for p in paths:
        (src / p.name).write_bytes(p.read_bytes())
        m['sources'][p.name] = {'path': str(p), 'sha256': sha(p)}
    for p in dependencies:
        assert p.is_file(), p
        m['dependencies'][str(p)] = sha(p)
    (out / 'runner.py').write_bytes(Path(__file__).read_bytes())
    save()
    try:
        for case in ('production32', 'exhaustion3'):
            d = out / case
            d.mkdir()
            (d / 'run.tcl').write_text('run 5ms\nquit\n')
            commands = [
                ('compile', [str(BIN / 'xvlog'), '--sv'] + (['--define', 'TOKEN_SMALL'] if case == 'exhaustion3' else []) + [str(src / p.name) for p in paths]),
                ('elaborate', [str(BIN / 'xelab'), 'tb_exclusion_label_adapter', '-s', 'labels', '--debug', 'typical', '--mt', '2']),
                ('simulate', [str(BIN / 'xsim'), 'labels', '--tclbatch', 'run.tcl', '--log', 'simulate.log'])]
            cm = m['cases'][case] = {'status': 'running', 'commands': []}
            save()
            for stage, argv in commands:
                t0 = time.monotonic()
                with (d / (stage + '.stdout.log')).open('w') as log:
                    proc = subprocess.Popen(argv, cwd=d, stdout=log, stderr=subprocess.STDOUT)
                    row = {'stage': stage, 'argv': argv, 'pid': proc.pid}
                    cm['commands'].append(row)
                    save()
                    row['exit_code'] = proc.wait(timeout=600)
                    row['elapsed_s'] = time.monotonic() - t0
                    save()
                assert row['exit_code'] == 0, (case, stage)
            log = (d / 'simulate.log').read_text()
            marker = 'EXCLUSION_LABEL_PASS ' if case == 'production32' else 'TOKEN_EXHAUSTION_PASS '
            matches = [line for line in log.splitlines() if line.startswith(marker)]
            assert len(matches) == 1 and 'Fatal:' not in log and 'Error:' not in log and '$finish' in log, (case, log[-2500:])
            cm.update(status='passed', result=matches[0], artifacts={p.name: sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.log', '.tcl')})
            print(case, matches[0], flush=True)
            save()
        for name, spec in m['sources'].items():
            assert sha(Path(spec['path'])) == spec['sha256'] == sha(src / name)
        for path, digest in m['dependencies'].items():
            assert sha(Path(path)) == digest
        m['status'] = 'passed'
        save()
    except Exception as exc:
        m.update(status='failed', error=repr(exc))
        save()
        raise

if __name__ == '__main__':
    main()
