#!/usr/bin/env python3
"""Seven randomized paired blocks using the frozen full source-to-route worker."""
import argparse
import copy
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from check_source_to_route import digest
from real_experiment import write_new

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / 'data/derived/source_to_route_validation_20261023_v1'
VALIDATION_AUDIT = ROOT / 'results/source_to_route_validation_audit_20261023_v1.json'
DRIVER = ROOT / 'scripts/source_to_route_experiment.py'
CHECKER = ROOT / 'scripts/check_source_to_route.py'


def block_orders(repeats, seed):
    generator = random.Random(seed)
    orders = []
    for _ in range(repeats):
        order = list(range(3))
        generator.shuffle(order)
        orders.append(order)
    return orders


def validate(files):
    for path, expected in files.items():
        if digest(path) != expected:
            raise ValueError('Frozen statistics dependency changed: ' + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, default=125)
    args = parser.parse_args()
    output = args.output.resolve()
    if args.cpu not in os.sched_getaffinity(0):
        raise ValueError('Requested CPU unavailable')
    audit = json.loads(VALIDATION_AUDIT.read_text())
    if audit['status'] != 'all_source_to_route_integration_trials_audited' or audit['completed_workers'] != 3:
        raise ValueError('Complete independent integration validation required')
    original = VALIDATION / 'plan.json'
    if audit['artifacts'][str(original)] != digest(original):
        raise ValueError('Validation plan changed')
    # The audit binds the actual raw results, not just a success flag.
    validate(audit['artifacts'])
    base = json.loads(original.read_text())
    files = dict(base['files'])
    for path in (Path(__file__), CHECKER, original, VALIDATION_AUDIT):
        files[str(path)] = digest(path)
    validate(files)
    orders = block_orders(7, 20261023)
    plan = {'owner_pid': os.getpid(), 'cpu': args.cpu, 'repeats': 7, 'seed': 20261023,
            'conditions': base['jobs'], 'block_orders': orders, 'files': files,
            'validation_plan': str(original), 'validation_audit': str(VALIDATION_AUDIT),
            'limitations': [s for s in base['limitations'] if not s.startswith('One full integration trial')]
                + ['Seven fresh processes per condition, randomized within each repeat block.',
                   'Each application wall measures regeneration and TWO batches, not single-batch latency.',
                   'All blocks run sequentially on one CPU; unrelated host workloads remain uncontrolled.']}
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / 'plan.json', plan)
    records = []
    for repeat, order in enumerate(orders):
        validate(files)
        directory = output / f'block_{repeat:03d}'
        directory.mkdir()
        inner = copy.deepcopy(base)
        inner.update(owner_pid=os.getpid(), cpu=args.cpu, files=files,
                     limitations=plan['limitations'], statistics_repeat=repeat, execution_order=order)
        write_new(directory / 'plan.json', inner)
        for position, index in enumerate(order):
            command = [sys.executable, '-u', str(DRIVER), '--output', str(directory), '--worker', str(index)]
            log = directory / f'worker_{index:03d}.log'
            started = time.monotonic_ns()
            with log.open('x') as stream:
                child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                         preexec_fn=lambda: os.sched_setaffinity(0, {args.cpu}))
                write_new(directory / f'worker_{index:03d}.submission.json',
                          {'owner_pid': os.getpid(), 'child_pid': child.pid, 'command': command,
                           'cpu': args.cpu, 'execution_position': position, 'started_monotonic_ns': started})
                code = child.wait()
            finished = time.monotonic_ns()
            write_new(directory / f'worker_{index:03d}.receipt.json',
                      {'exit_code': code, 'worker_process_wall_ms': (finished-started)/1e6,
                       'log_sha256': digest(log), 'finished_monotonic_ns': finished})
            if code:
                raise RuntimeError(f'Full integration failed: repeat={repeat} worker={index} exit={code}')
            print('SOURCE_STATISTICS_WORKER_DONE', repeat, index, flush=True)
        # Inner plans retain stable condition indices; actual execution order is separate.
        workers = [{'condition': job, 'report': str(directory / f'worker_{i:03d}/report.json'),
                    'sha256': digest(directory / f'worker_{i:03d}/report.json')}
                   for i, job in enumerate(base['jobs'])]
        write_new(directory / 'report.json', {'status': 'all_three_full_integration_trials_verified',
                  'plan_sha256': digest(directory / 'plan.json'), 'workers': workers})
        audit_path = directory / 'audit.json'
        command = [sys.executable, '-u', str(CHECKER), str(directory), '--output', str(audit_path)]
        with (directory / 'audit.log').open('x') as stream:
            code = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT).returncode
        if code:
            raise RuntimeError(f'Independent block audit failed: repeat={repeat} exit={code}')
        result = json.loads(audit_path.read_text())
        if result['status'] != 'all_source_to_route_integration_trials_audited' or result['completed_workers'] != 3:
            raise ValueError('Independent block audit incomplete')
        records.append({'repeat': repeat, 'audit': str(audit_path), 'sha256': digest(audit_path)})
        print('SOURCE_STATISTICS_BLOCK_AUDITED', repeat, flush=True)
    write_new(output / 'report.json', {'status': 'all_seven_source_to_route_blocks_audited',
              'plan_sha256': digest(output / 'plan.json'), 'blocks': records})


if __name__ == '__main__':
    main()
