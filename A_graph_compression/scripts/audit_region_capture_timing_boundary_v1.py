#!/usr/bin/env python3
"""Recover only timing quantities actually preserved by the original full capture."""
from datetime import datetime
import json
import math
from pathlib import Path
import resource

from check_vitis_kernel import digest, require
from real_experiment import write_new

ROOT = Path(__file__).resolve().parents[1]


def main():
    resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    folder = ROOT/'data/raw/region_u280_20261022_v1'
    paths = dict(state=ROOT/'results/region_u280_capture_20261022_v1.json',
                 plan=folder/'execution_plan.json', capture=folder/'capture.json',
                 orchestration=folder/'orchestration_receipt.json', selector=folder/'selector_receipt.json',
                 config=ROOT/'configs/region_u280_v1.json')
    records = {key: json.loads(path.read_text()) for key, path in paths.items()}
    state, plan, capture, config = [records[key] for key in ['state', 'plan', 'capture', 'config']]
    require(state['status']=='complete' and state['stage']=='capture_ready' and state['merge_exit_code']==0,
            'Original capture not complete')
    require(plan['workers']==config['workers']==8 and plan['vivado_threads_per_worker']==1,
            'Capture concurrency differs')
    require(plan['total_sources']==220973 and len(plan['jobs'])==len(state['jobs'])==8,
            'Incomplete capture scope')
    bindings = {str(path): digest(path) for path in paths.values()}

    def bind(path, expected):
        path = Path(path)
        actual = digest(path)
        require(actual==expected, 'Capture binding changed: '+str(path))
        bindings[str(path)] = actual

    for key in ['orchestration', 'selector']:
        for name, expected in records[key]['files'].items():
            bind(ROOT/name, expected)
    for document in [plan, capture]:
        for name, expected in document['code_sha256'].items():
            bind(ROOT/name, expected)
    bind(paths['config'], plan['config_sha256'])
    bind(ROOT/config['checkpoint'], config['checkpoint_sha256'])
    for entry in capture['files'].values():
        bind(ROOT/entry['path'], entry['sha256'])
    selection_path = ROOT/capture['source_selection']['path']
    selected = selection_path.read_text().splitlines()
    require(len(selected)==len(set(selected))==220973, 'Wrong complete source selection')
    combined, jobs = set(), []
    for index, (job, actual) in enumerate(zip(plan['jobs'], state['jobs'])):
        require(job['id']==f'{index:02d}' and all(actual[k]==v for k,v in job.items()), 'Wrong shard identity')
        require(actual['status']=='complete' and actual['exit_code']==0, 'Incomplete shard')
        bind(ROOT/job['roots'], job['roots_sha256'])
        roots = (ROOT/job['roots']).read_text().splitlines()
        require(len(roots)==len(set(roots))==job['sources']==actual['summary']['roots'], 'Partial source partition')
        require(not combined.intersection(roots), 'Overlapping source partitions')
        combined.update(roots)
        bind(ROOT/job['output'], actual['sha256'])
        require(capture['files'][job['output']]['sha256']==actual['sha256'], 'Merge used different shard')
        log = ROOT/actual['stdout']
        text = log.read_text()
        require('REGION_SHARD_COMPLETE id='+job['id']+' roots='+str(job['sources']) in text and 'ERROR:' not in text,
                'Missing successful Vivado completion marker')
        bindings[str(log)] = digest(log)
        command = actual['command']
        require(command[command.index('-source')+1]==str(ROOT/'adapters/export_region_shard.tcl') and
                command[command.index('-tclargs')+1:]==[str(ROOT/job['roots']),str(ROOT/job['output']),
                str(ROOT/config['checkpoint']),plan['config_sha256'],job['id']], 'Different actual capture command')
        value = actual['wall_seconds']
        require(type(value) in (int,float) and math.isfinite(value) and value>0, 'Invalid measured shard interval')
        jobs.append(dict(id=job['id'],sources=job['sources'],wall_seconds=value,
                         pid_at_capture=actual['pid'],output_sha256=actual['sha256']))
    require(combined==set(selected), 'Capture partitions do not cover the original region')
    started = datetime.fromisoformat(state['started_utc'])
    assembled = datetime.fromisoformat(capture['created_utc'])
    require(started.tzinfo is not None and assembled.tzinfo is not None and assembled>started,
            'Invalid recorded wall-clock endpoints')
    durations = [job['wall_seconds'] for job in jobs]
    bindings[str(Path(__file__))] = digest(Path(__file__))
    result = dict(status='original_full_region_capture_timing_boundaries_verified',
        scope=dict(part=capture['part'],sources=220973,workers=8,threads_per_vivado=1,
                   graph=capture['graph']['summary'],graph_sha256=capture['graph']['sha256']),
        shard_intervals=jobs,minimum_shard_wall_seconds=min(durations),maximum_shard_wall_seconds=max(durations),
        shard_timer_definition=dict(clock='time.perf_counter',
            starts='Immediately before opening stdout and spawning Vivado in the already-started worker thread',
            ends='After Vivado exits, log marker/error validation, read_export, canonical validation and exact root-domain check',
            includes=['Vivado startup/checkpoint load/export','stdout read and completion checks','Python full shard load/validation/root coverage'],
            excludes=['initial source selection','thread dispatch before local timer','final shard SHA and state publication','merge/final manifest']),
        recorded_utc_interval=dict(start=state['started_utc'],end=capture['created_utc'],
            difference_seconds=(assembled-started).total_seconds(),
            definition='Supervisor state creation to capture-manifest dictionary construction, before final hashing and publication',
            is_total_monotonic_acquisition_measurement=False),
        unmeasured=dict(source_selection_elapsed_seconds=None,merge_elapsed_seconds=None,
                        final_hashing_publication_seconds=None,total_monotonic_acquisition_seconds=None,
                        placement_to_board_end_to_end_seconds=None),
        limitations=['One historical capture, not repeated acquisition statistics.',
                     'Parallel shard wall intervals are not CPU time and must not be summed as acquisition latency.',
                     'The maximum shard interval is not a timer for the whole acquisition chain.',
                     'The UTC difference is arithmetic on recorded wall-clock timestamps, not a monotonic full-chain receipt.',
                     'Do not add this historical capture interval to new CPU timings and call the sum a measured end-to-end run.',
                     'Regional coverage, partial-site semantics and absent board measurements remain unchanged.'],
        full_experiment_complete=False, files=bindings)
    output = ROOT/'results/region_capture_timing_boundary_audit_20261027_v1.json'
    write_new(output,result)
    print(json.dumps(dict(output=str(output),bindings=len(bindings),maximum_shard_wall_seconds=max(durations),
                         recorded_utc_difference_seconds=(assembled-started).total_seconds())),flush=True)


if __name__=='__main__':
    main()
