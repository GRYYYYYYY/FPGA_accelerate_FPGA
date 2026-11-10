#!/usr/bin/env python3
"""Measured captured-TSV to two complete native routing batches, with regenerated inputs."""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from import_vivado import read_export
from packed_graph import PackedGraph,write_packed
from netlist import read_snapshot
from heldout import object_digest
from runtime_fixture_builder import build_runtime_payloads
from real_experiment import write_new
METRICS={'preparation_ms','route_ms','peak_kib','logical_bytes','cache_hits','cache_misses'}


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def validate_files(files):
    for path,value in files.items():
        if digest(path)!=value:raise ValueError('Frozen experiment input changed: '+path)


def worker(directory,index):
    plan=json.loads((directory/'plan.json').read_text());validate_files(plan['files'])
    job=plan['jobs'][index];mode=job['mode'];out=directory/f'worker_{index:03d}';out.mkdir(exist_ok=False)
    times={};application_start=time.perf_counter()
    def timed(name,fn):
        start=time.perf_counter();result=fn();times[name]=(time.perf_counter()-start)*1000;return result
    graph=timed('read_export_ms',lambda:read_export(plan['source']))
    bank=timed('bank_load_ms',lambda:json.loads(Path(plan['bank']).read_text()) if mode=='compact' else None)
    image_path=out/'image.agr'
    timed('serialize_ms',lambda:write_packed(image_path,graph,mode,bank))
    def load_evidence():
        snapshot=read_snapshot(plan['snapshot']);queries=json.loads(Path(plan['queries']).read_text())
        fixed=json.loads(Path(plan['fixed']).read_text());proofs=[json.loads(Path(p).read_text()) for p in plan['proofs']]
        return snapshot,queries,fixed,proofs
    snapshot,queries,fixed,proofs=timed('evidence_load_ms',load_evidence)
    image=timed('image_adapter_load_ms',lambda:PackedGraph(image_path))
    payload=timed('fixture_build_ms',lambda:build_runtime_payloads(image,snapshot,queries,fixed,proofs,graph['pips']))
    def persist():
        for name,key in [('routing.txt','routing_text'),('sites.txt','sites_text')]: (out/name).write_text(payload[key])
        for name,key in [('queries.json','queries'),('symbols.json','symbols')]:write_new(out/name,payload[key])
    timed('fixture_write_ms',persist)
    artifacts={}
    def check_generated():
        for name,value in plan['expected_inputs'][mode].items():
            actual=digest(out/name)
            if actual!=value:raise ValueError('Generated runtime input differs: '+name)
            artifacts[name]=actual
    timed('generated_input_validation_ms',check_generated)
    counts=payload['counts'];release_start=time.perf_counter()
    del graph,bank,image,payload,snapshot,queries,fixed,proofs;gc.collect()
    times['pre_native_cleanup_ms']=(time.perf_counter()-release_start)*1000
    parent_pre_native_peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    command=[plan['binary'],str(image_path),str(out/'routing.txt'),str(out/'sites.txt'),'4096','80','200000','8',job['execution']]
    start=time.perf_counter()
    with (out/'native.raw.json').open('x') as stream,(out/'native.log').open('x') as log:
        child=subprocess.Popen(command,stdout=stream,stderr=log)
        write_new(out/'native.submission.json',{'owner_pid':os.getpid(),'child_pid':child.pid,'command':command,'inherited_cpu':plan['cpu']})
        code=child.wait()
    times['native_process_ms']=(time.perf_counter()-start)*1000
    application_ms=(time.perf_counter()-application_start)*1000
    child_peak_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    write_new(out/'native.receipt.json',{'exit_code':code,'process_wall_ms':times['native_process_ms']})
    if code:raise RuntimeError('Native routing failed')
    audit_start=time.perf_counter()
    raw=json.loads((out/'native.raw.json').read_text());reference=json.loads(Path(plan['references'][mode]).read_text())
    expected={k:v for k,v in reference.items() if k not in METRICS}
    if raw['execution']!=job['execution'] or len(raw['batches'])!=2:raise ValueError('Executed batch domain differs')
    for batch in raw['batches']:
        if {k:v for k,v in batch.items() if k not in METRICS}!=expected:raise ValueError('Complete native semantics differ')
    for name in ('native.raw.json','native.log','native.submission.json','native.receipt.json'):artifacts[name]=digest(out/name)
    post_audit_ms=(time.perf_counter()-audit_start)*1000
    report={'status':'regenerated_inputs_and_two_full_batches_verified','condition':job,'counts':counts,
        'application_wall_ms':application_ms,'stage_ms':times,'post_route_audit_ms':post_audit_ms,
        'parent_pre_native_peak_kib':parent_pre_native_peak_kib,'native_child_peak_kib':child_peak_kib,
        'batches':[{k:b[k] for k in METRICS} for b in raw['batches']],'export_ms':raw['export_ms'],
        'materialization_ms':raw['materialization_ms'],'artifacts':artifacts}
    write_new(out/'report.json',report)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--worker',type=int);p.add_argument('--cpu',type=int,default=125);a=p.parse_args();a.output=a.output.resolve()
    if a.worker is not None:return worker(a.output,a.worker)
    if a.cpu not in os.sched_getaffinity(0):raise ValueError('CPU unavailable')
    original=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json';old=json.loads(original.read_text())
    files=dict(old['code_inputs_and_references']);files[str(original)]=digest(original)
    rebuild=ROOT/'data/derived/runtime_fixture_rebuild_20261023_v1/report.json'
    if json.loads(rebuild.read_text())['status']!='complete_query_and_site_fixtures_rebuilt_byte_identically':raise ValueError('Fixture builder unverified')
    for path in (Path(__file__),ROOT/'src/runtime_fixture_builder.py',rebuild):files[str(path)]=digest(path)
    source=ROOT/'data/raw/region_u280_20261022_v1/region.tsv';bank=ROOT/'data/derived/netlist_u280_bank_20261022_v1/bank.json'
    cfg_path=ROOT/'configs/region_u280_v1.json';cfg=json.loads(cfg_path.read_text())
    if digest(bank)!=cfg['training_bank_sha256']:raise ValueError('Bank file differs')
    base=ROOT/'data/derived/region_all_nets_cap8_20261022_v1'
    if object_digest(json.loads(bank.read_text()))!=json.loads((base/'report.json').read_text())['frozen_bank_sha256']:raise ValueError('Bank object differs')
    files[str(bank)]=digest(bank);validate_files(files)
    expected={}
    for mode in ('csr','compact'):
        sm=json.loads((ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1/manifest.json').read_text())
        routing=Path(sm['routing_fixture']).parent
        expected[mode]={'image.agr':files[sm['image']],**sm['outputs'],
            'routing.txt':files[str(routing/'routing.txt')],'queries.json':files[str(routing/'queries.json')]}
    jobs=[{'mode':m,'execution':e} for m,e in [('csr','direct'),('compact','direct'),('compact','expanded')]]
    random.Random(20261023).shuffle(jobs)
    plan={'owner_pid':os.getpid(),'cpu':a.cpu,'jobs':jobs,'files':files,'source':str(source),'bank':str(bank),
        'snapshot':str(ROOT/cfg['snapshot']),'queries':str(base/'queries.json'),'fixed':str(base/'fixed_site_state_v2.json'),
        'proofs':[str(ROOT/f'data/netlist/lut_route_probes_20261023_v{v}/verification.json') for v in (1,2)],
        'binary':str(ROOT/'build/native_site_runtime_20261023_v1'),'references':old['references'],'expected_inputs':expected,
        'limitations':['One full integration trial per condition, not formal repeated end-to-end statistics.',
            'Application timer covers existing captured TSV through two complete routing batches, including intermediate validation and exports.',
            'Excludes Vivado acquisition, bank training, board transfer and physical readback; these remain separate requirements.',
            'Preflight integrity checks and post-route semantic audit are outside application timer but inside process wall.',
            'Parent conversion peak and native child peak are distinct process measurements; do not sum them as simultaneous memory.',
            'Parent drops graph/adapter objects before native launch. Shared host, page cache and buffered disk writes remain uncontrolled.']}
    a.output.mkdir(parents=True,exist_ok=False);write_new(a.output/'plan.json',plan)
    records=[]
    for i,job in enumerate(jobs):
        command=[sys.executable,'-u',str(Path(__file__).resolve()),'--output',str(a.output),'--worker',str(i)]
        start=time.perf_counter();log=a.output/f'worker_{i:03d}.log'
        with log.open('x') as stream:
            child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,preexec_fn=lambda:os.sched_setaffinity(0,{a.cpu}))
            write_new(a.output/f'worker_{i:03d}.submission.json',{'owner_pid':os.getpid(),'child_pid':child.pid,'command':command,'cpu':a.cpu})
            code=child.wait()
        write_new(a.output/f'worker_{i:03d}.receipt.json',{'exit_code':code,'worker_process_wall_ms':(time.perf_counter()-start)*1000,'log_sha256':digest(log)})
        if code:raise RuntimeError('Integrated source-to-route worker failed '+str(i))
        report=a.output/f'worker_{i:03d}/report.json';records.append({'condition':job,'report':str(report),'sha256':digest(report)})
        print('SOURCE_TO_ROUTE_VERIFIED',i,job,flush=True)
    write_new(a.output/'report.json',{'status':'all_three_full_integration_trials_verified','plan_sha256':digest(a.output/'plan.json'),'workers':records})


if __name__=='__main__':main()
