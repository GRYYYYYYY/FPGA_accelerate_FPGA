#!/usr/bin/env python3
"""Isolated-process, seeded-order routing benchmark with identical row caches."""
import argparse
from datetime import datetime,timezone
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
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters'),str(ROOT/'scripts')]
from heldout import encode_frozen,object_digest
from import_vivado import read_export,sha256
from netlist import read_snapshot
from netlist_routing import route_batch,validate_routes
from real_experiment import write_new
from row_cache import RowCache
from search_experiment import ExplicitCSR,LazyTemplates
from template_codec import DirectDecoder,PreparedDecoder


def memory_kib():
    values={}
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith(('VmHWM:','VmRSS:')):
            key,value,*_=line.split();values[key.rstrip(':')]=int(value)
    return values


def normalized(result):
    return {k:v for k,v in result.items() if k!='wall_ms'}


def make_jobs(modes,capacities,repeats,seed):
    if repeats<1 or not modes or not capacities or any(c<0 for c in capacities):
        raise ValueError('Invalid benchmark design')
    if len(set(modes))!=len(modes) or len(set(capacities))!=len(capacities):
        raise ValueError('Duplicate benchmark condition')
    generator=random.Random(seed);jobs=[]
    for repeat in range(repeats):
        block=[{'repeat':repeat,'mode':mode,'capacity':cap} for mode in modes for cap in capacities]
        generator.shuffle(block);jobs.extend(block)
    return jobs


def worker(directory,index):
    plan=json.loads((directory/'plan.json').read_text());job=plan['jobs'][index]
    for name,digest in plan['files'].items():
        if sha256(ROOT/name)!=digest:raise ValueError('Frozen benchmark input/code changed: '+name)
    os.sched_setaffinity(0,{plan['cpu']})
    start=perf_counter()
    graph=read_export(ROOT/plan['graph'])
    snapshot=read_snapshot(ROOT/plan['snapshot'])
    experiment=ROOT/plan['experiment']
    queries=json.loads((experiment/'queries.json').read_text())
    expected=json.loads((experiment/'csr_routes.json').read_text())
    bank_path=ROOT/plan['bank']
    # Loading the frozen bank is a compact-specific cost; CSR does not need it.
    if job['mode']=='csr':provider=ExplicitCSR(graph)
    else:
        bank=json.loads(bank_path.read_text());compact=encode_frozen(graph,bank)
        if job['mode']=='expanded':
            expanded=PreparedDecoder(compact).materialize();provider=ExplicitCSR(expanded)
        else:
            provider=LazyTemplates(compact,DirectDecoder if job['mode']=='direct' else PreparedDecoder)
        del compact,bank
    provider=RowCache(provider,job['capacity'])
    gc.collect()
    preparation_ms=(perf_counter()-start)*1000
    memory={'after_preparation':memory_kib()};batches=[]
    for phase in ['first','resident']:
        settings=plan['route_settings']
        result=route_batch(provider,snapshot,queries,full_trace=False,**settings)
        route_ms=result['wall_ms']
        memory[phase]=memory_kib()
        # Validation and digest construction excluded from route timers.
        if normalized(result)!=normalized(expected):
            raise ValueError('Routing path/state/counters differ from the audited baseline')
        validation=validate_routes(graph,snapshot,queries,result)
        batches.append({'phase':phase,'route_ms':route_ms,'result_digest':object_digest(normalized(result)),
                        'validation':validation,'cache':provider.statistics()})
    record={'condition':job,'pid':os.getpid(),'cpu':plan['cpu'],'preparation_ms':preparation_ms,
            'first_end_to_end_ms':preparation_ms+batches[0]['route_ms'],
            'batches':batches,'memory_kib':memory,
            'memory_scope':'Whole Python worker includes audit graph and snapshot. VmHWM is cumulative per fresh process; resident follows first and validation.',
            'plan_sha256':sha256(directory/'plan.json')}
    write_new(directory/f'worker_{index:03d}.json',record)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment',type=Path)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/netlist_u280_v2.json')
    parser.add_argument('--bank',type=Path,default=ROOT/'data/derived/netlist_u280_bank_20261022_v1/bank.json')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--modes',nargs='+',choices=['csr','direct','prepared','expanded'],default=['csr','direct','prepared','expanded'])
    parser.add_argument('--capacities',nargs='+',type=int,default=[0,64,4096])
    parser.add_argument('--repeats',type=int,default=7)
    parser.add_argument('--seed',type=int,default=20261022)
    parser.add_argument('--cpu',type=int)
    parser.add_argument('--worker',type=int)
    args=parser.parse_args();directory=args.output.resolve()
    if args.worker is not None:return worker(directory,args.worker)
    if args.experiment is None:parser.error('--experiment is required')
    jobs=make_jobs(args.modes,args.capacities,args.repeats,args.seed)
    cfg=json.loads(args.config.read_text());raw=ROOT/cfg['output_dir']
    capture=json.loads((raw/'capture.json').read_text())
    graph=ROOT/capture['graph']['path'] if capture.get('scope_kind')=='independent_endpoint_region' else raw/'reference_domain.tsv'
    experiment=args.experiment.resolve();audit=json.loads((experiment/'report.json').read_text())
    if audit['inputs']['config']!=sha256(args.config) or audit['inputs']['capture']!=sha256(raw/'capture.json'):
        raise ValueError('Benchmark domain differs from audited routing experiment')
    for entry in capture['files'].values():
        if sha256(ROOT/entry['path'])!=entry['sha256']:
            raise ValueError('Captured benchmark input changed: '+entry['path'])
    if object_digest(json.loads(args.bank.read_text()))!=audit['frozen_bank_sha256']:
        raise ValueError('Benchmark training bank differs from audited experiment')
    if sha256(ROOT/cfg['snapshot'])!=audit['inputs']['snapshot']:
        raise ValueError('Benchmark snapshot changed')
    for name,digest in audit['artifacts'].items():
        if sha256(experiment/name)!=digest:raise ValueError('Audited artifact changed: '+name)
    settings=audit['route_settings']
    cpu=args.cpu if args.cpu is not None else min(os.sched_getaffinity(0))
    if cpu not in os.sched_getaffinity(0):raise ValueError('Unavailable CPU')
    paths=[args.config.resolve(),raw/'capture.json',graph,ROOT/cfg['snapshot'],args.bank.resolve(),
           experiment/'report.json',experiment/'queries.json',experiment/'csr_routes.json',Path(__file__).resolve(),
           *[ROOT/p for p in ['src/row_cache.py','src/netlist_routing.py','src/search_experiment.py',
                             'src/template_codec.py','src/heldout.py','src/canonical_graph.py']]]
    plan={'created_utc':datetime.now(timezone.utc).isoformat(),'seed':args.seed,'cpu':cpu,'jobs':jobs,
          'experiment':str(experiment.relative_to(ROOT)),'graph':str(graph.relative_to(ROOT)),
          'snapshot':cfg['snapshot'],'bank':str(args.bank.resolve().relative_to(ROOT)),
          'files':{str(p.relative_to(ROOT)):sha256(p) for p in paths},
          'route_settings':settings,'scope':audit['scope'],
          'limitations':['Python representation/control cost; not native or FPGA performance.',
                         'Audit graph remains resident in all workers; peak RSS is whole-process memory.',
                         'OS page cache is uncontrolled; concurrent host workload may affect results.',
                         'Resident batch retains adjacency cache but resets routing occupancy/costs.']}
    directory.mkdir(parents=True,exist_ok=False);write_new(directory/'plan.json',plan)
    records=[]
    for index,job in enumerate(jobs):
        print('BENCHMARK_WORKER',index,job,flush=True)
        with (directory/f'worker_{index:03d}.log').open('x') as stream:
            subprocess.run([sys.executable,str(Path(__file__).resolve()),'--output',str(directory),'--worker',str(index)],
                           cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
        records.append(json.loads((directory/f'worker_{index:03d}.json').read_text()))
    digests={batch['result_digest'] for record in records for batch in record['batches']}
    if len(digests)!=1:raise ValueError('Cross-condition routing differs')
    summaries=[]
    for mode in args.modes:
        for capacity in args.capacities:
            selected=[r for r in records if r['condition']['mode']==mode and r['condition']['capacity']==capacity]
            summaries.append({'mode':mode,'capacity':capacity,'n':len(selected),
                'preparation_ms_median':statistics.median(r['preparation_ms'] for r in selected),
                'first_end_to_end_ms_median':statistics.median(r['first_end_to_end_ms'] for r in selected),
                'first_route_ms_median':statistics.median(r['batches'][0]['route_ms'] for r in selected),
                'resident_route_ms_median':statistics.median(r['batches'][1]['route_ms'] for r in selected),
                'worker_peak_kib': [max(m['VmHWM'] for m in r['memory_kib'].values()) for r in selected]})
    write_new(directory/'report.json',{'status':'equivalent','plan_sha256':sha256(directory/'plan.json'),
        'workers':len(records),'summaries':summaries,'limitations':plan['limitations'],
        'worker_sha256':{f'worker_{i:03d}.json':sha256(directory/f'worker_{i:03d}.json') for i in range(len(records))}})


if __name__=='__main__':main()
