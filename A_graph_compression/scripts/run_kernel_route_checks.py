#!/usr/bin/env python3
"""Complete negotiation differential through the actual production C top."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from derive_search_kernel_route_adapter import ROOT,TARGET,derive
from kernel_routes_transform import transform_routes
from prepare_search_heap_router import digest
OUT=ROOT/'data/derived/kernel_route_checks_20261024_v1'

def driver():
    s=(ROOT/'tests/test_snapshot_routes_random.cpp').read_text()
    s=s.replace('../src/native/site_routes.hpp',str(ROOT/'src/native/site_routes.hpp')).replace('snapshot_route::','kernel_route::').replace('controller_adapter::','flat_controller_adapter::')
    begin=s.index('struct RandomRouteLimits:');end=s.index('struct RandomRouteGraph',begin)
    s=s[:begin]+'using RandomRouteLimits=kernel_route::RegionLimits;\n#include "synthetic_search_image.hpp"\n'+s[end:]
    s=s.replace('    size_t node_count()const{return rows.size();}', '    bool native_allowed=true;\n    size_t node_count()const{return rows.size();}')
    s=s.replace('bool neighbors(unsigned n,std::vector<Edge>& out){','bool neighbors(unsigned n,std::vector<Edge>& out){if(!native_allowed)throw std::logic_error("native fallback during kernel test");')
    anchor='        site_native::SiteState fixed(sites.fixed_signals,sites.fixed);'
    s=s.replace(anchor,'''        // Make physical wire aliases canonical, then match production ordering
        // before evaluating either implementation. Preserve all parallel edges.
        for(unsigned n=0;n<graph.rows.size();++n){
            for(auto& e:graph.rows[n]){e.up=e.dir?e.dst:n;e.down=e.dir?n:e.dst;}
            std::stable_sort(graph.rows[n].begin(),graph.rows[n].end(),[](const Edge& a,const Edge& b){return std::make_tuple(a.dst,a.tile,a.pip,a.dir,a.dir?a.down:a.up,a.dir?a.up:a.down)<std::make_tuple(b.dst,b.tile,b.pip,b.dir,b.dir?b.down:b.up,b.dir?b.up:b.down);});
        }
'''+anchor)
    anchor='        kernel_route::counters={};flat_controller_adapter::counters={};'
    s=s.replace(anchor,'''        graph.native_allowed=false;
        for(unsigned mode=0;mode<2;++mode){
        SyntheticSearchImage image(graph.rows,graph.unknown,sites.attributes,mode);kernel_route::ImageScope scope(image.view());
        kernel_route::kernel_counters={};
'''+anchor)
    anchor='rounds+=actual.iterations.size();++statuses[actual.status];'
    s=s.replace(anchor,anchor+'''
        assert(kernel_route::kernel_counters.calls==expected_searches && kernel_route::kernel_counters.packets==c.snapshots);
        }
''')
    s=s.replace('SNAPSHOT_ROUTE_MISMATCH','KERNEL_ROUTE_MISMATCH').replace('SNAPSHOT_ROUTE_RANDOM_PASS cases=200','KERNEL_ROUTE_RANDOM_PASS cases=400 modes=2').replace('SNAPSHOT_ROUTE_FULL_RESULTS_PASS','KERNEL_ROUTE_FULL_RESULTS_PASS')
    return s

def save(p,value):
    with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    if TARGET.read_text()!=derive():raise ValueError('Different route adapter derivation')
    prior=ROOT/'data/derived/search_kernel_cpu_20261024_v3/plan.json';frozen=json.loads(prior.read_text())['files']
    OUT.mkdir(exist_ok=False);source=OUT/'source';source.mkdir();files={str(prior):digest(prior)}
    for p in (ROOT/'src/native').glob('*.hpp'):files[str(p)]=digest(p)
    kernel_source=ROOT/'hardware/vitis/search_kernel_offsets_v3'
    for p in kernel_source.iterdir():
        if digest(p)!=frozen[str(p)]:raise ValueError('Changed production top '+str(p))
        files[str(p)]=digest(p)
    generated=transform_routes((ROOT/'src/native/site_routes.hpp').read_text()).replace('namespace site_native {','namespace snapshot_test_native {\nusing namespace site_native;')
    for name in ['site_search.hpp','site_ledger.hpp','netlist_routes.hpp','search_kernel_route_adapter.hpp']:
        generated=generated.replace('#include "'+name+'"','#include "'+str(ROOT/'src/native'/name)+'"')
    (source/'snapshot_test_routes.hpp').write_text(generated);(source/'driver.cpp').write_text(driver());(source/'sites.txt').write_text('NATIVE_SITES_V1 16 4 4 0 0 0 0 1 1\n')
    objects=[]
    for mode in ['csr','compact']:
        p=prior.parent/('search_kernel_'+mode+'.o')
        if digest(p)!=frozen[str(p)]:raise ValueError('Changed production object '+str(p))
        target=source/p.name;shutil.copyfile(p,target);objects.append(str(target))
    for p in source.iterdir():files[str(p)]=digest(p)
    for name in ['scripts/run_kernel_route_checks.py','scripts/derive_search_kernel_route_adapter.py','scripts/kernel_routes_transform.py','tests/synthetic_search_image.hpp','tests/test_snapshot_routes_random.cpp']:
        p=ROOT/name;files[str(p)]=digest(p)
    binary=OUT/'check';command=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas','-fsanitize=address,undefined','-I'+str(kernel_source),'-I'+str(ROOT/'hardware/vitis'),'-I'+str(ROOT/'src/native'),'-I'+str(ROOT/'tests'),'-I'+str(source),str(source/'driver.cpp'),*objects,'-o',str(binary)]
    save(OUT/'plan.json',{'files':files,'compile_command':command,'scope':'200 random full negotiation problems, both CSR and compact synthetic payloads, actual production top/full capacities; no native adjacency fallback.'})
    state={'owner_pid':os.getpid(),'status':'running','stage':'compile'}
    def update():
        p=OUT/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(OUT/'state.json')
    update()
    try:
        for name,cmd in [('compile',command),('run',['taskset','-c','119',str(binary),str(source/'sites.txt')])]:
            log=OUT/(name+'.log')
            with log.open('x') as stream:
                child=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT);state.update(stage=name,child_pid=child.pid);update();code=child.wait()
            save(OUT/(name+'.receipt.json'),{'exit_code':code,'command':cmd,'log_sha256':digest(log),'plan_sha256':digest(OUT/'plan.json'),'binary_sha256':digest(binary) if binary.exists() else None})
            if code:raise RuntimeError('Kernel route '+name+' failed')
        state.update(status='complete',stage='cpu_differential_verified');update();print((OUT/'run.log').read_text(),flush=True)
    except BaseException as e:
        state.update(status='failed',error=str(e));update();raise

if __name__=='__main__':main()
