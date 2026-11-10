"""Quality-first real-router pilot of RAII leased synchronous page residency."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'adapters'), str(ROOT / 'scripts')]
from prepare_real import sha
from profile_real import parse_log


def main():
    directory = ROOT / 'build/resident_real_v3'
    build = json.loads((directory / 'build.json').read_text())
    proof = json.loads((directory / 'semantic_tests.json').read_text())
    reference_path = ROOT / 'results/research_chain_20261022T183749Z/matrix/manifest.json'
    reference = json.loads(reference_path.read_text())
    if proof['status'] != 'passed' or proof['router_source_sha256'] != sha(directory / 'router.cpp'):
        raise ValueError('Matching native semantic proof required')
    if proof['test_source_sha256'] != sha(ROOT / 'tests/resident_semantics.cpp'):
        raise ValueError('Native test source changed')
    def bindings():
        for path, digest in build['inputs'].items():
            if sha(path) != digest:
                raise ValueError('Resident source changed: ' + path)
        if sha(directory / 'router') != build['binary_sha256'] or sha(directory / 'router.cpp') != build['source_sha256']:
            raise ValueError('Resident build changed')
    bindings()
    out = ROOT / 'results' / ('resident_pilot_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    (out / 'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    record = dict(status='running', runner_pid=os.getpid(), execution_kind='real_router_cpu_resident_pilot',
                  scope='Single repeat, synchronous CPU backing copies. No DMA/hardware or speedup claim.',
                  build=build, semantic_tests=proof, reference_manifest_sha256=sha(reference_path),
                  tool_sha256=sha(__file__), runs=[])
    def save():
        temp = out / 'manifest.json.tmp'
        temp.write_text(json.dumps(record, indent=2) + '\n')
        temp.replace(out / 'manifest.json')
    save()
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('RW_', 'B_'))}
    cases = [('logicnets_jscl', False), ('logicnets_jscl', True), ('vtr_mcml', True)]
    try:
        for dataset_id, resident in cases:
            dataset = next(d for d in reference['config']['datasets'] if d['id'] == dataset_id)
            if sha(ROOT / dataset['input']) != dataset['input_sha256']:
                raise ValueError('Input changed')
            name = dataset_id + ('_resident64_p6' if resident else '_flat_lease_control')
            prefix = out / name
            env = dict(RW_MAX_THREADS='1', RW_PAR_PART='0', RW_PAR_ITER1='0', RW_OVERLAP='0',
                       RW_BATCH_T='0', RW_GPU_FLOOD='0', RW_BATCH_PBITS='6', B_RESIDENT_PAGES='64',
                       B_LABEL_REPORT=str(prefix.with_suffix('.labels.json')))
            if resident:
                env['B_SERIAL_PAGED'] = '1'
            command = ['/usr/bin/time', '-v', '-o', str(prefix.with_suffix('.time')), 'taskset', '-c', '8',
                       str(directory / 'router'), str(ROOT / dataset['input']), str(prefix.with_suffix('.result'))]
            row = dict(name=name, dataset=dataset_id, resident=resident, command=command, environment=env)
            record['runs'].append(row)
            with prefix.with_suffix('.log').open('w') as log:
                proc = subprocess.Popen(command, env=dict(clean, **env), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                row['pid'] = proc.pid
                save()
                try:
                    proc.wait(timeout=1200)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=10)
                    raise RuntimeError('Resident pilot timed out: ' + name)
            if proc.returncode:
                raise RuntimeError('Router failed: ' + name)
            metrics = parse_log(prefix.with_suffix('.log').read_text())
            digest = sha(prefix.with_suffix('.result'))
            golden = next(r for r in reference['runs'] if r['dataset'] == dataset_id and r['mode'] == 'serial')
            if digest != golden['result_sha256'] or metrics['convergence'] != golden['metrics']['convergence']:
                raise ValueError('Same-schedule result/convergence mismatch: ' + name)
            labels = json.loads(prefix.with_suffix('.labels.json').read_text())
            if resident:
                c = labels['contexts'][0]
                if c['physical_pages'] != 64 or not c['writebacks'] or not c['refills']:
                    raise ValueError('Real eviction/refill was not exercised')
            row.update(verified=True, exit_code=proc.returncode, metrics=metrics,
                       result_sha256=digest, labels=labels)
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
