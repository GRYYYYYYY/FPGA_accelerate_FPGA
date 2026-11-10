"""Connect both bounded ledgers directly to the production snapshot-building C top."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    text=text.replace('"node_occupancy_adapter.hpp"','"node_occupancy_snapshot_adapter.hpp"')
    text=text.replace('"site_occupancy_adapter.hpp"','"site_occupancy_snapshot_adapter.hpp"')
    text=one(text,'snapshot(graph,metadata);','snapshot(graph,metadata,protected_nodes,reserved);')
    text=one(text,'''            std::set<Id> forbidden=protected_nodes;
            for (auto [node,owner]:reserved) if (owner!=q.net) forbidden.insert(node);
            snapshot.bind(q.net,present,owners,ledger,forbidden);''',
             '            snapshot.bind(q.net,present,owners,ledger);')
    return text


def adapter(text):
    text=text.replace('"node_occupancy_adapter.hpp"','"node_occupancy_snapshot_adapter.hpp"')
    text=text.replace('"site_occupancy_adapter.hpp"','"site_occupancy_snapshot_adapter.hpp"')
    text=one(text,'#include "search_kernel_packet.hpp"','#include "resident_snapshot_adapter.hpp"')
    text=one(text,'    Provider provider_;\n','')
    text=one(text,'    std::vector<uint64_t> forbidden_,nodes_,owners_,history_,packet_;',
             '    resident_snapshot_host::Builder builder_;\n    std::vector<uint64_t> packet_;\n    unsigned packet_words_=0;')
    text=one(text,'Context(Graph& graph,const snapshot_inputs::SiteBuffers<Limits>& sites):adjacency_{graph,{}},sites_(sites),provider_(adjacency_) {',
             '''Context(Graph& graph,const snapshot_inputs::SiteBuffers<Limits>& sites,const std::set<uint32_t>& protected_nodes,
            const std::map<uint32_t,uint32_t>& reserved):adjacency_{graph,{}},sites_(sites),
            builder_(unsigned(graph.node_count()),sites,protected_nodes,reserved),packet_(4194304) {''')
    text=one(text,'        forbidden_.resize((graph.node_count()+63)/64);nodes_.resize(2*graph.node_count());\n','')
    start=text.index('    // Called after releasing this net;')
    end=text.index('    site_native::SearchResult search(',start)
    text=text[:start]+'''    // Mutable ledger snapshots and packet layout execute the bounded top.
    void bind(uint32_t net,uint64_t present,const node_occupancy_host::OwnerTable& node_owners,
              const site_occupancy_host::Ledger& site_ledger) {
        ++counters.snapshots;
        if(node_owners.size()!=adjacency_.node_count())fail(false,"snapshot node domain mismatch");
        const auto r=builder_.build(net,present,node_owners,site_ledger,packet_.data());
        packet_words_=unsigned(r[1]);
        ++kernel_counters.packets;kernel_counters.serialized_words+=packet_words_;
        kernel_counters.max_packet_words=std::max(kernel_counters.max_packet_words,packet_words_);
        counters.node_occupied+=r[2];counters.node_history+=r[3];counters.site_occupied+=(r[4]!=0);counters.site_history+=(r[5]!=0);
        counters.max_site_owners=std::max(counters.max_site_owners,unsigned(r[4]));
        counters.max_site_history=std::max(counters.max_site_history,unsigned(r[5]));
    }
'''+text[end:]
    start=text.index('        if(packet_.size()<32+')
    end=text.index('        kernel_counters.max_roots=',start)
    text=text[:start]+'''        if(!packet_words_)fail(false,"kernel search before snapshot bind");
        builder_.patch(packet_.data(),packet_words_,target,unsigned(sorted_roots.size()),budget,state);
'''+text[end:]
    text=one(text,'unsigned(packet_.size()),w.heap','packet_words_,w.heap')
    return text.replace('provider_.node_count()','adjacency_.node_count()')
