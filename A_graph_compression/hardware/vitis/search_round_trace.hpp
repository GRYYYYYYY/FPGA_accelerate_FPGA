#pragma once
#include "search_trace_v2.hpp"
#include "search_node_occupancy.hpp"
#include "search_site_occupancy.hpp"
namespace fpga_search {
// phase0: decision before advance; phase1: both histories successfully advanced.
// Full domain counts/history make absence explicit. Active site banks are exact.
template<unsigned Words=16777216,unsigned Nodes=1048576,unsigned Owners=65536,unsigned Nets=65536>
struct RoundTrace {
    using Base=SearchTraceV2<Words>;
    using Node=NodeOccupancy<Nodes,2097152>;
    using Site=SiteOccupancy<Owners,Owners,Owners>;
    static unsigned write(unsigned phase,const uint64_t* control,const uint64_t* result,
        const uint32_t* complete,const uint64_t* node_meta,const uint32_t* counts,const uint64_t* history,
        const uint64_t* site_meta,const uint64_t* owners,const uint64_t* site_history,
        unsigned groups,const uint64_t* summaries,uint64_t* meta,uint64_t* out){
        unsigned status=Base::reserve(0,meta);if(status)return status;
        if(phase>1 || !Node::valid_meta(node_meta) || !Site::valid(site_meta) || control[0]!=node_meta[1] ||
           !control[1] || control[1]>Nets || control[6] || control[7] || result[0] || groups>Owners ||
           control[5]!=groups || result[6]>1 || (phase==1 && !result[6]))return Base::reject(meta,1);
        const unsigned nodes=unsigned(control[0]),nets=unsigned(control[1]),ns=unsigned(site_meta[2]),nh=unsigned(site_meta[4]);
        for(unsigned i=0;i<nets;++i)if(complete[i]>1)return Base::reject(meta,1);
        const uint64_t size=42+uint64_t(nodes)*2+(nets+1)/2+uint64_t(ns)*4+uint64_t(nh)*2+uint64_t(groups)*2;
        status=Base::reserve(size,meta);if(status)return status;
        unsigned at=unsigned(meta[2]);const uint64_t h[16]={3,size,control[2],phase,nodes,nets,ns,nh,groups,0,0,0,0,0,0,0};
        for(unsigned i=0;i<16;++i)out[at++]=h[i];
        for(unsigned i=0;i<8;++i)out[at++]=control[i];
        for(unsigned i=0;i<8;++i)out[at++]=result[i];
        for(unsigned i=0;i<4;++i)out[at++]=node_meta[i];
        for(unsigned i=0;i<6;++i)out[at++]=site_meta[i];
        for(unsigned i=0;i<nodes;++i){out[at++]=counts[i];out[at++]=history[i];}
        for(unsigned i=0;i<(nets+1)/2;++i)out[at++]=uint64_t(complete[2*i])|(2*i+1<nets?uint64_t(complete[2*i+1])<<32:0);
        const unsigned ob=unsigned(site_meta[1])*Owners*4,hb=unsigned(site_meta[3])*Owners*2;
        for(unsigned i=0;i<ns*4;++i)out[at++]=owners[ob+i];
        for(unsigned i=0;i<nh*2;++i)out[at++]=site_history[hb+i];
        for(unsigned i=0;i<groups*2;++i)out[at++]=summaries[i];
        Base::commit(unsigned(size),meta);return 0;
    }
};
}
