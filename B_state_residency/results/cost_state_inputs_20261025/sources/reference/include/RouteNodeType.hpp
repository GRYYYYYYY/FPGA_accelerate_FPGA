// Pure-C++ port of com.xilinx.rapidwright.rwroute.RouteNodeType.
// Ordinals MUST match the Java enum order exactly (they are serialised as the
// node "type" byte by the Java exporter and used in routing decisions).
#pragma once
#include <cstdint>

namespace com::xilinx::rapidwright::rwroute {

enum class RouteNodeType : uint8_t {
    EXCLUSIVE_SOURCE = 0,
    EXCLUSIVE_SINK_BOTH = 1,
    EXCLUSIVE_SINK_EAST = 2,
    EXCLUSIVE_SINK_WEST = 3,
    EXCLUSIVE_SINK_NON_LOCAL = 4,

    SUPER_LONG_LINE = 5,

    LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA = 6,
    LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA = 7,
    LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA = 8,
    LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA = 9,
    NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA = 10,
    NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA = 11,

    NON_LOCAL = 12,

    LOCAL_BOTH = 13,
    LOCAL_EAST = 14,
    LOCAL_WEST = 15,

    LOCAL_RESERVED = 16,

    INACCESSIBLE = 17,
};

inline bool isAnyExclusiveSink(RouteNodeType t) {
    return t == RouteNodeType::EXCLUSIVE_SINK_BOTH || t == RouteNodeType::EXCLUSIVE_SINK_EAST ||
           t == RouteNodeType::EXCLUSIVE_SINK_WEST || t == RouteNodeType::EXCLUSIVE_SINK_NON_LOCAL;
}

inline bool isAnyLocal(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_BOTH || t == RouteNodeType::LOCAL_EAST ||
           t == RouteNodeType::LOCAL_WEST || t == RouteNodeType::LOCAL_RESERVED ||
           t == RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA;
}

inline bool isEastLocal(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_EAST ||
           t == RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA;
}

inline bool isWestLocal(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_WEST ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA;
}

inline bool isLocalLeadingToLaguna(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA;
}

inline bool leadsToLaguna(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA ||
           t == RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA;
}

inline bool leadsToNorthboundLaguna(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_EAST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_NORTHBOUND_LAGUNA ||
           t == RouteNodeType::NON_LOCAL_LEADING_TO_NORTHBOUND_LAGUNA;
}

inline bool leadsToSouthboundLaguna(RouteNodeType t) {
    return t == RouteNodeType::LOCAL_EAST_LEADING_TO_SOUTHBOUND_LAGUNA ||
           t == RouteNodeType::LOCAL_WEST_LEADING_TO_SOUTHBOUND_LAGUNA ||
           t == RouteNodeType::NON_LOCAL_LEADING_TO_SOUTHBOUND_LAGUNA;
}

}  // namespace com::xilinx::rapidwright::rwroute
