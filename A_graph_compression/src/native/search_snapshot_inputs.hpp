#pragma once
// Host-side builder; not part of the HLS call graph. Buffers remain immutable
// while a bound search is active. Metadata does not certify physical legality.
#include "site_inputs.hpp"
#include "search_site_state.hpp"
#include <array>
#include <algorithm>

namespace snapshot_inputs {
template<class Limits> struct SiteBuffers {
    using State=fpga_search::SiteState<Limits::signals,Limits::bits,Limits::values>;
    std::vector<uint64_t> semantics_keys,fixed,protected_pips;
    std::vector<State> requirements;
    std::vector<uint8_t> pseudo_attributes,blocked_attributes;
    static State pack(const site_native::Normalized& n) {
        if(n.signals.size()>Limits::signals || n.bits.size()>Limits::bits || n.values.size()>Limits::values)throw std::length_error("snapshot path state capacity exceeded");
        State s{};
        for(auto v:n.signals)s.signals.data[s.signals.count++]=v;
        for(auto v:n.bits)s.bits.data[s.bits.count++]={v.first,v.second.first,v.second.second};
        for(auto v:n.values)s.values.data[s.values.count++]={v.first,v.second};
        return s;
    }
    explicit SiteBuffers(const site_native::SiteInputs& sites,const std::set<std::pair<uint32_t,uint32_t>>& protected_set={},const std::set<uint32_t>& blocked_set={}):
        pseudo_attributes(sites.attributes),blocked_attributes(sites.attributes) {
        for(auto a:sites.pseudo_attributes)pseudo_attributes.at(a)=1;
        for(auto a:blocked_set)blocked_attributes.at(a)=1;
        for(auto p:protected_set)protected_pips.push_back((uint64_t(p.first)<<32)|p.second);
        for(const auto& p:sites.requirements) {
            semantics_keys.push_back((uint64_t(p.first.first)<<32)|p.first.second);
            requirements.push_back(pack(site_native::normalize(p.second)));
        }
        std::vector<std::array<uint64_t,4>> rows;
        for(auto p:sites.fixed_signals)rows.push_back({p.first,p.second,0,0});
        const auto config=site_native::normalize(sites.fixed);
        if(!config.signals.empty())throw std::invalid_argument("fixed signals require owners");
        for(auto p:config.bits)rows.push_back({(uint64_t(1)<<32)|p.first,0,p.second.first,p.second.second});
        for(auto p:config.values)rows.push_back({(uint64_t(2)<<32)|p.first,0,0,p.second});
        std::sort(rows.begin(),rows.end());
        for(const auto& row:rows)fixed.insert(fixed.end(),row.begin(),row.end());
    }
};
} // namespace snapshot_inputs
