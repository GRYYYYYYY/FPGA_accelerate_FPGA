#include "search_trace_v2.hpp"
#include <array>
#include <fstream>
#include <vector>
#include <cassert>
using T=fpga_search::SearchTraceV2<512>;
int main(int argc,char** argv){
    assert(argc==2);std::array<uint64_t,8> m{};std::vector<uint64_t> data(512),r(81);uint32_t roots[2]={0,2};
    uint32_t path[16]={0,1,UINT32_MAX,7,1,2,0xabcdef01,1,1,65,0,8,2,3,UINT32_MAX,0};uint64_t unknown[2]={8,1},pips[1]={(UINT64_C(0xffffffff)<<32)|11};
    r[0]=0;r[1]=35;r[7]=2;r[8]=2;r[9]=1;r[15]=1;r[16]=65;
    assert(T::reset(512,m.data())==0 && T::search(4,7,65,66,roots,2,r.data(),path,unknown,pips,m.data(),data.data())==0);
    r.assign(81,0);r[0]=6;r[15]=1;
    assert(T::search(4,8,65,66,roots,1,r.data(),nullptr,unknown,pips,m.data(),data.data())==0);
    std::ofstream out(argv[1],std::ios::binary);assert(out);
    auto put=[&](uint64_t w){for(unsigned b=0;b<8;++b)out.put(char((w>>(8*b))&255));};
    for(auto w:m){put(w);}
    for(unsigned i=0;i<m[2];++i){put(data[i]);}
    out.close();assert(out);
}
