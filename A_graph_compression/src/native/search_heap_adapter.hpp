#pragma once
// CPU integration harness only. Heap storage allocation and counters are not HLS.
// The exact push/pop implementation is copied from hardware/vitis/search_heap.hpp.
#include "search_heap.hpp"
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
    std::unique_ptr<fpga_search::Entry[]> storage{new fpga_search::Entry[Capacity]};
    unsigned count=0;
public:
    Queue() {++counters.searches;}
    bool empty() const {return count==0;}
    bool emplace(uint64_t cost,uint64_t serial,uint64_t label) {
        if (!fpga_search::Heap<Capacity>::push(storage.get(),count,{cost,serial,label})) {
            ++counters.failures;return false;
        }
        ++counters.pushes;counters.peak=std::max(counters.peak,count);return true;
    }
    std::tuple<uint64_t,uint64_t,size_t> top() const {
        if (!count) throw std::logic_error("heap top on empty queue");
        const auto& e=storage[0];return {e.cost,e.serial,size_t(e.label)};
    }
    void pop() {
        fpga_search::Entry result;
        if (!fpga_search::Heap<Capacity>::pop(storage.get(),count,result))
            throw std::logic_error("heap pop on invalid queue");
        ++counters.pops;
    }
};
} // namespace heap_adapter
