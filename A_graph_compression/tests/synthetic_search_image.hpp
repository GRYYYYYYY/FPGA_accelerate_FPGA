#pragma once
// Synthetic decoder payloads only. These deliberately do not claim to be
// physical AGRAPH01 captures; production loading uses host_contract validation.
#include "search_kernel_binding.hpp"
#include <set>
struct SyntheticSearchImage {
    std::vector<uint32_t> image;std::array<uint32_t,32> config{};
    SyntheticSearchImage(const std::vector<std::vector<Edge>>& rows,const std::set<unsigned>& unknown,unsigned attributes,unsigned mode) {
        using namespace fpga_search::graph_decode;
        const unsigned nodes=unsigned(rows.size());unsigned tiles=1,strings=nodes;
        for(unsigned n=0;n<nodes;++n)for(const auto& e:rows[n]){
            if(e.up!=(e.dir?e.dst:n) || e.down!=(e.dir?n:e.dst))throw std::logic_error("synthetic wire aliases do not match canonical nodes");
            tiles=std::max(tiles,e.tile+1);strings=std::max(strings,e.pip+1);
        }
        config[MODE]=mode;config[STRING_COUNT]=strings;config[ATTR_COUNT]=attributes;
        auto section=[&](unsigned at,unsigned count,const std::vector<uint32_t>& data){config[at]=unsigned(image.size());config[at+1]=count;image.insert(image.end(),data.begin(),data.end());};
        std::vector<uint32_t> words;
        for(unsigned n=0;n<nodes;++n)words.insert(words.end(),{0,0,0,unknown.count(n)?UINT32_MAX:n});section(NODE_BASE,nodes,words);words.clear();
        for(unsigned t=0;t<tiles;++t)words.insert(words.end(),{0,0,t,0,0,0});section(TILE_BASE,tiles,words);words.clear();
        for(unsigned t=0;t<tiles;++t)words.insert(words.end(),{t,0,t});section(GRID_BASE,tiles,words);words.clear();
        for(unsigned t=0;t<tiles;++t)for(unsigned n=0;n<nodes;++n)words.insert(words.end(),{t,n,n});section(ALIAS_BASE,tiles*nodes,words);words.clear();
        unsigned total=0;std::vector<uint32_t> edges;
        for(unsigned n=0;n<nodes;++n){
            const unsigned count=unknown.count(n)?0:unsigned(rows[n].size());
            if(mode==0)words.insert(words.end(),{total,0});
            else words.insert(words.end(),{UINT32_MAX,0,0,total,count,0,0});
            if(count)for(const auto& e:rows[n]){
                if(mode==0)edges.insert(edges.end(),{e.dst,e.tile,e.pip,e.up,e.down,e.attr,e.dir});
                else edges.insert(edges.end(),{e.tile,0,e.pip,e.up,e.down,e.attr,e.dir});
            }
            total+=count;
        }
        if(mode==0){words.insert(words.end(),{total,0});section(CSR_OFF_BASE,nodes+1,words);section(CSR_EDGE_BASE,total,edges);}
        else {section(INSTANCE_BASE,nodes,words);section(ADD_BASE,total,edges);}
        config[IMAGE_WORDS]=unsigned(image.size());
    }
    kernel_route::ImageView view()const{return {image.data(),config.data(),unsigned(image.size())};}
};
