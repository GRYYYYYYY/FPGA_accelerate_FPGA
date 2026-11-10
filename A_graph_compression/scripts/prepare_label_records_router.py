#!/usr/bin/env python3
"""Prepare bounded cost/parent/edge storage on the full-state indexed router."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import digest
from label_records_transform import transform_search,transform_runtime

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/label_records_router_20261024_v1'
BASE=ROOT/'data/derived/label_index_router_20261024_v1'

def main():
    pp=BASE/'plan.json';original=json.loads(pp.read_text())
    for p,h in {**original['files'],**original['generated']}.items():
        if digest(p)!=h:raise ValueError('Changed predecessor '+p)
    files={**original['files'],str(pp):digest(pp)}
    extra=[Path(__file__).resolve(),ROOT/'scripts/label_records_transform.py',ROOT/'scripts/label_records_router_pipeline.py',ROOT/'scripts/check_label_records_router.py',
           ROOT/'src/native/search_record_adapter.hpp',ROOT/'hardware/vitis/search_label_records.hpp']
    for p in extra:files[str(p)]=digest(p)
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';shutil.copytree(BASE/'source',source)
    for p in extra[-2:]:shutil.copyfile(p,source/p.name)
    for name,transform in [('site_search.hpp',transform_search),('site_runtime.cpp',transform_runtime)]:
        p=source/name;old=p.read_text();new=transform(old);p.write_text(new)
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='label_index/'+name,tofile='label_records/'+name)))
    generated={str(p):digest(p) for p in source.iterdir()}
    binary=OUT/'router';command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(source/'site_runtime.cpp'),'-o',str(binary)]
    with (OUT/'compile.log').open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    generated[str(binary)]=digest(binary)
    plan={k:original[k] for k in ['inputs','references','jobs','capacity','label_capacity','index_slots','state_capacity']}
    plan.update(files=files,generated=generated,binary=str(binary),record_words=10,
                limitations=['CPU full search with bounded full-state index and explicit heap/label word storage; no board execution.',
                             'Native temporary site views/merge, result retention, graph access, occupancy and negotiation remain CPU containers.',
                             'Only 14 physically evidenced site instances; full special-resource semantics remain incomplete.',
                             'Key and label limits await complete workload validation; failures remain explicit.',
                             'Single diagnostic run per condition, not performance statistics.'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('LABEL_RECORDS_ROUTER_PREPARED',OUT,flush=True)

if __name__=='__main__':main()
