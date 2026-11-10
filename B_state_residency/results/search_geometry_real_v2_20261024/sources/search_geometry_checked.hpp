#pragma once
#include "geometry.hpp"
#include <stdexcept>
namespace search_geometry {
inline int require(Scalar r){
 if(r.status)throw std::runtime_error("search geometry invalid status="+std::to_string(r.status));
 return r.value;
}
}
