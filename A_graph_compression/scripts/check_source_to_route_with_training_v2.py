#!/usr/bin/env python3
"""Audit actual regenerated-input consumption and complete source-to-route timing."""
import argparse
import gc
import hashlib
import json
import math
from pathlib import Path
import random
from real_experiment import write_new
from fresh_training_contract_v1 import TRAINING_STAGES,validate_training
from native_output_segments_v1 import audit_native_output
ROOT=Path(__file__).resolve().parents[1]
METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}
STAGES={'read_export_ms','bank_load_ms','serialize_ms','evidence_load_ms','image_adapter_load_ms',
        'fixture_build_ms','fixture_write_ms','generated_input_validation_ms','pre_native_cleanup_ms','native_process_ms'} | TRAINING_STAGES


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def check_timing(report,outer_receipt,native_receipt,raw):
    times=report['stage_ms']
    if set(times)!=STAGES:raise ValueError('Incomplete stage accounting')
    values=[*times.values(),report['application_wall_ms'],report['post_route_audit_ms'],outer_receipt['worker_process_wall_ms']]
    values.extend(raw['export_ms']);values.append(raw['materialization_ms'])
    for b in raw['batches']:values.extend(b[k] for k in METRICS)
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values):raise ValueError('Invalid timing/counter')
    if report['application_wall_ms']+2<sum(times.values()):raise ValueError('Application excludes measured stages')
    if outer_receipt['worker_process_wall_ms']+2<report['application_wall_ms']+report['post_route_audit_ms']:raise ValueError('Worker wall excludes application/audit')
    if native_receipt['process_wall_ms']!=times['native_process_ms']:raise ValueError('Native wall differs')
    first,resident=raw['batches']
    if first['preparation_ms']!=resident['preparation_ms'] or first['preparation_ms']+0.001<raw['materialization_ms']:
        raise ValueError('Preparation/materialization mismatch')
    native=first['preparation_ms']+sum(b['route_ms'] for b in raw['batches'])+sum(raw['export_ms'])
    if times['native_process_ms']+2<native:raise ValueError('Native process excludes components')
    if resident['peak_kib']<first['peak_kib'] or report['native_child_peak_kib']<resident['peak_kib']:
        raise ValueError('Inconsistent lifetime peaks')
    if report['parent_pre_native_peak_kib']<=0:raise ValueError('Missing preparation peak')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path)
    p.add_argument('--partial',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args();directory=a.experiment.resolve()
    plan_path=directory/'plan.json';plan=json.loads(plan_path.read_text());jobs=[{'mode':m,'execution':e} for m,e in [('csr','direct'),('compact','direct'),('compact','expanded')]]
    random.Random(20261023).shuffle(jobs)
    if plan['jobs']!=jobs:raise ValueError('Integration condition domain/order differs')
    for name,value in plan['files'].items():
        if digest(name)!=value:raise ValueError('Frozen pipeline evidence changed: '+name)
    rebuild_path=ROOT/'data/derived/runtime_fixture_rebuild_20261023_v1/report.json';rebuild=json.loads(rebuild_path.read_text())
    for path in (ROOT/'src/runtime_fixture_builder.py',ROOT/'src/packed_graph.py',ROOT/'src/netlist.py',ROOT/'src/lut_equation.py'):
        if digest(path)!=rebuild['files'][str(path)]:raise ValueError('Verified fixture builder dependency changed')
    artifacts={str(plan_path):digest(plan_path)};summaries=[]
    for index,job in enumerate(jobs):
        worker=directory/f'worker_{index:03d}';outer_path=directory/f'worker_{index:03d}.receipt.json'
        if a.partial and not outer_path.exists():continue
        report_path=worker/'report.json';report=json.loads(report_path.read_text());outer=json.loads(outer_path.read_text())
        if report['status']!='regenerated_inputs_and_two_full_batches_verified' or report['condition']!=job or outer['exit_code']:
            raise ValueError('Worker failed or scope differs')
        submission_path=directory/f'worker_{index:03d}.submission.json';submission=json.loads(submission_path.read_text())
        if submission['cpu']!=plan['cpu'] or submission['owner_pid']!=plan['owner_pid']:raise ValueError('Outer execution binding differs')
        if submission['command'][-4:]!=['--output',str(directory),'--worker',str(index)]:raise ValueError('Executed worker differs')
        if digest(directory/f'worker_{index:03d}.log')!=outer['log_sha256']:raise ValueError('Worker log changed')
        if report['counts']!=rebuild['modes'][job['mode']]['counts']:raise ValueError('Complete fixture scope differs')
        expected=plan['expected_inputs'][job['mode']]
        for name,value in expected.items():
            if digest(worker/name)!=value or report['artifacts'][name]!=value:raise ValueError('Regenerated input differs')
        native_submission=json.loads((worker/'native.submission.json').read_text());native_receipt=json.loads((worker/'native.receipt.json').read_text())
        command=[plan['binary'],str(worker/'image.agr'),str(worker/'routing.txt'),str(worker/'sites.txt'),'4096','80','200000','8',job['execution']]
        if native_submission['command']!=command or native_submission['owner_pid']!=submission['child_pid'] or native_submission['inherited_cpu']!=plan['cpu']:
            raise ValueError('Native did not consume this worker regenerated inputs')
        if native_receipt['exit_code']:raise ValueError('Native failed')
        for name,value in report['artifacts'].items():
            if digest(worker/name)!=value:raise ValueError('Worker artifact changed')
        reference=plan['references'][job['mode']]
        raw=audit_native_output(worker/'native.raw.json',reference,plan['files'][reference],job['execution'])
        if report['semantic_audit']!=raw['semantic_audit']:raise ValueError('Complete output comparison receipt differs')
        receipt_keys=['condition','counts','training','address_space_limit_bytes','application_wall_ms','stage_ms',
                      'parent_pre_native_peak_kib','native_child_peak_kib']
        application=json.loads((worker/'application.receipt.json').read_text())
        if application!=dict(status='native_returned_zero_output_audit_pending',**{key:report[key] for key in receipt_keys}):
            raise ValueError('Preserved application timing receipt differs')
        if report['artifacts'].get('application.receipt.json')!=digest(worker/'application.receipt.json'):
            raise ValueError('Application receipt not bound')
        if report['batches']!=[{k:b[k] for k in METRICS} for b in raw['batches']] or report['export_ms']!=raw['export_ms'] or report['materialization_ms']!=raw['materialization_ms']:
            raise ValueError('Reported native metrics differ')
        validate_training(plan,job,worker,report)
        if report['address_space_limit_bytes']!=16*1024**3:raise ValueError('Wrong worker AS limit')
        check_timing(report,outer,native_receipt,raw)
        summaries.append({'condition':job,'application_wall_ms':report['application_wall_ms'],'stage_ms':report['stage_ms'],
                          'worker_process_wall_ms':outer['worker_process_wall_ms'],'parent_pre_native_peak_kib':report['parent_pre_native_peak_kib'],
                          'native_child_peak_kib':report['native_child_peak_kib']})
        for path in (report_path,outer_path,submission_path):artifacts[str(path)]=digest(path)
        artifacts.update({str(worker/name):value for name,value in report['artifacts'].items()})
        del raw;gc.collect()
    if not summaries:raise ValueError('No completed integration workers')
    if not a.partial:
        final_path=directory/'report.json';final=json.loads(final_path.read_text())
        expected_workers=[{'condition':job,'report':str(directory/f'worker_{i:03d}/report.json'),'sha256':digest(directory/f'worker_{i:03d}/report.json')} for i,job in enumerate(jobs)]
        if final['status']!='all_three_full_integration_trials_verified' or final['plan_sha256']!=digest(plan_path) or final['workers']!=expected_workers:raise ValueError('Incomplete final integration report')
        artifacts[str(final_path)]=digest(final_path)
    result={'status':'partial_source_to_route_workers_audited' if a.partial else 'all_source_to_route_integration_trials_audited',
            'completed_workers':len(summaries),'planned_workers':3,'summaries':summaries,'artifacts':artifacts,
            'auditor_sha256':digest(Path(__file__)),'limitations':plan['limitations']}
    write_new(a.output,result);print(json.dumps({'status':result['status'],'workers':len(summaries)}))


if __name__=='__main__':main()
