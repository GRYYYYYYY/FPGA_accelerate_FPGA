#pragma once
// Host marshals immutable metadata once. Per-net packet construction and query
// patching execute the actual bounded component top, not the vector serializer.
#include "search_resident_snapshot.hpp"
#include "node_occupancy_snapshot_adapter.hpp"
#include "site_occupancy_snapshot_adapter.hpp"
#include <array>
#include <stdexcept>

extern "C" void search_resident_snapshot_top(const uint64_t*,const uint64_t*,const uint64_t*,
    const uint64_t*,const uint32_t*,const uint64_t*,const uint64_t*,const uint32_t*,
    const uint64_t*,const uint64_t*,const uint64_t*,uint64_t*,uint64_t*);

namespace resident_snapshot_host {
using Core=fpga_search::ProductionResidentSnapshot;
template<class Sites>
std::vector<uint64_t> static_image(unsigned nodes,const Sites& sites,const std::set<uint32_t>& protected_nodes,
                                  const std::map<uint32_t,uint32_t>& reserved) {
    const size_t attrs=sites.pseudo_attributes.size(),np=sites.protected_pips.size(),ns=sites.semantics_keys.size();
    if(!nodes || nodes>1048576 || !attrs || attrs>65536 || np>1048576 || ns>256 || sites.fixed.size()%4 ||
       sites.fixed.size()/4>65536 || reserved.size()>1048576)throw std::length_error("static snapshot capacity");
    if(sites.blocked_attributes.size()!=attrs || sites.requirements.size()!=ns)throw std::invalid_argument("static snapshot section size");
    std::vector<uint64_t> out(16+(nodes+63)/64,0);
    for(auto n:protected_nodes){if(n>=nodes)throw std::invalid_argument("protected node outside domain");out[16+n/64]|=uint64_t(1)<<(n%64);}
    for(auto r:reserved){if(r.first>=nodes)throw std::invalid_argument("reserved node outside domain");out.push_back((uint64_t(r.first)<<32)|r.second);}
    for(const auto* flags:{&sites.pseudo_attributes,&sites.blocked_attributes})for(size_t i=0;i<attrs;i+=8) {
        uint64_t word=0;
        for(unsigned j=0;j<8 && i+j<attrs;++j){if((*flags)[i+j]>1)throw std::invalid_argument("invalid snapshot flag");word|=uint64_t((*flags)[i+j])<<(8*j);}
        out.push_back(word);
    }
    out.insert(out.end(),sites.protected_pips.begin(),sites.protected_pips.end());
    out.insert(out.end(),sites.semantics_keys.begin(),sites.semantics_keys.end());
    for(const auto& state:sites.requirements) {
        const size_t at=out.size();out.resize(at+Core::Words::Words);
        if(!Core::Words::store(out.data()+at,0,{0,state}))throw std::invalid_argument("invalid static site state");
    }
    out.insert(out.end(),sites.fixed.begin(),sites.fixed.end());
    if(out.size()>Core::StaticWords)throw std::length_error("static snapshot image capacity");
    const uint64_t header[8]={Core::StaticMagic,out.size(),nodes,attrs,np,ns,sites.fixed.size()/4,reserved.size()};
    for(unsigned i=0;i<8;++i)out[i]=header[i];
    return out;
}

class Builder {
    std::vector<uint64_t> static_;
    static void check(uint64_t status) {
        if(status==2)throw std::length_error("resident snapshot capacity exceeded");
        if(status)throw std::invalid_argument("resident snapshot operation rejected");
    }
public:
    template<class Sites> Builder(unsigned nodes,const Sites& sites,const std::set<uint32_t>& protected_nodes,
                                  const std::map<uint32_t,uint32_t>& reserved):static_(static_image(nodes,sites,protected_nodes,reserved)){}
    std::array<uint64_t,8> build(uint32_t net,uint64_t present,const node_occupancy_host::OwnerTable& nodes,
                               const site_occupancy_host::Ledger& sites,uint64_t* packet)const {
        const uint64_t control[16]={0,net,present,0,1,1,static_.size(),4194304,0,0,0,0,0,0,0,0};
        const uint64_t initial[65]{};std::array<uint64_t,8> result{};
        const auto n=nodes.buffers();const auto s=sites.buffers();
        search_resident_snapshot_top(control,static_.data(),initial,n.meta,n.counts,n.history,n.keys,n.flags,
                                     s.meta,s.owners,s.history,packet,result.data());
        check(result[0]);return result;
    }
    void patch(uint64_t* packet,unsigned packet_words,uint32_t target,unsigned nroots,uint64_t budget,
               const fpga_search::SiteState<32,16,8>& state)const {
        uint64_t initial[65]{};
        if(!Core::Words::store(initial,0,{0,state}))throw std::invalid_argument("invalid query initial state");
        const uint64_t control[16]={1,0,0,target,nroots,budget,0,packet_words,0,0,0,0,0,0,0,0};
        uint64_t result[8]{};
        // Patch does not access ledgers/static data. These same typed nonnull
        // dummy buffers are used only in the CPU bridge; RTL TB allocates full depths.
        const uint64_t nm[4]{},nh[1]{},nk[1]{},sm[6]{},so[1]{},sh[1]{};
        const uint32_t counts[1]{},flags[1]{};
        search_resident_snapshot_top(control,static_.data(),initial,nm,counts,nh,nk,flags,sm,so,sh,packet,result);
        check(result[0]);if(result[1]!=packet_words)throw std::logic_error("query patch changed packet length");
    }
};
} // namespace resident_snapshot_host
