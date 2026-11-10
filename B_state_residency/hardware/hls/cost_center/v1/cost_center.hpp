#pragma once
#include <cstdint>
#include "../../search_cost/exact_v2/softfloat32.hpp"
namespace cost_center {
// Net centers must be finite. Integer coordinates are converted exactly as C++ float.
inline std::uint32_t evaluate(const std::uint32_t input[4],std::uint32_t& distance){
 distance=0;
 if((input[2]&0x7f800000U)==0x7f800000U||(input[3]&0x7f800000U)==0x7f800000U)return 1;
 const auto dx=softfp::add(softfp::from_int(std::int32_t(input[0])),input[2]^0x80000000U)&0x7fffffffU;
 const auto dy=softfp::add(softfp::from_int(std::int32_t(input[1])),input[3]^0x80000000U)&0x7fffffffU;
 distance=softfp::add(dx,dy);return 0;
}
}
