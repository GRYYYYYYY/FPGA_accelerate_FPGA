#pragma once
#include <stdint.h>

namespace fpga_search {
// Matches site_search.hpp's (cost, insertion serial, label index) order.
// Stale entries are retained: the search controller checks label costs on pop.
struct Entry { uint64_t cost, serial, label; };
inline bool less(const Entry& a, const Entry& b) {
    if (a.cost != b.cost) return a.cost < b.cost;
    if (a.serial != b.serial) return a.serial < b.serial;
    return a.label < b.label;
}

// Caller owns storage and count, allowing a later AXI-backed implementation.
// Capacity failures do not mutate storage/count; the controller must report
// capacity_exhausted, never no_path or a truncated successful search.
template<unsigned Capacity> struct Heap {
    static_assert(Capacity > 0 && Capacity <= 0x7fffffffu, "invalid heap capacity");
    static bool push(Entry* storage, unsigned& count, Entry entry) {
        if (count >= Capacity) return false;
        unsigned hole = count;
        // A heap with <= 2^31-1 entries has at most 30 parent links.
        for (unsigned level = 0; level < 31; ++level) {
            if (!hole) break;
            const unsigned parent = (hole - 1) / 2;
            if (!less(entry, storage[parent])) break;
            storage[hole] = storage[parent];
            hole = parent;
        }
        storage[hole] = entry;
        ++count;
        return true;
    }
    static bool pop(Entry* storage, unsigned& count, Entry& result) {
        if (!count || count > Capacity) return false;
        result = storage[0];
        --count;
        if (!count) return true;
        const Entry last = storage[count];
        unsigned hole = 0;
        for (unsigned level = 0; level < 31; ++level) {
            unsigned child = hole * 2 + 1;
            if (child >= count) break;
            if (child + 1 < count && less(storage[child + 1], storage[child])) ++child;
            if (!less(storage[child], last)) break;
            storage[hole] = storage[child];
            hole = child;
        }
        storage[hole] = last;
        return true;
    }
};
} // namespace fpga_search
