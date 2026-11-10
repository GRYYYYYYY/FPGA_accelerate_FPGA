"""Single-repeat paired discovery pilot; never a formal speedup claim."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'adapters'), str(ROOT / 'scripts')]
from prepare_real import sha
from profile_real import parse_log
from research_matrix import check_bindings


def main():
    frozen = json.loads((ROOT / 'results/research_chain_20261022T183749Z/matrix/manifest.json').read_text())
    assert frozen['status'] == 'passed'
    builds = [json.loads((ROOT / p).read_text()) for p in ('build/compact_real_v1/build.json', 'build/identity_real_v1/build.json')]
    config = frozen['config']
    check_bindings(config, builds)
    proof = json.loads((ROOT / 'build/identity_real_v1/semantic_tests.json').read_text())
    assert proof['status'] == 'passed'
    assert proof['test_source_sha256'] == sha(ROOT / 'tests/identity_semantics.cpp')
    assert proof['router_source_sha256'] == builds[1]['variants']['sparse_identity']['source_sha256']
    out = ROOT / 'results' / ('identity_pilot_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    (out / 'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    record = dict(status='running', purpose='single_repeat_discovery_not_formal', driver_pid=os.getpid(),
                  tool_sha256=sha(__file__), semantic_tests=proof, builds=builds, runs=[])
    def save():
        tmp = out / 'manifest.json.tmp'
        tmp.write_text(json.dumps(record, indent=2) + '\n')
        tmp.replace(out / 'manifest.json')
    save()
    variants = {k: v for b in builds for k, v in b['variants'].items()}
    schedule = [(d, mode, variant) for d in config['datasets'] for mode in ('serial', 'batch') for variant in variants]
    random.Random(491).shuffle(schedule)
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('RW_', 'B_'))}
    try:
        for dataset, mode, variant in schedule:
            bits = 6 if mode == 'serial' else 9
            name = f"{dataset['id']}_{mode}_{variant}_p{bits}"
            prefix = out / name
            env = ({'RW_MAX_THREADS': '1', 'RW_PAR_PART': '0', 'RW_PAR_ITER1': '0', 'RW_OVERLAP': '0',
                    'RW_BATCH_T': '0', 'RW_GPU_FLOOD': '0', 'B_SERIAL_PAGED': '1'} if mode == 'serial'
                   else dict(config['batch_environment']))
            env.update(RW_BATCH_PBITS=str(bits), B_LABEL_REPORT=str(prefix.with_suffix('.labels.json')))
            cpus = config['serial_cpu'] if mode == 'serial' else config['batch_cpus']
            command = ['taskset', '-c', cpus, variants[variant]['binary'], str(ROOT / dataset['input']), str(prefix.with_suffix('.result'))]
            row = dict(name=name, dataset=dataset['id'], mode=mode, variant=variant, page_bits=bits, environment=env, command=command)
            record['runs'].append(row)
            with prefix.with_suffix('.log').open('w') as log:
                proc = subprocess.Popen(command, env=dict(clean, **env), stdout=log, stderr=subprocess.STDOUT)
                row['pid'] = proc.pid
                save()
                code = proc.wait()
            row['exit_code'] = code
            if code:
                raise RuntimeError('Router failed: ' + name)
            metrics = parse_log(prefix.with_suffix('.log').read_text())
            reference = next(r for r in frozen['runs'] if r['dataset'] == dataset['id'] and r['mode'] == mode)
            digest = sha(prefix.with_suffix('.result'))
            if digest != dataset['reference_results'][mode] or metrics['convergence'] != reference['metrics']['convergence']:
                raise ValueError('Same-schedule mismatch: ' + name)
            row.update(verified=True, result_sha256=digest, metrics=metrics,
                       labels=json.loads(prefix.with_suffix('.labels.json').read_text()))
            save()
            print(name, metrics['route_ms'], 'ms; quality matches', flush=True)
        check_bindings(config, builds)
        record['status'] = 'passed'
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        save()
    print(out, flush=True)


if __name__ == '__main__':
    main()
