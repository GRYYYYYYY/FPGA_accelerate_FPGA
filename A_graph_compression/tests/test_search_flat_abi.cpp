#include "search_controller_flat.hpp"
#include <cassert>
#include <cstdio>
struct L {
    static constexpr unsigned nodes=4,degree=2,roots=4,unknown_pips=4,path=8,expansions=8;
    static constexpr unsigned signals=2,bits=2,values=2,slots=16,labels=8,heap=8;
};
using Core=fpga_search::FlatSearchController<L>;
struct Provider {
    unsigned node_count()const{return 4;}
    bool blocked_node(uint32_t)const{return false;}
    bool blocked(uint32_t,const fpga_search::LabelEdge&)const{return false;}
    bool compatible(const Core::State&)const{return true;}
    bool step_cost(uint32_t,const fpga_search::LabelEdge&,const Core::State&,const Core::State&,uint64_t& cost)const{cost=1;return true;}
    fpga_search::SemanticsStatus semantics(uint32_t,const fpga_search::LabelEdge&,Core::State& out)const{out={};return fpga_search::SemanticsStatus::verified;}
    fpga_search::RowStatus neighbors(uint32_t n,fpga_search::LabelEdge* e,unsigned,unsigned& count)const{
        count=n<3?1:0;if(count)e[0]={n+1,10+n,20+n,30+n,40+n,50+n,n%2};return fpga_search::RowStatus::known;
    }
};
int main(){
    uint64_t heap[24]{},slots[16]{},records[80]{},unknown[1]{},keys[8*Core::Index::Storage::Words]{};
    fpga_search::LabelEdge edges[2]{};uint64_t pips[6];uint32_t path[66];
    for(auto& v:pips)v=0xaabbccddeeff0123ULL;
    for(auto& v:path)v=0xabcdef01u;
    Core::Workspace w{heap,slots,records,unknown,keys,edges,pips+1,path+1,0,0};
    Provider provider;uint32_t roots[1]={0};auto r=Core::run(provider,w,roots,1,3,{},8);
    assert(r.status==fpga_search::SearchStatus::found && r.path_length==3 && r.cost==3);
    const uint32_t literal[24]={0,1,10,20,30,40,50,0,1,2,11,21,31,41,51,1,2,3,12,22,32,42,52,0};
    for(unsigned i=0;i<24;++i)assert(path[i+1]==literal[i]);
    assert(path[0]==0xabcdef01u);for(unsigned i=25;i<66;++i)assert(path[i]==0xabcdef01u);
    Core::Result evidence;
    assert(Core::add_unknown_pip(w,evidence,{UINT32_MAX,0}));
    assert(Core::add_unknown_pip(w,evidence,{0,UINT32_MAX}));
    assert(Core::add_unknown_pip(w,evidence,{1,0}));
    assert(Core::add_unknown_pip(w,evidence,{0,0}));
    assert(evidence.unknown_pip_count==4);
    const uint64_t expected[4]={0,0xffffffffULL,0x100000000ULL,0xffffffff00000000ULL};
    for(unsigned i=0;i<4;++i)assert(pips[i+1]==expected[i]);
    assert(Core::add_unknown_pip(w,evidence,{0,UINT32_MAX}));
    assert(!Core::add_unknown_pip(w,evidence,{UINT32_MAX,UINT32_MAX}));
    assert(evidence.unknown_pip_count==4);
    for(unsigned i=0;i<4;++i)assert(pips[i+1]==expected[i]);
    assert(pips[0]==0xaabbccddeeff0123ULL && pips[5]==pips[0]);
    w.epoch=UINT32_MAX;r=Core::run(provider,w,roots,1,0,{},8);
    assert(r.status==fpga_search::SearchStatus::found && r.path_length==0 && r.unknown_pip_count==0 && w.epoch==1);
    for(unsigned i=0;i<24;++i)assert(path[i+1]==literal[i]);
    std::puts("FLAT_LITERAL_ABI_PASS path_words=24 pip_words=4 guards=pass epoch_wrap=pass");
}
