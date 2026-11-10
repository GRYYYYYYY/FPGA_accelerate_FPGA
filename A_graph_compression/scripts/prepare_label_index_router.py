#!/usr/bin/env python3
"""Prepare full-state label-index integration on top of external heap routing."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import digest
from label_index_transform import transform_search,transform_runtime

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/label_index_router_20261024_v1'
BASE=ROOT/'data/derived/external_heap_router_20261024_v1'

def main():
    pp=BASE/'plan.json';original=json.loads(pp.read_text())
    for p,h in {**original['files'],**original['generated']}.items():
        if digest(p)!=h:raise ValueError('Changed predecessor '+p)
    files={**original['files'],str(pp):digest(pp)}
    extra=[Path(__file__).resolve(),ROOT/'scripts/label_index_transform.py',ROOT/'scripts/label_index_router_pipeline.py',ROOT/'scripts/check_label_index_router.py',
           ROOT/'src/native/search_label_adapter.hpp',ROOT/'hardware/vitis/search_label_index.hpp',ROOT/'hardware/vitis/search_site_state.hpp']
    for p in extra:files[str(p)]=digest(p)
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';shutil.copytree(BASE/'source',source)
    for p in extra[-3:]:shutil.copyfile(p,source/p.name)
    for name,transform in [('site_search.hpp',transform_search),('site_runtime.cpp',transform_runtime)]:
        p=source/name;old=p.read_text();new=transform(old);p.write_text(new)
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='external_heap/'+name,tofile='label_index/'+name)))
    generated={str(p):digest(p) for p in source.iterdir()}
    binary=OUT/'router';command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(source/'site_runtime.cpp'),'-o',str(binary)]
    with (OUT/'compile.log').open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    generated[str(binary)]=digest(binary)
    plan={k:original[k] for k in ['inputs','references','jobs','capacity']}
    plan.update(files=files,generated=generated,label_capacity=524288,index_slots=1048576,state_capacity=[32,16,8],binary=str(binary),
                limitations=['CPU full search with bounded exact full-state hash index and external-layout heap; no board execution.',
                             'Key state capacities cover the current fixture union (18 signals,11 bit fields,7 categories); not a universal FPGA-resource bound.',
                             '524288 label capacity is an explicit trial limit, not yet justified by full-workload peak measurements.',
                             'Native cost/parent labels, state merge, occupancy and negotiation are still CPU containers.',
                             'Only 14 physically evidenced site instances; full special-resource semantics remain incomplete.',
                             'Single diagnostic run per condition; timings not performance statistics.'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('LABEL_INDEX_ROUTER_PREPARED',OUT,flush=True)

if __name__=='__main__':main()
