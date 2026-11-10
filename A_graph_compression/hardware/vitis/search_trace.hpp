#pragma once
#include <cstdint>
namespace fpga_search {
// Exact bounded diagnostic records. Disjoint/exclusive metadata and word buffer.
// meta8=[magic,capacity_words,committed_words,records,sticky_status,version,0,0].
// A rejected frame changes only sticky_status; never writes its partial payload.
template<unsigned Words=16777216> struct SearchTrace {
    static_assert(Words>0 && Words<=16777216,"trace capacity exceeded");
    static constexpr uint64_t Magic=UINT64_C(0x4154524143453031);
    static unsigned reset(unsigned capacity,uint64_t* m){
        if(!capacity || capacity>Words)return 2;
        m[0]=Magic;m[1]=capacity;m[2]=0;m[3]=0;m[4]=0;m[5]=1;m[6]=m[7]=0;return 0;
    }
    static unsigned reject(uint64_t* m,unsigned status){m[4]=status;return status;}
    static unsigned reserve(uint64_t words,uint64_t* m){
        if(m[0]!=Magic || !m[1] || m[1]>Words || m[2]>m[1] || m[3]>m[2] || !m[5] || m[6] || m[7])return reject(m,1);
        if(m[4])return unsigned(m[4]);
        if(m[5]==UINT64_MAX)return reject(m,3);
        if(words>m[1]-m[2])return reject(m,2);
        return 0;
    }
    static void commit(unsigned words,uint64_t* m){m[2]+=words;++m[3];++m[5];}
    // frame=[type1,total_words,iteration,query_index,target,nroots,nunknown_nodes,nunknown_pips],
    // result81, packed roots(two u32/word, low lane first, final high lane zero),
    // packed path(four u64/edge), ascending unknown node IDs(u64), raw PIP keys(u64).
    static unsigned search(uint64_t iteration,uint64_t query,uint32_t target,unsigned nodes,
                           const uint32_t* roots,unsigned root_count,const uint64_t* result,
                           const uint32_t* path,const uint64_t* unknown_nodes,const uint64_t* unknown_pips,
                           uint64_t* m,uint64_t* output){
        unsigned prior=reserve(0,m);if(prior)return prior;
        if(!nodes || nodes>1048576 || target>=nodes || root_count>1048576 || result[0]>6 || result[15]!=1 || result[7]>524288 || result[8]>1048576 || result[9]>1100754)return reject(m,1);
        if(result[0]!=0){if(result[7])return reject(m,1);for(unsigned i=16;i<81;++i)if(result[i])return reject(m,1);}
        for(unsigned i=0;i<root_count;++i)if(roots[i]>=nodes || (i && roots[i]<=roots[i-1]))return reject(m,1);
        for(unsigned i=0;i<unsigned(result[7]);++i)if(path[8*i]>=nodes || path[8*i+1]>=nodes || path[8*i+7]>1)return reject(m,1);
        const unsigned nw=(nodes+63)/64;
        if(nodes%64 && (unknown_nodes[nw-1]>>(nodes%64)))return reject(m,1);
        unsigned unknown_count=0;
        for(unsigned i=0;i<nw;++i){const uint64_t value=unknown_nodes[i];if(value)for(unsigned bit=0;bit<64;++bit)unknown_count+=unsigned((value>>bit)&1);}
        if(unknown_count!=result[8])return reject(m,1);
        const unsigned root_words=(root_count+1)/2;
        const uint64_t size=89+uint64_t(root_words)+4*result[7]+result[8]+result[9];
        unsigned status=reserve(size,m);if(status)return status;
        unsigned at=unsigned(m[2]);const uint64_t header[8]={1,size,iteration,query,target,root_count,result[8],result[9]};
        for(unsigned i=0;i<8;++i)output[at++]=header[i];
        for(unsigned i=0;i<81;++i)output[at++]=result[i];
        for(unsigned i=0;i<root_words;++i)output[at++]=uint64_t(roots[2*i])|(2*i+1<root_count?uint64_t(roots[2*i+1])<<32:0);
        for(unsigned i=0;i<unsigned(result[7])*4;++i)output[at++]=uint64_t(path[2*i])|(uint64_t(path[2*i+1])<<32);
        for(unsigned word=0;word<nw;++word){const uint64_t value=unknown_nodes[word];if(value)for(unsigned bit=0;bit<64;++bit)if((value>>bit)&1)output[at++]=uint64_t(word)*64+bit;}
        for(unsigned i=0;i<unsigned(result[9]);++i)output[at++]=unknown_pips[i];
        commit(unsigned(size),m);return 0;
    }
};
}
