// Fixture copied from the production full-state boundary test. Synthetic only.
// Full production top: exact state capacities and overflow through real search.
#include "search_kernel_packet.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#ifndef SEARCH_GRAPH_MODE
#define SEARCH_GRAPH_MODE 0
#endif
#ifndef SEARCH_TOP_NAME
#define SEARCH_TOP_NAME search_kernel_top
#endif
extern "C" void SEARCH_TOP_NAME(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
struct Image {
    std::vector<uint32_t> data;std::array<uint32_t,32> config{};
    Image(unsigned mode){
        using namespace fpga_search::graph_decode;
        config[MODE]=mode;config[STRING_COUNT]=13;config[ATTR_COUNT]=2;
        auto section=[&](unsigned index,unsigned count,std::initializer_list<uint32_t> words){config[index]=unsigned(data.size());config[index+1]=count;data.insert(data.end(),words);};
        section(NODE_BASE,4,{0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,UINT32_MAX});
        section(TILE_BASE,1,{0,0,0,0,0,0});section(GRID_BASE,1,{0,0,0});
        section(ALIAS_BASE,3,{0,10,0,0,11,1,0,12,2});
        if(mode==0){section(CSR_OFF_BASE,4,{0,0,1,0,2,0,2,0});section(CSR_EDGE_BASE,2,{1,0,3,10,11,1,0,2,0,7,11,12,1,0});}
        else {section(INSTANCE_BASE,3,{UINT32_MAX,0,0,0,1,0,0,UINT32_MAX,0,0,1,1,0,0,UINT32_MAX,0,0,2,0,0,0});section(ADD_BASE,2,{0,0,3,10,11,1,0,0,0,7,11,12,1,0});}
        config[IMAGE_WORDS]=unsigned(data.size());
    }
};

