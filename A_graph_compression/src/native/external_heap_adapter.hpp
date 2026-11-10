#pragma once
// CPU integration harness only. Heap storage allocation and counters are not HLS.
// Uses the same explicit three-word layout and helper as the external AXI top.
#include "search_heap_external.hpp"
#include <memory>
#include <tuple>
#include <stdexcept>
#include <algorithm>
namespace heap_adapter {
struct Counters {
    uint64_t searches=0, pushes=0, pops=0, failures=0;
    unsigned peak=0;
};
inline Counters counters;
template<unsigned Capacity> class Queue {
    std::unique_ptr<uint64_t[]> storage{new uint64_t[3*Capacity]};
    unsigned count=0;
public:
    Queue() {++counters.searches;}
    bool empty() const {return count==0;}
    bool emplace(uint64_t cost,uint64_t serial,uint64_t label) {
        if (!fpga_search::ExternalHeap<Capacity>::push(storage.get(),count,{cost,serial,label})) {
            ++counters.failures;return false;
        }
        ++counters.pushes;counters.peak=std::max(counters.peak,count);return true;
    }
    std::tuple<uint64_t,uint64_t,size_t> top() const {
        if (!count) throw std::logic_error("heap top on empty queue");
        const auto e=fpga_search::ExternalHeap<Capacity>::load(storage.get(),0);return {e.cost,e.serial,size_t(e.label)};
    }
    void pop() {
        fpga_search::Entry result;
        if (!fpga_search::ExternalHeap<Capacity>::pop(storage.get(),count,result))
            throw std::logic_error("heap pop on invalid queue");
        ++counters.pops;
    }
};
} // namespace heap_adapter
