#pragma once
// CPU bridge for the same bounded helper intended for the occupancy HLS top.
// Host vectors only allocate backing memory; they do not maintain an ownership
// set or history map. Exported conflict maps are observations, never live state.
#include "search_node_occupancy.hpp"
#include <array>
#include <map>
#include <set>
#include <stdexcept>
#include <vector>

namespace node_occupancy_host {
class OwnerTable {
    using Core=fpga_search::ProductionNodeOccupancy;
    using Status=fpga_search::OccupancyStatus;
    std::array<uint64_t,4> meta_{{0,0,0,0}};
    std::vector<uint32_t> counts_,flags_;
    std::vector<uint64_t> history_,keys_;
    static void check(Status status) {
        if(status==Status::capacity)throw std::length_error("canonical node occupancy capacity exceeded");
        if(status!=Status::ok)throw std::invalid_argument("canonical node occupancy operation rejected");
    }
    void valid_node(uint32_t node)const {if(node>=size())throw std::out_of_range("occupancy node outside domain");}
public:
    explicit OwnerTable(size_t nodes):counts_(nodes),flags_(2097152),history_(nodes),keys_(2097152) {
        if(!nodes || nodes>1048576)throw std::length_error("canonical node domain exceeds occupancy capacity");
        check(Core::reset(unsigned(nodes),meta_.data(),counts_.data(),history_.data(),flags_.data()));
    }
    size_t size()const {return size_t(meta_[1]);}
    struct Buffers {const uint64_t *meta;const uint32_t *counts;const uint64_t *history,*keys;const uint32_t *flags;};
    Buffers buffers()const{return {meta_.data(),counts_.data(),history_.data(),keys_.data(),flags_.data()};}
    struct Node {
        OwnerTable& owner;uint32_t node;
        size_t size()const {return owner.counts_[node];}
        size_t count(uint32_t net)const {
            bool found=false;Core::locate(owner.keys_.data(),owner.flags_.data(),Core::key(net,node),found);return found?1:0;
        }
        unsigned erase(uint32_t net) {
            const auto status=Core::update(net,&node,1,nullptr,0,owner.meta_.data(),owner.counts_.data(),owner.keys_.data(),owner.flags_.data());
            if(status==Status::missing_owner)return 0;
            check(status);return 1;
        }
        void insert(uint32_t net) {
            check(Core::update(net,nullptr,0,&node,1,owner.meta_.data(),owner.counts_.data(),owner.keys_.data(),owner.flags_.data()));
        }
    };
    Node operator[](uint32_t node) {valid_node(node);return {*this,node};}
    void snapshot(uint32_t net,uint64_t* output)const {
        check(Core::snapshot(net,meta_.data(),counts_.data(),history_.data(),keys_.data(),flags_.data(),output));
    }
    std::map<uint32_t,std::set<uint32_t>> conflicts()const {
        std::map<uint32_t,std::set<uint32_t>> out;
        for(unsigned i=0;i<2097152;++i)if(flags_[i]==1) {
            const auto node=uint32_t(keys_[i]);
            if(counts_[node]>1)out[node].insert(uint32_t(keys_[i]>>32));
        }
        for(const auto& item:out)if(item.second.size()!=counts_[item.first])throw std::logic_error("occupancy conflict export mismatch");
        return out;
    }
    void advance(size_t expected_conflicts) {
        uint64_t observed=0;check(Core::advance(meta_.data(),counts_.data(),history_.data(),observed));
        if(observed!=expected_conflicts)throw std::logic_error("occupancy history conflict count mismatch");
    }
};
} // namespace node_occupancy_host
