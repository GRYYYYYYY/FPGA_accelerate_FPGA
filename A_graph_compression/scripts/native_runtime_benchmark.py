#!/usr/bin/env python3
"""Seeded fresh-process first/resident trials with full-workload semantic gates."""
import argparse
import gc
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
from time import perf_counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'src')]
from import_vivado import sha256
from real_experiment import write_new

METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}


def jobs(capacities,repeats,seed):
    if repeats<1 or not capacities or min(capacities)<0 or len(set(capacities))!=len(capacities):
        raise ValueError('Invalid benchmark design')
    generator=random.Random(seed);result=[]
    for repeat in range(repeats):
        block=[{'repeat':repeat,'mode':mode,'execution':execution,'capacity':cap}
               for mode,execution in [('csr','direct'),('compact','direct'),('compact','expanded')]
               for cap in capacities]
        generator.shuffle(block);result.extend(block)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--capacities',nargs='+',type=int,default=[4096]);p.add_argument('--repeats',type=int,default=1)
    p.add_argument('--seed',type=int,default=20261023);p.add_argument('--cpu',type=int)
    a=p.parse_args();design=jobs(a.capacities,a.repeats,a.seed)
    cpu=a.cpu if a.cpu is not None else min(os.sched_getaffinity(0))
    if cpu not in os.sched_getaffinity(0):raise ValueError('CPU unavailable')
    reference_dir=ROOT/'data/derived/native_region_routing_20261023_v1'
    verified_path=ROOT/'results/native_region_check_20261023_v1.json'
    verified=json.loads(verified_path.read_text());old_plan=json.loads((reference_dir/'plan.json').read_text())
    if sha256(reference_dir/'plan.json')!=verified['plan_sha256']:raise ValueError('Verified reference plan changed')
    for name,digest in old_plan['code_and_binary'].items():
        if sha256(Path(name))!=digest:raise ValueError('Verified integration code changed')
    inputs={};references={};files={str(verified_path):sha256(verified_path)}
    for mode in ('csr','compact'):
        for name,digest in verified['modes'][mode]['artifacts'].items():
            if sha256(Path(name))!=digest:raise ValueError('Verified native result changed')
        fixture=Path(old_plan['inputs'][mode]['directory']);manifest=json.loads((fixture/'manifest.json').read_text())
        for name,digest in manifest['files'].items():
            if sha256(Path(name))!=digest:raise ValueError('Fixture input changed')
        for name,digest in manifest['outputs'].items():
            if sha256(fixture/name)!=digest:raise ValueError('Numeric fixture changed')
        inputs[mode]={'image':manifest['image'],'fixture':str(fixture/'routing.txt')}
        references[mode]=str(reference_dir/(mode+'_routes.json'))
        for path in (Path(inputs[mode]['image']),fixture/'routing.txt',fixture/'manifest.json',Path(references[mode])):
            files[str(path)]=sha256(path)
    binary=ROOT/'build/native_runtime_20261023_v1'
    sources=[ROOT/'src/native'/name for name in ('netlist_runtime.cpp','netlist_routes.hpp','netlist_connect.hpp','packed_graph.hpp')]
    for path in [binary,Path(__file__),*sources]:files[str(path.resolve())]=sha256(path)
    a.output.mkdir(parents=True,exist_ok=False)
    write_new(a.output/'plan.json',{'owner_pid':os.getpid(),'jobs':design,'seed':a.seed,'cpu':cpu,
        'code_inputs_and_references':files,'inputs':inputs,'references':references,
        'scope':'Complete 1062-query canonical-node workload; full traces retained equally in all conditions.',
        'limitations':['Site/configuration legality and real board measurements remain separate requirements.',
            'Input conversion to packed images/fixtures is outside native child timing; not source-graph end-to-end.',
            'VmHWM is native child lifetime peak including traces, excluding Python audit/orchestration parent.',
            'Shared host and OS page cache are uncontrolled despite pinned native CPU.',
            'Resident route batch keeps graph/cache but resets routing occupancy and history.']})
    records=[]
    for index,job in enumerate(design):
        for name,digest in files.items():
            if sha256(Path(name))!=digest:raise ValueError('Frozen runtime input/code changed: '+name)
        mode=job['mode'];prefix=a.output/f'worker_{index:03d}'
        command=[str(binary),inputs[mode]['image'],inputs[mode]['fixture'],str(job['capacity']),
                 '80','200000','8',job['execution']]
        print('NATIVE_RUNTIME_BEGIN',index,job,flush=True);start=perf_counter()
        with prefix.with_suffix('.raw.json').open('x') as stream,prefix.with_suffix('.log').open('x') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=log,
                                   preexec_fn=lambda:os.sched_setaffinity(0,{cpu}))
            write_new(prefix.with_suffix('.submission.json'),{'owner_pid':os.getpid(),'child_pid':child.pid,'command':command})
            code=child.wait()
        process_ms=(perf_counter()-start)*1000
        write_new(prefix.with_suffix('.receipt.json'),{'exit_code':code,'process_wall_ms':process_ms,
            'raw_sha256':sha256(prefix.with_suffix('.raw.json')),'log_sha256':sha256(prefix.with_suffix('.log'))})
        if code:raise RuntimeError('Native runtime child failed')
        raw=json.loads(prefix.with_suffix('.raw.json').read_text())
        reference=json.loads(Path(references[mode]).read_text())
        expected={k:v for k,v in reference.items() if k not in METRICS}
        if len(raw['batches'])!=2 or len(raw['export_ms'])!=2:raise ValueError('First/resident batch domain differs')
        measurements=[]
        for batch in raw['batches']:
            if {k:v for k,v in batch.items() if k not in METRICS}!=expected:
                raise ValueError('Full first/resident semantics differ from verified native workload')
            measurements.append({key:batch[key] for key in METRICS})
        record={'condition':job,'both_complete_batches_verified':True,'batches':measurements,
            'export_ms':raw['export_ms'],'process_wall_ms':process_ms,
            'raw_sha256':sha256(prefix.with_suffix('.raw.json'))}
        write_new(prefix.with_suffix('.json'),record);records.append(record)
        del raw,reference,expected;gc.collect()
        print('NATIVE_RUNTIME_VERIFIED',index,flush=True)
    summaries=[]
    for mode,execution,capacity in sorted({(r['condition']['mode'],r['condition']['execution'],r['condition']['capacity']) for r in records}):
        selected=[r for r in records if (r['condition']['mode'],r['condition']['execution'],r['condition']['capacity'])==(mode,execution,capacity)]
        summaries.append({'mode':mode,'execution':execution,'capacity':capacity,'n':len(selected),
            'preparation_ms_median':statistics.median(r['batches'][0]['preparation_ms'] for r in selected),
            'first_route_ms_median':statistics.median(r['batches'][0]['route_ms'] for r in selected),
            'resident_route_ms_median':statistics.median(r['batches'][1]['route_ms'] for r in selected),
            'process_wall_ms_median':statistics.median(r['process_wall_ms'] for r in selected),
            'peak_native_kib':[max(b['peak_kib'] for b in r['batches']) for r in selected]})
    write_new(a.output/'report.json',{'status':'all_complete_batches_equivalent','workers':len(records),
        'plan_sha256':sha256(a.output/'plan.json'),'summaries':summaries,
        'worker_sha256':{f'worker_{i:03d}.json':sha256(a.output/f'worker_{i:03d}.json') for i in range(len(records))}})


if __name__=='__main__':main()
