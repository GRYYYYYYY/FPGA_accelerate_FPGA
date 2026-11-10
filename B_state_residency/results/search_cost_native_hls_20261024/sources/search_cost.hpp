#pragma once
#include <algorithm>
#include <cstdint>
// Scalar IEEE-754 reference decomposition, NOT yet an HLS floating-point gate.
// Preserve source evaluation order; no FMA, reciprocal approximation or reassociation.
namespace search_cost {
inline float sharing_factor(float weight,int count) {return 1 + weight * count;}
inline float node_cost(float base,float hist,float present,float sharing,
                       int connections,float distance_to_center,int double_hpwl) {
    float bias = base / connections * distance_to_center / double_hpwl;
    float node = base * hist * present / sharing;
    return node + std::min(bias,node / 2);
}
inline float partial_cost(float parent,float node,float wire_weight,int length,float sharing) {
    float partial=parent;
    partial += node;
    partial += wire_weight * length / sharing;
    return partial;
}
inline float heuristic(float estimated_weight,int distance,bool landmarks,
                       const std::uint16_t target[8],const std::uint16_t child[8],float inv_scale) {
    float base=estimated_weight * (float)distance;
    if(landmarks) {
        int best=0;
        for(int i=0;i<8;i++) {int d=(int)target[i]-(int)child[i]-1;if(d>best)best=d;}
        float alt=best * inv_scale;
        if(alt>base)base=alt;
    }
    return base;
}
inline float total_cost(float partial,float heuristic,float sharing) {return partial + heuristic / sharing;}
}
