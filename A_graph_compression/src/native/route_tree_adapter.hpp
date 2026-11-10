#pragma once
#include "search_route_tree.hpp"
#include <array>
#include <vector>
#include <stdexcept>
extern "C" void search_route_tree_top(const uint64_t*,uint64_t*,uint64_t*,uint64_t*,const uint64_t*,const uint32_t*,const uint32_t*,uint32_t*,uint64_t*);

namespace route_tree_host {
// Host owns buffers only. Live membership/demand mutation uses the actual top.
// Dummy inputs below are CPU-only; an RTL TB must allocate full port depths.
class Tree {
    unsigned nodes_;
    std::array<uint64_t,5> meta_{};
    std::array<uint64_t,65> demands_{};
    std::vector<uint64_t> bits_=std::vector<uint64_t>(16384);
    std::vector<uint32_t> roots_=std::vector<uint32_t>(1048576);
    std::array<uint64_t,6> invoke(const uint64_t* config,const uint64_t* search=nullptr,
                               const uint32_t* path=nullptr,const uint32_t* sinks=nullptr) {
        const uint64_t dummy_search[81]{};const uint32_t dummy_path[1]{},dummy_sinks[1]{};
        std::array<uint64_t,6> result{};
        search_route_tree_top(config,meta_.data(),bits_.data(),demands_.data(),search?search:dummy_search,
            path?path:dummy_path,sinks?sinks:dummy_sinks,roots_.data(),result.data());
        if(result[0]==2)throw std::length_error("route tree capacity exceeded");
        if(result[0]==3)throw std::overflow_error("route tree version overflow");
        if(result[0])throw std::invalid_argument("route tree rejected operation");
        return result;
    }
public:
    explicit Tree(unsigned nodes):nodes_(nodes){if(!nodes || nodes>1048576)throw std::length_error("route tree node domain");}
    void reset(uint32_t source){const uint64_t c[8]={0,nodes_,source,0,0,0,0,0};invoke(c);}
    void accept(uint32_t target,const uint64_t* search,const uint32_t* path){const uint64_t c[8]={1,0,0,target,0,0,0,0};invoke(c,search,path);}
    unsigned emit_roots(){const uint64_t c[8]={2,0,0,0,0,0,0,0};return unsigned(invoke(c)[4]);}
    const uint32_t* roots()const{return roots_.data();}
    const uint64_t* demands()const{return demands_.data();}
    bool complete(const std::vector<uint32_t>& sinks){
        if(sinks.size()>1048576)throw std::length_error("route tree sink capacity");
        const uint64_t c[8]={3,0,0,0,sinks.size(),0,0,0};return invoke(c,nullptr,nullptr,sinks.data())[5]!=0;
    }
};
} // namespace route_tree_host
