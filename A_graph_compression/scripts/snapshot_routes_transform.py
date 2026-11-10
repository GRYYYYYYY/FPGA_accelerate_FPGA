"""Replace only search invocation/binding in an isolated negotiation engine."""
from label_index_transform import replace_once
from controller_search_transform import transform_runtime as controller_runtime

def transform_routes(text):
    text=replace_once(text,'#include "netlist_routes.hpp"','#include "netlist_routes.hpp"\n#include "search_snapshot_route_adapter.hpp"')
    text=replace_once(text,'template<class Provider,class Semantics,class Blocked>','template<class Limits=snapshot_route::RegionLimits,class Provider>')
    text=replace_once(text,'SiteBatch route_batch(','SiteBatch route_snapshot_batch(')
    text=replace_once(text,'const std::set<Id>& protected_nodes,const SiteState& fixed,\n                     Semantics semantics,Blocked blocked,unsigned max_iterations,',
                      'const std::set<Id>& protected_nodes,const snapshot_inputs::SiteBuffers<Limits>& metadata,\n                     unsigned max_iterations,')
    text=replace_once(text,'    SiteBatch result;DemandLedger ledger;','    SiteBatch result;DemandLedger ledger;\n    snapshot_route::Context<Limits,Provider> snapshot(graph,metadata);')
    anchor='            auto targets=q.sinks;std::sort(targets.begin(),targets.end());std::vector<SearchResult> connections;'
    text=replace_once(text,anchor,'            snapshot.bind(q.net,present,owners,history,result.site_demands,site_history,forbidden);\n'+anchor)
    start='                auto connection=site_native::search('
    end='                if (connection.status=="found") {'
    if text.count(start)!=1 or text.count(end)!=1:raise ValueError('Unknown search block')
    begin=text.index(start);finish=text.index(end)
    if finish<=begin or not text[begin:finish].endswith('                    });\n'):raise ValueError('Unknown callback block')
    text=text[:begin]+'                auto connection=snapshot.search(route.nodes,target,demands,budget);\n'+text[finish:]
    return text

def transform_runtime(text):
    text=controller_runtime(text)
    text=replace_once(text,'    site_native::SiteState fixed(sites.fixed_signals,sites.fixed);',
                     '    snapshot_inputs::SiteBuffers<snapshot_route::RegionLimits> metadata(sites,protected_pips,blocked_attributes);')
    text=replace_once(text,'    auto r=site_native::route_batch(graph,queries,protected_nodes,fixed,\n        [&](uint32_t,const Edge& e) {return sites.semantics(e);},\n        [&](uint32_t,uint32_t,const Edge& e) {return protected_pips.count({e.tile,e.pip})||blocked_attributes.count(e.attr);},',
                     '    auto r=site_native::route_snapshot_batch(graph,queries,protected_nodes,metadata,')
    text=replace_once(text,'    controller_adapter::counters={};','    controller_adapter::counters={};snapshot_route::counters={};')
    anchor='    const auto cc=controller_adapter::counters;'
    extra='''    const auto sc=snapshot_route::counters;
    std::cerr<<"SNAPSHOT_COUNTERS "<<batch<<' '<<sc.snapshots<<' '<<sc.node_occupied<<' '<<sc.node_history<<' '<<sc.site_occupied<<' '<<sc.site_history<<' '<<sc.site_found_paths<<' '<<sc.failures<<' '<<sc.max_site_owners<<' '<<sc.max_site_history<<'\\n';
    require(sc.failures==0,"snapshot construction/search failed");
'''
    return replace_once(text,anchor,extra+anchor)
