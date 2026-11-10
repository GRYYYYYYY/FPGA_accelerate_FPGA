#include "search_trace_records.hpp"
#include <array>
#include <cassert>
#include <fstream>
#include <vector>
using T=fpga_search::SearchTraceRecords<512,8,16,8,8>;
int main(int argc,char** argv){
    assert(argc==2);std::array<uint64_t,8> tm{},result{{0,10,0,1,1,1,2,1}};uint64_t nm[4]{},rm[6]{},em[6]{},sm[6]{},tree[5]{},demands[65]{};
    std::vector<uint32_t> counts(8),flags(16),edge(16*18),roots{0,1};std::vector<uint64_t> history(8),keys(16),retained(32),owners(64),data(513,0xdeadbeef);
    assert(T::Node::reset(8,nm,counts.data(),history.data(),flags.data())==fpga_search::OccupancyStatus::ok);
    assert(T::Node::update(7,nullptr,0,roots.data(),2,nm,counts.data(),keys.data(),flags.data())==fpga_search::OccupancyStatus::ok);
    assert(T::Retained::reset(8,rm)==fpga_search::RetainedStatus::ok);
    assert(T::Retained::replace(7,roots.data(),2,rm,retained.data())==fpga_search::RetainedStatus::ok);
    assert(T::Edges::reset(8,em)==fpga_search::RetainedEdgeStatus::ok);uint32_t path[8]={0,1,9,11,2,3,4,1};
    assert(T::Edges::update(7,path,1,false,em,edge.data())==fpga_search::RetainedEdgeStatus::ok);
    assert(T::Site::reset(sm)==fpga_search::SiteOccupancyStatus::ok);uint64_t request[9]={3,0,0,(UINT64_C(1)<<32)|4,1,1,(UINT64_C(2)<<32)|5,0,2};
    assert(T::Site::replace(7,request,3,sm,owners.data())==fpga_search::SiteOccupancyStatus::ok);
    tree[0]=fpga_search::ProductionRouteTree::Magic;tree[1]=8;tree[2]=0;tree[3]=2;tree[4]=2;
    demands[0]=(UINT64_C(1)<<32)|(UINT64_C(1)<<40)|(UINT64_C(1)<<48);demands[1]=3;demands[17]=4;demands[25]=1;demands[41]=1;demands[57]=(UINT64_C(2)<<32)|5;
    auto invoke=[&](){return T::net(0,0,7,roots.data(),2,result.data(),demands,tree,nm,counts.data(),history.data(),keys.data(),flags.data(),rm,retained.data(),em,edge.data(),sm,owners.data(),tm.data(),data.data());};
    assert(T::Base::reset(512,tm.data())==0 && invoke()==0 && tm[2]==140 && tm[3]==1);
    auto before=data;assert(T::Base::reset(139,tm.data())==0 && invoke()==2 && data==before && !tm[2]);
    assert(T::Base::reset(512,tm.data())==0 && invoke()==0 && data.back()==0xdeadbeef);
    std::ofstream out(argv[1],std::ios::binary);auto put=[&](uint64_t w){for(unsigned b=0;b<8;++b){out.put(char((w>>(8*b))&255));}};
    for(auto v:tm){put(v);}for(unsigned i=0;i<tm[2];++i){put(data[i]);}out.close();assert(out);
}
