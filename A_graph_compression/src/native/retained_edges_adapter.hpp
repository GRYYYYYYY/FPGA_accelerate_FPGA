#pragma once
#include <array>
#include <cstdint>
#include <vector>
#include <stdexcept>
extern "C" void search_retained_edges_top(const uint64_t*,uint64_t*,uint32_t*,const uint32_t*,uint32_t*,uint64_t*);
namespace retained_edges_host {
class Store {
    std::array<uint64_t,6> meta_{};
    std::vector<uint32_t> rows_=std::vector<uint32_t>(37748736);
    std::vector<uint32_t> output_=std::vector<uint32_t>(16777216);
    unsigned invoke(unsigned op,uint32_t net,unsigned nodes,unsigned count,const uint32_t* path=nullptr){
        const uint64_t c[8]={op,net,nodes,count,0,0,0,0};const uint32_t unused[1]{};uint64_t r[5]{};
        // CPU-only short unused input. RTL requires full declared buffers.
        search_retained_edges_top(c,meta_.data(),rows_.data(),path?path:unused,output_.data(),r);
        if(r[0]==2)throw std::length_error("retained edge capacity");
        if(r[0]==3)throw std::overflow_error("retained edge version");
        if(r[0])throw std::invalid_argument("retained edge input");
        return unsigned(r[4]);
    }
public:
    explicit Store(unsigned nodes){invoke(0,0,nodes,0);}
    void clear(uint32_t net){invoke(1,net,0,0);}
    void append(uint32_t net,const uint32_t* path,unsigned count){invoke(3,net,0,count,path);}
    unsigned get(uint32_t net){return invoke(2,net,0,0);}
    const uint32_t* output()const{return output_.data();}
};
}
