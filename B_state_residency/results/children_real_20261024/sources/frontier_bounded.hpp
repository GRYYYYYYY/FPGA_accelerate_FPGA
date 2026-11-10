#pragma once
#include "frontier_api.hpp"
namespace frontier {
// IEEE binary32 relational semantics; retain raw payloads, signed zeros and NaNs.
// NaN comparisons are unordered; floating-point exception flags are not modeled.
inline bool is_nan(std::uint32_t bits) {
    return (bits & 0x7f800000u)==0x7f800000u && (bits & 0x007fffffu)!=0;
}
inline bool less(std::uint32_t a,std::uint32_t b) {
    if(is_nan(a)||is_nan(b))return false;
    if((a & 0x7fffffffu)==0 && (b & 0x7fffffffu)==0)return false;
    const bool sa=(a>>31)!=0,sb=(b>>31)!=0;
    if(sa!=sb)return sa;
    return sa ? a>b : a<b;
}
inline bool less_equal(std::uint32_t a,std::uint32_t b) {
    if(is_nan(a)||is_nan(b))return false;
    if(a==b || ((a & 0x7fffffffu)==0 && (b & 0x7fffffffu)==0))return true;
    return less(a,b);
}
inline bool offer(Entry heap[capacity],std::uint32_t& size,Entry value) {
    if(size>=capacity)return false;
    std::uint32_t k=size;
    // Largest valid index65535 has exactly six ancestor edges in an8-ary heap.
    for(unsigned level=0;level<6;++level) {
        if(k==0)break;
        const std::uint32_t parent=(k-1)/8;
        if(less_equal(heap[parent].key_bits,value.key_bits))break;
        heap[k]=heap[parent];k=parent;
    }
    heap[k]=value;++size;return true;
}
inline bool poll(Entry heap[capacity],std::uint32_t& size,Entry& value) {
    if(size==0)return false;
    value=heap[0];--size;
    if(size!=0) {
        const Entry last=heap[size];std::uint32_t k=0;
        for(unsigned level=0;level<6;++level) {
            const std::uint32_t first=k*8+1;
            if(first>=size)break;
            std::uint32_t best=first,best_bits=heap[first].key_bits;
            for(unsigned child=1;child<8;++child) {
                const std::uint32_t index=first+child;
                if(index<size && less(heap[index].key_bits,best_bits)) {
                    best_bits=heap[index].key_bits;best=index;
                }
            }
            if(less_equal(last.key_bits,best_bits))break;
            heap[k]=heap[best];k=best;
        }
        heap[k]=last;
    }
    return true;
}
}
