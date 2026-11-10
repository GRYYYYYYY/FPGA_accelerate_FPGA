// Independent37-transaction v2: first cases have one owner per node, proving the>1 threshold.
// Full declared depths on every call; v1 is preserved separately.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
extern "C" void search_round_control_top(const uint64_t*,const uint32_t*,const uint32_t*,uint64_t*);
constexpr unsigned N=1048576,Q=65536;
constexpr uint64_t G=UINT64_C(0xabcdef0123456789);
struct Bench{
    std::array<uint64_t,9> c{{N,Q,0,80,8,0,0,0,G}};
    std::vector<uint32_t> counts=std::vector<uint32_t>(N+1,0),flags=std::vector<uint32_t>(Q+1,1);
    unsigned tx=0;
    Bench(){std::fill(counts.begin(),counts.end()-1,1);counts.back()=flags.back()=0xdeadbeef;}
    static uint64_t penalty(uint64_t iteration,uint64_t cap){uint64_t p=1;for(unsigned i=0;i<20 && i<iteration;++i)p*=2;return std::min(p,cap);}
    void call(unsigned status=0){
        const auto input_c=c;const auto input_counts=counts,input_flags=flags;
        std::array<uint64_t,9> result{},expected{};result.fill(G);expected.back()=G;expected[0]=status;
        if(!status){
            uint64_t groups=std::count_if(counts.begin(),counts.begin()+c[0],[](uint32_t n){return n>=2;});
            uint64_t missing=std::count(flags.begin(),flags.begin()+c[1],0u);
            for(unsigned i=0;i<c[1];++i)assert(flags[i]<=1);
            const bool conflict=groups || c[5];unsigned action=!conflict && !missing?0:1;
            if(conflict && c[2]<c[3]-1)action=2;
            expected[1]=groups;expected[2]=missing;expected[3]=action;
            expected[4]=action==2?c[2]+1:0;expected[5]=action==2?penalty(c[2]+1,c[4]):0;
            expected[6]=conflict;expected[7]=penalty(c[2],c[4]);
        }
        search_round_control_top(c.data(),counts.data(),flags.data(),result.data());
        assert(c==input_c && counts==input_counts && flags==input_flags && result==expected);
        std::cout<<"ROUND_RTL_TX "<<tx++;
        for(unsigned i=0;i<8;++i)std::cout<<' '<<result[i];
        std::cout<<'\n';
    }
};
int main(){
    Bench b;b.call();b.flags[Q-1]=0;b.call();b.counts[0]=2;b.call();
    b.c[2]=79;b.call();std::fill(b.counts.begin(),b.counts.end()-1,2);b.c[2]=0;b.call();
    std::fill(b.counts.begin(),b.counts.end()-1,0);std::fill(b.flags.begin(),b.flags.end()-1,1);b.c[5]=65536;b.call();
    b.c[5]=0;b.call();b.c[2]=19;b.c[4]=UINT64_MAX;b.c[5]=1;b.call();
    b.c[2]=20;b.call();b.c[2]=21;b.call();b.c[2]=UINT32_MAX-1;b.c[3]=UINT32_MAX;b.call();
    b.c[2]=0;b.c[3]=1;b.call();b.c[5]=0;b.c[4]=1;b.call();b.flags[Q-1]=0;b.call();
    b.c={{64,4,0,2,3,0,0,0,G}};b.call();b.flags[3]=2;b.call(1);b.flags[3]=1;b.call();
    const auto good=b.c;
    auto reject=[&](unsigned status){b.call(status);b.c=good;};
    b.c[0]=N+1;reject(2);b.c[1]=Q+1;reject(2);b.c[5]=65537;reject(2);
    b.c[0]=0;reject(1);b.c[1]=0;reject(1);b.c[3]=0;reject(1);b.c[2]=b.c[3];reject(1);b.c[4]=0;reject(1);
    b.c[2]=UINT64_C(1)<<32;reject(1);b.c[3]=UINT64_C(1)<<32;reject(1);b.c[6]=1;reject(1);b.c[7]=1;reject(1);
    b.counts[63]=3;b.flags[3]=0;b.call();b.c[2]=1;b.call();b.counts[63]=0;b.call();b.flags[3]=1;b.call();
    b.c[4]=100;b.call();b.counts[1000]=UINT32_MAX;b.flags[Q-1]=7;b.call();
    b.c={{N,Q,0,80,8,0,0,0,G}};b.call(1);b.counts[1000]=0;b.flags[Q-1]=1;b.call();
    assert(b.tx==37);std::cout<<"ROUND_RTL_GOLDEN_PASS transactions=37 nodes=1048576 nets=65536 full_depths=1 readonly=1\n";
}
