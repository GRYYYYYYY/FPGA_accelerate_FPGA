#include "search_snapshot_provider.hpp"
#include <cassert>
#include <cstdio>
struct StaticLimits {
    static constexpr unsigned nodes=4,degree=2,roots=4,unknown_pips=4,path=8,expansions=8;
    static constexpr unsigned signals=2,bits=2,values=2,slots=16,labels=8,heap=8;
};
struct StaticAdjacency {
    unsigned node_count()const{return 4;}
    fpga_search::RowStatus neighbors(uint32_t n,fpga_search::LabelEdge* row,unsigned,unsigned& count)const {
        count=0;
        if(n==0){row[0]={1,2,3,4,5,1,0};count=1;}
        else if(n==1){row[0]={2,2,7,8,9,0,0};count=1;}
        return fpga_search::RowStatus::known;
    }
};
using Provider=fpga_search::SearchSnapshotProvider<StaticLimits,StaticAdjacency,2,2,2,4,4,4>;
using Core=Provider::Core;
int main() {
    uint64_t heap[24]{},slots[16]{},records[80]{},unknown[1]{};
    Core::Key keys[8]{};fpga_search::LabelEdge edges[2]{};
    fpga_search::PipIdentity pips[4]{};fpga_search::PathEdge path[8]{};
    Core::Workspace w{heap,slots,records,unknown,keys,edges,pips,path,0,0};
    uint64_t forbidden[1]{},node_costs[8]={0,0,2,1,0,2,0,0};uint8_t pseudo[2]={0,1},blocked[2]{};
    uint64_t sem_keys[1]={(uint64_t(2)<<32)|3};Core::State requirements[1]{};
    requirements[0].signals.count=1;requirements[0].signals.data[0]=3;
    requirements[0].bits.count=1;requirements[0].bits.data[0]={4,1,1};
    requirements[0].values.count=1;requirements[0].values.data[0]={5,2};
    uint64_t owners[12]={3,9,0,0,(uint64_t(1)<<32)|4,9,1,0,(uint64_t(2)<<32)|5,9,0,3};
    uint64_t history[6]={3,2,(uint64_t(1)<<32)|4,3,(uint64_t(2)<<32)|5,5};
    uint64_t fixed[4]={(uint64_t(1)<<32)|4,0,1,1};
    StaticAdjacency adjacency;Provider provider(adjacency);
    Provider::View view{4,2,forbidden,node_costs,pseudo,blocked,nullptr,sem_keys,requirements,0,1,{owners,history,fixed,3,3,1},7,4};
    assert(provider.bind(view)==fpga_search::CostStatus::ok);uint32_t roots[1]={0};
    auto r=Core::run(provider,w,roots,1,2,{},8);
    assert(r.status==fpga_search::SearchStatus::found && r.cost==35 && r.path_length==2);
    assert(path[0].source==0 && path[0].edge.pip==3 && path[1].source==1 && path[1].edge.pip==7);
    assert(r.demands.signals.count==1 && r.demands.bits.count==1 && r.demands.values.count==1);
    view.semantics_count=0;assert(provider.bind(view)==fpga_search::CostStatus::ok);
    r=Core::run(provider,w,roots,1,2,{},8);
    assert(r.status==fpga_search::SearchStatus::unknown_site_semantics && r.unknown_pip_count==1 && pips[0].pip==3);
    view.semantics_count=1;fixed[3]=0;assert(provider.bind(view)==fpga_search::CostStatus::ok);
    r=Core::run(provider,w,roots,1,2,{},8);
    assert(r.status==fpga_search::SearchStatus::no_path && r.blocked==1);
    // Reject malformed metadata before a search can use stale bindings.
    auto bad=view;bad.forbidden=nullptr;assert(provider.bind(bad)==fpga_search::CostStatus::invalid && provider.node_count()==0);
    bad=view;bad.node_costs=nullptr;assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    bad=view;bad.requirements=nullptr;assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    bad=view;bad.protected_count=1;assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    pseudo[1]=2;assert(provider.bind(view)==fpga_search::CostStatus::invalid);pseudo[1]=1;
    blocked[1]=2;assert(provider.bind(view)==fpga_search::CostStatus::invalid);blocked[1]=0;
    uint64_t duplicate_keys[2]={sem_keys[0],sem_keys[0]};Core::State two_states[2]={requirements[0],requirements[0]};
    bad=view;bad.semantics_keys=duplicate_keys;bad.requirements=two_states;bad.semantics_count=2;
    assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    duplicate_keys[1]=0;assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    bad=view;two_states[0].signals.count=3;bad.requirements=two_states;
    assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    bad=view;bad.protected_pips=duplicate_keys;bad.protected_count=2;
    assert(provider.bind(bad)==fpga_search::CostStatus::invalid);
    assert(provider.bind(view)==fpga_search::CostStatus::ok);
    std::puts("SNAPSHOT_CXX14_COMPLETE_SEARCH_PASS transactions=3");
    std::puts("SNAPSHOT_METADATA_REJECTION_PASS");
}
