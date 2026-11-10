#pragma once
#include "search_controller_flat.hpp"
#include "search_snapshot_provider.hpp"
#include "search_graph_adjacency.hpp"

namespace fpga_search {
struct SearchRegionLimits {
    static constexpr unsigned nodes=1048576,degree=1024,roots=1048576,unknown_pips=1100754,path=524288,expansions=200000;
    static constexpr unsigned signals=32,bits=16,values=8,slots=1048576,labels=524288,heap=131072;
};
struct SearchMetadataLimits {
    static constexpr unsigned semantics=256,attributes=65536,protected_pips=1048576,owners=65536,history=65536,fixed=65536;
};
// Packet v1 uses uint64 words. Header (32 words): magic,total_words,nodes,
// attributes,net,present,target,nroots,budget,nsemantics,nprotected,nowners,
// nhistory,nfixed,18 reserved zeros. Contiguous sections in this exact order:
// initial key (node=0), forbidden ceil(nodes/64), node costs 2*nodes,
// pseudo flags ceil(attributes/8), blocked flags ceil(attributes/8), protected
// PIP keys, semantic PIP keys, semantic keys' requirements (node=0), owner
// records 4*nowners, history records 2*nhistory, fixed records 4*nfixed.
// Flags are 8 little-significance byte lanes per word; unused bytes must be 0.
// Roots are a separate sorted uint32 buffer. All buffers are non-aliasing and
// caller-sized; image/config must pass the host AGRAPH01 descriptor validator.
// This kernel performs one complete search. Host still constructs snapshots
// and performs negotiation/occupancy updates between searches.
static constexpr uint64_t SearchPacketMagic=0x4153454152434831ULL;
static constexpr unsigned SearchPacketMaxWords=4194304;
static constexpr unsigned SearchResultHeaderWords=16;
template<unsigned Mode,class L=SearchRegionLimits,class M=SearchMetadataLimits>
struct SearchKernel {
    using Core=FlatSearchController<L>;
    using State=typename Core::State;
    using StateWords=LabelKeyWords<1,L::signals,L::bits,L::values>;
    using Adjacency=ImageAdjacency<Mode>;
    using Provider=SearchSnapshotProvider<L,Adjacency,M::semantics,M::attributes,M::protected_pips,M::owners,M::history,M::fixed>;
    static constexpr unsigned ResultWords=SearchResultHeaderWords+StateWords::Words;
    static bool flags(const uint64_t* packed,unsigned count,uint8_t* output) {
        for(unsigned i=0;i<M::attributes;++i){
            if(i>=count)break;
            const unsigned value=unsigned((packed[i/8]>>(8*(i%8)))&255);
            if(value>1)return false;
            output[i]=uint8_t(value);
        }
        if(count%8 && (packed[count/8]>>(8*(count%8))))return false;
        return true;
    }
    static void run(const uint32_t* image,const uint32_t* config,unsigned image_words,
            const uint32_t* roots,const uint64_t* packet,unsigned packet_words,
            uint64_t* heap,uint64_t* slots,uint64_t* records,uint64_t* keys,
            uint64_t* unknown_nodes,uint64_t* unknown_pips,uint32_t* path,
            uint64_t* meta,uint64_t* result) {
#pragma HLS INLINE

        // result must always have ResultWords words. Rejected preflight calls
        // leave workspace/meta unchanged and expose only invalid/capacity status.
        for(unsigned i=0;i<ResultWords;++i)result[i]=0;
        result[0]=uint64_t(SearchStatus::invalid_input);result[15]=1;
        if(!packet || !config || !image || !roots || !heap || !slots || !records || !keys || !unknown_nodes || !unknown_pips || !path || !meta)return;
        if(packet_words<32)return;
        if(packet_words>SearchPacketMaxWords){result[0]=uint64_t(SearchStatus::capacity_exhausted);return;}
        uint64_t h[32];for(unsigned i=0;i<32;++i)h[i]=packet[i];
        if(h[0]!=SearchPacketMagic || h[1]!=packet_words)return;
        for(unsigned i=14;i<32;++i)if(h[i])return;
        if(h[2]>L::nodes || h[3]>M::attributes || h[7]>L::roots || h[8]>L::expansions || h[9]>M::semantics || h[10]>M::protected_pips || h[11]>M::owners || h[12]>M::history || h[13]>M::fixed){result[0]=uint64_t(SearchStatus::capacity_exhausted);return;}
        if(!h[2] || !h[3] || h[4]>UINT32_MAX || !h[5] || h[6]>=h[2] || !h[7] || !h[8] || meta[0]>UINT32_MAX || meta[1]>L::labels || (!meta[0] && meta[1]))return;
        const unsigned nodes=unsigned(h[2]),attributes=unsigned(h[3]);
        const unsigned nsem=unsigned(h[9]),nprotected=unsigned(h[10]),nowners=unsigned(h[11]),nhistory=unsigned(h[12]),nfixed=unsigned(h[13]);
        const uint64_t forbidden_at=32+StateWords::Words;
        const uint64_t costs_at=forbidden_at+(nodes+63)/64;
        const uint64_t pseudo_at=costs_at+uint64_t(2)*nodes;
        const uint64_t blocked_at=pseudo_at+(attributes+7)/8;
        const uint64_t protected_at=blocked_at+(attributes+7)/8;
        const uint64_t semantics_at=protected_at+nprotected;
        const uint64_t requirements_at=semantics_at+nsem;
        const uint64_t owners_at=requirements_at+uint64_t(nsem)*StateWords::Words;
        const uint64_t history_at=owners_at+uint64_t(4)*nowners;
        const uint64_t fixed_at=history_at+uint64_t(2)*nhistory;
        if(fixed_at+uint64_t(4)*nfixed!=packet_words)return;
        typename StateWords::Key initial{};
        if(!StateWords::load(packet+32,0,initial) || initial.node)return;
        State requirements[M::semantics];
        for(unsigned i=0;i<M::semantics;++i){
            if(i>=nsem)break;
            typename StateWords::Key key{};
            if(!StateWords::load(packet+requirements_at+uint64_t(i)*StateWords::Words,0,key) || key.node)return;
            requirements[i]=key.state;
        }
        uint8_t pseudo[M::attributes],blocked[M::attributes];
        if(!flags(packet+pseudo_at,attributes,pseudo) || !flags(packet+blocked_at,attributes,blocked))return;
        uint32_t descriptor[32];for(unsigned i=0;i<32;++i)descriptor[i]=config[i];
        Adjacency adjacency;
        if(adjacency.bind(image,descriptor,image_words)!=RowStatus::known || descriptor[graph_decode::NODE_COUNT]!=nodes || descriptor[graph_decode::ATTR_COUNT]!=attributes)return;
        Provider provider(adjacency);
        typename Provider::View view{nodes,attributes,packet+forbidden_at,packet+costs_at,pseudo,blocked,packet+protected_at,packet+semantics_at,requirements,nprotected,nsem,
            {packet+owners_at,packet+history_at,packet+fixed_at,nowners,nhistory,nfixed},uint32_t(h[4]),h[5]};
        const auto bound=provider.bind(view);
        if(bound!=CostStatus::ok){if(bound==CostStatus::capacity_exhausted)result[0]=uint64_t(SearchStatus::capacity_exhausted);return;}
        LabelEdge edges[L::degree];
        typename Core::Workspace workspace{heap,slots,records,unknown_nodes,keys,edges,unknown_pips,path,uint32_t(meta[0]),unsigned(meta[1])};
        const auto out=Core::run(provider,workspace,roots,unsigned(h[7]),uint32_t(h[6]),initial.state,h[8]);
        meta[0]=workspace.epoch;meta[1]=workspace.key_count;
        // Header: status,cost,expanded,blocked,pushes,pops,improvements,path_len,
        // unknown_nodes,unknown_pips,labels,max_heap,max_probes,epoch,key_count,1.
        result[0]=uint64_t(out.status);result[1]=out.cost;result[2]=out.expanded;result[3]=out.blocked;
        result[4]=out.pushes;result[5]=out.pops;result[6]=out.improvements;result[7]=out.path_length;
        result[8]=out.unknown_node_count;result[9]=out.unknown_pip_count;result[10]=out.label_count;
        result[11]=out.max_heap;result[12]=out.max_probes;result[13]=workspace.epoch;result[14]=workspace.key_count;
        if(out.status==SearchStatus::found){
            const typename StateWords::Key key{uint32_t(h[6]),out.demands};
            if(!StateWords::store(result+16,0,key))result[0]=uint64_t(SearchStatus::invalid_input);
        }
    }
};
} // namespace fpga_search
