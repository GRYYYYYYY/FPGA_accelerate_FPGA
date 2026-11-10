#!/usr/bin/env python3
"""Freeze actual production top binaries, then test packet ABI and real searches."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
OUT=ROOT/'data/derived/search_kernel_cpu_20261024_v3'

def save(path,obj):
    with path.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')

def main():
    from derive_search_kernel_offsets import verify,OUT as OFFSET_SOURCE
    verify()
    graph_plan=ROOT/'data/derived/search_graph_checks_20261024_v1/plan.json'
    probe_plan=ROOT/'data/derived/search_snapshot_probes_20261024_v1/plan.json'
    graph=json.loads(graph_plan.read_text());probes=json.loads(probe_plan.read_text())
    OUT.mkdir(exist_ok=False);files={};inputs={}
    for name in ['packet','real','cost']:
        path=OUT/name;shutil.copyfile('/tmp/a_search_kernel_'+name+'_offsets_20261024',path);path.chmod(0o755);files[str(path)]=digest(path)
    for mode in ['csr','compact']:
        inputs[mode]={**probes['inputs'][mode],'config':graph['inputs'][mode]['config']}
        for key,p in inputs[mode].items():
            frozen=graph['files'] if key=='config' else probes['files']
            if digest(p)!=frozen[p]:raise ValueError('Changed real input '+p)
            files[p]=digest(p)
    for folder in ['hardware/vitis','src/native']:
        for p in (ROOT/folder).glob('*.hpp'):files[str(p)]=digest(p)
    for p in [graph_plan,probe_plan,ROOT/'hardware/vitis/search_kernel_top.cpp',ROOT/'tests/test_search_kernel_packet.cpp',ROOT/'tests/test_search_offset_cost.cpp',ROOT/'tests/test_search_kernel_real.cpp',Path(__file__).resolve()]:files[str(p)]=digest(p)
    for mode in ['csr','compact']:
        p=OUT/('search_kernel_'+mode+'.o');shutil.copyfile('/tmp/a_search_kernel_offsets_'+mode+'_20261024.o',p);files[str(p)]=digest(p)
    for p in OFFSET_SOURCE.iterdir():files[str(p)]=digest(p)
    p=ROOT/'scripts/derive_search_kernel_offsets.py';files[str(p)]=digest(p)
    save(OUT/'plan.json',{'files':files,'inputs':inputs,'compiler_flags':'-O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined; C++14 packet test; C++17 production top/oracle; -Wno-unknown-pragmas for top objects',
        'top_macros':{'csr':['SEARCH_GRAPH_MODE=0','SEARCH_TOP_NAME=search_kernel_csr'],'compact':['SEARCH_GRAPH_MODE=1','SEARCH_TOP_NAME=search_kernel_compact']},
        'scope':'Offset-based production top C model at full workspace limits, real image decoder and packet; 16 empty occupancy/history probes plus 16 deterministic node penalty probes per mode.',
        'limitations':['Probe workload, not complete 1062-net negotiation.','Only existing 14 physically evidenced site instances.','No HLS synthesis, RTL or board performance evidence.']})
    jobs=[('packet',['taskset','-c','120',str(OUT/'packet')]),('cost',['taskset','-c','120',str(OUT/'cost')])]
    for mode in ['csr','compact']:
        inp=inputs[mode];jobs.append((mode,['taskset','-c','120',str(OUT/'real'),inp['image'],inp['fixture'],inp['sites'],inp['config']]))
    state={'owner_pid':os.getpid(),'status':'running','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        for name,command in jobs:
            log=OUT/(name+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT)
                save(OUT/(name+'.submission.json'),{'command':command,'pid':child.pid,'plan_sha256':digest(OUT/'plan.json')})
                state.update(case=name,child_pid=child.pid);update();code=child.wait()
            save(OUT/(name+'.receipt.json'),{'exit_code':code,'command':command,'log_sha256':digest(log)})
            if code:raise RuntimeError('Kernel CPU check failed '+name)
            state['completed'].append(name);update();print(log.read_text(),flush=True)
        state['status']='complete';update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
