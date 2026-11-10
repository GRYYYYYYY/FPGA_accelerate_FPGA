"""Three randomized blocks: resident capacities and same-run original control."""
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
    dirs = {'zero_bypass': ROOT / 'build/resident_zero_v1'}
    capacities = [64, 256, 4096]
    original_dir = ROOT / "build/real_trace"
    original_build = json.loads((original_dir / "build.json").read_text())["original"]
    builds = {k: json.loads((p / 'build.json').read_text()) for k, p in dirs.items()}
    proofs = {k: json.loads((p / 'semantic_tests.json').read_text()) for k, p in dirs.items()}
    def bindings():
        if sha(original_dir / "router_original") != original_build["binary_sha256"] or sha(original_dir / "original.cpp") != original_build["source_sha256"]:
            raise ValueError("Original control changed")
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
            if sha(directory / 'test_labels') != proof['test_binary_sha256'] or sha(directory / 'semantic_tests.log') != proof['log_sha256']:
                raise ValueError('Native proof artifacts changed')
    bindings()
    ref_path = ROOT / 'results/research_chain_20261022T183749Z/matrix/manifest.json'
    ref = json.loads(ref_path.read_text())
    out = ROOT / 'results' / ('resident_repeated_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    (out / 'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    record = dict(status='running', runner_pid=os.getpid(), purpose='three_repeat_capacity_with_original', repeats=3, original_build=original_build, capacities=capacities, page_bits=6, random_seed=17431,
                  scope='Synchronous CPU, same serial schedule, 64/256/4096 frames x 64 nodes and original flat control; three randomized blocks. No hardware/DMA or formal speedup claim.',
                  builds=builds, semantic_tests=proofs, reference_manifest_sha256=sha(ref_path),
                  tool_sha256=sha(__file__), runs=[])
    def save():
        temp = out / 'manifest.json.tmp'
        temp.write_text(json.dumps(record, indent=2) + '\n')
        temp.replace(out / 'manifest.json')
    save()
    cases = []
    rng = random.Random(17431)
    for repeat in range(1, 4):
        block = [(d, 'zero_bypass', c, repeat) for d in ref['config']['datasets'] for c in capacities]
        block += [(d, 'original', 0, repeat) for d in ref['config']['datasets']]
        rng.shuffle(block)
        cases.extend(block)
    record['planned_cases'] = [dict(dataset=d['id'], access_mode=m, physical_pages=c, repeat=r) for d,m,c,r in cases]
    if original_build['binary_sha256'] != ref['original_binary_sha256']:
        raise ValueError('Original differs from frozen reference')
    save()
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('RW_', 'B_'))}
    try:
        for dataset, mode, capacity, repeat in cases:
            if sha(ROOT / dataset['input']) != dataset['input_sha256']:
                raise ValueError('Dataset changed')
            name = dataset['id'] + '_' + mode + '_c' + str(capacity) + '_r' + str(repeat)
            prefix = out / name
            env = dict(RW_MAX_THREADS='1', RW_PAR_PART='0', RW_PAR_ITER1='0', RW_OVERLAP='0', RW_BATCH_T='0',
                       RW_GPU_FLOOD='0', RW_BATCH_PBITS='6', B_RESIDENT_PAGES=str(capacity), B_SERIAL_PAGED='1',
                       B_LABEL_REPORT=str(prefix.with_suffix('.labels.json')))
            if mode == 'original':
                env = {k:v for k,v in env.items() if not k.startswith('B_')}
            cmd = ['/usr/bin/time', '-v', '-o', str(prefix.with_suffix('.time')), 'taskset', '-c', '8',
                   str(original_dir / 'router_original' if mode == 'original' else dirs[mode] / 'router'), str(ROOT / dataset['input']), str(prefix.with_suffix('.result'))]
            row = dict(name=name, dataset=dataset['id'], access_mode=mode, physical_pages=capacity, repeat=repeat, command=cmd, environment=env)
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
            labels = None
            if mode != 'original':
                labels = json.loads(prefix.with_suffix('.labels.json').read_text())
                if (len(labels['contexts']) != 1 or labels['contexts'][0]['physical_pages'] != capacity
                        or labels['contexts'][0]['page_bits'] != 6
                        or labels['contexts'][0]['resident_payload_bytes'] != capacity * 64 * labels['node_size']
                        or not labels['contexts'][0]['zero_reads']):
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
