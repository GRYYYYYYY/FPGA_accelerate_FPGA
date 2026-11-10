#!/usr/bin/env python3
"""Build an isolated observer of the unchanged full site router."""
import argparse
import difflib
import json
from pathlib import Path
import subprocess
from check_vitis_kernel import digest,require
from profile_vitis_decoder import once

ROOT=Path(__file__).resolve().parents[1]


def transform(text):
    text=once(text,'#include "site_inputs.hpp"','#include "site_inputs.hpp"\n#include "router_access_profile.hpp"')
    text=once(text,'    Graph graph;','    Graph graph;\n    RouterAccessProfile access;')
    text=once(text,'RoutingGraph(const std::string& path,size_t cache):graph(path,cache) {}',
              'RoutingGraph(const std::string& path,size_t cache):graph(path,cache),access(graph.node_count()) {}')
    text=once(text,'        if (!graph.neighbors(n,out)) return false;',
              '''        auto old_hits=graph.hits,old_misses=graph.misses;
        bool known=graph.neighbors(n,out);
        access.observe(n,known,out.size(),graph.hits-old_hits,graph.misses-old_misses);
        if (!known) return false;''')
    text=once(text,'require(argc==9,"usage: site_runtime image routing sites cache iterations budget cap direct|expanded");',
              'require(argc==10,"usage: access_runtime image routing sites cache iterations budget cap direct access_prefix");')
    text=once(text,'require(execution=="direct"||execution=="expanded","invalid execution mode");',
              'require(execution=="direct","access profiling requires direct execution");')
    text=once(text,'    auto logical_start=graph.graph.logical_bytes,',
              '    graph.access.reset();\n    auto logical_start=graph.graph.logical_bytes,')
    text=once(text,'    auto route_ms=ms(route_start);uint64_t peak_kib=0;',
              '    auto route_ms=ms(route_start);\n    graph.access.write(argv[9],batch);\n    uint64_t peak_kib=0;')
    return text


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    old_plan=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    old=json.loads(old_plan.read_text());files=dict(old['code_inputs_and_references'])
    # Reference raw hashes remain bound; the final independent audit reads them.
    references=set(old['references'].values())
    for name,sha in files.items():
        if name not in references:require(digest(name)==sha,'Frozen input changed: '+name)
    for path in [old_plan,Path(__file__).resolve(),ROOT/'scripts/profile_vitis_decoder.py',
                 ROOT/'src/native/router_access_profile.hpp',ROOT/'tests/test_router_access_profile.cpp']:
        files[str(path)]=digest(path)
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    original=(ROOT/'src/native/site_runtime.cpp').read_text();modified=transform(original)
    (out/'site_runtime.cpp').write_text(modified)
    (out/'runtime.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),modified.splitlines(True),fromfile='baseline/site_runtime.cpp',tofile='profile/site_runtime.cpp')))
    (out/'router_access_profile.hpp').write_bytes((ROOT/'src/native/router_access_profile.hpp').read_bytes())
    common=['taskset','-c','123','g++','-std=c++17','-Wall','-Wextra','-Werror','-I'+str(out),'-I'+str(ROOT/'src/native')]
    for name,command in [('helper_compile',[*common,'-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',
            str(ROOT/'tests/test_router_access_profile.cpp'),'-o',str(out/'helper_test')]),
            ('helper_test',['taskset','-c','123',str(out/'helper_test')]),
            ('router_compile',[*common,'-O2',str(out/'site_runtime.cpp'),'-o',str(out/'router')])]:
        with (out/(name+'.log')).open('x') as stream:
            subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True)
    require((out/'helper_test.log').read_text()=='ROUTER_ACCESS_PROFILE_PASS rejected=8 reset=pass\n','Helper test incomplete')
    for name,sha in files.items():
        if name not in references:require(digest(name)==sha,'Input changed during preparation')
    plan={'status':'compiled_diagnostic_observer_not_yet_full_router_validated','files':files,
          'generated':{str(path):digest(path) for path in out.iterdir()},'inputs':old['inputs']['compact'],
          'reference':old['references']['compact'],'binary':str(out/'router'),
          'scope':'Two full1062-net compact/direct batches with cache4096, identical search/site/occupancy/ordering; observer only.',
          'limitations':['Diagnostic counting overhead is present; timings are not performance comparisons.',
                         'Per-node counts do not preserve temporal ordering.',
                         'One fixed workload, cache capacity and partial14-instance site model, not population estimates.',
                         'Native CPU access observations are not board memory traffic or measured RTL cycles.']}
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'output':str(out),'status':plan['status']}))


if __name__=='__main__':main()
