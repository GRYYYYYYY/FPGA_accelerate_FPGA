#pragma once
#include "search_trace_v2.hpp"
namespace fpga_search {
template<unsigned Words=16777216> struct BatchTraceFrames {
    using Base=SearchTraceV2<Words>;
    // BEGIN: raw batch control + exact immutable schedule and complete sink pool.
    static unsigned begin(const uint64_t* control,const uint64_t* queries,const uint32_t* sinks,uint64_t* meta,uint64_t* out){
        unsigned s=Base::reserve(0,meta);if(s)return s;
        if(control[2]>65536 || control[3]>4194304)return Base::reject(meta,1);
        const unsigned nets=unsigned(control[2]),ns=unsigned(control[3]);
        const uint64_t size=24+4*uint64_t(nets)+(ns+1)/2;
        s=Base::reserve(size,meta);if(s)return s;
        unsigned at=unsigned(meta[2]);const uint64_t h[8]={4,size,1,nets,ns,0,0,0};
        for(unsigned i=0;i<8;++i)out[at++]=h[i];
        for(unsigned i=0;i<16;++i)out[at++]=control[i];
        for(unsigned i=0;i<4*nets;++i)out[at++]=queries[i];
        for(unsigned i=0;i<(ns+1)/2;++i)out[at++]=uint64_t(sinks[2*i])|(2*i+1<ns?uint64_t(sinks[2*i+1])<<32:0);
        Base::commit(unsigned(size),meta);return 0;
    }
    // Terminal records are required even for early routing errors. A sticky
    // trace failure prevents this commit and therefore invalidates completeness.
    static unsigned terminal(const uint64_t* result,uint64_t* meta,uint64_t* out){
        unsigned s=Base::reserve(20,meta);if(s)return s;
        unsigned at=unsigned(meta[2]);const uint64_t h[8]={5,20,1,0,0,0,0,0};
        for(unsigned i=0;i<8;++i)out[at++]=h[i];
        for(unsigned i=0;i<12;++i)out[at++]=result[i];
        Base::commit(20,meta);return 0;
    }
};
}
