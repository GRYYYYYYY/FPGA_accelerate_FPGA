"""Reconstruct the independent native-float golden heap from the frozen router."""
def generate(source):
 start=source.index('    struct DaryPQ {');end=source.index('    std::vector<DaryPQ::E> pqStorage;',start)
 body=source[start:end]
 return '#pragma once\n#include <vector>\n#include <cstdint>\n#include <cstring>\nnamespace golden {\n'+body+'\ninline float as_float(std::uint32_t b){float x;std::memcpy(&x,&b,4);return x;}\ninline std::uint32_t as_bits(float x){std::uint32_t b;std::memcpy(&b,&x,4);return b;}\n}\n'
