// Full declared depths on every transaction, including errors and reset.
// Independent oracle: canonical-node set and literal packed-state layout.
// No DUT helper/header is included here.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <set>
#include <vector>
extern "C" void search_route_tree_top(const uint64_t*,uint64_t*,uint64_t*,uint64_t*,const uint64_t*,const uint32_t*,const uint32_t*,uint32_t*,uint64_t*);
constexpr unsigned N=1048576,P=524288;
constexpr uint64_t G=UINT64_C(0xbad0cafe12345678),Magic=UINT64_C(0x4154524545535431);
constexpr uint32_t G32=0xdeadbeef;
struct Bench {
    std::vector<uint64_t> meta=std::vector<uint64_t>(6,G),bits=std::vector<uint64_t>(16385,G),demands=std::vector<uint64_t>(66,G);
    std::vector<uint64_t> em=meta,eb=bits,ed=demands;
    std::vector<uint32_t> roots=std::vector<uint32_t>(N+1,G32),er=roots;
    std::vector<uint32_t> path=std::vector<uint32_t>(4194305,G32),sinks=std::vector<uint32_t>(N+1,G32);
    std::array<uint64_t,82> search{};
    std::set<uint32_t> nodes;
    unsigned transaction=0;
    Bench(){search.back()=G;}
    void state(unsigned ns,unsigned nb,unsigned nv,unsigned target){
        std::fill(search.begin(),search.begin()+81,0);search[15]=1;
        search[16]=target|(uint64_t(ns)<<32)|(uint64_t(nb)<<40)|(uint64_t(nv)<<48);
        for(unsigned i=0;i<ns;++i)search[17+i/2]|=uint64_t(2*i+1)<<(32*(i%2));
        for(unsigned i=0;i<nb;++i){search[33+i/2]|=uint64_t(3*i+2)<<(32*(i%2));search[41+i]=UINT64_MAX;search[57+i]=uint64_t(1)<<(32+i);}
        for(unsigned i=0;i<nv;++i)search[73+i]=(uint64_t(i+9)<<32)|(4*i+3);
    }
    void chain(unsigned start,unsigned length){
        search[7]=length;search[1]=length;
        for(unsigned i=0;i<length;++i){std::fill(path.begin()+8*i,path.begin()+8*i+8,0);path[8*i]=start+i;path[8*i+1]=start+i+1;path[8*i+7]=i%2;}
    }
    void call(unsigned op,unsigned expected,unsigned reset=0,unsigned source=0,unsigned target=0,unsigned count=0,
              bool reserved=false,bool wide=false){
        std::array<uint64_t,9> config{{op,reset,source,target,count,0,0,0,G}};
        if(reserved)config[5]=1;
        if(wide)config[3]=UINT64_C(1)<<32;
        std::array<uint64_t,7> result{{G,G,G,G,G,G,G}};
        const auto c=config;const auto s=search;const auto pi=path,si=sinks;
        uint64_t applied=0,nroots=0,done=0;
        if(!expected){
            if(op==0){nodes.clear();nodes.insert(source);em[0]=Magic;em[1]=reset;em[2]=source;em[3]=1;em[4]=1;
                std::fill(eb.begin(),eb.begin()+(reset+63)/64,0);eb[source/64]|=uint64_t(1)<<(source%64);std::fill(ed.begin(),ed.begin()+65,0);
            }else if(op==1 && search[0]==0){
                for(unsigned i=0;i<search[7];++i){unsigned n=path[8*i+1];nodes.insert(n);eb[n/64]|=uint64_t(1)<<(n%64);}
                em[3]=nodes.size();++em[4];applied=1;std::copy(search.begin()+16,search.begin()+81,ed.begin());ed[0]&=UINT64_C(0xffffffff00000000);
            }else if(op==2){nroots=nodes.size();std::copy(nodes.begin(),nodes.end(),er.begin());}
            else if(op==3){done=1;for(unsigned i=0;i<count;++i)if(!nodes.count(sinks[i]))done=0;}
        }
        search_route_tree_top(config.data(),meta.data(),bits.data(),demands.data(),search.data(),path.data(),sinks.data(),roots.data(),result.data());
        assert(config==c && search==s && path==pi && sinks==si);
        assert(meta==em && bits==eb && demands==ed && roots==er);
        const std::array<uint64_t,7> want{{expected,expected?0:em[3],expected?0:em[4],applied,nroots,done,G}};
        assert(result==want);
        std::cout<<"TREE_RTL_TX "<<transaction++<<' '<<op;
        for(unsigned i=0;i<6;++i)std::cout<<' '<<result[i];
        std::cout<<'\n';
    }
};
int main(){
    Bench b;
    b.call(0,0,N); // Full active domain, never reduced production capacity.
    b.state(32,16,8,P);b.chain(0,P);b.call(1,0,0,0,P);
    b.state(32,16,8,N-1);b.chain(P,P-1);b.call(1,0,0,0,N-1);
    b.call(2,0);
    for(unsigned i=0;i<N;++i)b.sinks[i]=i;
    b.call(3,0,0,0,0,N);
    b.search[7]=P+1;b.call(1,2,0,0,N-1);
    b.call(3,2,0,0,0,N+1);
    b.sinks[N-1]=N;b.call(3,1,0,0,0,N);b.sinks[N-1]=N-1;
    b.call(0,2,N+1);b.call(0,1,N,N);b.call(0,1,0);
    b.call(0,0,64,63); // Inactive bitset/root tails must survive.
    b.call(2,0);b.call(3,0); // Empty sink list is complete.
    b.sinks[0]=63;b.sinks[1]=0;b.call(3,0,0,0,0,2);
    b.state(1,1,1,1);b.chain(63,1);b.path[1]=1;b.call(1,0,0,0,1);
    b.sinks[1]=1;b.sinks[2]=1;b.call(3,0,0,0,0,3);
    b.call(2,0);
    for(unsigned status=1;status<=6;++status){b.state(0,0,0,0);b.search[0]=status;b.call(1,0,0,0,2);}
    auto good=[&](){b.state(1,1,1,2);b.chain(1,1);};
    good();b.search[15]=0;b.call(1,1,0,0,2);
    good();b.search[0]=7;b.call(1,1,0,0,2);
    good();b.search[1]=UINT64_MAX;b.call(1,1,0,0,2);
    good();b.path[0]=0;b.call(1,1,0,0,2); // Existing-domain non-tree start.
    good();b.path[1]=64;b.call(1,1,0,0,2);
    good();b.path[7]=2;b.call(1,1,0,0,2);
    good();b.chain(1,2);b.path[8]=3;b.call(1,1,0,0,2); // Late disconnected edge.
    good();b.search[16]^=1;b.call(1,1,0,0,2);
    good();b.search[16]|=UINT64_C(1)<<56;b.call(1,1,0,0,2);
    good();b.search[16]-=UINT64_C(1)<<32;b.call(1,1,0,0,2); // Lost signal demand.
    good();b.search[57]^=1;b.call(1,1,0,0,2); // Incompatible bit assignment.
    good();b.search[73]^=UINT64_C(1)<<32;b.call(1,1,0,0,2);
    good();b.search[0]=1;b.call(1,1,0,0,2); // Failed result cannot carry a path.
    good();b.search[0]=1;b.search[7]=0;b.call(1,1,0,0,2); // Nor demands.
    good();b.search[7]=0;b.call(1,1,0,0,2); // Empty path to absent target.
    b.state(2,1,1,1);b.call(1,1,0,0,1); // Empty path cannot acquire demands.
    b.state(1,1,1,1);b.call(1,0,0,0,1);
    good();b.meta[4]=b.em[4]=UINT64_MAX;b.call(1,3,0,0,2); // Explicit saturation injection.
    b.meta[4]=b.em[4]=3;
    good();b.call(1,1,0,0,2,0,true);b.call(1,1,0,0,2,0,false,true);
    b.call(4,1);b.call(2,1,1);
    good();b.call(1,0,0,0,2);b.call(2,0);
    b.call(0,0,N,N-1);b.call(2,0);
    assert(b.transaction==50);
    std::cout<<"ROUTE_TREE_RTL_GOLDEN_PASS transactions=50 nodes=1048576 path=524288 full_depths=1\n";
}
