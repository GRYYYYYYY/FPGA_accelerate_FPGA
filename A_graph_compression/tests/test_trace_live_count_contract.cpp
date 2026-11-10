#include "search_trace_records.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

using Trace = fpga_search::SearchTraceRecords<512,8,16,8,8>;
int main() {
    uint64_t nm[4]{}, rm[6]{}, em[6]{}, sm[6]{}, tree[5]{}, demands[65]{};
    std::array<uint64_t,8> tm{}, result{{0,10,0,1,1,1,2,1}};
    std::vector<uint32_t> counts(8), flags(16), edges(16*18), roots{0,1};
    std::vector<uint64_t> history(8), keys(16), retained(32), owners(64), output(513,0xdeadbeef);
    assert(Trace::Node::reset(8,nm,counts.data(),history.data(),flags.data())==fpga_search::OccupancyStatus::ok);
    assert(Trace::Node::update(7,nullptr,0,roots.data(),2,nm,counts.data(),keys.data(),flags.data())==fpga_search::OccupancyStatus::ok);
    assert(Trace::Retained::reset(8,rm)==fpga_search::RetainedStatus::ok);
    assert(Trace::Edges::reset(8,em)==fpga_search::RetainedEdgeStatus::ok);
    assert(Trace::Site::reset(sm)==fpga_search::SiteOccupancyStatus::ok);
    tree[0]=Trace::Tree::Magic; tree[1]=8; tree[3]=2; tree[4]=2;
    auto invoke=[&]() {
        assert(Trace::Base::reset(512,tm.data())==0);
        return Trace::net(0,0,7,roots.data(),2,result.data(),demands,tree,nm,counts.data(),history.data(),keys.data(),flags.data(),rm,retained.data(),em,edges.data(),sm,owners.data(),tm.data(),output.data());
    };
    assert(nm[2]==2 && Trace::Node::valid_meta(nm));
    assert(invoke()==0 && output[7]==2);
    auto trusted=output; auto trusted_size=tm[2];
    // A range-valid but inconsistent external state is outside NodeOccupancy's
    // trusted-state contract. The existing writer nevertheless scans flags.
    nm[2]=0;
    assert(Trace::Node::valid_meta(nm));
    assert(invoke()==0 && output[7]==2 && tm[2]==trusted_size);
    for(unsigned i=0;i<tm[2];++i)if(i!=96)assert(output[i]==trusted[i]);
    assert(output[96]==0 && trusted[96]==2); // serialized node_meta[2]
    std::cout << "TRACE_LIVE_COUNT_CONTRACT_PASS trusted_live=2 inconsistent_meta=0 original_owned=2\n";
}
