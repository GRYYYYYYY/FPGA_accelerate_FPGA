#pragma once
#include <fstream>
#include "exclusion_machine.hpp"
#include "frontier_bounded.hpp"
#include <unordered_set>

namespace btrace {
inline std::ofstream metadata, accesses;
inline uint64_t attempts = 0, selected = 0, byteOffset = 0;
inline unsigned stride = 512, cap = 200000;
struct Access { int32_t node, sourceLine; };
struct Attempt;
inline Attempt* current = nullptr;
inline void init() {
    const char* prefix = std::getenv("B_TRACE_PREFIX");
    if (!prefix) return;
    metadata.open(std::string(prefix)+".jsonl");
    accesses.open(std::string(prefix)+".accesses", std::ios::binary);
    if (const char* s = std::getenv("B_TRACE_STRIDE")) stride = std::max(1, std::atoi(s));
    if (!metadata || !accesses) throw std::runtime_error("trace output open failed");
}
struct Attempt {
    uint64_t id; bool enabled; uint64_t count = 0; uint64_t frontierPushes=0, frontierPolls=0, frontierPeak=0, frontierCleared=0;
    std::vector<Access> events;
    std::vector<int> previousPath;
    Attempt* parent;
    Attempt() : id(++attempts), enabled(metadata.is_open() && id % stride == 0), parent(current) {
        current = this;
        if (enabled) { ++selected; events.reserve(4096); }
    }
    ~Attempt() { current = parent; }
};
inline void label(int id, int line) {
    if (!current) return;
    ++current->count;
    if (current->enabled && current->events.size()<cap) current->events.push_back({id,line});
}
inline void flush() { metadata.flush(); accesses.flush(); }
}
