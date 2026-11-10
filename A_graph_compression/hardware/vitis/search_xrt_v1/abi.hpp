#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
namespace search_xrt {
struct Argument {const char* name;const char* port;size_t bytes;unsigned offset;unsigned host_size;};
inline constexpr std::array<Argument,15> arguments{{
    {"image","M_AXI_GRAPH_MEM",134217728,16,8},
    {"config","M_AXI_INPUT_MEM",128,28,8},
    {"image_words","S_AXI_CONTROL",0,40,4},
    {"roots","M_AXI_INPUT_MEM",4194304,48,8},
    {"packet","M_AXI_INPUT_MEM",33554432,60,8},
    {"packet_words","S_AXI_CONTROL",0,72,4},
    {"heap","M_AXI_HEAP_MEM",3145728,80,8},
    {"slots","M_AXI_INDEX_MEM",8388608,92,8},
    {"records","M_AXI_RECORD_MEM",41943040,104,8},
    {"keys","M_AXI_KEY_MEM",272629760,116,8},
    {"unknown_nodes","M_AXI_OUTPUT_MEM",131072,128,8},
    {"unknown_pips","M_AXI_OUTPUT_MEM",8806032,140,8},
    {"path","M_AXI_OUTPUT_MEM",16777216,152,8},
    {"meta","M_AXI_OUTPUT_MEM",16,164,8},
    {"result","M_AXI_OUTPUT_MEM",648,176,8},
}};
inline size_t allocation_size(unsigned id){return (arguments.at(id).bytes+4095)/4096*4096;}
} // namespace search_xrt
