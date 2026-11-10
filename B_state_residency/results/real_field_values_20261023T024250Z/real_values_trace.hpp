#pragma once
#include <fstream>
#include <set>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>

// Single serial owner only. Explicit little-endian records, no native padding.
namespace bvalues {
inline std::ofstream events, metadata;
inline std::set<uint64_t> selected, seen;
inline uint64_t attempts = 0, offset = 0;
inline bool failed = false;
struct Attempt;
inline Attempt* current = nullptr;
inline void init() {
    const char* prefix = std::getenv("B_VALUES_PREFIX");
    const char* selection = std::getenv("B_VALUES_SELECTION");
    if (!prefix || !selection) throw std::runtime_error("Value trace requires prefix and selection");
    std::ifstream input(selection);
    uint64_t id;
    while (input >> id) {
        if (!id || !selected.insert(id).second) throw std::runtime_error("Invalid trace selection");
    }
    if (!input.eof() || selected.empty()) throw std::runtime_error("Invalid selection file");
    metadata.open(std::string(prefix)+".queries.jsonl");
    events.open(std::string(prefix)+".values", std::ios::binary);
    if (!events || !metadata) throw std::runtime_error("Cannot open value trace");
}
struct Attempt {
    uint64_t id, begin, count = 0, reads = 0, writes = 0;
    int iteration, connection, connectionId, net;
    bool enabled;
    Attempt* parent;
    Attempt(int iter, int conn, int cid, int nid)
        : id(++attempts), begin(offset), iteration(iter), connection(conn), connectionId(cid), net(nid),
          enabled(selected.count(id) != 0), parent(current) {
        if (parent) throw std::runtime_error("Nested query unsupported in serial value trace");
        current = this;
        if (enabled) seen.insert(id);
    }
    ~Attempt() {
        if (enabled) {
            metadata << "{\"attempt\":" << id << ",\"iteration\":" << iteration
                << ",\"connection_index\":" << connection << ",\"connection_id\":" << connectionId
                << ",\"net_index\":" << net << ",\"byte_offset\":" << begin << ",\"count\":" << count
                << ",\"reads\":" << reads << ",\"writes\":" << writes << "}\n";
            if (!metadata) failed = true;
        }
        current = parent;
    }
};
template<class T> inline uint32_t bits(T value) {
    static_assert(sizeof(T) <= 4, "Trace field wider than 32 bits");
    uint32_t raw = 0;
    std::memcpy(&raw, &value, sizeof(T));
    return raw;
}
inline void put32(unsigned char* to, uint32_t value) {
    for (unsigned i=0; i<4; ++i) to[i] = static_cast<unsigned char>(value >> (8*i));
}
template<class T> inline void emit(int node, int line, unsigned field, bool write, T value, float hist) {
    if (!current || !current->enabled) return;
    // node:u32, sourceLine:u32, valueBits:u32, field:u8, write:u8, reserved:u16, histBits:u32
    unsigned char record[20] = {};
    put32(record, uint32_t(node)); put32(record+4, uint32_t(line)); put32(record+8, bits(value));
    record[12] = static_cast<unsigned char>(field); record[13] = write ? 1 : 0;
    put32(record+16, bits(hist));
    events.write(reinterpret_cast<const char*>(record), sizeof(record));
    ++current->count; if (write) ++current->writes; else ++current->reads;
    offset += sizeof(record);
    if (!events) failed = true;
}
inline void finish() {
    events.flush(); metadata.flush();
    if (current || failed || !events || !metadata || seen != selected)
        throw std::runtime_error("Value trace incomplete or failed");
    std::fprintf(stderr, "B_VALUE_TRACE attempts=%llu selected=%zu bytes=%llu\n",
        static_cast<unsigned long long>(attempts), seen.size(), static_cast<unsigned long long>(offset));
}
}
