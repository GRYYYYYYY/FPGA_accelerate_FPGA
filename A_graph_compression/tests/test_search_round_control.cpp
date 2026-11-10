#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
extern "C" void search_round_control_top(const uint64_t*,const uint32_t*,const uint32_t*,uint64_t*);
constexpr uint64_t G=UINT64_C(0xabcdef0123456789);
int main(){
    std::vector<uint32_t> counts(1048577,0xdeadbeef),complete(65537,0xdeadbeef);
    std::array<uint64_t,9> c{{64,16,0,8,8,0,0,0,G}},result{};
    std::mt19937 rng(0x41524f55);unsigned rejected=0;
    auto penalty=[](uint64_t i,uint64_t cap){uint64_t p=1;for(uint64_t k=0;k<i && k<20;++k)p*=2;return std::min(p,cap);};
    auto call=[&](unsigned status){
        const auto cc=c;const auto old_counts=counts,old_complete=complete;result.fill(G);
        search_round_control_top(c.data(),counts.data(),complete.data(),result.data());
        assert(c==cc && counts==old_counts && complete==old_complete && result.back()==G && result[0]==status);
        if(status){for(unsigned i=1;i<8;++i)assert(result[i]==0);++rejected;return;}
        uint64_t node_groups=std::count_if(counts.begin(),counts.begin()+c[0],[](uint32_t n){return n>=2;});
        uint64_t missing=std::count(complete.begin(),complete.begin()+c[1],0u);
        bool conflict=node_groups || c[5];unsigned action=!conflict && !missing?0:1;
        if(conflict && c[2]<c[3]-1)action=2;
        assert(result[1]==node_groups && result[2]==missing && result[3]==action && result[6]==conflict && result[7]==penalty(c[2],c[4]));
        assert(result[4]==(action==2?c[2]+1:0) && result[5]==(action==2?penalty(c[2]+1,c[4]):0));
    };
    for(unsigned trial=0;trial<3000;++trial){
        c={{1+rng()%64,1+rng()%16,rng()%8,8,1+rng()%33,rng()%3,0,0,G}};
        for(unsigned i=0;i<c[0];++i)counts[i]=rng()%5;
        for(unsigned i=0;i<c[1];++i)complete[i]=rng()%2;
        call(0);
    }
    std::fill(counts.begin(),counts.end()-1,0);std::fill(complete.begin(),complete.end()-1,1);
    c={{1048576,65536,0,80,8,0,0,0,G}};call(0);assert(result[3]==0 && result[6]==0);
    complete[65535]=0;call(0);assert(result[3]==1 && result[6]==0);
    for(unsigned i=0;i<1048576;++i)counts[i]=2;
    c[2]=79;call(0);assert(result[1]==1048576 && result[3]==1 && result[6]==1);
    for(uint64_t i:{UINT64_C(19),UINT64_C(20),UINT64_C(21),UINT64_C(4294967294)}){c[2]=i;c[3]=UINT32_MAX;c[4]=UINT64_MAX;call(0);}
    auto good=c;
    auto reject=[&](unsigned status){call(status);c=good;};
    c[0]=1048577;reject(2);c[1]=65537;reject(2);c[5]=65537;reject(2);
    c[0]=0;reject(1);c[1]=0;reject(1);c[3]=0;reject(1);c[2]=c[3];reject(1);c[4]=0;reject(1);
    c[2]=UINT64_C(1)<<32;reject(1);c[3]=UINT64_C(1)<<32;reject(1);c[6]=1;reject(1);c[7]=1;reject(1);
    complete[65535]=2;call(1);complete[65535]=0;
    assert(rejected==13);
    std::cout<<"ROUND_CONTROL_CPU_PASS random=3000 nodes=1048576 nets=65536 rejected=13 final_conflict_advances=1 input_immutable=1\n";
}
