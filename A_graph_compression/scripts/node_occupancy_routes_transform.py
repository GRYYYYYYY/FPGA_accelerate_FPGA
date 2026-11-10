"""Replace only mutable canonical-node ownership/history in a frozen kernel router."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    text = one(text, '#include "netlist_routes.hpp"', '#include "netlist_routes.hpp"\n#include "node_occupancy_adapter.hpp"')
    text = one(text, 'std::vector<std::set<Id>> owners(graph.node_count());',
               'node_occupancy_host::OwnerTable owners(graph.node_count());')
    text = one(text, 'std::map<Id,uint64_t> history;SiteHistory site_history;', 'SiteHistory site_history;')
    text = one(text, 'snapshot.bind(q.net,present,owners,history,result.site_demands,site_history,forbidden);',
               'snapshot.bind(q.net,present,owners,result.site_demands,site_history,forbidden);')
    text = one(text, 'for (Id node=0;node<owners.size();++node) if (owners[node].size()>1) round.conflicts[node]=owners[node];',
               'round.conflicts=owners.conflicts();')
    old = '''        for (const auto& c:last.conflicts) {
            uint64_t delta=c.second.size()-1;auto& h=history[c.first];
            if (h>std::numeric_limits<uint64_t>::max()-delta) throw std::invalid_argument("node history overflow");
            h+=delta;
        }'''
    return one(text, old, '        owners.advance(last.conflicts.size());')


def adapter(text):
    text = one(text, '#include "site_ledger.hpp"', '#include "site_ledger.hpp"\n#include "node_occupancy_adapter.hpp"')
    text = one(text, 'const std::vector<std::set<uint32_t>>& node_owners,\n              const std::map<uint32_t,uint64_t>& node_history,',
               'const node_occupancy_host::OwnerTable& node_owners,')
    text = one(text, 'std::fill(forbidden_.begin(),forbidden_.end(),0);std::fill(nodes_.begin(),nodes_.end(),0);',
               'std::fill(forbidden_.begin(),forbidden_.end(),0);')
    old = '''        bool occupied=false;
        for(size_t n=0;n<count;++n){nodes_[2*n]=node_owners[n].size()-node_owners[n].count(net);occupied=occupied || nodes_[2*n]!=0;}
        for(auto h:node_history){if(h.first>=count)fail(false,"snapshot history node outside domain");nodes_[2*h.first+1]=h.second;}'''
    new = '''        node_owners.snapshot(net,nodes_.data());
        bool occupied=false,past=false;
        for(size_t n=0;n<count;++n){occupied=occupied || nodes_[2*n]!=0;past=past || nodes_[2*n+1]!=0;}'''
    text = one(text, old, new)
    return one(text, 'counters.node_history+=!node_history.empty();', 'counters.node_history+=past;')
