"""Derive a router using raw search -> tree -> snapshot state without host sets."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    text=one(text,'    node_occupancy_host::OwnerTable owners(graph.node_count());',
        '    node_occupancy_host::OwnerTable owners(graph.node_count());\n    route_tree_host::Tree tree(unsigned(graph.node_count()));')
    text=one(text,'ledger.release(q.net);Normalized demands;', 'ledger.release(q.net);tree.reset(q.source);')
    text=one(text,'route{q.source,q.sinks,{q.source},{},false}', 'route{q.source,q.sinks,{},{},false}')
    text=one(text,'snapshot.search(route.nodes,target,demands,budget)', 'snapshot.search(tree,target,budget)')
    text=one(text,'''                    for (const auto& p:connection.path) route.nodes.insert(p.second.dst);
                    demands=connection.demands;
''','')
    text=one(text,'            route.complete=std::all_of(q.sinks.begin(),q.sinks.end(),[&](Id node){return route.nodes.count(node);});',
        '''            route.complete=tree.complete(q.sinks);
            const unsigned nroots=tree.emit_roots();
            route.nodes.insert(tree.roots(),tree.roots()+nroots);
            typename fpga_search::ProductionRouteTree::Words::Key demand_key{};
            if(!fpga_search::ProductionRouteTree::Words::load(tree.demands(),0,demand_key) || demand_key.node)
                throw std::logic_error("invalid final route tree state");
            auto demands=flat_controller_adapter::unpack(demand_key.state);''')
    return text


def adapter(text):
    text=one(text,'#include "resident_snapshot_adapter.hpp"', '#include "resident_snapshot_adapter.hpp"\n#include "route_tree_adapter.hpp"')
    start=text.index('    site_native::SearchResult search(')
    end=text.index('        if(!packet_words_)',start)
    text=text[:start]+'''    site_native::SearchResult search(route_tree_host::Tree& tree,uint32_t target,uint64_t budget) {
        auto& c=flat_controller_adapter::counters;++c.searches;
        site_native::SearchResult out;
        const unsigned nroots=tree.emit_roots();
        if(nroots>Limits::roots){++c.capacity_failures;out.status="capacity_exhausted";return out;}
        auto& w=flat_controller_adapter::storage<Limits>().workspace;
'''+text[end:]
    text=one(text,'unsigned(sorted_roots.size()),budget,state','nroots,budget,tree.demands()')
    text=one(text,'unsigned(sorted_roots.size())','nroots')
    text=one(text,'image_,sorted_roots.data(),packet_.data()', 'image_,tree.roots(),packet_.data()')
    text=one(text,'        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);',
        '        tree.accept(target,result,w.path);\n        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);')
    return text


def builder(text):
    return one(text,'''               const fpga_search::SiteState<32,16,8>& state)const {
        uint64_t initial[65]{};
        if(!Core::Words::store(initial,0,{0,state}))throw std::invalid_argument("invalid query initial state");''',
        '               const uint64_t* initial)const {')
