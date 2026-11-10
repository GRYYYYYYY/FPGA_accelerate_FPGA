#!/usr/bin/env python3
"""Re-read raw first/resident results and independently audit the trial matrix."""
import argparse
import gc
import json
import math
from pathlib import Path
import random
import statistics
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'src')]
import hashlib

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
from real_experiment import write_new

METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}


def audit(directory,capacities,repeats,partial=False):
    plan_path=directory/'plan.json';plan=json.loads(plan_path.read_text())
    generator=random.Random(plan['seed']);expected_jobs=[]
    for repeat in range(repeats):
        block=[{'repeat':repeat,'mode':mode,'execution':execution,'capacity':cap}
               for mode,execution in [('csr','direct'),('compact','direct'),('compact','expanded')]
               for cap in capacities]
        generator.shuffle(block);expected_jobs.extend(block)
    if plan['jobs']!=expected_jobs:raise ValueError('Trial design/order differs from requested matrix')
    for path,digest in plan['code_inputs_and_references'].items():
        if sha256(Path(path))!=digest:raise ValueError('Frozen input/code/reference changed: '+path)
    artifacts={str(plan_path):sha256(plan_path)};records=[];cached_mode=None;reference=None
    for index,condition in enumerate(expected_jobs):
        prefix=directory/f'worker_{index:03d}';worker_path=prefix.with_suffix('.json')
        if not worker_path.exists():
            if partial:continue
            raise ValueError('Missing completed worker: '+str(index))
        record=json.loads(worker_path.read_text());receipt_path=prefix.with_suffix('.receipt.json')
        receipt=json.loads(receipt_path.read_text());raw_path=prefix.with_suffix('.raw.json');log_path=prefix.with_suffix('.log')
        if record['condition']!=condition or not record['both_complete_batches_verified']:
            raise ValueError('Worker condition or declared validation differs')
        if receipt['exit_code'] or sha256(raw_path)!=receipt['raw_sha256'] or receipt['raw_sha256']!=record['raw_sha256']:
            raise ValueError('Native raw result/receipt mismatch')
        if sha256(log_path)!=receipt['log_sha256']:raise ValueError('Native log changed')
        if receipt['process_wall_ms']!=record['process_wall_ms']:raise ValueError('Process measurement changed')
        mode=condition['mode']
        if cached_mode!=mode:
            reference=None;gc.collect()
            reference=json.loads(Path(plan['references'][mode]).read_text())
            reference={k:v for k,v in reference.items() if k not in METRICS};cached_mode=mode
        submission_path=prefix.with_suffix('.submission.json');submission=json.loads(submission_path.read_text())
        inputs=plan['inputs'][mode]
        expected_command=[str(ROOT/'build/native_site_runtime_20261023_v1'),inputs['image'],inputs['fixture'],inputs['sites'],
                          str(condition['capacity']),'80','200000','8',condition['execution']]
        if submission['command']!=expected_command or submission['owner_pid']!=plan['owner_pid']:
            raise ValueError('Execution submission differs from plan')
        artifacts[str(submission_path)]=sha256(submission_path)
        raw=json.loads(raw_path.read_text())
        if raw['execution']!=condition['execution']:raise ValueError('Executed representation differs')
        if raw['materialization_ms']!=record['materialization_ms'] or not math.isfinite(raw['materialization_ms']) or raw['materialization_ms']<0:
            raise ValueError('Invalid/changed materialization timing')
        if len(raw['batches'])!=2 or len(raw['export_ms'])!=2:raise ValueError('Missing first/resident batch')
        if raw['export_ms']!=record['export_ms']:raise ValueError('Export times changed')
        if any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in raw['export_ms']):
            raise ValueError('Invalid export timing')
        if not math.isfinite(record['process_wall_ms']) or record['process_wall_ms']<0:
            raise ValueError('Invalid process wall timing')
        for batch,measurement in zip(raw['batches'],record['batches']):
            if {k:v for k,v in batch.items() if k not in METRICS}!=reference:
                raise ValueError('Raw complete workload semantics differ: '+str(index))
            if measurement!={k:batch[k] for k in METRICS}:raise ValueError('Raw/summary metrics differ')
            if batch['status']!='routed' or len(batch['routes'])!=1062:raise ValueError('Incomplete real workload')
            for key,value in measurement.items():
                if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
                    raise ValueError('Invalid numeric measurement: '+key)
        if len(record['batches'])!=2:raise ValueError('Summary batch count differs')
        first,resident=record['batches']
        if resident['peak_kib']<first['peak_kib']:raise ValueError('Lifetime peak RSS decreased')
        if first['preparation_ms']+0.001<raw['materialization_ms']:raise ValueError('Materialization not included in preparation')
        if first['preparation_ms']!=resident['preparation_ms']:raise ValueError('Shared preparation differs')
        accounted=first['preparation_ms']+sum(b['route_ms'] for b in record['batches'])+sum(raw['export_ms'])
        if record['process_wall_ms']+2<accounted:raise ValueError('Process wall time below measured components')
        for path in (worker_path,receipt_path,raw_path,log_path):artifacts[str(path)]=sha256(path)
        records.append(record);del raw;gc.collect()
    if not records:raise ValueError('No completed workers available for audit')
    summaries=[]
    for mode,execution,capacity in sorted({(r['condition']['mode'],r['condition']['execution'],r['condition']['capacity']) for r in records}):
        selected=[r for r in records if (r['condition']['mode'],r['condition']['execution'],r['condition']['capacity'])==(mode,execution,capacity)]
        summaries.append({'mode':mode,'execution':execution,'capacity':capacity,'n':len(selected),
            'preparation_ms_median':statistics.median(r['batches'][0]['preparation_ms'] for r in selected),
            'first_route_ms_median':statistics.median(r['batches'][0]['route_ms'] for r in selected),
            'resident_route_ms_median':statistics.median(r['batches'][1]['route_ms'] for r in selected),
            'first_preparation_plus_route_ms_median':statistics.median(r['batches'][0]['preparation_ms']+r['batches'][0]['route_ms'] for r in selected),
            'export_first_ms_median':statistics.median(r['export_ms'][0] for r in selected),
            'export_resident_ms_median':statistics.median(r['export_ms'][1] for r in selected),
            'process_wall_ms_median':statistics.median(r['process_wall_ms'] for r in selected),
            'peak_native_kib':[max(b['peak_kib'] for b in r['batches']) for r in selected]})
    if not partial:
        final_path=directory/'report.json';final=json.loads(final_path.read_text())
        if final['status']!='all_complete_site_batches_equivalent' or final['workers']!=len(expected_jobs):
            raise ValueError('Final report incomplete')
        if final['plan_sha256']!=sha256(plan_path):raise ValueError('Final report plan differs')
        expected_workers={f'worker_{i:03d}.json':sha256(directory/f'worker_{i:03d}.json') for i in range(len(expected_jobs))}
        if final['worker_sha256']!=expected_workers:raise ValueError('Final worker domain/hashes differ')
        projected=[{k:v for k,v in summary.items() if k not in ('first_preparation_plus_route_ms_median','export_first_ms_median','export_resident_ms_median')} for summary in summaries]
        if final['summaries']!=projected:raise ValueError('Final summary differs from independent recomputation')
        artifacts[str(final_path)]=sha256(final_path)
    return {'status':'partial_completed_workers_audited' if partial else 'complete_site_runtime_matrix_independently_audited',
        'completed_workers':len(records),'planned_workers':len(expected_jobs),'summaries':summaries,
        'all_raw_complete_workloads_rechecked':True,'artifacts':artifacts,
        'auditor_sha256':sha256(Path(__file__)),
        'limitations':plan['limitations']+['No confidence interval or significance claim is inferred from incomplete trials.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path)
    p.add_argument('--capacities',nargs='+',type=int,default=[0,64,4096]);p.add_argument('--repeats',type=int,default=7)
    p.add_argument('--partial',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=audit(a.experiment,a.capacities,a.repeats,a.partial);write_new(a.output,report)
    print(json.dumps({'output':str(a.output),'status':report['status'],'completed_workers':report['completed_workers']}))


if __name__=='__main__':main()
