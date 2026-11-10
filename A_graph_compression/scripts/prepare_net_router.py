#!/usr/bin/env python3
"""Replace host sink iteration with the actual integrated top; raw frames are observations."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from check_vitis_kernel import digest,require
from derive_search_flat_controller import replace_once as one
from net_router_transform import adapt
ROOT=Path(__file__).resolve().parents[1]
def main():
    base=ROOT/'data/derived/retained_edges_integration_20261024_v1'
    evidence=ROOT/'results/retained_edges_component_20261024_v1.json';proof=json.loads(evidence.read_text())
    for p,h in proof['files'].items():require(digest(p)==h,'Changed complete edge integration '+p)
    out=ROOT/'data/derived/net_router_20261025_v1';out.mkdir(exist_ok=False);source=out/'source';shutil.copytree(base/'source',source)
    top=ROOT/'hardware/vitis/search_net_observed_top.cpp';shutil.copyfile(top,source/top.name)
    for name in ['search_resident_snapshot.hpp','search_node_occupancy.hpp','search_site_occupancy.hpp','search_route_tree.hpp','search_retained_edges.hpp','search_retained_nodes.hpp','search_site_request.hpp']:
        original=ROOT/'hardware/vitis'/name;require(digest(original)==digest(source/name),'Different component core '+name)
    # Expose exclusively owned backing buffers to the actual integrated CPU top.
    p=source/'route_tree_adapter.hpp';s=p.read_text();s=one(s,'    unsigned emit_roots()', '    uint64_t* resident_meta(){return meta_.data();}\n    uint64_t* resident_bits(){return bits_.data();}\n    uint64_t* resident_demands(){return demands_.data();}\n    uint32_t* resident_roots(){return roots_.data();}\n    unsigned emit_roots()');p.write_text(s)
    p=source/'retained_edges_adapter.hpp';s=p.read_text();s=one(s,'    void clear(uint32_t net)', '    uint64_t* resident_meta(){return meta_.data();}\n    uint32_t* resident_rows(){return rows_.data();}\n    void clear(uint32_t net)');p.write_text(s)
    raw=top.read_text();declaration=raw[raw.index('extern "C" void SEARCH_TOP_NAME'):raw.index(' {',raw.index('extern "C" void SEARCH_TOP_NAME'))]+';'
    observer='''#pragma once
#include <array>
#include <vector>
#include <algorithm>
#include <stdexcept>
namespace sink_loop_observation {
struct Frame {uint32_t target;unsigned roots;std::array<uint64_t,81> result;std::vector<uint64_t> unknown_nodes,unknown_pips;std::vector<uint32_t> path;};
inline thread_local std::vector<Frame>* active=nullptr;
struct Scope {explicit Scope(std::vector<Frame>& frames){if(active)throw std::logic_error("nested sink observer");active=&frames;}~Scope(){active=nullptr;}Scope(const Scope&)=delete;Scope& operator=(const Scope&)=delete;};
}
extern "C" void search_sink_loop_observe(uint32_t target,unsigned roots,const uint64_t* result,const uint64_t* nodes,const uint64_t* pips,const uint32_t* path,unsigned domain){
    using namespace sink_loop_observation;
    if(!active || result[7]>524288 || result[8]>1048576 || result[9]>1100754 || result[15]!=1)throw std::logic_error("invalid sink observer frame");
    Frame f{};f.target=target;f.roots=roots;std::copy(result,result+81,f.result.begin());
    f.path.assign(path,path+8*result[7]);f.unknown_nodes.assign(nodes,nodes+(domain+63)/64);f.unknown_pips.assign(pips,pips+result[9]);active->push_back(std::move(f));
}
'''
    observer+=declaration.replace('SEARCH_TOP_NAME','search_net_csr')+'\n'+declaration.replace('SEARCH_TOP_NAME','search_net_compact')+'\n'
    (source/'sink_loop_observer.hpp').write_text(observer)
    p=source/'search_kernel_route_adapter.hpp';s=p.read_text();s=one(s,'#pragma once','#pragma once\n#include "sink_loop_observer.hpp"')
    start=s.index('    site_native::SearchResult search(');tail=s.index('        typename Core::Result r;',start);end=s.index('        return out;',tail)
    decode=s[tail:end].replace('w.path','frame.path.data()').replace('w.unknown_nodes','frame.unknown_nodes.data()').replace('w.unknown_pips','frame.unknown_pips.data()')
    method='''    std::vector<site_native::SearchResult> search_all(route_tree_host::Tree& tree,const std::vector<uint32_t>& targets,uint64_t budget,retained_edges_host::Store& retained_edges,uint32_t net){
        if(!packet_words_ || packet_[4]!=net || targets.size()>1048576)fail(false,"invalid integrated sink invocation");
        auto& w=flat_controller_adapter::storage<Limits>().workspace;
        packet_[8]=budget;uint64_t meta[2]={w.epoch,w.key_count},result[81]{},summary[8]{};
        std::vector<sink_loop_observation::Frame> frames;
        {sink_loop_observation::Scope observe(frames);
            auto kernel=image_.config[0]==0?search_net_csr:search_net_compact;
            kernel(image_.image,image_.config,image_.image_words,tree.resident_roots(),packet_.data(),packet_words_,w.heap,w.slots,w.records,w.keys,w.unknown_nodes,w.unknown_pips,w.path,meta,result,tree.resident_meta(),tree.resident_bits(),tree.resident_demands(),retained_edges.resident_meta(),retained_edges.resident_rows(),summary,targets.data(),unsigned(targets.size()));
        }
        if(summary[0])fail(summary[0]==4,"integrated sink loop rejected operation");
        if(summary[2]!=targets.size() || frames.size()!=targets.size() || meta[0]>UINT32_MAX || meta[1]>Limits::labels)fail(false,"integrated sink observations incomplete");
        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);
        std::vector<site_native::SearchResult> outputs;
        for(size_t index=0;index<frames.size();++index){
            const auto& frame=frames[index];const uint64_t* result=frame.result.data();uint32_t target=targets[index];
            if(frame.target!=target || result[0]>6 || result[7]>Limits::path || result[8]>Limits::nodes || result[9]>Limits::unknown_pips)fail(false,"invalid per-sink observation");
            ++kernel_counters.calls;kernel_counters.submitted_words+=packet_words_;kernel_counters.max_roots=std::max(kernel_counters.max_roots,frame.roots);
            auto& c=flat_controller_adapter::counters;++c.searches;site_native::SearchResult out;
'''+decode+'''            outputs.push_back(std::move(out));
        }
        return outputs;
    }
'''
    # Replace the complete old per-sink method, preserving the class terminator.
    finish=s.index('\n    }',end)+len('\n    }');s=s[:start]+method+s[finish:];p.write_text(s)
    for name in ['site_routes.hpp','snapshot_test_routes.hpp']:
        p=source/name;s=p.read_text();old='''            auto targets=q.sinks;std::sort(targets.begin(),targets.end());std::vector<SearchResult> connections;
            for (auto target:targets) {
                auto connection=snapshot.search(tree,target,budget,retained_edges,q.net);
                connections.push_back(std::move(connection));
            }'''
        new='''            auto targets=q.sinks;std::sort(targets.begin(),targets.end());
            auto connections=snapshot.search_all(tree,targets,budget,retained_edges,q.net);'''
        p.write_text(one(s,old,new))
    adapt(source)
    command=json.loads((base/'compile_command.json').read_text());command=[x.replace(str(base/'source'),str(source)).replace(str(base/'differential'),str(out/'differential')) for x in command]
    command[2]='125';command.insert(command.index('-o'),str(out/'sink_csr.o'));command.insert(command.index('-o'),str(out/'sink_compact.o'))
    files={str(Path(p)):h for p,h in proof['files'].items()}
    for p in [top,evidence,ROOT/'scripts/net_router_transform.py',Path(__file__).resolve()]:files[str(p)]=digest(p)
    generated={str(p):digest(p) for p in source.iterdir()}
    (out/'plan.json').write_text(json.dumps(dict(files=files,generated=generated,command=command),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='prepare')
    def save():
        q=out/'state.tmp';q.write_text(json.dumps(state,indent=2)+'\n');q.replace(out/'state.json')
    def run(phase,cmd):
        state['stage']=phase;save();env={k:v for k,v in os.environ.items() if k!='LD_PRELOAD'};env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
        with (out/(phase+'.log')).open('x') as f:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/(phase+'.receipt.json')).write_text(json.dumps(dict(command=cmd,exit_code=code,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n');require(code==0,'Integrated router phase failed '+phase)
        print(phase,'PASS',flush=True)
    save()
    try:
        for mode,name in [(0,'csr'),(1,'compact')]:run('compile_'+name,['taskset','-c','125','g++','-std=c++14','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wno-unknown-pragmas','-DSEARCH_SINK_LOOP_OBSERVE=1','-DSEARCH_GRAPH_MODE='+str(mode),'-DSEARCH_TOP_NAME=search_net_'+name,'-c',str(source/top.name),'-o',str(out/('sink_'+name+'.o'))])
        run('compile_differential',command)
        run('differential',['taskset','-c','125',str(out/'differential'),str(source/'sites.txt')])
        expected=('ROUND_CONTROL_ROUTE_RANDOM_PASS cases=400 modes=2 snapshots=3750 searches=4938 rounds=1250 node_history_snapshots=2412 site_history_snapshots=2106 site_paths=2896 incomplete=190 routed=210\nROUND_CONTROL_ROUTE_FULL_RESULTS_PASS\n')
        require((out/'differential.log').read_text()==expected,'Different complete differential scope')
        for p,h in {**files,**generated}.items():require(digest(p)==h,'Changed integration input '+p)
        state.update(status='complete',stage='complete_negotiation_intermediate_differential_verified');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
