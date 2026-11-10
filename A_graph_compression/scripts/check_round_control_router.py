#!/usr/bin/env python3
"""Compare all raw full-workload outputs with the already audited production router."""
import argparse
import gc
import json
import math
from pathlib import Path
import re

from check_vitis_kernel import digest, require

METRICS = {'preparation_ms', 'route_ms', 'peak_kib', 'logical_bytes', 'cache_hits', 'cache_misses'}
NAMES = ('CONTROLLER_COUNTERS', 'SNAPSHOT_COUNTERS', 'KERNEL_COUNTERS')


def semantic_batch(batch):
    require(METRICS <= batch.keys(), 'Missing measured fields')
    require(batch['status'] == 'routed' and len(batch['routes']) == 1062, 'Incomplete real workload')
    require(batch['logical_bytes'] == batch['cache_hits'] == batch['cache_misses'] == 0, 'Native adjacency fallback')
    for key in METRICS: require(math.isfinite(batch[key]) and batch[key] >= 0, 'Invalid metric ' + key)
    return {k: v for k, v in batch.items() if k not in METRICS}


def counters(log):
    out = {}
    for name in NAMES:
        lines = re.findall(r'^' + name + r' (\d+(?: \d+)*)$', log, re.M)
        require(len(lines) == 2, 'Missing counter batches: ' + name)
        rows = [list(map(int, row.split())) for row in lines]
        require([r[0] for r in rows] == [0, 1], 'Counter batch order differs')
        out[name] = rows
    return out


def audit(bundle, output):
    require(not output.exists(), 'Refusing to overwrite audit')
    plan = json.loads((bundle / 'plan.json').read_text())
    execution = json.loads((bundle / 'execution_plan.json').read_text())
    for p, sha in execution['files'].items(): require(digest(p) == sha, 'Changed execution dependency: ' + p)
    prepared = json.loads((bundle / 'report.json').read_text())
    require(prepared['status'] == 'round_control_full_search_cpu_differential_verified_full_workload_pending', 'Missing preparation proof')
    for p, sha in {**prepared['files'], **prepared['artifacts']}.items(): require(digest(p) == sha, 'Changed prepared artifact ' + p)
    old_audit_path = Path(__file__).resolve().parents[1] / 'results/retained_nodes_router_audit_20261024_v1.json'; old_audit = json.loads(old_audit_path.read_text())
    require(old_audit['status'] == 'retained_nodes_two_full_router_conditions_independently_verified', 'Unverified predecessor')
    require([(j['mode'], j['execution']) for j in plan['jobs']] == [('csr', 'kernel'), ('compact', 'kernel')], 'Incomplete matrix')
    bound = {}; results = []
    for path in [bundle / 'plan.json', bundle / 'execution_plan.json', bundle / 'report.json', old_audit_path]:bound[str(path)] = digest(path)
    for i, job in enumerate(plan['jobs']):
        prefix = bundle / f'worker_{i:03d}'; old_prefix = Path(plan['prior_bundle']) / f'worker_{i:03d}'
        receipt_path = prefix.with_suffix('.receipt.json'); submit_path = prefix.with_suffix('.submission.json')
        receipt = json.loads(receipt_path.read_text()); submitted = json.loads(submit_path.read_text())
        inp = plan['inputs'][job['mode']]
        command = ['taskset', '-c', str(job['cpu']), plan['binary'], inp['image'], inp['fixture'], inp['sites'],
                   '4096', '80', '200000', '8', 'kernel', inp['config']]
        require(receipt['command'] == submitted['command'] == command and receipt['condition'] == submitted['condition'] == job
                and receipt['exit_code'] == 0 and submitted['execution_plan_sha256'] == digest(bundle / 'execution_plan.json'),
                'Wrong or failed workload execution')
        require(math.isfinite(receipt['process_wall_ms']) and receipt['process_wall_ms'] > 0, 'Invalid process wall')
        old_log = old_prefix.with_suffix('.log'); old_raw = old_prefix.with_suffix('.raw.json')
        for path in [old_log, old_raw]:require(digest(path) == old_audit['files'][str(path)], 'Changed predecessor raw evidence')
        log = prefix.with_suffix('.log'); raw_path = prefix.with_suffix('.raw.json')
        require(digest(log) == receipt['log_sha256'] and digest(raw_path) == receipt['raw_sha256'], 'New raw evidence drift')
        actual_counters = counters(log.read_text()); expected_counters = counters(old_log.read_text())
        require(actual_counters == expected_counters, 'Search/snapshot/ABI counters differ from full predecessor')
        actual = json.loads(raw_path.read_text()); expected = json.loads(old_raw.read_text())
        require(actual['execution'] == expected['execution'] == 'kernel', 'Wrong execution mode')
        require(len(actual['batches']) == len(expected['batches']) == len(actual['export_ms']) == 2, 'Missing complete batches')
        for a, b in zip(actual['batches'], expected['batches']):
            require(semantic_batch(a) == semantic_batch(b), 'Full paths, states, site demands or negotiation rounds differ')
        for value in [actual['materialization_ms'], *actual['export_ms']]:require(math.isfinite(value) and value >= 0, 'Invalid runtime metric')
        results.append(dict(condition=job, full_batches_verified=2, routes_per_batch=1062, counters=actual_counters))
        for path in [receipt_path, submit_path, log, raw_path, old_log, old_raw]: bound[str(path)] = digest(path)
        del actual, expected;gc.collect()
    result = dict(status='round_control_two_full_router_conditions_independently_verified',
                  files=bound, results=results, hardware_executed=False, limitations=plan['limitations'])
    with output.open('x') as stream:json.dump(result, stream, indent=2);stream.write('\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();audit(a.bundle.resolve(), a.output.resolve())
