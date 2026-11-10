#!/usr/bin/env python3
"""Validate the search adjacency on every canonical row of both real images."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from prepare_search_heap_router import ROOT,digest
from derive_search_graph_adjacency import derive,TARGET,BASE
OUT=ROOT/'data/derived/search_graph_checks_20261024_v1'

def save(path,obj):
    with path.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')

def main():
    if TARGET.read_text()!=derive():raise ValueError('Different graph decoder derivation')
    pp=BASE.parent/'plan.json';prior=json.loads(pp.read_text());frozen={**prior['files'],**prior['generated']}
    inputs={};files={str(pp):digest(pp)}
    for mode in ['csr','compact']:
        manifest=BASE.parent/mode/'board.txt';image,config,_=manifest.read_text().splitlines()[0].split()
        inputs[mode]={'image':image,'config':config}
        for p in [str(manifest),image,config,str(BASE/'graph_body.cpp'),str(BASE/'graph_body.hpp')]:
            if digest(p)!=frozen[p]:raise ValueError('Changed frozen graph input '+p)
            files[p]=digest(p)
    for name in ['tests/test_search_graph_adjacency.cpp','src/native/packed_graph.hpp','hardware/vitis/host_contract.hpp','scripts/run_search_graph_checks.py','scripts/derive_search_graph_adjacency.py']:
        files[str(ROOT/name)]=digest(ROOT/name)
    for name in ['search_controller.hpp','search_heap.hpp','search_heap_external.hpp','search_site_state.hpp','search_label_index.hpp','search_label_records.hpp','search_graph_adjacency.hpp']:
        p=ROOT/'hardware/vitis'/name;files[str(p)]=digest(p)
    OUT.mkdir(exist_ok=False);binary=OUT/'check';shutil.copyfile('/tmp/a_search_graph_adjacency_20261024',binary);binary.chmod(0o755);files[str(binary)]=digest(binary)
    save(OUT/'plan.json',{'owner_pid':os.getpid(),'files':files,'inputs':inputs,'binary':str(binary),'compiler_flags':'-std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined','limitations':['CPU full-row differential validation; no HLS or RTL evidence for this new search adjacency.','Host validates full AGRAPH01 descriptor identity; hardware bind checks section spans and mode.']})
    state={'owner_pid':os.getpid(),'status':'running','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        for mode in ['csr','compact']:
            inp=inputs[mode];command=['taskset','-c','120',str(binary),inp['image'],inp['config']]
            with (OUT/(mode+'.log')).open('x') as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
                save(OUT/(mode+'.submission.json'),{'command':command,'pid':child.pid,'plan_sha256':digest(OUT/'plan.json')})
                state.update(mode=mode,child_pid=child.pid);update();code=child.wait()
            save(OUT/(mode+'.receipt.json'),{'exit_code':code,'command':command,'log_sha256':digest(OUT/(mode+'.log'))})
            if code:raise RuntimeError('Graph check failed '+mode)
            state['completed'].append(mode);update();print((OUT/(mode+'.log')).read_text(),flush=True)
        state['status']='complete';update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
