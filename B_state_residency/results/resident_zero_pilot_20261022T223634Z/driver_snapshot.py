"""Single-repeat serial paired pilot: explicit dirty leases versus read-zero bypass."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'adapters'), str(ROOT / 'scripts')]
from prepare_real import sha
from profile_real import parse_log


def main():
    dirs = {'explicit_rw': ROOT / 'build/resident_rw_v2', 'zero_bypass': ROOT / 'build/resident_zero_v1'}
    builds = {k: json.loads((p / 'build.json').read_text()) for k, p in dirs.items()}
    proofs = {k: json.loads((p / 'semantic_tests.json').read_text()) for k, p in dirs.items()}
    def bindings():
        for mode, directory in dirs.items():
            build = builds[mode]
            for path, digest in build['inputs'].items():
                if sha(path) != digest:
                    raise ValueError('Source changed: ' + path)
            if sha(directory / 'router') != build['binary_sha256'] or sha(directory / 'router.cpp') != build['source_sha256']:
                raise ValueError('Binary/source changed')
            source = ROOT / ('tests/resident_rw_semantics.cpp' if mode == 'explicit_rw' else 'tests/resident_zero_semantics.cpp')
            proof = proofs[mode]
            if proof['status'] != 'passed' or proof['router_source_sha256'] != build['source_sha256'] or proof['test_source_sha256'] != sha(source):
                raise ValueError('Native proof mismatch')
    bindings()
    ref_path = ROOT / 'results/research_chain_20261022T183749Z/matrix/manifest.json'
    ref = json.loads(ref_path.read_text())
    out = ROOT / 'results' / ('resident_zero_pilot_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    (out / 'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    record = dict(status='running', runner_pid=os.getpid(), purpose='single_repeat_paired_discovery',
                  scope='Synchronous CPU, same serial schedule, 64 frames x 64 nodes. No hardware/DMA or formal speedup claim.',
                  builds=builds, semantic_tests=proofs, reference_manifest_sha256=sha(ref_path),
                  tool_sha256=sha(__file__), runs=[])
    def save():
        temp = out / 'manifest.json.tmp'
        temp.write_text(json.dumps(record, indent=2) + '\n')
        temp.replace(out / 'manifest.json')
    save()
    cases = [(d, mode) for d in ref['config']['datasets'] for mode in dirs]
    random.Random(5831).shuffle(cases)
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('RW_', 'B_'))}
    try:
        for dataset, mode in cases:
            if sha(ROOT / dataset['input']) != dataset['input_sha256']:
                raise ValueError('Dataset changed')
            name = dataset['id'] + '_' + mode
            prefix = out / name
            env = dict(RW_MAX_THREADS='1', RW_PAR_PART='0', RW_PAR_ITER1='0', RW_OVERLAP='0', RW_BATCH_T='0',
                       RW_GPU_FLOOD='0', RW_BATCH_PBITS='6', B_RESIDENT_PAGES='64', B_SERIAL_PAGED='1',
                       B_LABEL_REPORT=str(prefix.with_suffix('.labels.json')))
            cmd = ['/usr/bin/time', '-v', '-o', str(prefix.with_suffix('.time')), 'taskset', '-c', '8',
                   str(dirs[mode] / 'router'), str(ROOT / dataset['input']), str(prefix.with_suffix('.result'))]
            row = dict(name=name, dataset=dataset['id'], access_mode=mode, command=cmd, environment=env)
            record['runs'].append(row)
            with prefix.with_suffix('.log').open('w') as log:
                proc = subprocess.Popen(cmd, env=dict(clean, **env), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                row['pid'] = proc.pid
                save()
                try:
                    proc.wait(timeout=1200)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait()
                    raise RuntimeError('Paired pilot timeout')
            if proc.returncode:
                raise RuntimeError('Router failed: ' + name)
            metrics = parse_log(prefix.with_suffix('.log').read_text())
            digest = sha(prefix.with_suffix('.result'))
            golden = next(r for r in ref['runs'] if r['dataset'] == dataset['id'] and r['mode'] == 'serial')
            if digest != golden['result_sha256'] or metrics['convergence'] != golden['metrics']['convergence']:
                raise ValueError('Same-schedule mismatch')
            labels = json.loads(prefix.with_suffix('.labels.json').read_text())
            if len(labels['contexts']) != 1 or labels['contexts'][0]['physical_pages'] != 64 or not labels['contexts'][0]['refills']:
                raise ValueError('Resident path not exercised')
            row.update(verified=True, exit_code=proc.returncode, result_sha256=digest, metrics=metrics, labels=labels)
            save()
            print(name, metrics['route_ms'], 'ms; quality matches', flush=True)
        bindings()
        record['status'] = 'passed'
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        save()
    print(out, flush=True)


if __name__ == '__main__':
    main()
