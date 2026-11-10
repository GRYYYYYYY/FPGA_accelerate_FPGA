#!/usr/bin/env python3
"""Compile and execute independently referenced searches through flat storage."""
import json
import os
import subprocess
from pathlib import Path
from derive_search_flat_controller import ROOT,core,adapter,replace_once
from run_word_controller_checks import expected_driver,NAMES
from prepare_search_heap_router import digest
OUT=ROOT/'data/derived/flat_controller_checks_20261024_v1'

def driver(name):
    if name=='test_search_flat_abi':return (ROOT/'tests'/f'{name}.cpp').read_text()
    s=expected_driver(name).replace('search_word_controller_adapter.hpp','search_flat_controller_adapter.hpp').replace('word_controller_adapter::','flat_controller_adapter::').replace('search_controller_words.hpp','search_controller_flat.hpp').replace('WordSearchController','FlatSearchController')
    if name=='test_search_snapshot_provider':
        s=replace_once(s,'auto p=expected.path[i];const auto& e=w.path[i].edge;',
            'auto p=expected.path[i];const uint32_t* words=w.path+uint64_t(i)*8;const fpga_search::LabelEdge e{words[1],words[2],words[3],words[4],words[5],words[6],words[7]};')
        s=replace_once(s,'w.path[i].source','words[0]')
        s=replace_once(s,'w.unknown_pips[i].tile,w.unknown_pips[i].pip','uint32_t(w.unknown_pips[i]>>32),uint32_t(w.unknown_pips[i])')
    if name=='test_search_snapshot_cxx14':
        s=replace_once(s,'fpga_search::PipIdentity pips[4]{};fpga_search::PathEdge path[8]{};',
            'uint64_t pips[4]{};uint32_t path[8*8]{};')
        s=s.replace('path[0].source','path[0]').replace('path[0].edge.pip','path[3]').replace('path[1].source','path[8]').replace('path[1].edge.pip','path[11]').replace('pips[0].pip==3','pips[0]==((uint64_t(2)<<32)|3)')
    return s

def save(p,value):
    with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    if (ROOT/'hardware/vitis/search_controller_flat.hpp').read_text()!=core() or (ROOT/'src/native/search_flat_controller_adapter.hpp').read_text()!=adapter():raise ValueError('Unaccounted algorithm change')
    OUT.mkdir(exist_ok=False);source=OUT/'source';source.mkdir()
    files={};names=NAMES+['test_search_flat_abi'];commands={}
    for name in names:
        p=source/(name+'.cpp');p.write_text(driver(name));files[str(p)]=digest(p)
        files[str(ROOT/'tests'/(name+'.cpp'))]=digest(ROOT/'tests'/(name+'.cpp'))
        standard='c++14' if name in ['test_search_snapshot_cxx14','test_search_flat_abi'] else 'c++17'
        commands[name]=['taskset','-c','120','g++','-std='+standard,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT/'hardware/vitis'),'-I'+str(ROOT/'src/native'),str(p),'-o',str(OUT/name)]
    for folder in ['hardware/vitis','src/native']:
        for p in (ROOT/folder).glob('*.hpp'):files[str(p)]=digest(p)
    for name in ['derive_search_flat_controller.py','run_flat_controller_checks.py','run_word_controller_checks.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    save(OUT/'plan.json',{'files':files,'compile_commands':commands,'cases':names,'scope':'Full single-search differential with explicit PIP and path word layout; CPU only.'})
    state={'owner_pid':os.getpid(),'status':'running','completed':[]}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        for name in names:
            for stage,cmd in [('compile',commands[name]),('run',['taskset','-c','120',str(OUT/name)])]:
                prefix=OUT/(name+'.'+stage);log=prefix.with_suffix(prefix.suffix+'.log')
                with log.open('x') as stream:
                    child=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT)
                    state.update(case=name,stage=stage,child_pid=child.pid);update();code=child.wait()
                receipt={'exit_code':code,'command':cmd,'log_sha256':digest(log),'plan_sha256':digest(OUT/'plan.json')}
                if stage=='run':receipt['binary_sha256']=digest(OUT/name)
                save(prefix.with_suffix(prefix.suffix+'.receipt.json'),receipt)
                if code:raise RuntimeError(name+' '+stage+' failed')
            state['completed'].append(name);update();print(log.read_text(),flush=True)
        state['status']='complete';update()
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
