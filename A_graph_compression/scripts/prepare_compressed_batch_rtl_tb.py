#!/usr/bin/env python3
"""Generate a full-depth diagnostic TB with complete port payload snapshots."""
import json
from pathlib import Path
from search_kernel_memory_plan import parse_source,sha,require
ROOT=Path(__file__).resolve().parents[1]
def derive():
    source=ROOT/'hardware/vitis/search_batch_trace_top_v2.cpp';args=parse_source(source)
    prior=Path('/tmp/A_graph_compression_recovery_20261025_v1/trace_v2_cpu/source/test_search_batch_trace.cpp')
    text=prior.read_text();text='#include <cstdlib>\n#include <cstdint>\n'+text
    require(text.count('trace_control[8]={262144,')==1 and text.count('trace_data(262145,')==1,'Changed CPU fixture')
    text=text.replace('trace_control[8]={262144,','trace_control[8]={16777216,').replace('trace_data(262145,','trace_data(16777217,')
    start=text.index('auto invoke=[&](){search_batch_trace_top_v2(')+len('auto invoke=[&](){search_batch_trace_top_v2(')
    end=text.index(');',start);expressions=text[start:end].split(',');require(len(expressions)==len(args)==45,'Changed actual call ABI')
    rows=[];inventory=[]
    for arg,expr in zip(args,expressions):
        if not arg['pointer']:continue
        expr=expr.strip();available=expr[:-7]+'.size()' if expr.endswith('.data()') else 'sizeof('+expr+')/sizeof('+expr+'[0])'
        rows.append('        {'+','.join([str(arg['id']),str(arg['element_bytes']),str(arg['depth']),available,expr])+'}')
        inventory.append(dict(**arg,actual_expression=expr,extent_expression=available))
    block='''    struct SnapshotPort {unsigned id,bytes;uint64_t depth,available;const void* data;};
    const SnapshotPort ports[]={
'''+',\n'.join(rows)+'''
    };
    static_assert(sizeof(ports)/sizeof(ports[0])==44,"full pointer inventory");
    for(const auto& port:ports)assert(port.available>=port.depth);
    auto full_snapshot=[&](unsigned transaction){
        const char* prefix=std::getenv("A_BATCH_RTL_SNAPSHOT_PREFIX");assert(prefix && *prefix);
        const uint16_t endian=1;assert(*reinterpret_cast<const uint8_t*>(&endian)==1);
        const std::string name=std::string(prefix)+"_"+std::to_string(SEARCH_GRAPH_MODE)+"_"+std::to_string(transaction)+".bin";
        std::ofstream out(name,std::ios::binary);
        auto put=[&](uint64_t word){for(unsigned b=0;b<8;++b)out.put(char(word>>(8*b)));};
        put(UINT64_C(0x4142534e41503031));put(SEARCH_GRAPH_MODE);put(transaction);put(44);
        for(const auto& port:ports){put(port.id);put(port.bytes);put(port.depth);out.write(reinterpret_cast<const char*>(port.data),std::streamsize(port.depth*port.bytes));}
        out.close();assert(out);
    };
'''
    text=text.replace('    auto invoke=',block+'    auto invoke=',1)
    needle='trace_control,trace_meta,trace_data.data());'
    require(text.count(needle)==1,'Changed diagnostic invocation');text=text.replace(needle,needle+'\n        full_snapshot(invocation);')
    # The historical packet View is only setup scaffolding, not a DUT port.
    text=text.replace('    using Node=', '    (void)view;\n    using Node=',1)
    text=text.replace('    std::printf("SEARCH_BATCH_PASS', '    assert(invocation==4);\n    std::printf("FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=%u ports=44 transactions=4\\n",SEARCH_GRAPH_MODE);\n    std::printf("SEARCH_BATCH_PASS')
    return text,inventory,prior
if __name__=='__main__':
    text,inventory,prior=derive();target=ROOT/'hardware/vitis/test_compressed_batch_rtl_full_depth.cpp'
    with target.open('x') as f:f.write(text)
    p=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    with p.open('x') as f:json.dump(dict(status='source_depth_inventory_generated_runtime_verification_pending',ports=inventory,files={str(x):sha(x) for x in [target,prior,ROOT/'hardware/vitis/search_batch_trace_top_v2.cpp',Path(__file__).resolve()]}),f,indent=2);f.write('\n')
