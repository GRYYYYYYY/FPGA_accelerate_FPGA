#!/usr/bin/env python3
"""Build an explicit hardware-only adjacency transport for the unchanged CPU router."""
import difflib
import json
from pathlib import Path
import subprocess
from datetime import datetime,timezone
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/kernel_router_xrt_20261023_v1'


def once(text,old,new):
    require(text.count(old)==1,'Unexpected C-model adapter anchor: '+old)
    return text.replace(old,new)


def transform(text):
    text=once(text,'#include "router_provider.hpp"','#include "router_provider.hpp"\n#include "router_xrt_transport.hpp"')
    text=once(text,'extern "C" void graph_accel(const uint32_t*,const uint32_t*,const uint32_t*,uint32_t*,uint32_t*,uint32_t*,uint32_t,uint32_t);\n','')
    text=once(text,'    kernel_router::Provider graph;','    std::shared_ptr<kernel_router::XrtTransport> transport;\n    kernel_router::Provider graph;')
    text=once(text,'    RoutingGraph(const std::string& path,const std::string& config,size_t cache):graph(path,config,cache,graph_accel) {}',
'''    RoutingGraph(const std::string& path,const std::string& config,size_t cache,
                 const std::string& binary,const std::string& device,const std::string& bank,const std::string& evidence):
        transport(std::make_shared<kernel_router::XrtTransport>(path,config,binary,device,bank,evidence)),
        graph(path,config,cache,[this](const uint32_t* im,const uint32_t* cf,const uint32_t* rq,
            uint32_t* out,uint32_t* result,uint32_t* counts,uint32_t n,uint32_t capacity) {
                (*transport)(im,cf,rq,out,result,counts,n,capacity);
            }) {}''')
    text=once(text,'int main(int argc,char** argv) {try {','''int main(int argc,char** argv) {try {
    if(argc==5&&std::string(argv[1])=="--preflight") {
        std::string mode=argv[4];require(mode=="csr"||mode=="compact","Expected explicit mode");
        auto image=board_graph::words(argv[2],board_graph::image_words),config=board_graph::words(argv[3],32);
        board_graph::descriptor(image,config,mode=="compact");
        std::cout<<"XRT_ROUTER_SHAPE_PASS hardware_executed=false\\n";return 0;
    }''')
    text=once(text,'    require(argc==10,"usage: kernel_router image routing sites cache iterations budget cap direct|expanded config");',
        '    require(argc==14,"usage: xrt_router image routing sites cache iterations budget cap direct|expanded config xclbin device DDR[0]|HBM[0] NEW_transport_dir");')
    text=once(text,'RoutingGraph graph(argv[1],argv[9],std::stoull(argv[4]));',
        'RoutingGraph graph(argv[1],argv[9],std::stoull(argv[4]),argv[10],argv[11],argv[12],argv[13]);')
    text=once(text,'cpu_vitis_abi_cmodel','xrt_hardware_adjacency_cpu_search')
    text=once(text,'    auto launches_start=graph.graph.kernel_calls;',
        '    auto launches_start=graph.graph.kernel_calls;\n    auto transport_start=graph.transport->stats();')
    old='        <<",\\"kernel_calls\\":"<<(graph.graph.kernel_calls-launches_start)'
    text=once(text,old,old+'''
        <<",\\"xrt_h2d_ms\\":"<<(graph.transport->stats().h2d_ms-transport_start.h2d_ms)
        <<",\\"xrt_kernel_wall_ms\\":"<<(graph.transport->stats().kernel_wall_ms-transport_start.kernel_wall_ms)
        <<",\\"xrt_d2h_ms\\":"<<(graph.transport->stats().d2h_ms-transport_start.d2h_ms)''')
    text=once(text,'    require(bool(std::cout),"write runtime result");return 0;',
        '    require(bool(std::cout),"write runtime result");graph.transport->write_summary(true);return 0;')
    return text


def main():
    prior=ROOT/'data/derived/kernel_router_cmodel_20261023_v1';pp=prior/'plan.json';plan=json.loads(pp.read_text())
    prep_path=prior/'preparation.json';prep=json.loads(prep_path.read_text())
    require(prep['status']=='both_full_graph_abi_providers_verified_router_not_yet_executed'
            and digest(pp)==prep['plan_sha256'],'C-model provider preparation changed')
    for path,sha in plan['generated'].items():require(digest(path)==sha,'Frozen C-model adapter changed')
    mock=ROOT/'results/router_exchange_mock_20261023_v1.log'
    require(mock.read_text()=='ROUTER_EXCHANGE_MOCK_PASS cases=8 failed_launches=8 invalid_bounds=3 hardware_executed=false\n','Exchange mock test did not pass')
    OUT.mkdir(parents=True,exist_ok=False)
    original=(prior/'site_runtime.cpp').read_text();updated=transform(original)
    (OUT/'site_runtime_xrt.cpp').write_text(updated)
    (OUT/'runtime.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),
        fromfile='cpu_cmodel/site_runtime.cpp',tofile='xrt/site_runtime.cpp')))
    dependencies=[Path(__file__).resolve(),pp,prep_path,prior/'site_runtime.cpp',mock,
                  ROOT/'build/test_router_exchange_20261023_v1',ROOT/'results/router_exchange_compile_20261023_v1.log']
    for name in ['router_provider.hpp','host_contract.hpp','router_exchange.hpp','router_xrt_transport.hpp','test_router_exchange.cpp']:
        path=ROOT/'hardware/vitis'/name;dependencies.append(path);(OUT/name).write_bytes(path.read_bytes())
    dependencies+=sorted((ROOT/'src/native').glob('*.hpp'))
    files={str(p):digest(p) for p in dependencies}
    binary=OUT/'router';command=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas',
        '-I'+str(ROOT/'src/native'),'-I'+str(OUT),'-I/opt/xilinx/xrt/include',str(OUT/'site_runtime_xrt.cpp'),
        '-L/opt/xilinx/xrt/lib','-Wl,-rpath,/opt/xilinx/xrt/lib','-lxrt_coreutil','-luuid','-pthread','-o',str(binary)]
    with (OUT/'compile.log').open('x') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    preflights=[]
    for mode in ['csr','compact']:
        image=plan['inputs'][mode]['image'];config=ROOT/'data/derived/hls_region_fixtures_20261023_v1'/mode/'config.bin'
        args=[str(binary),'--preflight',image,str(config),mode]
        result=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (OUT/(mode+'.preflight.log')).write_text(result.stdout)
        require(result.returncode==0 and result.stdout=='XRT_ROUTER_SHAPE_PASS hardware_executed=false\n','Shape preflight failed')
        preflights.append({'mode':mode,'command':args,'exit_code':0})
        files[image]=digest(image);files[str(config)]=digest(config)
    symbols=subprocess.check_output(['nm','--defined-only','-C',str(binary)],text=True)
    require('graph_expand_body' not in symbols and not any(' graph_accel(' in line for line in symbols.splitlines()),'CPU kernel accidentally linked into hardware runner')
    with (OUT/'report.json').open('x') as f:
        json.dump({'status':'xrt_router_compiled_mock_exchange_and_shape_preflights_passed_no_hardware_execution',
            'created_utc':datetime.now(timezone.utc).isoformat(),'files':files,
            'generated':{str(p):digest(p) for p in OUT.iterdir() if p.is_file() and p.name!='report.json'},
            'compile_command':command,'compile_exit_code':0,'preflights':preflights,
            'no_cpu_kernel_symbols':True,'mock_test_scope':'Eight fake-device exchange cases, eight failed launches, three bounds errors, ASAN/UBSAN. Not a real xclbin/device test.',
            'limitations':['Actual platform/xclbin/card still required; no hardware programming or execution occurred.',
                           'Search, ownership and negotiation remain on CPU; only adjacency callback uses XRT.',
                           'Production launch must bind audited platform-linked kernel, inputs and output audit; this binary alone is not an audited board experiment.',
                           'Kernel wall is host-observed launch/wait time, not device profiling; direct per-row launches may be expensive.']},f,indent=2);f.write('\n')
    print('XRT_ROUTER_OFFLINE_PREPARATION_PASS')


if __name__=='__main__':main()
