#pragma once
#include "search_heap.hpp"

namespace fpga_search {
// Explicit three-word ABI avoids tool-dependent aggregate padding on AXI.
// Counts and entries belong to the caller; there is no implicit reset or state.
template<unsigned Capacity> struct ExternalHeap {
    static_assert(Capacity>0 && Capacity<=0x1fffffffu,"heap word offset overflow");
    static Entry load(const uint64_t* words,unsigned index) {
        const unsigned offset=3*index;
        return {words[offset],words[offset+1],words[offset+2]};
    }
    static void store(uint64_t* words,unsigned index,const Entry& entry) {
        const unsigned offset=3*index;
        words[offset]=entry.cost;words[offset+1]=entry.serial;words[offset+2]=entry.label;
    }
    static bool push(uint64_t* words,unsigned& count,const Entry& entry) {
        if (count>=Capacity) return false;
        unsigned hole=count;
        for (unsigned level=0;level<31;++level) {
            if (!hole) break;
            const unsigned parent=(hole-1)/2;const Entry previous=load(words,parent);
            if (!less(entry,previous)) break;
            store(words,hole,previous);hole=parent;
        }
        store(words,hole,entry);++count;return true;
    }
    static bool pop(uint64_t* words,unsigned& count,Entry& result) {
        if (!count || count>Capacity) return false;
        result=load(words,0);--count;
        if (!count) return true;
        const Entry last=load(words,count);unsigned hole=0;
        for (unsigned level=0;level<31;++level) {
            unsigned child=hole*2+1;
            if (child>=count) break;
            Entry chosen=load(words,child);
            if (child+1<count) {
                const Entry right=load(words,child+1);
                if (less(right,chosen)) {++child;chosen=right;}
            }
            if (!less(chosen,last)) break;
            store(words,hole,chosen);hole=child;
        }
        store(words,hole,last);return true;
    }
};
static constexpr unsigned ExternalHeapCapacity=131072;
} // namespace fpga_search
