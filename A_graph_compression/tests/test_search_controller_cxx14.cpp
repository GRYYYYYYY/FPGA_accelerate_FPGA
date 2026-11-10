#include "search_controller.hpp"
#include <cassert>
#include <cstdio>
struct Cxx14Limits {
    static constexpr unsigned nodes=4,degree=2,roots=4,unknown_pips=4,path=8,expansions=8;
    static constexpr unsigned signals=2,bits=2,values=2,slots=16,labels=8,heap=8;
};
using Core=fpga_search::SearchController<Cxx14Limits>;
struct Provider {
    bool unknown=false;
    unsigned node_count() const {return 4;}
    bool blocked_node(uint32_t) const {return false;}
    bool blocked(uint32_t,const fpga_search::LabelEdge&) const {return false;}
    fpga_search::RowStatus neighbors(uint32_t n,fpga_search::LabelEdge* row,unsigned,unsigned& count) const {
        count=0;
        if (n==0) {row[0]={1,2,3,4,5,6,1};count=1;}
        else if (n==1) {row[0]={2,2,7,8,9,10,0};count=1;}
        return fpga_search::RowStatus::known;
    }
    fpga_search::SemanticsStatus semantics(uint32_t,const fpga_search::LabelEdge&,Core::State& state) const {
        state={};state.signals.count=1;state.signals.data[0]=3;
        return unknown?fpga_search::SemanticsStatus::unknown:fpga_search::SemanticsStatus::verified;
    }
    bool compatible(const Core::State&) const {return true;}
    bool step_cost(uint32_t,const fpga_search::LabelEdge&,const Core::State&,const Core::State&,uint64_t& cost) const {cost=2;return true;}
};
int main() {
    uint64_t heap[24]{},slots[16]{},records[80]{},unknown[1]{};
    Core::Key keys[8]{};fpga_search::LabelEdge edges[2]{};
    fpga_search::PipIdentity pips[4]{};fpga_search::PathEdge path[8]{};
    Core::Workspace w{heap,slots,records,unknown,keys,edges,pips,path,0,0};
    uint32_t roots[1]={0};Provider provider;
    auto r=Core::run(provider,w,roots,1,2,{},8);
    assert(r.status==fpga_search::SearchStatus::found && r.cost==4 && r.expanded==2 && r.path_length==2);
    assert(path[0].source==0 && path[0].edge.pip==3 && path[0].edge.dir==1 && path[1].source==1 && path[1].edge.pip==7);
    assert(r.demands.signals.count==1 && r.demands.signals.data[0]==3);
    provider.unknown=true;r=Core::run(provider,w,roots,1,2,{},8);
    assert(r.status==fpga_search::SearchStatus::unknown_site_semantics && r.unknown_pip_count==1 && pips[0].tile==2 && pips[0].pip==3);
    assert(w.epoch==2);
    std::puts("CONTROLLER_CXX14_STATIC_PROVIDER_PASS");
}
