#include <stdint.h>
#include <iostream>
#include <functional>
#include <queue>
#include <tuple>
#include <vector>
#include <random>
extern "C" void search_heap_top(const uint64_t*,uint64_t*,unsigned);
int main() {
    using T=std::tuple<uint64_t,uint64_t,uint64_t>;
    std::mt19937_64 random(20261024);
    for(unsigned batch=0;batch<2;++batch) {
        std::vector<uint64_t> input(4096*4),output(4096*5,0xdeadbeef),expected(4096*5);
        std::priority_queue<T,std::vector<T>,std::greater<T>> oracle;
        for(unsigned i=0;i<4096;++i) {
            // First batch fills, overflows, drains, underflows, then mixes.
            unsigned op=batch?unsigned(random()%4):(i<1100?1:i<2200?2:unsigned(random()%4));
            uint64_t cost=i%13==0?UINT64_MAX:random()%17,serial=random()%31,label=random()%23;
            input[4*i]=op;input[4*i+1]=cost;input[4*i+2]=serial;input[4*i+3]=label;
            bool ok=false;T value{0,0,0};
            if(op==1 && oracle.size()<1023) {oracle.emplace(cost,serial,label);ok=true;}
            if(op==2 && !oracle.empty()) {value=oracle.top();oracle.pop();ok=true;}
            expected[5*i]=ok;expected[5*i+1]=oracle.size();expected[5*i+2]=std::get<0>(value);
            expected[5*i+3]=std::get<1>(value);expected[5*i+4]=std::get<2>(value);
        }
        search_heap_top(input.data(),output.data(),4096);
        if(output!=expected) {std::cerr<<"HEAP_TOP_MISMATCH batch="<<batch<<'\n';return 1;}
        std::cout<<"HEAP_TOP_BATCH_PASS "<<batch<<" operations=4096\n";
    }
    std::cout<<"HEAP_TOP_ALL_PASS\n";
    return 0;
}
