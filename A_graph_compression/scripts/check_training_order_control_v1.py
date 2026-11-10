#!/usr/bin/env python3
"""Accept all six supplemental order permutations and18 full original-oracle workers."""
import argparse
import copy
import json
import math
from pathlib import Path
import random
import statistics
from check_source_to_route import digest
from real_experiment import write_new
from training_order_control_contract_v1 import schedule,validate_schedule,SEED,CPU,AS_BYTES,POLICY,ACCEPTED,CONTROL,PREPARATION,ORIGINAL,OUT
from owned_sim_resource_policy_v1 import abort_reason
from check_vitis_kernel import require


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
    expected = {(r, m, e) for r in range(6) for m, e in conditions}
    keys = [(r['repeat'], r['condition']['mode'], r['condition']['execution']) for r in records]
    if len(keys) != 18 or len(set(keys)) != 18 or set(keys) != expected:
        raise ValueError('Incomplete or duplicate six-permutation matrix')
    metrics = ('application_wall_ms', 'worker_process_wall_ms', 'parent_pre_native_peak_kib', 'native_child_peak_kib')
    for record in records:
        for key in metrics:
            value = record[key]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError('Invalid full-process measurement')
    summaries = []
    for mode, execution in sorted(conditions):
        selected = [r for r in records if r['condition'] == {'mode': mode, 'execution': execution}]
        if len(selected) != 6:
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
                  lookup[r, 'csr', 'direct']['application_wall_ms'] for r in range(6)]
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
    require(directory==OUT,'Different supplemental trial')
    plan_path = directory / 'plan.json'
    plan = json.loads(plan_path.read_text())
    if plan['repeats'] != 6 or plan['seed'] != SEED:
        raise ValueError('Unexpected repeat design')
    orders = schedule()
    validate_schedule(plan['block_orders'])
    if plan['block_orders'] != orders:
        raise ValueError('Randomized execution schedule changed')
    for path, value in plan['files'].items():
        if digest(path) != value:
            raise ValueError('Statistics dependency changed: ' + path)
    require(plan['cpu']==CPU and plan['resource_policy']==POLICY and plan['worker_as_bytes']==AS_BYTES,'Wrong supplemental resource/CPU policy')
    require(plan['original_seven_block_report']==str(ORIGINAL) and plan['original_seven_block_sha256']==digest(ORIGINAL),'Original seven-block evidence changed')
    guard=json.loads((CONTROL/'six_complete_permutations.receipt.json').read_text())
    require(guard['exit_code']==0 and guard['resource_abort'] is False and guard['resource_policy']==POLICY and abort_reason(guard['start_memory'],guard['end_memory']) is None,'Failed or unguarded supplemental execution')
    control_plan=json.loads((CONTROL/'plan.json').read_text())
    require(guard['command']==control_plan['commands'][0][1] and guard['plan_sha256']==digest(CONTROL/'plan.json') and guard['log_sha256']==digest(CONTROL/'six_complete_permutations.log') and guard['elapsed_seconds']>0,'Different guarded execution receipt')
    require(guard['actual_owner_limits']['address_space']==[AS_BYTES]*2 and guard['actual_owner_limits']['core']==[0,0] and guard['actual_owner_limits']['cpu']==[CPU],'Wrong guarded driver limits')
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
        checker = Path(__file__).with_name('check_source_to_route_with_training_v2.py')
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
            limit_path=block/f'worker_{index:03d}.actual_limits.json'
            limits=json.loads(limit_path.read_text())
            require(limits['owner']['pid']==submissions[index]['child_pid'] and limits['argv']==submissions[index]['command'] and limits['address_space']==[AS_BYTES]*2 and limits['core']==[0,0] and limits['cpu']==[CPU],'Wrong actual full worker limits')
            artifacts[str(limit_path)]=digest(limit_path)
            native_path=block/f'worker_{index:03d}.native_limits.json'
            native=json.loads(native_path.read_text())
            submitted=json.loads((block/f'worker_{index:03d}/native.submission.json').read_text())
            require(native['owner']['pid']==submitted['child_pid'] and native['argv']==submitted['command'] and native['address_space']==[AS_BYTES]*2 and native['core']==[0,0] and native['cpu']==[CPU],'Wrong actual native limits')
            artifacts[str(native_path)]=digest(native_path)
            summary = audit['summaries'][index]
            if summary['condition'] != condition:
                raise ValueError('Audited condition differs')
            records.append({'repeat': repeat, **summary})
        previous_end = check_sequence(order, submissions, receipts, plan['owner_pid'], plan['cpu'], previous_end)
        blocks.append({'repeat': repeat, 'audit': str(audit_path), 'sha256': digest(audit_path)})
        artifacts[str(audit_path)] = digest(audit_path)
    final_path = directory / 'report.json'
    final = json.loads(final_path.read_text())
    if final != {'status': 'all_six_order_control_blocks_audited', 'plan_sha256': digest(plan_path), 'blocks': blocks}:
        raise ValueError('Final statistics completion receipt differs')
    for path in [CONTROL/'plan.json',CONTROL/'six_complete_permutations.receipt.json',CONTROL/'six_complete_permutations.log',PREPARATION,ORIGINAL]:artifacts[str(path)]=digest(path)
    state=json.loads((directory/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='all18_full_workers_and_six_original_block_audits_complete' and (state['completed_workers'],state['completed_blocks'])==(18,6),'Incomplete driver terminal state')
    artifacts[str(directory/'state.json')]=digest(directory/'state.json')
    summaries, paired = summarize(records)
    artifacts[str(final_path)] = digest(final_path)
    write_new(args.output, {'status': ACCEPTED, 'completed_workers': 18, 'completed_blocks': 6, 'orders':orders, 'resource_policy':POLICY, 'supplemental_to_original_seven_blocks':True,
              'summaries': summaries, 'paired_comparisons': paired, 'workers': records, 'artifacts': artifacts,
              'auditor_sha256': digest(Path(__file__)), 'limitations': plan['limitations']})
    print('SIX_PERMUTATION_FULL_WORKLOAD_AUDITED 18')


if __name__ == '__main__':
    main()
