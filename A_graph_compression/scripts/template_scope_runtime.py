#!/usr/bin/env python3
"""Fair full-query first/resident measurements for CSR and four dictionary scopes."""
import argparse
import gc
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from check_source_to_route import digest, METRICS
from real_experiment import write_new
ROOT = Path(__file__).resolve().parents[1]
SCOPES = ('csr', 'global', 'span16', 'span4', 'span1')


def design(repeats):
    if repeats not in (1, 7): raise ValueError('Use validation1 or formal7 repetitions')
    generator = random.Random(20261023); jobs = []
    for repeat in range(repeats):
        block = [{'repeat': repeat, 'scope': scope} for scope in SCOPES]
        generator.shuffle(block); jobs.extend(block)
    return jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, choices=[1, 7], default=1)
    parser.add_argument('--cpu', type=int, default=126)
    args = parser.parse_args(); args.output = args.output.resolve()
    if args.cpu not in os.sched_getaffinity(0): raise ValueError('CPU unavailable')
    scope_path = ROOT/'data/derived/template_scope_region_20261023_v1/report.json'
    scope_report = json.loads(scope_path.read_text())
    if scope_report['status'] != 'all_four_full_region_template_scopes_verified': raise ValueError('Scope semantics not verified')
    baseline_path = ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    baseline = json.loads(baseline_path.read_text())
    files = dict(baseline['code_inputs_and_references'])
    for path in (Path(__file__), Path(__file__).with_name('check_template_scope_runtime.py'),
                 Path(__file__).with_name('check_source_to_route.py'), scope_path, baseline_path):
        files[str(path)] = digest(path)
    inputs = {'csr': {**baseline['inputs']['csr'], 'mode': 'csr'}}
    for variant in scope_report['variants']:
        audit_path = Path(variant['audit'])
        if digest(audit_path) != variant['audit_sha256'] or digest(variant['image']) != variant['sha256']:
            raise ValueError('Scope artifact changed')
        audit = json.loads(audit_path.read_text())
        if audit['status'] != 'complete_template_scope_equivalence_verified': raise ValueError('Scope audit incomplete')
        files.update(audit['files']); files[str(audit_path)] = digest(audit_path)
        inputs[variant['name']] = {**baseline['inputs']['compact'], 'mode': 'compact', 'image': variant['image']}
    if set(inputs) != set(SCOPES): raise ValueError('Scope matrix incomplete')
    for path, value in files.items():
        if digest(path) != value: raise ValueError('Frozen dependency changed: '+path)
    binary = ROOT/'build/native_site_runtime_20261023_v1'
    args.output.mkdir(parents=True, exist_ok=False)
    jobs = design(args.repeats)
    plan = {'owner_pid': os.getpid(), 'cpu': args.cpu, 'repeats': args.repeats, 'seed': 20261023,
            'jobs': jobs, 'files': files, 'inputs': inputs, 'references': baseline['references'], 'binary': str(binary),
            'limitations': ['Complete1062-query workload under14 physically tested site instances; remaining pseudo semantics unknown.',
                           'Dictionary sharing extent only, frozen template rules and exceptions; not family retraining or data pruning.',
                           'Native first/resident batches, cache4096, direct execution; occupancy/history reset between batches.',
                           'Preparation includes input load but excludes scope-image generation, capture and bank training.',
                           'Raw result export separate; peak is child lifetime including traces, not just graph memory.',
                           'Pinned CPU126 on shared host with uncontrolled page cache; not board or isolated-host measurements.']}
    write_new(args.output/'plan.json', plan); reports = []
    for index, job in enumerate(jobs):
        for path, value in files.items():
            if digest(path) != value: raise ValueError('Frozen runtime dependency changed: '+path)
        prefix = args.output/f'worker_{index:03d}'; inputs_here = inputs[job['scope']]
        command = [str(binary), inputs_here['image'], inputs_here['fixture'], inputs_here['sites'], '4096', '80', '200000', '8', 'direct']
        print('SCOPE_RUNTIME_BEGIN', index, job, flush=True); start = time.perf_counter()
        with prefix.with_suffix('.raw.json').open('x') as stream, prefix.with_suffix('.log').open('x') as log:
            child = subprocess.Popen(command, stdout=stream, stderr=log,
                                     preexec_fn=lambda: os.sched_setaffinity(0, {args.cpu}))
            write_new(prefix.with_suffix('.submission.json'), {'owner_pid': os.getpid(), 'child_pid': child.pid,
                      'command': command, 'cpu': args.cpu, 'condition': job})
            code = child.wait()
        wall = (time.perf_counter()-start)*1000
        receipt = {'exit_code': code, 'process_wall_ms': wall, 'raw_sha256': digest(prefix.with_suffix('.raw.json')),
                   'log_sha256': digest(prefix.with_suffix('.log'))}
        write_new(prefix.with_suffix('.receipt.json'), receipt)
        if code: raise RuntimeError('Full native scope trial failed: '+str(index))
        raw = json.loads(prefix.with_suffix('.raw.json').read_text())
        reference = json.loads(Path(plan['references'][inputs_here['mode']]).read_text())
        expected = {k: v for k, v in reference.items() if k not in METRICS}
        if raw['execution'] != 'direct' or len(raw['batches']) != 2 or len(raw['export_ms']) != 2: raise ValueError('Batch protocol differs')
        for batch in raw['batches']:
            if {k: v for k, v in batch.items() if k not in METRICS} != expected: raise ValueError('Full route semantics differ')
        report = {'condition': job, 'status': 'two_full_scope_batches_equivalent', 'process_wall_ms': wall,
                  'batches': [{k: batch[k] for k in METRICS} for batch in raw['batches']],
                  'export_ms': raw['export_ms'], 'materialization_ms': raw['materialization_ms'], 'raw_sha256': receipt['raw_sha256']}
        path = prefix.with_suffix('.json'); write_new(path, report)
        reports.append({'path': str(path), 'sha256': digest(path)})
        del raw, reference, expected; gc.collect(); print('SCOPE_RUNTIME_VERIFIED', index, flush=True)
    write_new(args.output/'report.json', {'status': 'all_scope_runtime_workers_verified',
              'plan_sha256': digest(args.output/'plan.json'), 'workers': reports})


if __name__ == '__main__': main()
