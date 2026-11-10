#pragma once
#include <array>
#include <cstdint>
#include <vector>
#include <stdexcept>
extern "C" void search_retained_nodes_top(const uint64_t*,uint64_t*,uint64_t*,const uint32_t*,uint32_t*,uint64_t*);
namespace retained_nodes_host {
class Store {
    std::array<uint64_t,6> meta_{};
    std::vector<uint64_t> rows_=std::vector<uint64_t>(4194304);
    std::vector<uint32_t> output_=std::vector<uint32_t>(1048576);
    std::array<uint64_t,5> invoke(const uint64_t* c,const uint32_t* nodes=nullptr){
        const uint32_t unused[1]{};std::array<uint64_t,5> r{};
        // Short unused input is CPU-only; RTL TB must allocate full port depth.
        search_retained_nodes_top(c,meta_.data(),rows_.data(),nodes?nodes:unused,output_.data(),r.data());
        if(r[0]==2)throw std::length_error("retained nodes capacity exceeded");
        if(r[0]==3)throw std::overflow_error("retained nodes version overflow");
        if(r[0])throw std::invalid_argument("retained nodes operation rejected");
        return r;
    }
public:
    explicit Store(unsigned nodes){const uint64_t c[8]={0,0,nodes,0,0,0,0,0};invoke(c);}
    unsigned get(uint32_t net){const uint64_t c[8]={2,net,0,0,0,0,0,0};return unsigned(invoke(c)[4]);}
    const uint32_t* output()const{return output_.data();}
    void replace(uint32_t net,const uint32_t* nodes,unsigned count){const uint64_t c[8]={1,net,0,count,0,0,0,0};invoke(c,nodes);}
};
}
