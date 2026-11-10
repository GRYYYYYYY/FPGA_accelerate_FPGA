"""Replace host per-net mutations with the actual net transaction; diagnostics only."""
from derive_search_flat_controller import replace_once as one

def adapt(source):
    p=source/'node_occupancy_snapshot_adapter.hpp';s=p.read_text();anchor='    struct Buffers {'
    s=one(s,anchor,'''    struct ResidentBuffers {uint64_t *meta;uint32_t *counts;uint64_t *history,*keys;uint32_t *flags;};
    ResidentBuffers resident_buffers(){return {meta_.data(),counts_.data(),history_.data(),keys_.data(),flags_.data()};}
'''+anchor);p.write_text(s)
    p=source/'site_occupancy_snapshot_adapter.hpp';s=p.read_text();anchor='    struct Buffers {'
    s=one(s,anchor,'''    struct ResidentBuffers {uint64_t *meta,*owners,*history,*request;};
    ResidentBuffers resident_buffers(){return {meta_.data(),owners_.data(),history_.data(),request_.data()};}
'''+anchor);p.write_text(s)
    p=source/'retained_nodes_adapter.hpp';s=p.read_text();s=one(s,'    unsigned get(uint32_t net)', '''    uint64_t* resident_meta(){return meta_.data();}
    uint64_t* resident_rows(){return rows_.data();}
    uint32_t* resident_output(){return output_.data();}
    unsigned get(uint32_t net)''');p.write_text(s)
    p=source/'resident_snapshot_adapter.hpp';s=p.read_text();s=one(s,'    template<class Sites> Builder(','''    const uint64_t* static_data()const{return static_.data();}
    size_t static_words()const{return static_.size();}
    template<class Sites> Builder(''');p.write_text(s)
    p=source/'search_kernel_route_adapter.hpp';s=p.read_text()
    s=one(s,'#include "sink_loop_observer.hpp"','#include "sink_loop_observer.hpp"\n#include "retained_nodes_adapter.hpp"')
    start=s.index('    std::vector<site_native::SearchResult> search_all(')
    stop=s.index('        std::vector<site_native::SearchResult> outputs;',start)
    prefix='''    std::vector<site_native::SearchResult> route_net(route_tree_host::Tree& tree,const std::vector<uint32_t>& targets,uint64_t budget,retained_edges_host::Store& retained_edges,uint32_t net,uint32_t source_node,uint64_t present,node_occupancy_host::OwnerTable& owners,site_occupancy_host::Ledger& ledger,retained_nodes_host::Store& retained){
        if(targets.size()>1048576)fail(true,"net sink capacity");
        auto& w=flat_controller_adapter::storage<Limits>().workspace;
        auto node=owners.resident_buffers();auto site=ledger.resident_buffers();
        uint64_t meta[2]={w.epoch,w.key_count},result[81]{},summary[8]{},net_result[8]{};
        const uint64_t control[8]={net,source_node,present,budget,builder_.static_words(),targets.size(),0,0};
        std::vector<sink_loop_observation::Frame> frames;
        {sink_loop_observation::Scope observe(frames);
            auto kernel=image_.config[0]==0?search_net_csr:search_net_compact;
            kernel(image_.image,image_.config,image_.image_words,tree.resident_roots(),packet_.data(),w.heap,w.slots,w.records,w.keys,w.unknown_nodes,w.unknown_pips,w.path,meta,result,tree.resident_meta(),tree.resident_bits(),tree.resident_demands(),retained_edges.resident_meta(),retained_edges.resident_rows(),summary,targets.data(),control,builder_.static_data(),node.meta,node.counts,node.history,node.keys,node.flags,site.meta,site.owners,site.history,site.request,retained.resident_meta(),retained.resident_rows(),retained.resident_output(),net_result);
        }
        if(net_result[0])fail(false,"integrated net transaction rejected operation");
        if(net_result[3]!=targets.size() || frames.size()!=targets.size() || meta[0]>UINT32_MAX || meta[1]>Limits::labels)fail(false,"net observations incomplete");
        packet_words_=unsigned(packet_[1]);w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);
        ++counters.snapshots;++kernel_counters.packets;kernel_counters.serialized_words+=packet_words_;
        kernel_counters.max_packet_words=std::max(kernel_counters.max_packet_words,packet_words_);
        const unsigned domain=unsigned(packet_[2]);const unsigned cost_at=97+(domain+63)/64;bool occupied=false,past=false;
        for(unsigned i=0;i<domain;++i){occupied=occupied || packet_[cost_at+2*i]!=0;past=past || packet_[cost_at+2*i+1]!=0;}
        counters.node_occupied+=occupied;counters.node_history+=past;counters.site_occupied+=packet_[11]!=0;counters.site_history+=packet_[12]!=0;
        counters.max_site_owners=std::max(counters.max_site_owners,unsigned(packet_[11]));counters.max_site_history=std::max(counters.max_site_history,unsigned(packet_[12]));
'''
    s=s[:start]+prefix+s[stop:];p.write_text(s)
    for name in ['site_routes.hpp','snapshot_test_routes.hpp']:
        p=source/name;s=p.read_text()
        s=one(s,'''            const unsigned old_count=retained.get(q.net);
            if(old_count)owners.erase_nodes(q.net,retained.output(),old_count);
            ledger.release(q.net);tree.reset(q.source);retained_edges.clear(q.net);
''','')
        s=one(s,'            snapshot.bind(q.net,present,owners,ledger);\n','')
        s=one(s,'snapshot.search_all(tree,targets,budget,retained_edges,q.net)','snapshot.route_net(tree,targets,budget,retained_edges,q.net,q.source,present,owners,ledger,retained)')
        s=one(s,'''            owners.insert_nodes(q.net,tree.roots(),nroots);
            retained.replace(q.net,tree.roots(),nroots);
            ledger.replace_packed(q.net,tree.demands());result.site_demands[q.net]=std::move(demands);''','''            result.site_demands[q.net]=std::move(demands);''')
        p.write_text(s)
