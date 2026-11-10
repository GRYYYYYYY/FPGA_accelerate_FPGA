#pragma once
#include <fstream>
#include <unordered_set>

namespace btrace {
inline std::ofstream metadata, accesses;
inline uint64_t attempts = 0, selected = 0, byteOffset = 0;
inline unsigned stride = 512, cap = 3112021;
inline std::unordered_set<uint64_t> selectedIds = {472505,495400,504884,505992,507751,522333,531645,531662,531663,531706,531707,531708,531807,531956,537506,543648,550387,551295,551296};
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
    uint64_t id; bool enabled; uint64_t count = 0;
    std::vector<Access> events;
    std::vector<int> previousPath;
    Attempt* parent;
    Attempt() : id(++attempts), enabled(metadata.is_open() && selectedIds.count(id) != 0), parent(current) {
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
