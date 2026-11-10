#pragma once
#include "search_trace_v2.hpp"
#include "search_trace_set_codec.hpp"
namespace fpga_search {
struct BitmapTraceRuns {
    using Codec=TraceSetCodec<>;
    static bool bit(const uint64_t* bitmap,unsigned node){return ((bitmap[node/64]>>(node%64))&1)!=0;}
    static uint64_t measure(const uint64_t* bitmap,unsigned nodes,unsigned& count){
        uint64_t bytes=0;unsigned start=0,previous=0;bool run=false,first=true;count=0;
        for(unsigned n=0;n<=nodes;++n){
            const bool active=n<nodes && bit(bitmap,n);
            if(active){++count;if(!run){start=n;run=true;}}
            else if(run){bytes+=Codec::leb_size(first?start:start-previous)+Codec::leb_size(n-start);previous=n-1;first=false;run=false;}
        }
        return bytes;
    }
    static void emit(const uint64_t* bitmap,unsigned nodes,unsigned encoding,uint64_t* out){
        if(!encoding){unsigned at=0;for(unsigned n=0;n<nodes;++n)if(bit(bitmap,n))out[at++]=n;return;}
        Codec::Bytes writer{out};unsigned start=0,previous=0;bool run=false,first=true;
        for(unsigned n=0;n<=nodes;++n){
            const bool active=n<nodes && bit(bitmap,n);
            if(active && !run){start=n;run=true;}
            else if(!active && run){writer.leb(first?start:start-previous);writer.leb(n-start);previous=n-1;first=false;run=false;}
        }
        writer.finish();
    }
};
template<unsigned Words=16777216> struct SearchTraceV3 : SearchTraceV2<Words> {
    using Base=SearchTraceV2<Words>;using Codec=TraceSetCodec<>;
    static unsigned search(uint64_t iteration,uint64_t query,uint32_t target,unsigned nodes,
        const uint32_t* roots,unsigned root_count,const uint64_t* result,const uint32_t* path,
        const uint64_t* unknown_nodes,const uint64_t* unknown_pips,uint64_t* m,uint64_t* output){
        unsigned status=Base::reserve(0,m);if(status)return status;
        if(!nodes || nodes>1048576 || target>=nodes || root_count>1048576 || result[0]>6 || result[15]!=1 || result[7]>524288 || result[8]>nodes || result[9]>1100754)return Base::reject(m,1);
        if(result[0]){if(result[7])return Base::reject(m,1);for(unsigned i=16;i<81;++i)if(result[i])return Base::reject(m,1);}
        for(unsigned i=0;i<root_count;++i)if(roots[i]>=nodes || (i && roots[i]<=roots[i-1]))return Base::reject(m,1);
        for(unsigned i=0;i<unsigned(result[7]);++i)if(path[8*i]>=nodes || path[8*i+1]>=nodes || path[8*i+7]>1)return Base::reject(m,1);
        if(result[8] && nodes%64 && unknown_nodes[nodes/64]>>(nodes%64))return Base::reject(m,1);
        unsigned count=0;const uint64_t rle=result[8]?BitmapTraceRuns::measure(unknown_nodes,nodes,count):0;
        if(count!=result[8])return Base::reject(m,1);
        const unsigned node_encoding=rle<8*result[8]?1:0;
        const uint64_t node_bytes=node_encoding?rle:8*result[8];
        unsigned pip_encoding=0;uint64_t pip_bytes=0;
        if(!Codec::measure(unknown_pips,unsigned(result[9]),pip_encoding,pip_bytes))return Base::reject(m,1);
        const unsigned root_words=(root_count+1)/2;
        const uint64_t size=93+root_words+4*result[7]+(node_bytes+7)/8+(pip_bytes+7)/8;
        status=Base::reserve(size,m);if(status)return status;
        unsigned at=unsigned(m[2]);const uint64_t header[12]={6,size,iteration,query,target,root_count,result[8],result[9],node_encoding,node_bytes,pip_encoding,pip_bytes};
        for(unsigned i=0;i<12;++i)output[at++]=header[i];
        for(unsigned i=0;i<81;++i)output[at++]=result[i];
        for(unsigned i=0;i<root_words;++i)output[at++]=uint64_t(roots[2*i])|(2*i+1<root_count?uint64_t(roots[2*i+1])<<32:0);
        for(unsigned i=0;i<unsigned(result[7])*4;++i)output[at++]=uint64_t(path[2*i])|(uint64_t(path[2*i+1])<<32);
        if(result[8])BitmapTraceRuns::emit(unknown_nodes,nodes,node_encoding,output+at);
        at+=unsigned((node_bytes+7)/8);
        Codec::encode(unknown_pips,unsigned(result[9]),unsigned((pip_bytes+7)/8),output+at,pip_encoding,pip_bytes);
        Base::commit(unsigned(size),m);return 0;
    }
};
}
