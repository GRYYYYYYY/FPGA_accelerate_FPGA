// Full-depth37-transaction oracle; no DUT header/helper is included.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>
extern "C" void search_retained_nodes_top(const uint64_t*,uint64_t*,uint64_t*,const uint32_t*,uint32_t*,uint64_t*);
constexpr unsigned N=1048576,P=2097152;
constexpr uint64_t G=UINT64_C(0x123456789abcdef0),Magic=UINT64_C(0x415245544e4f4431);
struct Bench{
    std::vector<uint64_t> meta=std::vector<uint64_t>(7,G),rows=std::vector<uint64_t>(2*P+1,G),em=meta,er=rows;
    std::vector<uint32_t> nodes=std::vector<uint32_t>(N+1,0xdeadbeef),output=std::vector<uint32_t>(N+1,0xdeadbeef),eo=output;
    std::map<uint32_t,std::vector<uint32_t>> nets;
    unsigned tx=0;
    void full(){for(unsigned i=0;i<N;++i)nodes[i]=i;}
    void call(unsigned op,uint32_t net,unsigned reset,unsigned count,unsigned status,bool reserved=false,bool wide=false){
        std::array<uint64_t,9> c{{op,net,reset,count,0,0,0,0,G}};
        if(reserved)c[4]=1;
        if(wide)c[1]=UINT64_C(1)<<32;
        auto original_c=c;const auto original_nodes=nodes;std::array<uint64_t,6> result{{G,G,G,G,G,G}};
        unsigned returned=0;
        if(!status){
            if(op==0){nets.clear();em[0]=Magic;em[1]=reset;em[2]=0;em[3]=0;em[4]=0;em[5]=1;}
            if(op==1){
                assert(count<=em[1] && std::is_sorted(nodes.begin(),nodes.begin()+count));
                for(unsigned i=0;i<count;++i)assert(nodes[i]<em[1] && (!i || nodes[i]>nodes[i-1]));
                if(count)nets[net]=std::vector<uint32_t>(nodes.begin(),nodes.begin()+count);else nets.erase(net);
                unsigned at=0;const unsigned dst=(1-unsigned(em[3]))*P;
                for(const auto& route:nets)for(auto node:route.second)er[dst+at++]=(uint64_t(route.first)<<32)|node;
                assert(at<=P && nets.size()<=65536);em[2]=at;em[3]=1-em[3];em[4]=nets.size();++em[5];
            }
            if(op==2){auto it=nets.find(net);if(it!=nets.end()){returned=it->second.size();std::copy(it->second.begin(),it->second.end(),eo.begin());}}
        }
        search_retained_nodes_top(c.data(),meta.data(),rows.data(),nodes.data(),output.data(),result.data());
        assert(c==original_c && nodes==original_nodes && meta==em && rows==er && output==eo && result.back()==G);
        std::array<uint64_t,6> expected{{status,status?0:em[2],status?0:em[4],status?0:em[5],returned,G}};
        assert(result==expected);
        std::cout<<"RETAINED_RTL_TX "<<tx++<<' '<<op;
        for(unsigned i=0;i<5;++i)std::cout<<' '<<result[i];
        std::cout<<'\n';
    }
    void seed_nets(){
        // A valid boundary injected explicitly, not65536 preceding updates.
        nets.clear();meta[2]=em[2]=meta[4]=em[4]=65536;
        for(unsigned i=0;i<65535;++i){nets[i]={0};rows[i]=er[i]=uint64_t(i)<<32;}
        nets[UINT32_MAX]={0};rows[65535]=er[65535]=uint64_t(UINT32_MAX)<<32;
    }
};
int main(){
    Bench b;b.call(0,0,N,0,0);b.full();
    b.call(1,0,0,N,0);b.call(1,UINT32_MAX,0,N,0);
    b.call(2,UINT32_MAX,0,0,0);b.call(2,1,0,0,0);b.call(1,1,0,1,2);b.call(2,0,0,0,0);
    b.call(1,0,0,0,0);b.call(1,1,0,N,0);b.call(1,1,0,N+1,2);
    b.nodes[1]=0;b.call(1,1,0,2,1);b.nodes[0]=N;b.call(1,1,0,1,1);
    b.meta[5]=b.em[5]=UINT64_MAX;b.call(1,1,0,0,3);b.meta[5]=b.em[5]=5;
    b.call(1,1,0,0,1,true);b.call(1,1,0,0,1,false,true);
    b.call(0,0,N+1,0,2);b.call(0,0,0,0,1);b.call(0,0,64,0,0);
    b.nodes[0]=0;b.nodes[1]=63;b.call(1,UINT32_MAX,0,2,0);b.call(2,UINT32_MAX,0,0,0);
    b.nodes[0]=1;b.call(1,0,0,1,0);b.call(2,42,0,0,0);
    b.nodes[0]=3;b.call(1,UINT32_MAX,0,1,0);b.call(2,0,0,0,0);
    b.call(1,0,0,0,0);b.call(2,0,0,0,0);b.call(0,0,64,0,0);
    b.seed_nets();b.nodes[0]=0;b.call(1,65535,0,1,2);b.call(2,UINT32_MAX,0,0,0);
    b.nodes[0]=63;b.call(1,UINT32_MAX,0,1,0);b.call(2,UINT32_MAX,0,0,0);
    b.call(1,0,0,0,0);b.nodes[0]=2;b.call(1,65535,0,1,0);b.call(2,65535,0,0,0);
    b.call(3,0,0,0,1);b.call(0,0,64,0,0);b.call(2,UINT32_MAX,0,0,0);
    assert(b.tx==37);std::cout<<"RETAINED_RTL_GOLDEN_PASS transactions=37 pairs=2097152 seeded_nets=65536 full_depths=1\n";
}
