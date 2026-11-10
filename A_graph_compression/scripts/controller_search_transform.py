"""Replace the complete search body in an isolated native integration copy."""
from label_index_transform import replace_once

def transform_search(text):
    marker='// roots/resource IDs must follow the reference\'s lexical ordering.'
    if text.count(marker)!=1 or not text.endswith('} // namespace site_native\n'):raise ValueError('Unknown search source layout')
    prefix=text[:text.index(marker)]
    return prefix+'''} // namespace site_native
#include "search_controller_adapter.hpp"
#ifndef BOUNDED_CONTROLLER_LIMITS
#define BOUNDED_CONTROLLER_LIMITS controller_adapter::RegionLimits
#endif
namespace site_native {
template<class Provider,class Semantics,class Blocked,class Compatible,class Cost>
SearchResult search(Provider& graph,const std::set<Id>& roots,Id target,
                    const Demands& initial,uint64_t budget,const std::set<Id>& blocked_nodes,
                    Semantics semantics,Blocked blocked,Compatible compatible,Cost step_cost) {
    return controller_adapter::search<BOUNDED_CONTROLLER_LIMITS>(graph,roots,target,initial,budget,blocked_nodes,
                                                               semantics,blocked,compatible,step_cost);
}
} // namespace site_native
'''

def transform_runtime(text):
    text=replace_once(text,'    auto route_start=Clock::now();','    controller_adapter::counters={};\n    auto route_start=Clock::now();')
    return replace_once(text,'    auto route_ms=ms(route_start);uint64_t peak_kib=0;',
        '    const auto cc=controller_adapter::counters;\n'
        '    std::cerr<<"CONTROLLER_COUNTERS "<<batch<<\' \'<<cc.searches<<\' \'<<cc.pushes<<\' \'<<cc.pops<<\' \'<<cc.improvements<<\' \'<<cc.found<<\' \'<<cc.capacity_failures<<\' \'<<cc.invalid<<\' \'<<cc.max_heap<<\' \'<<cc.max_labels<<\' \'<<cc.max_probes<<\'\\n\';\n'
        '    require(cc.capacity_failures==0 && cc.invalid==0,"bounded search controller failed");\n'
        '    auto route_ms=ms(route_start);uint64_t peak_kib=0;')
