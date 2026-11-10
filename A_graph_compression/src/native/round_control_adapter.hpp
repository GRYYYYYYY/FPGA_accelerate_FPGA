#pragma once
#include <array>
#include <cstdint>
#include <vector>
#include <stdexcept>
extern "C" void search_round_control_top(const uint64_t*,const uint32_t*,const uint32_t*,uint64_t*);
namespace round_control_host {
class Context {
    std::vector<uint32_t> complete_=std::vector<uint32_t>(65536);
public:
    void mark(size_t at,bool complete){if(at>=65536)throw std::length_error("round net capacity");complete_[at]=complete;}
    std::array<uint64_t,8> finish(unsigned nodes,size_t nets,unsigned iteration,unsigned max_iterations,uint64_t cap,unsigned site_groups,const uint32_t* counts)const{
        const uint64_t c[8]={nodes,nets,iteration,max_iterations,cap,site_groups,0,0};std::array<uint64_t,8> r{};
        search_round_control_top(c,counts,complete_.data(),r.data());
        if(r[0]==2)throw std::length_error("round control capacity exceeded");
        if(r[0])throw std::invalid_argument("round control input rejected");
        return r;
    }
};
}
