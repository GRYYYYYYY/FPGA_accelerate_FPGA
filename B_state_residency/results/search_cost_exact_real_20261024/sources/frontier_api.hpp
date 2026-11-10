#pragma once
#include <cstdint>
namespace frontier {
static const std::uint32_t capacity=65536;
enum Op { CLEAR=0, OFFER=1, POLL=2, SIZE=3 };
enum Status { OK=0, EMPTY=1, FULL=2, BAD=3 };
struct Entry { std::uint32_t key_bits,id; };
}
void frontier_step(std::uint32_t op,std::uint32_t key_bits,std::uint32_t id,
                   std::uint32_t& status,std::uint32_t& result_bits,
                   std::uint32_t& result_id,std::uint32_t& size);
