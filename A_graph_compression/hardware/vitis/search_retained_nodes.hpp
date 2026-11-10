#pragma once
#include <cstdint>
namespace fpga_search {
enum class RetainedStatus:unsigned{ok=0,invalid=1,capacity=2,overflow=3};
// Two banks of sorted (net<<32)|canonical_node pairs. Trusted internal state,
// exclusive owner and disjoint full-depth buffers. No tombstone/sentinel IDs.
template<unsigned Nodes=1048576,unsigned Pairs=2097152,unsigned Nets=65536>
struct RetainedNodes {
    static_assert(Nodes>0 && Nodes<=1048576 && Pairs>0 && Pairs<=2097152 && Nets>0 && Nets<=65536,"invalid capacities");
    static constexpr uint64_t Magic=UINT64_C(0x415245544e4f4431);
    using Status=RetainedStatus;
    // meta=[magic,node_domain,pair_count,bank,net_count,version].
    static bool valid(const uint64_t* m){return m[0]==Magic && m[1]>0 && m[1]<=Nodes && m[2]<=Pairs && m[3]<2 && m[4]<=Nets && m[4]<=m[2] && m[5]>0;}
    static Status reset(unsigned nodes,uint64_t* m){
        if(nodes>Nodes)return Status::capacity;
        if(!nodes)return Status::invalid;
        m[0]=Magic;m[1]=nodes;m[2]=0;m[3]=0;m[4]=0;m[5]=1;return Status::ok;
    }
    static unsigned bound(const uint64_t* rows,unsigned base,unsigned count,uint32_t net,bool upper){
        unsigned lo=0,hi=count;
        for(unsigned step=0;step<22 && lo<hi;++step){
            const unsigned mid=lo+(hi-lo)/2;const uint32_t n=uint32_t(rows[base+mid]>>32);
            if(n<net || (upper && n==net))lo=mid+1;else hi=mid;
        }
        return lo;
    }
    static Status get(uint32_t net,const uint64_t* m,const uint64_t* rows,uint32_t* out,unsigned& count){
        count=0;if(!valid(m))return Status::invalid;
        const unsigned base=unsigned(m[3])*Pairs,n=unsigned(m[2]);
        const unsigned first=bound(rows,base,n,net,false),last=bound(rows,base,n,net,true);
        for(unsigned i=first;i<last;++i)out[i-first]=uint32_t(rows[base+i]);
        count=last-first;return Status::ok;
    }
    static Status replace(uint32_t net,const uint32_t* nodes,unsigned count,uint64_t* m,uint64_t* rows){
        if(!valid(m))return Status::invalid;
        if(count>Nodes)return Status::capacity;
        if(m[5]==UINT64_MAX)return Status::overflow;
        for(unsigned i=0;i<count;++i)if(nodes[i]>=m[1] || (i && nodes[i]<=nodes[i-1]))return Status::invalid;
        const unsigned n=unsigned(m[2]),base=unsigned(m[3])*Pairs,other=(1-unsigned(m[3]))*Pairs;
        const unsigned first=bound(rows,base,n,net,false),last=bound(rows,base,n,net,true);
        const uint64_t total=uint64_t(n)-(last-first)+count;
        const unsigned nets=unsigned(m[4])-unsigned(last!=first)+unsigned(count!=0);
        if(total>Pairs || nets>Nets)return Status::capacity;
        // Preflight complete: neither bank changes on any rejected operation.
        for(unsigned i=0;i<first;++i)rows[other+i]=rows[base+i];
        for(unsigned i=0;i<count;++i)rows[other+first+i]=(uint64_t(net)<<32)|nodes[i];
        for(unsigned i=last;i<n;++i)rows[other+first+count+i-last]=rows[base+i];
        m[2]=total;m[3]=1-m[3];m[4]=nets;++m[5];return Status::ok;
    }
};
}
