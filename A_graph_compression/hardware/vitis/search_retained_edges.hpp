#pragma once
#include <cstdint>
namespace fpga_search {
enum class RetainedEdgeStatus:unsigned {ok=0,invalid=1,capacity=2,overflow=3};
// Trusted exclusive state; disjoint buffers. Rows sorted by net, stable within net.
// Each row is [net,src,dst,tile,pip,upstream,downstream,attributes,direction].
// Two complete banks; rejected operations leave both banks and metadata unchanged.
template<unsigned Nodes=1048576,unsigned Edges=2097152,unsigned Nets=65536>
struct RetainedEdges {
    static_assert(Nodes>0 && Nodes<=1048576 && Edges>0 && Edges<=2097152 && Nets>0 && Nets<=65536,"invalid capacity");
    using Status=RetainedEdgeStatus;
    static constexpr uint64_t Magic=UINT64_C(0x4152455445444731);
    // magic, node_domain, edge_count, bank, nonempty_net_count, version
    static bool valid(const uint64_t* m){return m[0]==Magic && m[1]>0 && m[1]<=Nodes && m[2]<=Edges && m[3]<2 && m[4]<=Nets && m[4]<=m[2] && m[5]>0;}
    static Status reset(unsigned nodes,uint64_t* m){
        if(nodes>Nodes)return Status::capacity;
        if(!nodes)return Status::invalid;
        m[0]=Magic;m[1]=nodes;m[2]=0;m[3]=0;m[4]=0;m[5]=1;return Status::ok;
    }
    static unsigned bound(const uint32_t* rows,unsigned base,unsigned count,uint32_t net,bool upper){
        unsigned lo=0,hi=count;
        for(unsigned step=0;step<22 && lo<hi;++step){
            unsigned mid=lo+(hi-lo)/2;uint32_t n=rows[base+9*mid];
            if(n<net || (upper && n==net))lo=mid+1;else hi=mid;
        }
        return lo;
    }
    static Status get(uint32_t net,const uint64_t* m,const uint32_t* rows,uint32_t* out,unsigned& count){
        count=0;if(!valid(m))return Status::invalid;
        unsigned base=unsigned(m[3])*Edges*9,n=unsigned(m[2]);
        unsigned first=bound(rows,base,n,net,false),last=bound(rows,base,n,net,true);
        for(unsigned i=first;i<last;++i)for(unsigned j=0;j<8;++j)out[8*(i-first)+j]=rows[base+9*i+1+j];
        count=last-first;return Status::ok;
    }
    static Status update(uint32_t net,const uint32_t* path,unsigned count,bool append,uint64_t* m,uint32_t* rows){
        if(!valid(m))return Status::invalid;
        if(count>Edges)return Status::capacity;
        if(m[5]==UINT64_MAX)return Status::overflow;
        for(unsigned i=0;i<count;++i)if(path[8*i]>=m[1] || path[8*i+1]>=m[1] || path[8*i+7]>1)return Status::invalid;
        unsigned n=unsigned(m[2]),base=unsigned(m[3])*Edges*9,other=(1-unsigned(m[3]))*Edges*9;
        unsigned first=bound(rows,base,n,net,false),last=bound(rows,base,n,net,true);
        unsigned keep=append?last-first:0;
        uint64_t total=uint64_t(n)-(last-first)+keep+count;
        unsigned nets=unsigned(m[4])-unsigned(last!=first)+unsigned(keep+count!=0);
        if(total>Edges || nets>Nets)return Status::capacity;
        unsigned prefix=append?last:first;
        for(unsigned i=0;i<prefix*9;++i)rows[other+i]=rows[base+i];
        for(unsigned i=0;i<count;++i){
            rows[other+9*(prefix+i)]=net;
            for(unsigned j=0;j<8;++j)rows[other+9*(prefix+i)+1+j]=path[8*i+j];
        }
        for(unsigned i=last;i<n;++i)for(unsigned j=0;j<9;++j)rows[other+9*(prefix+count+i-last)+j]=rows[base+9*i+j];
        m[2]=total;m[3]=1-m[3];m[4]=nets;++m[5];return Status::ok;
    }
};
}
