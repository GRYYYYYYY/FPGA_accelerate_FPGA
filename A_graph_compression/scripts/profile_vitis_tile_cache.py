#!/usr/bin/env python3
"""Validate isolated tile cache and compare measured CPU operation counts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from check_vitis_kernel import digest, require, validate_case_log
from profile_vitis_decoder import HEADER, instrument

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();source=a.source.resolve();out=a.output.resolve()
    require(121 in os.sched_getaffinity(0),'CPU121 unavailable')
    source_plan=source/'plan.json';plan=json.loads(source_plan.read_text())
    files={**plan['files'],**plan['generated'],str(source_plan):digest(source_plan),
           str(Path(__file__).resolve()):digest(__file__)}
    old_report=ROOT/'data/derived/vitis_decoder_profile_20261023_v1/report.json'
    previous=json.loads(old_report.read_text());files[str(old_report)]=digest(old_report)
    files.update(previous['files']);files.update(previous['generated'])
    for path,sha in files.items():require(digest(path)==sha,'Frozen input changed: '+path)
    out.mkdir(parents=True,exist_ok=False)
    (out/'plan.json').write_text(json.dumps({'owner_pid':os.getpid(),'files':files},indent=2)+'\n')

    def run(command,name):
        log=out/(name+'.log')
        with log.open('x') as stream:
            result=subprocess.run(['taskset','-c','121',*map(str,command)],stdout=stream,stderr=subprocess.STDOUT)
        require(result.returncode==0,'Failed '+name+'; inspect '+str(log))
        return log.read_text()

    stress=out/'test_tile_cache'
    run(['g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',
         '-Wno-unknown-pragmas',source/'test_tile_cache.cpp','-o',stress],'stress_compile')
    stress_text=run([stress],'stress')
    require(stress_text.strip()=='TILE_CACHE_HELPER_PASS checks=773','Incomplete stress coverage')
    binary=out/'cpu_test'
    run(['g++','-std=c++14','-O2','-Wno-unknown-pragmas',
         *[source/name for name in ['graph_body.cpp','graph_accel.cpp','test_graph_expand.cpp']],
         '-o',binary],'plain_compile')
    plain=validate_case_log(run([binary,source/'validation.txt'],'plain_golden'),source/'validation.txt',1)
    require(len(plain)==23,'Missing full/stratified plain golden cases')
    baseline=ROOT/'data/derived/vitis_graph_kernel_20261023_v2/compact'
    stratified=ROOT/'data/derived/vitis_stratified_fixtures_20261023_v1/compact/rtl.txt'
    results={}
    for label,origin in [('baseline',baseline),('tile_cache',source)]:
        target=out/label;target.mkdir()
        (target/'graph_body.cpp').write_text(instrument((origin/'graph_body.cpp').read_text()))
        (target/'profile.hpp').write_text(HEADER)
        for name in ['graph_body.hpp','graph_accel.hpp','graph_accel.cpp','test_graph_expand.cpp']:
            (target/name).write_bytes((origin/name).read_bytes())
        executable=target/'profile'
        run(['g++','-std=c++14','-O2','-Wno-unknown-pragmas',
             *[target/name for name in ['graph_body.cpp','graph_accel.cpp','test_graph_expand.cpp']],
             '-o',executable],label+'_compile')
        results[label]={}
        for workload,manifest in [('full',baseline/'full.txt'),('original_rtl',baseline/'rtl.txt'),('stratified',stratified)]:
            text=run([executable,manifest],label+'_'+workload)
            cases=validate_case_log(text,manifest,1)
            profiles=[json.loads(line[8:]) for line in text.splitlines() if line.startswith('PROFILE ')]
            require(len(cases)==len(profiles),'Missing counter row')
            for case,profile in zip(cases,profiles):
                require(sum(profile['status'])==case['requests']==profile['requests'],'Request count mismatch')
                require(sum(profile['status'][1:])==case['failed'],'Failure count mismatch')
                case['profile']=profile
            results[label][workload]=cases
    comparisons={}
    for workload in results['baseline']:
        comparisons[workload]=[]
        for before,after in zip(results['baseline'][workload],results['tile_cache'][workload]):
            require({k:v for k,v in before.items() if k!='profile'}=={k:v for k,v in after.items() if k!='profile'},'Coverage mismatch')
            x,y=before['profile'],after['profile']
            require({k:v for k,v in x.items() if k not in ['tile_calls','tile_steps']}==
                    {k:v for k,v in y.items() if k not in ['tile_calls','tile_steps']},'Non-tile operation count changed')
            require(0<=y['tile_calls']<=x['tile_calls'] and 0<=y['tile_steps']<=x['tile_steps'],'Invalid lookup counts')
            comparisons[workload].append({'case':{k:v for k,v in before.items() if k!='profile'},
                'original_tile_calls':x['tile_calls'],'remaining_tile_calls':y['tile_calls'],
                'avoided_tile_calls':x['tile_calls']-y['tile_calls'],
                'original_tile_steps':x['tile_steps'],'remaining_tile_steps':y['tile_steps'],
                'avoided_tile_steps':x['tile_steps']-y['tile_steps'],'unchanged_alias_steps':x['alias_steps']})
    # Reproducing the previous independently saved baseline guards against drift
    # in profiling itself. Both old workloads must match all original counters.
    for workload,old_key in [('full','full'),('original_rtl','rtl')]:
        require(results['baseline'][workload]==previous['results']['compact'][old_key], 'Prior baseline profile not reproduced')
    for path,sha in files.items():require(digest(path)==sha,'Input changed during experiment: '+path)
    report={'status':'plain_and_instrumented_full_golden_and_helper_sanitizers_passed',
            'files':files,'generated':{str(path):digest(path) for path in out.rglob('*') if path.is_file()},
            'plain_cases':plain,'helper_checks':773,'results':results,'comparisons':comparisons,
            'limitations':['Operation counts are CPU observations, not RTL latency, AXI transactions or board measurements.',
                           'Full graph visits each canonical node once; actual router frequencies can differ.',
                           'Only tile lookup changed. Alias lookup and insertion sorting remain unchanged.',
                           'No HLS synthesis, RTL simulation or physical implementation evidence yet.']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'output':str(out)}))


if __name__=='__main__':main()
