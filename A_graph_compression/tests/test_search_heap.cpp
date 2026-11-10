#include "../hardware/vitis/search_heap.hpp"
#include <array>
#include <cassert>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <random>
#include <tuple>
#include <vector>

using E = fpga_search::Entry;
using T = std::tuple<uint64_t,uint64_t,uint64_t>;
T tuple(E e) { return {e.cost,e.serial,e.label}; }
template<unsigned N> void exercise() {
    std::array<E,N+2> storage{};
    const E guard{91,92,93};storage[0]=guard;storage[N+1]=guard;
    E* data=storage.data()+1;unsigned count=0;
    std::priority_queue<T,std::vector<T>,std::greater<T>> reference;
    std::mt19937_64 rng(20261024+N);
    for (unsigned i=0;i<100000;++i) {
        if (rng()%3) {
            E e{rng()%17,rng()%31,rng()%101};
            if (i%13==0) e.cost=std::numeric_limits<uint64_t>::max();
            const auto before=storage;
            bool ok=fpga_search::Heap<N>::push(data,count,e);
            assert(ok==(reference.size()<N));
            if(ok) reference.push(tuple(e));
            else for(unsigned j=0;j<N+2;++j) assert(tuple(storage[j])==tuple(before[j]));
        } else {
            E e=guard;bool ok=fpga_search::Heap<N>::pop(data,count,e);
            assert(ok==!reference.empty());
            if(ok) {assert(tuple(e)==reference.top());reference.pop();}
            else assert(tuple(e)==tuple(guard));
        }
        assert(count==reference.size());
        assert(tuple(storage[0])==tuple(guard)&&tuple(storage[N+1])==tuple(guard));
    }
    while(!reference.empty()) {
        E e{};assert(fpga_search::Heap<N>::pop(data,count,e));
        assert(tuple(e)==reference.top());reference.pop();
    }
    count=N+1;E result=guard;const auto before=storage;
    assert(!fpga_search::Heap<N>::push(data,count,guard));
    assert(!fpga_search::Heap<N>::pop(data,count,result));
    assert(count==N+1&&tuple(result)==tuple(guard));
    for(unsigned j=0;j<N+2;++j) assert(tuple(storage[j])==tuple(before[j]));
}
int main() {
    exercise<1>();exercise<2>();exercise<3>();exercise<17>();exercise<256>();exercise<1023>();
    std::cout<<"SEARCH_HEAP_PASS randomized_operations=600000 capacities=6 ordering=cost_serial_label overflow_atomic=pass\n";
}
