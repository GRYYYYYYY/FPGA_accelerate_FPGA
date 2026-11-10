#include "search_heap_external.hpp"
#include <algorithm>
#include <cassert>
#include <iostream>
#include <queue>
#include <random>
#include <tuple>
#include <vector>
extern "C" void search_heap_external_top(uint64_t*,uint64_t*,const uint64_t*,uint64_t*,unsigned);
using Tuple=std::tuple<uint64_t,uint64_t,uint64_t>;
using Oracle=std::priority_queue<Tuple,std::vector<Tuple>,std::greater<Tuple>>;
static constexpr unsigned capacity=131072;
static constexpr uint64_t guard=0xdeadbeef12345678ULL;
static void check(bool ok,const char* reason) {if (!ok) {std::cerr<<"EXTERNAL_HEAP_MISMATCH "<<reason<<'\n';std::exit(1);}}
int main() {
    static_assert(capacity==fpga_search::ExternalHeapCapacity,"test capacity mismatch");
    std::vector<uint64_t> backing(3*capacity+2,guard),commands(4*4096),responses(5*4096);
    uint64_t* heap=backing.data()+1;uint64_t meta[2]={0,99};Oracle oracle;std::mt19937_64 rng(20261024);
    auto seed=[&](unsigned count) {
        oracle=Oracle{};meta[0]=count;meta[1]=99;
        std::fill(heap,heap+3*capacity,guard);
        for (unsigned i=0;i<count;++i) {
            // Sorted tuples form a valid heap independently of tested push.
            Tuple t{1000+i/3,i%3,uint64_t(i)*0x100000001ULL};
            heap[3*i]=std::get<0>(t);heap[3*i+1]=std::get<1>(t);heap[3*i+2]=std::get<2>(t);oracle.push(t);
        }
    };
    for (unsigned batch=0;batch<7;++batch) {
        if (batch==0) seed(0);
        if (batch==1) seed(73388);
        // batch 2 resumes the exact external state produced by batch 1.
        if (batch==3) seed(capacity);
        if (batch==4) meta[0]=uint64_t(capacity)+1;
        if (batch==5) meta[0]=oracle.size();
        unsigned operations=batch<3?4096:batch==3?128:batch==4?8:batch==5?4097:0;
        const uint64_t initial=meta[0];const auto old_heap=backing;
        std::fill(responses.begin(),responses.end(),guard);auto expected=responses;
        for (unsigned i=0;i<std::min(operations,4096u);++i) {
            unsigned op=batch==3?(i%2?2:1):unsigned(rng()%4);
            if (batch==0 && i==0) op=2;
            uint64_t cost=i%17==0?UINT64_MAX:rng()%2000,serial=rng()%13,label=rng();
            commands[4*i]=op;commands[4*i+1]=cost;commands[4*i+2]=serial;commands[4*i+3]=label;
            if (batch==4 || batch==5) continue;
            bool ok=false;Tuple out{0,0,0};
            if (op==1 && oracle.size()<capacity) {oracle.emplace(cost,serial,label);ok=true;}
            if (op==2 && !oracle.empty()) {out=oracle.top();oracle.pop();ok=true;}
            expected[5*i]=ok;expected[5*i+1]=oracle.size();expected[5*i+2]=std::get<0>(out);
            expected[5*i+3]=std::get<1>(out);expected[5*i+4]=std::get<2>(out);
        }
        search_heap_external_top(heap,meta,commands.data(),responses.data(),operations);
        check(responses==expected,"responses");check(backing.front()==guard && backing.back()==guard,"heap guards");
        if (batch==4 || batch==5) {
            check(meta[0]==initial && meta[1]==(batch==4?1u:2u),"rejected metadata");check(backing==old_heap,"rejected heap changed");
        } else {
            check(meta[0]==oracle.size() && meta[1]==0,"final metadata");
            std::vector<Tuple> actual;actual.reserve(meta[0]);
            for (unsigned i=0;i<meta[0];++i) {
                actual.emplace_back(heap[3*i],heap[3*i+1],heap[3*i+2]);
                if (i) check(actual[(i-1)/2]<=actual[i],"heap order");
            }
            std::sort(actual.begin(),actual.end());auto remaining=oracle;
            for (auto t:actual) {check(!remaining.empty() && t==remaining.top(),"active entries");remaining.pop();}
            check(remaining.empty(),"missing entries");
            // No valid operation may reach a never-used slot beyond its largest possible count.
            unsigned limit=unsigned(initial)+operations;if (limit>capacity) limit=capacity;
            for (unsigned i=3*limit;i<3*capacity;++i) check(heap[i]==old_heap[i+1],"inactive tail changed");
        }
        std::cout<<"EXTERNAL_HEAP_BATCH_PASS "<<batch<<" initial="<<initial<<" operations="<<operations<<" final="<<meta[0]<<" status="<<meta[1]<<'\n';
    }
    std::cout<<"EXTERNAL_HEAP_ALL_PASS\n";
}
