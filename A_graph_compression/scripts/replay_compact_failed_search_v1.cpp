// Diagnostic replay of the saved first-search inputs using frozen production C++.
// This does not execute RTL or accept the failed full44 experiment.
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <vector>
#include "search_kernel.hpp"

struct Port {
    unsigned width = 0;
    uint64_t depth = 0;
    std::vector<uint32_t> u32;
    std::vector<uint64_t> u64;
};

static uint64_t word(std::ifstream& f) {
    uint64_t x = 0;
    for (unsigned i = 0; i < 8; ++i) {
        const int b = f.get();
        assert(b != EOF);
        x |= uint64_t(uint8_t(b)) << (8*i);
    }
    return x;
}

int main(int argc, char** argv) {
    assert(argc == 2);
    const uint16_t endian = 1;
    assert(*reinterpret_cast<const uint8_t*>(&endian) == 1);
    std::ifstream f(argv[1], std::ios::binary);
    assert(word(f) == UINT64_C(0x4142534e41503031));
    assert(word(f) == 1 && word(f) == 0 && word(f) == 44);
    std::array<Port, 45> ports;
    for (unsigned i = 0; i < 44; ++i) {
        const uint64_t id = word(f), width = word(f), depth = word(f);
        assert(id < ports.size() && id != 2 && ports[id].width == 0);
        assert((width == 4 || width == 8) && depth > 0 && depth <= 37748736);
        auto& p = ports[id];
        p.width = unsigned(width); p.depth = depth;
        if (width == 4) {
            p.u32.resize(depth);
            f.read(reinterpret_cast<char*>(p.u32.data()), depth*width);
        } else {
            p.u64.resize(depth);
            f.read(reinterpret_cast<char*>(p.u64.data()), depth*width);
        }
        assert(f);
    }
    assert(f.tellg() == 946498280 && f.peek() == EOF);
    auto p32 = [&](unsigned i) { assert(ports[i].width == 4); return ports[i].u32.data(); };
    auto p64 = [&](unsigned i) { assert(ports[i].width == 8); return ports[i].u64.data(); };
    assert(p64(12)[0] == 0 && p64(12)[1] == 0 && p64(4)[7] == 1 && p32(3)[0] == 0);
    auto run = [&](const uint32_t* image) {
        fpga_search::SearchKernel<1>::run(image, p32(1), p32(1)[27], p32(3), p64(4), unsigned(p64(4)[1]),
                p64(5), p64(6), p64(7), p64(8), p64(9), p64(10), p32(11), p64(12), p64(13));
    };
    run(nullptr);
    assert(p64(13)[0] == 6 && p64(12)[0] == 0 && p64(12)[1] == 0);
    std::printf("NULL_IMAGE_REJECTED 6\n");
    run(p32(0));
    std::printf("RESULT");
    for (unsigned i = 0; i < 81; ++i) std::printf(" %llu", (unsigned long long)p64(13)[i]);
    std::printf("\nPATH");
    assert(p64(13)[7] <= 524288);
    for (unsigned i = 0; i < 8*p64(13)[7]; ++i) std::printf(" %u", p32(11)[i]);
    std::printf("\nMETA %llu %llu\n", (unsigned long long)p64(12)[0], (unsigned long long)p64(12)[1]);
    return 0;
}
