#!/usr/bin/env python3
"""Re-read all scope-routing raw results and independently audit full matrix semantics."""
import argparse
import gc
import json
import math
from pathlib import Path
import random
import statistics
from check_source_to_route import digest, METRICS
from real_experiment import write_new


def check_worker(plan, job, submission, receipt, record, raw, reference):
    inputs = plan['inputs'][job['scope']]
    command = [plan['binary'], inputs['image'], inputs['fixture'], inputs['sites'], '4096', '80', '200000', '8', 'direct']
    if submission['command'] != command or submission['condition'] != job or submission['cpu'] != plan['cpu'] or submission['owner_pid'] != plan['owner_pid']:
        raise ValueError('Execution/image/CPU binding differs')
    if record['condition'] != job or record['status'] != 'two_full_scope_batches_equivalent' or receipt['exit_code']:
        raise ValueError('Worker failed or wrong condition')
    if record['process_wall_ms'] != receipt['process_wall_ms'] or record['raw_sha256'] != receipt['raw_sha256']:
        raise ValueError('Worker receipt differs')
    if raw['execution'] != 'direct' or len(raw['batches']) != 2 or len(raw['export_ms']) != 2:
        raise ValueError('Wrong first/resident protocol')
    expected = {k: v for k, v in reference.items() if k not in METRICS}
    for batch in raw['batches']:
        if {k: v for k, v in batch.items() if k not in METRICS} != expected or batch['status'] != 'routed' or len(batch['routes']) != 1062:
            raise ValueError('Complete actual workload differs')
    if record['batches'] != [{k: b[k] for k in METRICS} for b in raw['batches']] or record['export_ms'] != raw['export_ms'] or record['materialization_ms'] != raw['materialization_ms']:
        raise ValueError('Reported metrics differ')
    values = [record['process_wall_ms'], raw['materialization_ms'], *raw['export_ms'],
              *(v for b in record['batches'] for v in b.values())]
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('Invalid numeric measurement')
    first, resident = raw['batches']
    if first['preparation_ms'] != resident['preparation_ms'] or first['preparation_ms']+0.001 < raw['materialization_ms'] or resident['peak_kib'] < first['peak_kib']:
        raise ValueError('Preparation or lifetime peak inconsistent')
    total = first['preparation_ms'] + sum(b['route_ms'] for b in raw['batches']) + sum(raw['export_ms'])
    if record['process_wall_ms']+2 < total: raise ValueError('Process timing excludes measured components')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--repeats', type=int, choices=[1, 7], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); directory = args.experiment.resolve()
    plan_path = directory/'plan.json'; plan = json.loads(plan_path.read_text())
    scopes = ('csr', 'global', 'span16', 'span4', 'span1')
    generator = random.Random(20261023); jobs = []
    for repeat in range(args.repeats):
        block = [{'repeat': repeat, 'scope': scope} for scope in scopes]
        generator.shuffle(block); jobs.extend(block)
    if plan['jobs'] != jobs or plan['repeats'] != args.repeats or plan['seed'] != 20261023 or set(plan['inputs']) != set(scopes):
        raise ValueError('Matrix design differs')
    for path, value in plan['files'].items():
        if digest(path) != value: raise ValueError('Frozen evidence changed: '+path)
    records, artifacts, workers = [], {str(plan_path): digest(plan_path)}, []
    for index, job in enumerate(jobs):
        prefix = directory/f'worker_{index:03d}'
        paths = {name: prefix.with_suffix(suffix) for name, suffix in
                 [('record', '.json'), ('submission', '.submission.json'), ('receipt', '.receipt.json'), ('raw', '.raw.json'), ('log', '.log')]}
        record, submission, receipt = [json.loads(paths[k].read_text()) for k in ('record', 'submission', 'receipt')]
        if digest(paths['raw']) != receipt['raw_sha256'] or digest(paths['log']) != receipt['log_sha256']:
            raise ValueError('Raw result or log differs from receipt')
        mode = 'csr' if job['scope'] == 'csr' else 'compact'
        if plan['inputs'][job['scope']]['mode'] != mode: raise ValueError('Wrong mode-specific fixture')
        raw = json.loads(paths['raw'].read_text())
        reference = json.loads(Path(plan['references'][mode]).read_text())
        check_worker(plan, job, submission, receipt, record, raw, reference)
        records.append(record)
        workers.append({'path': str(paths['record']), 'sha256': digest(paths['record'])})
        artifacts.update({str(path): digest(path) for path in paths.values()})
        del raw, reference; gc.collect()
    final_path = directory/'report.json'; final = json.loads(final_path.read_text())
    if final != {'status': 'all_scope_runtime_workers_verified', 'plan_sha256': digest(plan_path), 'workers': workers}:
        raise ValueError('Incomplete final matrix receipt')
    summaries = []
    for scope in scopes:
        selected = [r for r in records if r['condition']['scope'] == scope]
        summaries.append({'scope': scope, 'n': len(selected), 'image_bytes': Path(plan['inputs'][scope]['image']).stat().st_size,
                          'preparation_ms_median': statistics.median(r['batches'][0]['preparation_ms'] for r in selected),
                          'first_route_ms_median': statistics.median(r['batches'][0]['route_ms'] for r in selected),
                          'resident_route_ms_median': statistics.median(r['batches'][1]['route_ms'] for r in selected),
                          'process_wall_ms_median': statistics.median(r['process_wall_ms'] for r in selected),
                          'peak_native_kib_median': statistics.median(max(b['peak_kib'] for b in r['batches']) for r in selected)})
    lookup = {(r['condition']['repeat'], r['condition']['scope']): r for r in records}
    paired = {scope: [lookup[r, scope]['process_wall_ms']/lookup[r, 'csr']['process_wall_ms']
                     for r in range(args.repeats)] for scope in scopes if scope != 'csr'}
    artifacts[str(final_path)] = digest(final_path)
    write_new(args.output, {'status': 'complete_scope_runtime_matrix_independently_audited', 'completed_workers': len(records),
              'repeats': args.repeats, 'summaries': summaries, 'paired_process_wall_over_csr': paired,
              'artifacts': artifacts, 'auditor_sha256': digest(Path(__file__)), 'limitations': plan['limitations'],
              'statistics_scope': 'Single trials: semantic protocol validation only.' if args.repeats == 1 else 'Seven paired blocks; shared host and page-cache limitations apply.'})
    print('SCOPE_RUNTIME_INDEPENDENTLY_AUDITED', len(records))


if __name__ == '__main__': main()
