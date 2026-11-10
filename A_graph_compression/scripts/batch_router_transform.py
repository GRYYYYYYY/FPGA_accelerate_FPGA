"""Execute the actual all-net/round top, preserving every native diagnostic result."""
from pathlib import Path
from derive_search_flat_controller import replace_once as one
ROOT=Path(__file__).resolve().parents[1]
def adapt(source):
    top=ROOT/'hardware/vitis/search_batch_observed_top.cpp';(source/top.name).write_text(top.read_text())
    p=source/'site_occupancy_snapshot_adapter.hpp';s=p.read_text();s=one(s,'struct ResidentBuffers {uint64_t *meta,*owners,*history,*request;};','struct ResidentBuffers {uint64_t *meta,*owners,*history,*request;uint32_t* flags;uint64_t* groups;};');s=one(s,'return {meta_.data(),owners_.data(),history_.data(),request_.data()};','return {meta_.data(),owners_.data(),history_.data(),request_.data(),flags_.data(),groups_.data()};');p.write_text(s)
    p=source/'sink_loop_observer.hpp';s=p.read_text();s=s[:s.index('extern "C" void search_net_csr')]
    raw=top.read_text();at=raw.index('extern "C" void SEARCH_TOP_NAME');decl=raw[at:raw.index(' {',at)]+';'
    s+='#include <functional>\nnamespace batch_observation {inline thread_local std::function<void(unsigned,unsigned,unsigned)>* active=nullptr;struct Scope{explicit Scope(std::function<void(unsigned,unsigned,unsigned)>& f){if(active)throw std::logic_error("nested batch observer");active=&f;}~Scope(){active=nullptr;}};}\n'
    s+='extern "C" void search_batch_boundary(unsigned kind,unsigned iteration,unsigned q){if(!batch_observation::active)throw std::logic_error("missing batch observer");(*batch_observation::active)(kind,iteration,q);}\n'
    s+=decl.replace('SEARCH_TOP_NAME','search_batch_csr')+'\n'+decl.replace('SEARCH_TOP_NAME','search_batch_compact')+'\n';p.write_text(s)
    p=source/'search_kernel_route_adapter.hpp';s=p.read_text();start=s.index('    std::vector<site_native::SearchResult> route_net(');decode_start=s.index('        std::vector<site_native::SearchResult> outputs;',start);end=s.index('\n    }',decode_start)+len('\n    }')
    decode=s[decode_start:end].replace('frames.size()','frames_.size()').replace('frame=frames[index]','frame=frames_[index]')
    method='''    std::vector<sink_loop_observation::Frame> frames_;
    std::array<uint64_t,8> last_net_{},last_round_{};
    std::vector<uint32_t> completion_=std::vector<uint32_t>(65536);
public:
    const uint64_t* net_observation()const{return last_net_.data();}
    const uint64_t* round_observation()const{return last_round_.data();}
    const uint32_t* completions()const{return completion_.data();}
    std::vector<site_native::SearchResult> decode_frames(const std::vector<uint32_t>& targets){
        if(frames_.size()!=targets.size())fail(false,"incomplete batch search trace");
'''+decode+'''
    template<class Query,class Observe>
    std::array<uint64_t,12> route_batch(route_tree_host::Tree& tree,const std::vector<Query>& queries,unsigned max_iterations,uint64_t budget,uint64_t cap,retained_edges_host::Store& retained_edges,node_occupancy_host::OwnerTable& owners,site_occupancy_host::Ledger& ledger,retained_nodes_host::Store& retained,Observe observation){
        if(queries.empty() || queries.size()>65536)fail(true,"batch query count");
        std::vector<uint64_t> table(262144);std::vector<uint32_t> sink_pool(4194304);size_t used=0;
        for(size_t q=0;q<queries.size();++q){auto targets=queries[q].sinks;std::sort(targets.begin(),targets.end());if(targets.size()>1048576 || targets.size()>4194304-used)fail(true,"batch sink pool");table[4*q]=queries[q].net;table[4*q+1]=queries[q].source;table[4*q+2]=used;table[4*q+3]=targets.size();std::copy(targets.begin(),targets.end(),sink_pool.begin()+used);used+=targets.size();}
        auto& w=flat_controller_adapter::storage<Limits>().workspace;auto node=owners.resident_buffers();auto site=ledger.resident_buffers();
        uint64_t meta[2]={w.epoch,w.key_count},result[81]{},nested[8]{};std::array<uint64_t,12> batch_result{};
        const uint64_t control[16]={cap,max_iterations,queries.size(),used,builder_.static_words(),budget,0,0,0,0,0,0,0,0,0,0};
        std::function<void(unsigned,unsigned,unsigned)> observer=[&](unsigned kind,unsigned iteration,unsigned q){
            if(kind==0){frames_.clear();return;}
            if(kind==1){
                packet_words_=unsigned(packet_[1]);++counters.snapshots;++kernel_counters.packets;kernel_counters.serialized_words+=packet_words_;kernel_counters.max_packet_words=std::max(kernel_counters.max_packet_words,packet_words_);
                unsigned domain=unsigned(packet_[2]),at=97+(domain+63)/64;bool occupied=false,past=false;
                for(unsigned i=0;i<domain;++i){occupied=occupied || packet_[at+2*i]!=0;past=past || packet_[at+2*i+1]!=0;}
                counters.node_occupied+=occupied;counters.node_history+=past;counters.site_occupied+=packet_[11]!=0;counters.site_history+=packet_[12]!=0;counters.max_site_owners=std::max(counters.max_site_owners,unsigned(packet_[11]));counters.max_site_history=std::max(counters.max_site_history,unsigned(packet_[12]));
            }
            observation(kind,iteration,q);
        };
        {sink_loop_observation::Scope search_observer(frames_);batch_observation::Scope batch_observer(observer);
            auto kernel=image_.config[0]==0?search_batch_csr:search_batch_compact;
            kernel(image_.image,image_.config,image_.image_words,tree.resident_roots(),packet_.data(),w.heap,w.slots,w.records,w.keys,w.unknown_nodes,w.unknown_pips,w.path,meta,result,tree.resident_meta(),tree.resident_bits(),tree.resident_demands(),retained_edges.resident_meta(),retained_edges.resident_rows(),nested,sink_pool.data(),builder_.static_data(),node.meta,node.counts,node.history,node.keys,node.flags,site.meta,site.owners,site.history,site.request,retained.resident_meta(),retained.resident_rows(),retained.resident_output(),last_net_.data(),control,table.data(),completion_.data(),site.flags,site.groups,last_round_.data(),batch_result.data());
        }
        if(batch_result[0] || meta[0]>UINT32_MAX || meta[1]>Limits::labels)fail(false,"integrated batch rejected operation");
        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);return batch_result;
    }
'''
    s=s[:start]+method+s[end:];p.write_text(s)
    for name in ['site_routes.hpp','snapshot_test_routes.hpp']:
        p=source/name;s=p.read_text();start=s.index('    round_control_host::Context control;');end=s.index('    return result;',start)
        body='''    SiteRound round;
    const auto summary=snapshot.route_batch(tree,queries,max_iterations,budget,present_cap,retained_edges,owners,ledger,retained,[&](unsigned kind,unsigned iteration,unsigned qindex){
        if(kind==1){
            const auto& q=queries[qindex];auto targets=q.sinks;std::sort(targets.begin(),targets.end());
            auto connections=snapshot.decode_frames(targets);const auto* nr=snapshot.net_observation();
            netlist_native::NetRoute route{q.source,q.sinks,{},{},nr[5]!=0};
            route.nodes.insert(tree.roots(),tree.roots()+nr[6]);const unsigned edge_count=retained_edges.get(q.net);
            for(unsigned i=0;i<edge_count;++i){const uint32_t* p=retained_edges.output()+8*i;route.edges.emplace_back(p[0],Edge{p[1],p[2],p[3],p[4],p[5],p[6],p[7]});}
            typename fpga_search::ProductionRouteTree::Words::Key demand{};if(!fpga_search::ProductionRouteTree::Words::load(tree.demands(),0,demand) || demand.node)throw std::logic_error("invalid batch observation demand");
            result.site_demands[q.net]=flat_controller_adapter::unpack(demand.state);result.routes.insert_or_assign(q.net,std::move(route));round.outcomes.push_back(std::move(connections));
            if(progress && round.outcomes.size()%50==0)progress(iteration,round.outcomes.size());
        }else if(kind==2){
            round.conflicts=owners.conflicts();round.site_conflicts=ledger.conflicts();
            for(size_t i=0;i<queries.size();++i)if(!snapshot.completions()[i])round.incomplete.insert(queries[i].net);
            const auto* rr=snapshot.round_observation();if(round.conflicts.size()!=rr[1] || round.incomplete.size()!=rr[2])throw std::logic_error("batch round observations differ");
            result.iterations.push_back(std::move(round));round=SiteRound{};if(progress)progress(iteration,queries.size());
        }
    });
    result.status=summary[7]?"routed":"incomplete";
'''
        s=s[:start]+body+s[end:];p.write_text(s)
