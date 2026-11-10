#!/usr/bin/env python3
"""Prepare exact word-layout heap integration, preserving the earlier experiment."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import digest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/external_heap_router_20261024_v1'
BASE=ROOT/'data/derived/search_heap_router_20261024_v1'

def main():
    pp=BASE/'plan.json';original=json.loads(pp.read_text())
    for p,h in {**original['files'],**original['generated']}.items():
        if digest(p)!=h:raise ValueError('Changed predecessor '+p)
    files={**original['files'],str(pp):digest(pp)}
    extra=[Path(__file__).resolve(),ROOT/'scripts/external_heap_router_pipeline.py',ROOT/'scripts/check_external_heap_router.py',
           ROOT/'src/native/external_heap_adapter.hpp',ROOT/'hardware/vitis/search_heap_external.hpp']
    for p in extra:files[str(p)]=digest(p)
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';shutil.copytree(BASE/'source',source)
    shutil.copyfile(ROOT/'hardware/vitis/search_heap_external.hpp',source/'search_heap_external.hpp')
    old=(source/'search_heap_adapter.hpp').read_text();new=(ROOT/'src/native/external_heap_adapter.hpp').read_text()
    (source/'search_heap_adapter.hpp').write_text(new)
    (OUT/'adapter.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original_heap_adapter',tofile='external_heap_adapter')))
    p=source/'site_search.hpp';text=p.read_text();assert text.count('#define SEARCH_HEAP_CAPACITY 1048576')==1
    p.write_text(text.replace('#define SEARCH_HEAP_CAPACITY 1048576','#define SEARCH_HEAP_CAPACITY 131072'))
    generated={str(p):digest(p) for p in source.iterdir()}
    binary=OUT/'router';command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(source/'site_runtime.cpp'),'-o',str(binary)]
    with (OUT/'compile.log').open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    generated[str(binary)]=digest(binary)
    plan={k:original[k] for k in ['inputs','references','jobs']}
    plan.update(files=files,generated=generated,capacity=131072,binary=str(binary),
                limitations=['CPU full search using the exact three-word external heap helper; no board execution.',
                             'External heap is host-allocated here; this does not measure AXI/DDR/HBM performance.',
                             'Labels, site state, occupancy and negotiation remain native CPU containers.',
                             'Only 14 physically evidenced site instances; complete special-resource semantics remain incomplete.',
                             'Single diagnostic run per condition, not performance statistics.'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('EXTERNAL_HEAP_ROUTER_PREPARED',OUT,flush=True)

if __name__=='__main__':main()
