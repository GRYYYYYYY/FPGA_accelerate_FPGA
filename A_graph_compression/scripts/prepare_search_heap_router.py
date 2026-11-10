#!/usr/bin/env python3
"""Isolate original native router and replace only its search priority queue."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/search_heap_router_20261024_v1'
CAPACITY=1048576

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('Unexpected source anchor: '+old)
    return text.replace(old,new)

def transform_search(text):
    text=replace_once(text,'#include <queue>','#include "search_heap_adapter.hpp"\n#ifndef SEARCH_HEAP_CAPACITY\n#define SEARCH_HEAP_CAPACITY 1048576\n#endif')
    text=replace_once(text,'    using Entry=std::tuple<uint64_t,uint64_t,size_t>;\n    std::priority_queue<Entry,std::vector<Entry>,std::greater<Entry>> queue;',
                      '    heap_adapter::Queue<SEARCH_HEAP_CAPACITY> queue;\n    SearchResult result;')
    text=replace_once(text,'    SearchResult result;std::vector<Edge> edges;','    std::vector<Edge> edges;')
    for call in ['queue.emplace(0,serial++,index);','queue.emplace(following,serial++,next);']:
        text=replace_once(text,call,'if (!'+call[:-1]+') {result.status="capacity_exhausted";return result;}')
    return text

def transform_runtime(text):
    text=replace_once(text,'    auto route_start=Clock::now();','    heap_adapter::counters={};\n    auto route_start=Clock::now();')
    text=replace_once(text,'    auto route_ms=ms(route_start);uint64_t peak_kib=0;',
        '    const auto hc=heap_adapter::counters;\n'
        '    std::cerr<<"HEAP_COUNTERS "<<batch<<\' \'<<hc.searches<<\' \'<<hc.pushes<<\' \'<<hc.pops<<\' \'<<hc.failures<<\' \'<<hc.peak<<\'\\n\';\n'
        '    require(hc.failures==0,"capacity_exhausted: bounded search queue");\n'
        '    auto route_ms=ms(route_start);uint64_t peak_kib=0;')
    return text

def prepare():
    rp=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    baseline=json.loads(rp.read_text());files={str(rp):digest(rp),str(Path(__file__).resolve()):digest(__file__)}
    originals=list((ROOT/'src/native').glob('*.hpp'))+[ROOT/'src/native/site_runtime.cpp',ROOT/'hardware/vitis/search_heap.hpp',ROOT/'tests/native_site_search_driver.cpp']
    for p in originals:
        h=digest(p)
        if str(p) in baseline['code_inputs_and_references'] and h!=baseline['code_inputs_and_references'][str(p)]:
            raise ValueError('Changed baseline source: '+str(p))
        files[str(p)]=h
    for p in [ROOT/'scripts/check_search_heap_router.py',ROOT/'scripts/search_heap_router_pipeline.py']:
        files[str(p)]=digest(p)
    for mode,inputs in baseline['inputs'].items():
        for p in inputs.values():
            h=digest(p)
            if h!=baseline['code_inputs_and_references'][p]:raise ValueError('Changed real fixture')
            files[p]=h
        p=baseline['references'][mode];files[p]=baseline['code_inputs_and_references'][p]
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';source.mkdir()
    for p in originals:shutil.copyfile(p,source/p.name)
    for name,transform in [('site_search.hpp',transform_search),('site_runtime.cpp',transform_runtime)]:
        p=source/name;old=p.read_text();new=transform(old);p.write_text(new)
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='baseline/'+name,tofile='heap/'+name)))
    driver=source/'native_site_search_driver.cpp'
    driver.write_text(driver.read_text().replace('../src/native/site_search.hpp','site_search.hpp'))
    generated={str(p):digest(p) for p in source.iterdir()}
    plan={'files':files,'generated':generated,'capacity':CAPACITY,'inputs':baseline['inputs'],'references':baseline['references'],
          'binary':str(OUT/'router'),'jobs':[{'mode':m,'execution':e,'cpu':c} for m,e,c in [('csr','direct',122),('csr','expanded',124),('compact','direct',125),('compact','expanded',126)]],
          'limitations':['CPU queue integration only; not a full HLS router.', '1048576-entry host-backed heap; 1023-entry HLS top is a separate component test.',
                         'Label/site maps, occupancy and negotiation remain CPU containers.','Only 14 physically evidenced site instances; no complete special-resource or board claim.',
                         'Single diagnostic run per condition; instrumentation timings are not performance statistics.']}
    command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(source/'site_runtime.cpp'),'-o',plan['binary']]
    with (OUT/'compile.log').open('x') as f:subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,check=True)
    plan['generated'][plan['binary']]=digest(plan['binary'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('HEAP_ROUTER_PREPARED',OUT,flush=True)
    return OUT

if __name__=='__main__':prepare()
