#!/usr/bin/env python3
"""Aggregate seven independently raw-audited blocks and verify their execution bindings."""
import argparse
import copy
import json
import math
from pathlib import Path
import random
import statistics
from check_source_to_route import digest
from real_experiment import write_new


def check_sequence(order, submissions, receipts, owner, cpu, previous_end=0):
    if sorted(order) != [0, 1, 2]:
        raise ValueError('Missing or duplicate condition')
    for position, index in enumerate(order):
        submission, receipt = submissions[index], receipts[index]
        start, end = submission['started_monotonic_ns'], receipt['finished_monotonic_ns']
        if type(start) is not int or type(end) is not int or start < previous_end or end <= start:
            raise ValueError('Execution reordered, overlapping, or invalid clock')
        if submission['execution_position'] != position or submission['owner_pid'] != owner or submission['cpu'] != cpu:
            raise ValueError('Execution order/owner/CPU differs')
        if receipt['exit_code'] or not math.isclose(receipt['worker_process_wall_ms'], (end-start)/1e6, abs_tol=1e-6):
            raise ValueError('Failed process or timing receipt differs')
        previous_end = end
    return previous_end


def summarize(records):
    conditions = {('csr', 'direct'), ('compact', 'direct'), ('compact', 'expanded')}
    expected = {(r, m, e) for r in range(7) for m, e in conditions}
    keys = [(r['repeat'], r['condition']['mode'], r['condition']['execution']) for r in records]
    if len(keys) != 21 or len(set(keys)) != 21 or set(keys) != expected:
        raise ValueError('Incomplete or duplicate seven-repeat matrix')
    metrics = ('application_wall_ms', 'worker_process_wall_ms', 'parent_pre_native_peak_kib', 'native_child_peak_kib')
    for record in records:
        for key in metrics:
            value = record[key]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError('Invalid full-process measurement')
    summaries = []
    for mode, execution in sorted(conditions):
        selected = [r for r in records if r['condition'] == {'mode': mode, 'execution': execution}]
        if len(selected) != 7:
            raise ValueError('Unexpected condition attributes')
        summaries.append({'mode': mode, 'execution': execution, 'n': len(selected),
                          'measurements': {key: {'median': statistics.median(r[key] for r in selected),
                                                'min': min(r[key] for r in selected),
                                                'max': max(r[key] for r in selected)} for key in metrics},
                          'stage_medians_ms': {key: statistics.median(r['stage_ms'][key] for r in selected)
                                               for key in selected[0]['stage_ms']}})
    paired = []
    lookup = {key: r for key, r in zip(keys, records)}
    for execution in ('direct', 'expanded'):
        ratios = [lookup[r, 'compact', execution]['application_wall_ms'] /
                  lookup[r, 'csr', 'direct']['application_wall_ms'] for r in range(7)]
        paired.append({'numerator': 'compact/' + execution, 'denominator': 'csr/direct',
                       'metric': 'application_wall_ms', 'ratios_by_repeat': ratios,
                       'median_paired_ratio': statistics.median(ratios)})
    return summaries, paired


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    directory = args.experiment.resolve()
    plan_path = directory / 'plan.json'
    plan = json.loads(plan_path.read_text())
    if plan['repeats'] != 7 or plan['seed'] != 20261023:
        raise ValueError('Unexpected repeat design')
    generator = random.Random(20261023)
    orders = []
    for _ in range(7):
        order = [0, 1, 2]
        generator.shuffle(order)
        orders.append(order)
    if plan['block_orders'] != orders:
        raise ValueError('Randomized execution schedule changed')
    for path, value in plan['files'].items():
        if digest(path) != value:
            raise ValueError('Statistics dependency changed: ' + path)
    base = json.loads(Path(plan['validation_plan']).read_text())
    if base.get('training_inclusive') is not True:raise ValueError('Fresh-training protocol missing')
    if plan['conditions'] != base['jobs']:
        raise ValueError('Conditions differ from validated protocol')
    validation = json.loads(Path(plan['validation_audit']).read_text())
    if validation['status'] != 'all_source_to_route_integration_trials_audited' or validation['completed_workers'] != 3:
        raise ValueError('Missing full integration validation')
    records, blocks, artifacts = [], [], {str(plan_path): digest(plan_path)}
    previous_end = 0
    for repeat, order in enumerate(orders):
        block = directory / f'block_{repeat:03d}'
        inner_path = block / 'plan.json'
        inner = json.loads(inner_path.read_text())
        expected = copy.deepcopy(base)
        expected.update(owner_pid=plan['owner_pid'], cpu=plan['cpu'], files=plan['files'],
                        limitations=plan['limitations'], statistics_repeat=repeat, execution_order=order)
        if inner != expected:
            raise ValueError('Inner block protocol or inputs changed')
        audit_path = block / 'audit.json'
        audit = json.loads(audit_path.read_text())
        checker = Path(__file__).with_name('check_source_to_route_with_training_v1.py')
        if audit['auditor_sha256'] != digest(checker) or audit['status'] != 'all_source_to_route_integration_trials_audited' or audit['completed_workers'] != 3:
            raise ValueError('Block independent audit incomplete')
        if audit['artifacts'][str(inner_path)] != digest(inner_path):
            raise ValueError('Block audit belongs to another plan')
        # Rehash every audited raw artifact once; semantic checking was done by the frozen block auditor.
        for path, value in audit['artifacts'].items():
            if digest(path) != value:
                raise ValueError('Audited block artifact changed: ' + path)
        submissions, receipts = {}, {}
        for index, condition in enumerate(plan['conditions']):
            submission_path = block / f'worker_{index:03d}.submission.json'
            receipt_path = block / f'worker_{index:03d}.receipt.json'
            for path in (submission_path, receipt_path):
                if str(path) not in audit['artifacts']:
                    raise ValueError('Execution receipt was not independently bound')
            submissions[index] = json.loads(submission_path.read_text())
            receipts[index] = json.loads(receipt_path.read_text())
            summary = audit['summaries'][index]
            if summary['condition'] != condition:
                raise ValueError('Audited condition differs')
            records.append({'repeat': repeat, **summary})
        previous_end = check_sequence(order, submissions, receipts, plan['owner_pid'], plan['cpu'], previous_end)
        blocks.append({'repeat': repeat, 'audit': str(audit_path), 'sha256': digest(audit_path)})
        artifacts[str(audit_path)] = digest(audit_path)
    final_path = directory / 'report.json'
    final = json.loads(final_path.read_text())
    if final != {'status': 'all_seven_source_to_route_blocks_audited', 'plan_sha256': digest(plan_path), 'blocks': blocks}:
        raise ValueError('Final statistics completion receipt differs')
    summaries, paired = summarize(records)
    artifacts[str(final_path)] = digest(final_path)
    write_new(args.output, {'status': 'complete_source_to_route_statistics_audited', 'completed_workers': 21,
              'summaries': summaries, 'paired_comparisons': paired, 'workers': records, 'artifacts': artifacts,
              'auditor_sha256': digest(Path(__file__)), 'limitations': plan['limitations']})
    print('SOURCE_TO_ROUTE_STATISTICS_AUDITED 21')


if __name__ == '__main__':
    main()
