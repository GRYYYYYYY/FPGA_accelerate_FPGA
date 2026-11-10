#include "search_round_trace.hpp"
#include "search_round_control.hpp"
#include <array>
#include <cassert>
#include <fstream>
#include <vector>
using T=fpga_search::RoundTrace<512,4,8,4>;
int main(int argc,char** argv){
    assert(argc==2);uint64_t c[8]={4,2,0,1,8,1,0,0},r[8]{},nm[4]{},sm[6]{},m[8]{},summary[16]{};
    uint32_t counts[4]={1,3,0,2},complete[2]={1,1},flags[8]{};
    uint64_t hist[4]={0,9,0,4},owners[64]{},sh[32]{};
    // Explicit valid state with three owners of signal3; no fake execution history.
    nm[0]=T::Node::Magic;nm[1]=4;nm[2]=6;nm[3]=7;
    assert(T::Site::reset(sm)==fpga_search::SiteOccupancyStatus::ok);
    const uint64_t req[3]={3,0,0};
    for(unsigned net=1;net<=3;++net)assert(T::Site::replace(net,req,1,sm,owners)==fpga_search::SiteOccupancyStatus::ok);
    unsigned groups=0;assert(T::Site::analyze(sm,owners,flags,summary,groups)==fpga_search::SiteOccupancyStatus::ok && groups==1);
    fpga_search::RoundControl<4,4>::run(c,counts,complete,r);
    assert(r[3]==1 && r[6]==1); // Last conflict round still advances.
    std::vector<uint64_t> data(513,0xdeadbeef);
    assert(T::Base::reset(512,m)==0);
    auto write=[&](unsigned phase){return T::write(phase,c,r,complete,nm,counts,hist,sm,owners,sh,groups,summary,m,data.data());};
    assert(write(0)==0 && m[2]==65);
    uint64_t ng=0;assert(T::Node::advance(nm,counts,hist,ng)==fpga_search::OccupancyStatus::ok && ng==2);
    assert(T::Site::advance(sm,owners,sh,flags,summary,groups)==fpga_search::SiteOccupancyStatus::ok);
    assert(write(1)==0 && m[2]==132 && data.back()==0xdeadbeef);
    std::array<uint64_t,8> pair_meta{};for(unsigned i=0;i<8;++i)pair_meta[i]=m[i];
    auto old=data;assert(T::Base::reset(64,m)==0 && write(0)==2 && data==old && m[2]==0);
    assert(T::Base::reset(512,m)==0 && write(1)==0);
    // Emit the original pre/post pair, retaining metadata from its two commits.
    data=old;for(unsigned i=0;i<8;++i)m[i]=pair_meta[i];
    std::ofstream out(argv[1],std::ios::binary);
    auto put=[&](uint64_t w){for(unsigned b=0;b<8;++b)out.put(char(w>>(8*b)));};
    for(auto w:m)put(w);
    for(unsigned i=0;i<m[2];++i)put(data[i]);
    out.close();assert(out);
}
