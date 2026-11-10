#!/usr/bin/env python3
"""Freeze two real full negotiated workloads using the production search top."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
from kernel_routes_transform import transform_routes,transform_runtime
from derive_search_kernel_offsets import OUT as KERNEL_SOURCE,verify
OUT=ROOT/'data/derived/complete_search_router_20261024_v1'
PRIOR=ROOT/'results/word_snapshot_router_audit_20261024_v1.json'
PRIOR_STATUS='four_full_router_word_snapshot_conditions_independently_verified'

def prepare():
    verify();component=ROOT/'results/kernel_route_component_20261024_v1.json';proof=json.loads(component.read_text())
    if proof['status']!='production_search_top_full_negotiation_cpu_differential_verified':raise ValueError('Missing negotiated kernel proof')
    for p,h in proof['artifacts'].items():
        if digest(p)!=h:raise ValueError('Changed component evidence '+p)
    baseline_path=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json';baseline=json.loads(baseline_path.read_text())
    graph_path=ROOT/'data/derived/search_graph_checks_20261024_v1/plan.json';graph=json.loads(graph_path.read_text())
    cpu_report=ROOT/'results/search_kernel_cpu_component_20261024_v3.json';cpu=json.loads(cpu_report.read_text())
    files={str(p):digest(p) for p in [component,baseline_path,graph_path,cpu_report]}
    originals=list((ROOT/'src/native').glob('*.hpp'))+[ROOT/'src/native/site_runtime.cpp',ROOT/'hardware/vitis/host_contract.hpp']+list(KERNEL_SOURCE.iterdir())
    for p in originals:
        h=digest(p)
        for bindings in [baseline['code_inputs_and_references'],cpu['artifacts']]:
            if str(p) in bindings and h!=bindings[str(p)]:raise ValueError('Changed frozen source '+str(p))
        files[str(p)]=h
    inputs={}
    for mode,inp in baseline['inputs'].items():
        inputs[mode]={**inp,'config':graph['inputs'][mode]['config']}
        for key,p in inputs[mode].items():
            h=digest(p);expected=graph['files'][p] if key=='config' else baseline['code_inputs_and_references'][p]
            if h!=expected:raise ValueError('Changed real input '+p)
            files[p]=h
    for p in baseline['references'].values():files[p]=baseline['code_inputs_and_references'][p]
    for name in ['prepare_complete_search_router.py','complete_search_router_pipeline.py','check_complete_search_router.py','kernel_routes_transform.py','derive_search_kernel_route_adapter.py','derive_search_kernel_offsets.py','check_word_snapshot_router.py','snapshot_routes_transform.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    OUT.mkdir(exist_ok=False);source=OUT/'source';source.mkdir()
    for p in originals:shutil.copyfile(p,source/p.name)
    for name,transform in [('site_routes.hpp',transform_routes),('site_runtime.cpp',transform_runtime)]:
        p=source/name;old=p.read_text();new=transform(old);p.write_text(new)
        (OUT/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='native/'+name,tofile='kernel/'+name)))
    flags=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas'];commands=[];objects=[]
    for mode_id,mode in enumerate(['csr','compact']):
        obj=OUT/('search_kernel_'+mode+'.o');objects.append(str(obj));commands.append(flags+['-DSEARCH_GRAPH_MODE='+str(mode_id),'-DSEARCH_TOP_NAME=search_kernel_'+mode,'-c',str(source/'search_kernel_top.cpp'),'-o',str(obj)])
    binary=OUT/'router';commands.append(flags+[str(source/'site_runtime.cpp'),*objects,'-o',str(binary)])
    with (OUT/'compile.log').open('x') as log:
        for command in commands:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    generated={str(p):digest(p) for p in source.iterdir()}
    for p in [binary,*map(Path,objects)]:generated[str(p)]=digest(p)
    plan=dict(files=files,generated=generated,binary=str(binary),compile_commands=commands,inputs=inputs,references=baseline['references'],prior_audit=str(PRIOR),prior_status=PRIOR_STATUS,
        jobs=[{'mode':'csr','execution':'kernel','cpu':122},{'mode':'compact','execution':'kernel','cpu':125}],
        key_words=65,key_pool_bytes=272629760,capacity=131072,label_capacity=524288,index_slots=1048576,state_capacity=[32,16,8],nodes=1048576,degree=1024,roots=1048576,unknown_pips=1100754,path=524288,expansions=200000,
        config_owners=65536,config_history=65536,fixed_records=65536,attributes=65536,semantics=256,protected_pips=1048576,packet_words=4194304,
        limitations=['CPU C model of actual production search top; no native graph adjacency fallback; two representations, two complete 1062-net resident batches.',
            'Only kernel execution conditions: no misleading direct/expanded labels when native adjacency is not used.',
            'Host constructs one snapshot packet per net after releasing its old route, updates initial demand/root/target per sink, and performs outer negotiation and occupancy changes.',
            'Kernel word counters are logical ABI volume, not measured PCIe/HBM traffic.',
            'Only 14 physically evidenced site instances; full special-resource semantics incomplete.',
            'Single diagnostic execution per condition; no statistical speedup or board performance claim.'])
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    print('KERNEL_ROUTER_PREPARED',OUT,flush=True)

if __name__=='__main__':prepare()
