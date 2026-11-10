#pragma once
// Host-only serializer for search packet v1; no native structs cross the ABI.
#include "search_kernel.hpp"
#include <vector>
#include <stdexcept>
namespace search_kernel_host {
template<class L,class View> std::vector<uint64_t> packet(const View& view,
        uint32_t target,unsigned nroots,uint64_t budget,const typename fpga_search::FlatSearchController<L>::State& initial) {
    using Words=fpga_search::LabelKeyWords<1,L::signals,L::bits,L::values>;
    const uint64_t total=32+Words::Words+(uint64_t(view.nodes)+63)/64+uint64_t(2)*view.nodes+
        uint64_t(2)*((uint64_t(view.attributes)+7)/8)+view.protected_count+view.semantics_count+
        uint64_t(Words::Words)*view.semantics_count+uint64_t(4)*view.cost.owner_count+
        uint64_t(2)*view.cost.history_count+uint64_t(4)*view.cost.fixed_count;
    if(total>fpga_search::SearchPacketMaxWords)throw std::length_error("search packet capacity");
    std::vector<uint64_t> out(32,0);out.reserve(size_t(total));
    const uint64_t header[14]={fpga_search::SearchPacketMagic,total,view.nodes,view.attributes,view.net,view.present,target,nroots,budget,view.semantics_count,view.protected_count,view.cost.owner_count,view.cost.history_count,view.cost.fixed_count};
    for(unsigned i=0;i<14;++i)out[i]=header[i];
    auto state=[&](const typename Words::Key& key){const auto at=out.size();out.resize(at+Words::Words);if(!Words::store(out.data()+at,0,key))throw std::invalid_argument("invalid search state");};
    auto words=[&](const uint64_t* data,uint64_t count){if(count && !data)throw std::invalid_argument("null packet section");for(uint64_t i=0;i<count;++i)out.push_back(data[i]);};
    auto flags=[&](const uint8_t* data){if(view.attributes && !data)throw std::invalid_argument("null flags");for(unsigned i=0;i<view.attributes;i+=8){uint64_t word=0;for(unsigned j=0;j<8 && j<view.attributes-i;++j){if(data[i+j]>1)throw std::invalid_argument("invalid flag");word|=uint64_t(data[i+j])<<(j*8);}out.push_back(word);}};
    state({0,initial});words(view.forbidden,(uint64_t(view.nodes)+63)/64);words(view.node_costs,uint64_t(2)*view.nodes);
    flags(view.pseudo_attributes);flags(view.blocked_attributes);words(view.protected_pips,view.protected_count);words(view.semantics_keys,view.semantics_count);
    if(view.semantics_count && !view.requirements)throw std::invalid_argument("null requirements");
    for(unsigned i=0;i<view.semantics_count;++i)state({0,view.requirements[i]});
    words(view.cost.owners,uint64_t(4)*view.cost.owner_count);words(view.cost.history,uint64_t(2)*view.cost.history_count);words(view.cost.fixed,uint64_t(4)*view.cost.fixed_count);
    if(out.size()!=total)throw std::logic_error("search packet size mismatch");
    return out;
}
} // namespace search_kernel_host
