#!/usr/bin/env python3
"""Freeze a full bounded-search integration against the original native router."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
from controller_search_transform import transform_search,transform_runtime

OUT=ROOT/'data/derived/controller_router_20261024_v1'
PRIOR=ROOT/'results/label_records_router_audit_20261024_v1.json'
PRIOR_STATUS='four_full_router_label_records_conditions_independently_verified'

def prepare():
    baseline_path=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    baseline=json.loads(baseline_path.read_text())
    files={str(baseline_path):digest(baseline_path)}
    originals=list((ROOT/'src/native').glob('*.hpp'))+[ROOT/'src/native/site_runtime.cpp']
    originals += [ROOT/'hardware/vitis'/name for name in ['search_heap.hpp','search_heap_external.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp','search_controller.hpp']]
    for p in originals:
        h=digest(p)
        if str(p) in baseline['code_inputs_and_references'] and h!=baseline['code_inputs_and_references'][str(p)]:
            raise ValueError('Changed baseline source '+str(p))
        files[str(p)]=h
    for inputs in baseline['inputs'].values():
        for p in inputs.values():
            h=digest(p)
            if h!=baseline['code_inputs_and_references'][p]:raise ValueError('Changed real input '+p)
            files[p]=h
    for p in baseline['references'].values():files[p]=baseline['code_inputs_and_references'][p]
    extras=['scripts/prepare_controller_router.py','scripts/controller_search_transform.py','scripts/label_index_transform.py',
            'scripts/prepare_search_heap_router.py','scripts/controller_router_pipeline.py','scripts/check_controller_router.py',
            'tests/test_search_controller.cpp','tests/test_search_controller_bounds.cpp','tests/test_controller_search_integration.py',
            'tests/test_controller_router_audit.py','results/search_controller_component_20261024_v1.json']
    for name in extras:
        p=ROOT/name;files[str(p)]=digest(p)
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';source.mkdir()
    for p in originals:shutil.copyfile(p,source/p.name)
    for name,transform in [('site_search.hpp',transform_search),('site_runtime.cpp',transform_runtime)]:
        p=source/name;old=p.read_text();new=transform(old);p.write_text(new)
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='native/'+name,tofile='controller/'+name)))
    binary=OUT/'router'
    command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(source/'site_runtime.cpp'),'-o',str(binary)]
    with (OUT/'compile.log').open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    generated={str(p):digest(p) for p in source.iterdir()};generated[str(binary)]=digest(binary)
    plan=dict(files=files,generated=generated,binary=str(binary),inputs=baseline['inputs'],references=baseline['references'],
              prior_audit=str(PRIOR),prior_status=PRIOR_STATUS,
              jobs=[{'mode':m,'execution':e,'cpu':c} for m,e,c in [('csr','direct',122),('csr','expanded',124),('compact','direct',125),('compact','expanded',126)]],
              capacity=131072,label_capacity=524288,index_slots=1048576,state_capacity=[32,16,8],
              nodes=1048576,degree=1024,roots=1048576,unknown_pips=1100754,path=524288,expansions=200000,
              limitations=['CPU integration of the entire bounded single-search controller; no HLS, RTL, physical timing or board evidence for this controller.',
                           'Native graph/semantics/compatibility/cost callbacks, occupancy, negotiation and result retention still execute on CPU.',
                           'Full normalized per-path state is merged in the bounded core; raw demand normalization remains a native callback.',
                           'Only 14 physically evidenced site instances; complete special-resource semantics remain incomplete.',
                           'Explicit limits are trial bounds pending full workload validation; no pruning or silent truncation.',
                           'Single diagnostic run per condition; timings are not performance statistics.'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('CONTROLLER_ROUTER_PREPARED',OUT,flush=True)

if __name__=='__main__':prepare()
