#!/usr/bin/env python3
"""Freeze complete negotiation with the static semantic and cost provider."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
from word_snapshot_routes_transform import transform_routes,transform_runtime

OUT=ROOT/'data/derived/word_snapshot_router_20261024_v1'
PRIOR=ROOT/'results/snapshot_router_audit_20261024_v1.json'
PRIOR_STATUS='four_full_router_snapshot_conditions_independently_verified'

def prepare():
    baseline_path=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    baseline=json.loads(baseline_path.read_text())
    files={str(baseline_path):digest(baseline_path)}
    originals=list((ROOT/'src/native').glob('*.hpp'))+[ROOT/'src/native/site_runtime.cpp']
    originals += [ROOT/'hardware/vitis'/name for name in ['search_heap.hpp','search_heap_external.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp','search_controller.hpp','search_cost_snapshot.hpp','search_snapshot_provider.hpp','search_key_words.hpp','search_controller_words.hpp']]
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
    extras=['scripts/prepare_word_snapshot_router.py','scripts/word_snapshot_routes_transform.py','scripts/snapshot_routes_transform.py','scripts/controller_search_transform.py',
            'scripts/label_index_transform.py','scripts/prepare_search_heap_router.py','scripts/word_snapshot_router_pipeline.py','scripts/check_word_snapshot_router.py','scripts/check_snapshot_router.py','scripts/prepare_snapshot_router.py',
            'tests/test_snapshot_routes_random.cpp','tests/test_snapshot_routes_integration.py','tests/test_snapshot_router_audit.py','tests/test_word_snapshot_routes.py','tests/test_word_snapshot_router_audit.py',
            'results/word_snapshot_routes_component_20261024_v1.json','results/search_word_controller_component_20261024_v1.json','results/search_snapshot_provider_component_20261024_v1.json']
    for name in extras:
        p=ROOT/name;files[str(p)]=digest(p)
    OUT.mkdir(parents=True,exist_ok=False);source=OUT/'source';source.mkdir()
    for p in originals:shutil.copyfile(p,source/p.name)
    for name,transform in [('site_routes.hpp',transform_routes),('site_runtime.cpp',transform_runtime)]:
        p=source/name;old=p.read_text();new=transform(old);p.write_text(new)
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='native/'+name,tofile='word_snapshot/'+name)))
    binary=OUT/'router'
    command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(source/'site_runtime.cpp'),'-o',str(binary)]
    with (OUT/'compile.log').open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    generated={str(p):digest(p) for p in source.iterdir()};generated[str(binary)]=digest(binary)
    plan=dict(files=files,generated=generated,binary=str(binary),inputs=baseline['inputs'],references=baseline['references'],
              prior_audit=str(PRIOR),prior_status=PRIOR_STATUS,
              jobs=[{'mode':m,'execution':e,'cpu':c} for m,e,c in [('csr','direct',122),('csr','expanded',124),('compact','direct',125),('compact','expanded',126)]],
              key_words=65,key_pool_bytes=272629760,capacity=131072,label_capacity=524288,index_slots=1048576,state_capacity=[32,16,8],
              nodes=1048576,degree=1024,roots=1048576,unknown_pips=1100754,path=524288,expansions=200000,config_owners=65536,config_history=65536,fixed_records=65536,attributes=65536,semantics=256,protected_pips=1048576,
              limitations=['CPU full negotiated routing using word-addressed keys, bounded controller and static semantic/cost provider; no HLS/RTL/physical timing/board result.',
                           'Native graph decoding, between-search snapshot construction, node/site occupancy updates, conflict detection and result retention still execute on CPU.',
                           'Metadata is normalized once; dynamic snapshots are bound after releasing the current net, then reused across its sinks.',
                           'Only 14 physically evidenced site instances; complete special-resource semantics remain incomplete.',
                           'Explicit snapshot and controller capacity limits; failures abort the batch, without pruning.',
                           'Single diagnostic run per condition; timings are not performance statistics.'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('WORD_SNAPSHOT_ROUTER_PREPARED',OUT,flush=True)

if __name__=='__main__':prepare()
