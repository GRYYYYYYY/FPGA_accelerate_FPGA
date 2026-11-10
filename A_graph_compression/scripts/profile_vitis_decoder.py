#!/usr/bin/env python3
"""Count operations in diagnostic CPU copies; preserve all frozen kernel inputs.

Counts are not measured RTL latency, bandwidth or FPGA acceleration.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
from check_vitis_kernel import digest,require,validate_case_log
ROOT=Path(__file__).resolve().parents[1]

HEADER=r'''#pragma once
#include <cstdint>
#include <iostream>
namespace prof {
struct Counters {
 uint64_t tile_calls=0,tile_steps=0,alias_calls=0,alias_steps=0,index_calls=0,index_steps=0;
 uint64_t expand_calls=0,sort_calls=0,sort_words=0,sort_shifts=0,requests=0,decoded_records=0,max_degree=0,status[5]={};
};
static Counters c;
struct Scope {
 Scope(){c=Counters();}
 ~Scope(){
  std::cout<<"PROFILE {\"tile_calls\":"<<c.tile_calls<<",\"tile_steps\":"<<c.tile_steps
  <<",\"alias_calls\":"<<c.alias_calls<<",\"alias_steps\":"<<c.alias_steps
  <<",\"index_calls\":"<<c.index_calls<<",\"index_steps\":"<<c.index_steps
  <<",\"expand_calls\":"<<c.expand_calls<<",\"sort_calls\":"<<c.sort_calls
  <<",\"sort_words\":"<<c.sort_words<<",\"sort_shifts\":"<<c.sort_shifts
  <<",\"requests\":"<<c.requests<<",\"decoded_records\":"<<c.decoded_records
  <<",\"max_degree\":"<<c.max_degree<<",\"status\":[";
  for(int i=0;i<5;i++){if(i)std::cout<<',';std::cout<<c.status[i];}
  std::cout<<"]}"<<std::endl;
 }
};
}
'''

def once(text,old,new):
    require(text.count(old)==1,'Instrumentation anchor ambiguous: '+old)
    return text.replace(old,new)

def instrument(source):
    source=once(source,'#include "graph_body.hpp"','#include "graph_body.hpp"\n#include "profile.hpp"')
    for function,next_function,prefix in [('tile_lookup','alias_lookup','tile'),('alias_lookup','indexed_find','alias'),('indexed_find','less_edge','index')]:
        start=source.index(' '+function+'(');end=source.index(' '+next_function+'(',start)
        # The function body begins at its first brace; no parameter types change.
        opening=source.index('{',start);part=source[opening:end]
        part=once(part,'uint32_t lo=0, hi=',f'++prof::c.{prefix}_calls;\n    uint32_t lo=0, hi=')
        part=once(part,'while (lo<hi) {',f'while (lo<hi) {{++prof::c.{prefix}_steps;')
        source=source[:opening]+part+source[end:]
    source=once(source,'static bool less_edge(const EdgeRecord &a, const EdgeRecord &b) {',
                'static bool less_edge(const EdgeRecord &a, const EdgeRecord &b) {\n    ++prof::c.sort_calls;')
    source=once(source,'for (unsigned i=0;i<7;i++) {if(a.w[i]',
                'for (unsigned i=0;i<7;i++) {++prof::c.sort_words;if(a.w[i]')
    source=once(source,'    EdgeRecord e;','    ++prof::c.expand_calls;\n    EdgeRecord e;')
    source=once(source,'{buffer[j]=buffer[j-1];j--;}',
                '{++prof::c.sort_shifts;buffer[j]=buffer[j-1];j--;}')
    source=once(source,'    uint32_t c[CFG_WORDS];','    prof::Scope profiling_scope;\n    uint32_t c[CFG_WORDS];')
    source=once(source,'        if(status==0) {','''        ++prof::c.requests;++prof::c.status[status];prof::c.decoded_records+=degree;
        if(degree>prof::c.max_degree)prof::c.max_degree=degree;
        if(status==0) {''')
    return source

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    bundle=ROOT/'data/derived/vitis_graph_kernel_20261023_v2'
    audit=ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json';proof=json.loads(audit.read_text())
    require(proof['status']=='verified_vitis_xo_not_platform_linked','Missing kernel audit')
    plan=json.loads((bundle/'plan.json').read_text())
    for path,value in {**plan['files'],**plan['generated']}.items():require(digest(path)==value,'Frozen source/input changed')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    bound={str(Path(__file__).resolve()):digest(__file__),str(audit):digest(audit),str(bundle/'plan.json'):digest(bundle/'plan.json')}
    results={};generated={}
    for mode in ['csr','compact']:
        original=bundle/mode;target=out/mode;target.mkdir()
        (target/'graph_body.cpp').write_text(instrument((original/'graph_body.cpp').read_text()))
        (target/'profile.hpp').write_text(HEADER)
        for name in ['graph_body.hpp','graph_accel.hpp','graph_accel.cpp','test_graph_expand.cpp']:
            (target/name).write_bytes((original/name).read_bytes())
        for path in target.iterdir():generated[str(path)]=digest(path)
        binary=target/'profile';command=['g++','-std=c++14','-O2','-Wno-unknown-pragmas',str(target/'graph_body.cpp'),str(target/'graph_accel.cpp'),str(target/'test_graph_expand.cpp'),'-o',str(binary)]
        with (target/'compile.log').open('x') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        generated[str(binary)]=digest(binary);results[mode]={}
        for workload in ['full','rtl']:
            manifest=original/(workload+'.txt');log_path=target/(workload+'.log')
            with log_path.open('x') as log:
                run=subprocess.run(['taskset','-c','121',str(binary),str(manifest)],stdout=log,stderr=subprocess.STDOUT)
            require(run.returncode==0,'Diagnostic output failed golden comparison')
            text=log_path.read_text();cases=validate_case_log(text,manifest,1)
            profiles=[json.loads(line.removeprefix('PROFILE ')) for line in text.splitlines() if line.startswith('PROFILE ')]
            require(len(profiles)==len(cases),'Missing diagnostic rows')
            for case,profile in zip(cases,profiles):
                require(sum(profile['status'])==case['requests']==profile['requests'],'Diagnostic request count differs')
                require(sum(profile['status'][1:])==case['failed'],'Diagnostic statuses differ')
                case['profile']=profile
            results[mode][workload]=cases;generated[str(log_path)]=digest(log_path)
    for path,value in {**bound,**generated}.items():require(digest(path)==value,'Diagnostic artifact changed')
    for path,value in {**plan['files'],**plan['generated']}.items():require(digest(path)==value,'Frozen kernel input changed during profiling')
    report={'status':'cpu_operation_counts_golden_outputs_verified','source_audit_sha256':digest(audit),'source_bundle':str(bundle),
        'files':bound,'generated':generated,'results':results,
        'scope':'CPU instrumented copies of unchanged algorithms; same full and RTL fixtures, all counters/status/8-field records/guards checked by original golden testbench.',
        'limitations':['Operation counts are not RTL cycles, physical memory transactions or board timings.',
            'Each full batch has many rows; maximum degree does not assign all operations to that row.',
            'Lookup/sort hypothesis requires independently measured architectural experiments; no optimization applied.']}
    with (out/'report.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'output':str(out)}))

if __name__=='__main__':main()
