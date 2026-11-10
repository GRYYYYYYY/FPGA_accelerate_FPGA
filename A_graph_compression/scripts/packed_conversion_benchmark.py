#!/usr/bin/env python3
"""Fresh-process source-export to byte-identical packed-image conversion costs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import read_export
from packed_graph import write_packed
from heldout import object_digest
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def worker(a):
    plan=json.loads((a.output/'plan.json').read_text());job=plan['jobs'][a.worker]
    prefix=a.output/f'worker_{a.worker:03d}';image_path=prefix.with_suffix('.agr')
    source=Path(plan['source']);bank_path=Path(plan['bank']);start=time.perf_counter()
    graph=read_export(source);read_ms=(time.perf_counter()-start)*1000
    bank_start=time.perf_counter();bank=json.loads(bank_path.read_text()) if job['mode']=='compact' else None
    bank_ms=(time.perf_counter()-bank_start)*1000
    pack_start=time.perf_counter();layout=write_packed(image_path,graph,job['mode'],bank)
    pack_ms=(time.perf_counter()-pack_start)*1000;conversion_ms=(time.perf_counter()-start)*1000
    peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    validation_start=time.perf_counter()
    actual=digest(image_path);expected=plan['expected_image_sha256'][job['mode']]
    if actual!=expected:raise ValueError('Regenerated packed image differs byte-for-byte')
    for path,value in plan['files'].items():
        if digest(path)!=value:raise ValueError('Frozen preparation dependency changed: '+path)
    report={'condition':job,'status':'byte_identical_to_verified_image','read_export_ms':read_ms,'bank_load_ms':bank_ms,
            'serialize_ms':pack_ms,'conversion_ms':conversion_ms,'validation_ms':(time.perf_counter()-validation_start)*1000,
            'peak_child_kib':peak_kib,'output_sha256':actual,'layout':layout,
            'graph_counts':{k:len(graph[k]) for k in ('nodes','roots','aliases','pips','edges')}}
    write_new(prefix.with_suffix('.json'),report)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeats',type=int,default=7);p.add_argument('--cpu',type=int,default=126)
    p.add_argument('--worker',type=int);a=p.parse_args();a.output=a.output.resolve()
    if a.worker is not None:return worker(a)
    if a.repeats<1 or a.cpu not in os.sched_getaffinity(0):raise ValueError('Invalid repeats/CPU')
    old=ROOT/'data/derived/native_site_routing_20261023_v2/plan.json';frozen=json.loads(old.read_text())['files']
    source=ROOT/'data/raw/region_u280_20261022_v1/region.tsv';bank=ROOT/'data/derived/netlist_u280_bank_20261022_v1/bank.json'
    reference=ROOT/'data/derived/region_all_nets_cap8_20261022_v1'
    sources=[Path(__file__),ROOT/'adapters/import_vivado.py',ROOT/'scripts/real_experiment.py',
             *[ROOT/'src'/name for name in ('packed_graph.py','canonical_graph.py','heldout.py','template_codec.py')]]
    paths=[source,bank,old,reference/'report.json',ROOT/'configs/region_u280_v1.json',*sources,*[reference/(mode+'.agr') for mode in ('csr','compact')]]
    files={str(path):digest(path) for path in paths}
    for path in (source,reference/'report.json',ROOT/'configs/region_u280_v1.json',*[reference/(mode+'.agr') for mode in ('csr','compact')]):
        if files[str(path)]!=frozen[str(path)]:raise ValueError('Verified conversion input changed')
    audited=json.loads((reference/'report.json').read_text());config=json.loads((ROOT/'configs/region_u280_v1.json').read_text())
    if object_digest(json.loads(bank.read_text()))!=audited['frozen_bank_sha256'] or files[str(bank)]!=config['training_bank_sha256']:raise ValueError('Frozen training bank changed')
    jobs=[];generator=random.Random(20261023)
    for repeat in range(a.repeats):
        block=[{'mode':mode,'repeat':repeat} for mode in ('csr','compact')];generator.shuffle(block);jobs.extend(block)
    a.output.mkdir(parents=True,exist_ok=False)
    plan={'owner_pid':os.getpid(),'jobs':jobs,'seed':20261023,'cpu':a.cpu,'source':str(source),'bank':str(bank),'files':files,
          'expected_image_sha256':{m:files[str(reference/(m+'.agr'))] for m in ('csr','compact')},
          'limitations':['CPU conversion from an existing captured TSV to AGR only; excludes Vivado acquisition, bank training, query/site fixture preparation, native routing and board transfer.',
              'Exact source graph and frozen bank; CSR does not pay unnecessary compact bank loading or exception construction.',
              'File writes close normally without fsync; page-cache and concurrent host activity are uncontrolled. This is not cold-disk IO.',
              'Child peak includes parser and serializer objects; parent/hash audit memory is excluded.',
              'Conversion phase excludes post-write hash validation; process wall includes interpreter/imports, conversion, validation, and cleanup.']}
    write_new(a.output/'plan.json',plan);records=[]
    for index,job in enumerate(jobs):
        prefix=a.output/f'worker_{index:03d}'
        command=[sys.executable,'-u',str(Path(__file__).resolve()),'--output',str(a.output),'--worker',str(index)]
        start=time.perf_counter()
        with prefix.with_suffix('.log').open('x') as stream:
            child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,preexec_fn=lambda:os.sched_setaffinity(0,{a.cpu}))
            write_new(prefix.with_suffix('.submission.json'),{'owner_pid':os.getpid(),'child_pid':child.pid,'command':command,'cpu':a.cpu})
            code=child.wait()
        receipt={'exit_code':code,'process_wall_ms':(time.perf_counter()-start)*1000,'log_sha256':digest(prefix.with_suffix('.log'))}
        write_new(prefix.with_suffix('.receipt.json'),receipt)
        if code:raise RuntimeError('Conversion worker failed '+str(index))
        result=json.loads(prefix.with_suffix('.json').read_text())
        if result['condition']!=job or result['output_sha256']!=plan['expected_image_sha256'][job['mode']]:raise ValueError('Worker differs')
        records.append((result,receipt));print('CONVERSION_VERIFIED',index,job,flush=True)
    summaries={}
    for mode in ('csr','compact'):
        selected=[(r,t) for r,t in records if r['condition']['mode']==mode]
        summaries[mode]={'n':len(selected),**{k:statistics.median(r[k] for r,t in selected)
            for k in ('read_export_ms','bank_load_ms','serialize_ms','conversion_ms','validation_ms','peak_child_kib')},
            'process_wall_ms':statistics.median(t['process_wall_ms'] for r,t in selected)}
    write_new(a.output/'report.json',{'status':'all_regenerated_images_byte_identical','plan_sha256':digest(a.output/'plan.json'),
        'workers':len(records),'summary_medians':summaries,
        'worker_sha256':{f'worker_{i:03d}.json':digest(a.output/f'worker_{i:03d}.json') for i in range(len(records))}})


if __name__=='__main__':main()
