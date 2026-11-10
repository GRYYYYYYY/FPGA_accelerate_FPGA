"""Isolated counters on unchanged D-ary heap order; preserve main source lines."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)

def generate(source,header,hooks):
 original_lines=source.count('\n')
 source=once(source,'inline void clear() { sz = 0; }','inline void clear() { if(btrace::current) btrace::current->frontierCleared += (uint64_t)sz; sz = 0; }')
 source=once(source,'h[k].lb = lb; h[k].id = id; sz++;','h[k].lb = lb; h[k].id = id; sz++; if(btrace::current) { ++btrace::current->frontierPushes; btrace::current->frontierPeak = std::max(btrace::current->frontierPeak, (uint64_t)sz); }')
 source=once(source,'int result = h[0].id;','int result = h[0].id; if(btrace::current) ++btrace::current->frontierPolls;')
 graph=''' auto b_frontier_graph = [&](const char* stage) { uint64_t edgeSum=0; int maxDegree=0; for(const auto& a:router.ns) { edgeSum+=(uint64_t)a.childCount; maxDegree=std::max(maxDegree,a.childCount); } std::fprintf(stderr,"FRONTIER_GRAPH stage=%s entry_bytes=%zu heap_arity=%d nodes=%zu edges=%zu edge_sum=%llu max_degree=%d lazy=%d\\n",stage,sizeof(Router::DaryPQ::E),router.heapArity,router.ns.size(),router.childIds.size(),(unsigned long long)edgeSum,maxDegree,(int)router.lazy); }; b_frontier_graph("before");'''
 source=once(source,'    router.load(argv[1]);','    router.load(argv[1]);'+graph)
 source=once(source,'    router.writeResult(argv[2]);','    b_frontier_graph("after"); router.writeResult(argv[2]);')
 assert source.count('\n')==original_lines,'TLD sourceLine locations must remain unchanged'
 header=once(header,'uint64_t count = 0;', 'uint64_t count = 0; uint64_t frontierPushes=0, frontierPolls=0, frontierPeak=0, frontierCleared=0;')
 anchor='            << ",\\\"routed\\\":"'
 # Insert only metadata fields, preserving the existing record values and access stream.
 assert hooks.count(anchor)==1
 fields='''            << ",\\\"frontier_pushes\\\":" << a.frontierPushes << ",\\\"frontier_polls\\\":" << a.frontierPolls
            << ",\\\"frontier_peak\\\":" << a.frontierPeak << ",\\\"frontier_cleared\\\":" << a.frontierCleared
'''
 hooks=hooks.replace(anchor,fields+anchor)
 return {'trace.cpp':source,'real_trace.hpp':header,'real_router_hooks.inc':hooks}
