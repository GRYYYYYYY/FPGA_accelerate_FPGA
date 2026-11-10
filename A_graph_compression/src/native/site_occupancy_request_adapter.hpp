#pragma once
// Host allocation/marshalling for the same bounded mutable site ledger. No
// duplicate live std::map ownership or history. Exported maps are observations.
#include "search_site_occupancy.hpp"
#include "site_ledger.hpp"
#include <array>

extern "C" void search_site_request_top(const uint64_t*,uint64_t*,uint64_t*);

namespace site_occupancy_host {
class Ledger {
    using Core=fpga_search::ProductionSiteOccupancy;
    using Status=fpga_search::SiteOccupancyStatus;
    std::array<uint64_t,6> meta_{};
    std::vector<uint64_t> owners_=std::vector<uint64_t>(8*65536);
    std::vector<uint64_t> history_=std::vector<uint64_t>(4*65536);
    std::vector<uint64_t> request_=std::vector<uint64_t>(3*65536);
    mutable std::vector<uint32_t> flags_=std::vector<uint32_t>(65536);
    mutable std::vector<uint64_t> groups_=std::vector<uint64_t>(2*65536);
    static void check(Status status) {
        if(status==Status::capacity)throw std::length_error("site ledger capacity exceeded");
        if(status!=Status::ok)throw std::invalid_argument("site ledger operation rejected");
    }
public:
    Ledger(){check(Core::reset(meta_.data()));}
    struct Buffers {const uint64_t *meta,*owners,*history;};
    Buffers buffers()const{return {meta_.data(),owners_.data(),history_.data()};}
    void replace(uint32_t net,const site_native::Normalized& demands) {
        const auto entries=site_native::entries(demands);
        if(entries.size()>65536)throw std::length_error("site request capacity exceeded");
        unsigned i=0;
        for(const auto& e:entries) {
            request_[3*i]=(uint64_t(e.first.first)<<32)|e.first.second;
            request_[3*i+1]=e.second.first;request_[3*i+2]=e.second.second;++i;
        }
        check(Core::replace(net,request_.data(),i,meta_.data(),owners_.data()));
    }
    void replace_packed(uint32_t net,const uint64_t* state) {
        uint64_t result[2]{};
        search_site_request_top(state,request_.data(),result);
        if(result[0]==2)throw std::length_error("packed site request capacity exceeded");
        if(result[0] || result[1]>56)throw std::invalid_argument("invalid packed site request");
        check(Core::replace(net,request_.data(),unsigned(result[1]),meta_.data(),owners_.data()));
    }
    void release(uint32_t net){check(Core::replace(net,request_.data(),0,meta_.data(),owners_.data()));}
    std::map<site_native::ResourceKey,std::set<uint32_t>> conflicts()const {
        unsigned groups=0;check(Core::analyze(meta_.data(),owners_.data(),flags_.data(),groups_.data(),groups));
        std::map<site_native::ResourceKey,std::set<uint32_t>> out;
        const unsigned base=unsigned(meta_[1])*65536*4;
        for(unsigned i=0;i<meta_[2];++i)if(flags_[i]) {
            const uint64_t key=owners_[base+4*i];
            out[{unsigned(key>>32),uint32_t(key)}].insert(uint32_t(owners_[base+4*i+1]));
        }
        if(out.size()!=groups)throw std::logic_error("site conflict export mismatch");
        return out;
    }
    void advance(size_t expected_groups) {
        unsigned groups=0;check(Core::advance(meta_.data(),owners_.data(),history_.data(),flags_.data(),groups_.data(),groups));
        if(groups!=expected_groups)throw std::logic_error("site history conflict count mismatch");
    }
    void snapshot(uint32_t net,std::vector<uint64_t>& owners,std::vector<uint64_t>& history)const {
        owners.resize(4*65536);history.resize(2*65536);unsigned n=0;
        check(Core::snapshot(net,meta_.data(),owners_.data(),history_.data(),owners.data(),history.data(),n));
        owners.resize(4*n);history.resize(2*meta_[4]);
    }
};
} // namespace site_occupancy_host
