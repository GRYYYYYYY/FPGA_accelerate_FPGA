#include "search_trace.hpp"
#include <array>
#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>
using T=fpga_search::SearchTrace<512>;
int main(){
    constexpr uint64_t G=UINT64_C(0xdeadbeef01234567);
    std::array<uint64_t,9> m{};m.back()=G;std::vector<uint64_t> out(513,G),r(81);r[0]=0;r[1]=35;r[2]=2;r[4]=r[5]=3;r[7]=2;r[8]=2;r[9]=1;r[10]=3;r[11]=r[12]=r[13]=1;r[14]=3;r[15]=1;r[16]=65;r[17]=1;r[20]=9;
    uint32_t roots[2]={0,2},path[16]={0,1,UINT32_MAX,7,1,2,0xabcdef01,1,1,65,0,8,2,3,UINT32_MAX,0};uint64_t unknown[2]={8,1},pips[1]={(UINT64_C(0xffffffff)<<32)|11};
    auto call=[&](){return T::search(4,7,65,66,roots,2,r.data(),path,unknown,pips,m.data(),out.data());};
    assert(T::reset(512,m.data())==0 && call()==0 && m[2]==101 && m[3]==1 && m[5]==2);
    std::vector<uint64_t> expected={1,101,4,7,65,2,2,1};expected.insert(expected.end(),r.begin(),r.end());expected.push_back(UINT64_C(2)<<32);
    const uint64_t packed_path[8]={UINT64_C(0x0000000100000000),UINT64_C(0x00000007ffffffff),UINT64_C(0x0000000200000001),UINT64_C(0x00000001abcdef01),UINT64_C(0x0000004100000001),UINT64_C(0x0000000800000000),UINT64_C(0x0000000300000002),UINT64_C(0x00000000ffffffff)};
    expected.insert(expected.end(),packed_path,packed_path+8);expected.push_back(3);expected.push_back(64);expected.push_back(pips[0]);
    assert(expected.size()==101 && std::equal(expected.begin(),expected.end(),out.begin()));
    assert(std::all_of(out.begin()+101,out.end(),[](uint64_t v){return v==G;}));
    auto old=out;const auto oldr=r;r[8]=3;assert(call()==1 && out==old && m[2]==101 && m[3]==1);r=oldr;
    assert(call()==1 && out==old); // Sticky failure cannot be silently cleared.
    assert(T::reset(100,m.data())==0 && call()==2 && out==old && !m[2] && !m[3]);
    r[8]=3;assert(call()==2 && out==old);r[8]=2;
    assert(T::reset(512,m.data())==0);m[5]=UINT64_MAX;assert(call()==3 && out==old && !m[2]);
    assert(T::reset(512,m.data())==0);roots[0]=65;roots[1]=0;assert(call()==1 && out==old);roots[0]=0;roots[1]=2;
    assert(T::reset(512,m.data())==0);unknown[1]=8;assert(call()==1 && out==old);unknown[1]=1;
    assert(T::reset(512,m.data())==0);path[15]=2;assert(call()==1 && out==old);path[15]=0;
    assert(T::reset(512,m.data())==0 && call()==0);r.assign(81,0);r[0]=1;r[15]=1;uint64_t empty[2]{};
    assert(T::search(4,8,65,66,roots,1,r.data(),path,empty,pips,m.data(),out.data())==0);
    assert(m[2]==191 && m[3]==2 && m[5]==3 && m.back()==G && out.back()==G && out[101]==1 && out[102]==90 && out[190]==0);
    {
        using Production=fpga_search::SearchTrace<>;std::array<uint64_t,9> pm{};pm.back()=G;
        std::vector<uint64_t> production(16777217,G);r=oldr;
        assert(Production::reset(16777216,pm.data())==0);
        assert(Production::search(4,7,65,66,roots,2,r.data(),path,unknown,pips,pm.data(),production.data())==0);
        assert(pm[2]==101 && pm[3]==1 && pm.back()==G && std::equal(expected.begin(),expected.end(),production.begin()));
        assert(std::all_of(production.begin()+101,production.end(),[](uint64_t v){return v==G;}));
    }
    std::cout<<"SEARCH_TRACE_CPU_PASS exact_search_fields=1 frames=2 rejected=6 guards=1 sticky=1 production_words=16777216\n";
}
