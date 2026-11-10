#!/usr/bin/env python3
"""Create isolated full-router copies that call the audited Vitis C-model ABI."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import difflib
import json
from pathlib import Path
import subprocess
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/kernel_router_cmodel_20261023_v1'


def transform(original):
    text=original.replace('#include "site_inputs.hpp"', '#include "site_inputs.hpp"\n#include "router_provider.hpp"\n'
        'extern "C" void graph_accel(const uint32_t*,const uint32_t*,const uint32_t*,uint32_t*,uint32_t*,uint32_t*,uint32_t,uint32_t);')
    substitutions={
        '    Graph graph;':'    kernel_router::Provider graph;',
        'RoutingGraph(const std::string& path,size_t cache):graph(path,cache) {}':
            'RoutingGraph(const std::string& path,const std::string& config,size_t cache):graph(path,config,cache,graph_accel) {}',
        'require(argc==9,"usage: site_runtime image routing sites cache iterations budget cap direct|expanded");':
            'require(argc==10,"usage: kernel_router image routing sites cache iterations budget cap direct|expanded config");',
        'RoutingGraph graph(argv[1],std::stoull(argv[4]));':'RoutingGraph graph(argv[1],argv[9],std::stoull(argv[4]));',
        '    auto route_start=Clock::now();':'    auto launches_start=graph.graph.kernel_calls;\n    auto route_start=Clock::now();',
    }
    for old,new in substitutions.items():
        require(text.count(old)==1,'Unrecognized original runtime anchor: '+old)
        text=text.replace(old,new)
    require(text.count('graph.graph.logical_bytes')==2,'Unexpected logical-byte counters')
    text=text.replace('graph.graph.logical_bytes','graph.graph.kernel_payload_bytes')
    text=text.replace('\\"logical_bytes\\"','\\"kernel_payload_bytes\\"')
    old='        <<",\\"peak_kib\\":"<<peak_kib<<"}\\n";'
    new='        <<",\\"kernel_calls\\":"<<(graph.graph.kernel_calls-launches_start)\n'+old
    require(text.count(old)==1,'Missing batch metrics anchor');text=text.replace(old,new)
    old='"{\\"execution\\":\\""'
    require(text.count(old)==1,'Missing backend declaration anchor')
    text=text.replace(old,'"{\\"backend\\":\\"cpu_vitis_abi_cmodel\\",\\"execution\\":\\""')
    return text


def main():
    audit_path=ROOT/'results/vitis_graph_kernel_audit_20261023_v2.json';audit=json.loads(audit_path.read_text())
    require(audit['status']=='verified_vitis_xo_not_platform_linked','Audited Vitis baseline missing')
    bp=ROOT/'data/derived/vitis_graph_kernel_20261023_v2/plan.json';baseline=json.loads(bp.read_text())
    runtime_plan_path=ROOT/'data/derived/native_site_runtime_validation_20261023_v1/plan.json'
    runtime_plan=json.loads(runtime_plan_path.read_text())
    files={**audit['artifacts'],**baseline['files'],**baseline['generated'],**runtime_plan['code_inputs_and_references']}
    # Avoid repeatedly reading huge unchanged raw traces; their original audit remains bound.
    reference_paths=set(runtime_plan['references'].values())
    for path,sha in files.items():
        if path not in reference_paths:require(digest(path)==sha,'Frozen integration input changed: '+path)
    dependencies=[Path(__file__).resolve(),audit_path,bp,runtime_plan_path,ROOT/'hardware/vitis/router_provider.hpp',
                  ROOT/'hardware/vitis/test_router_provider.cpp',ROOT/'hardware/vitis/host_contract.hpp']
    files.update({str(p):digest(p) for p in dependencies})
    original=(ROOT/'src/native/site_runtime.cpp').read_text();text=transform(original)
    OUT.mkdir(parents=True,exist_ok=False);(OUT/'site_runtime.cpp').write_text(text)
    (OUT/'runtime.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),
        fromfile='native/site_runtime.cpp',tofile='kernel_router/site_runtime.cpp')))
    for name in ['router_provider.hpp','test_router_provider.cpp','host_contract.hpp']:
        (OUT/name).write_bytes((ROOT/'hardware/vitis'/name).read_bytes())
    generated={str(p):digest(p) for p in OUT.iterdir() if p.is_file()}
    plan={'created_utc':datetime.now(timezone.utc).isoformat(),'files':files,'generated':generated,
          'inputs':runtime_plan['inputs'],'references':runtime_plan['references'],
          'scope':'Original site search/occupancy/negotiation/output; only adjacency adapter calls original audited Vitis C model. CPU execution, not XRT/FPGA.',
          'limitations':['Expanded mode materializes all kernel-decoded rows before routing; direct mode invokes the kernel on cache misses.',
                         'Runtime guards cover the declared per-batch capacity and eight guard words, not every byte of the maximum possible AXI address space.',
                         'Only14 physically evidenced site instances; other special-resource semantics remain incomplete.',
                         'kernel_payload_bytes counts logical ABI payload, not kernel physical memory traffic or measured PCIe transfer.']}
    with (OUT/'plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
    def build(mode,cpu):
        work=OUT/mode;work.mkdir();source=ROOT/'data/derived/vitis_graph_kernel_20261023_v2'/mode
        common=['taskset','-c',str(cpu),'g++','-std=c++17','-O2','-Wall','-Wextra','-Wno-unknown-pragmas',
                '-I'+str(ROOT/'src/native'),'-I'+str(OUT),str(source/'graph_body.cpp'),str(source/'graph_accel.cpp')]
        for name,code in [('provider_test',OUT/'test_router_provider.cpp'),('router',OUT/'site_runtime.cpp')]:
            with (work/(name+'.compile.log')).open('x') as log:
                subprocess.run([*common,str(code),'-o',str(work/name)],stdout=log,stderr=subprocess.STDOUT,check=True)
        config=ROOT/'data/derived/hls_region_fixtures_20261023_v1'/mode/'config.bin'
        command=['taskset','-c',str(cpu),str(work/'provider_test'),plan['inputs'][mode]['image'],str(config),str(source/'full.txt')]
        with (work/'provider_test.log').open('x') as log:
            run=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        require(run.returncode==0,'Provider full-graph test failed: '+mode)
        require((work/'provider_test.log').read_text()=='KERNEL_PROVIDER_PASS nodes=274732 edges=1100754 unknown=53759 mutations=20 cache_and_materialization=pass\n','Provider coverage differs')
        return mode,{'command':command,'exit_code':run.returncode,'files':{str(p):digest(p) for p in work.iterdir() if p.is_file()}}
    results={}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(build,mode,cpu) for mode,cpu in [('csr',122),('compact',124)]]):
            mode,result=future.result();results[mode]=result;print('PROVIDER_TEST_PASS',mode,flush=True)
    with (OUT/'preparation.json').open('x') as f:
        json.dump({'status':'both_full_graph_abi_providers_verified_router_not_yet_executed','plan_sha256':digest(OUT/'plan.json'),'modes':results},f,indent=2);f.write('\n')


if __name__=='__main__':main()
