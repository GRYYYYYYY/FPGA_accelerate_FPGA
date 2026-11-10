#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>

// Observation only: the router still executes its original owner-slot updates.
// All records are little-endian u32, including the -1 owner sentinel.
namespace bowner {
inline std::ofstream events;
inline std::string prefix;
inline std::map<std::string,uint64_t> stats;
inline void require_impl(bool condition, int line) {
    if (!condition) throw std::runtime_error("owner profile invariant/domain failure at header line " + std::to_string(line));
}
#define B_OWNER_REQUIRE(condition) require_impl((condition), __LINE__)
inline void peak(const char* key, uint64_t value) {
    if (stats[key] < value) stats[key] = value;
}
template<class R> void start(const R& r) {
    const char* p = std::getenv("B_OWNER_PREFIX"); B_OWNER_REQUIRE(p != nullptr);
    prefix = p; events.open(prefix+".events",std::ios::binary); B_OWNER_REQUIRE(bool(events));
    B_OWNER_REQUIRE(!r.occLocking);
    for (size_t i=0;i<r.ownerNet.size();++i)
        B_OWNER_REQUIRE(r.ownerNet[i]==-1 && r.ownerCnt[i]==0 && r.occCnt[i]==0 && r.userOverflow[i]==nullptr);
    stats["initial_nodes"] = r.ownerNet.size();
}
struct Before { int count, occupancy, owner; size_t overflow; };
template<class R> Before before(const R& r, int node, int net, unsigned op) {
    if (!events.is_open()) start(r);
    B_OWNER_REQUIRE(events.is_open() && !r.occLocking && node>=0 && size_t(node)<r.ownerNet.size() && net>=0);
    int count=r.countUserSlot(node,net);
    // Reject, rather than execute, the original uint16 wrap/narrowing domain.
    B_OWNER_REQUIRE(count>=0 && (op==1 ? count<65535 : count>0));
    B_OWNER_REQUIRE(op!=1 || count!=0 || r.occCnt[node]<65535);
    return {count,r.occCnt[node],r.ownerNet[node],r.userOverflow[node]?r.userOverflow[node]->size():0};
}
template<class R> void after(const R& r,int node,int net,unsigned op,Before b) {
    int count=r.countUserSlot(node,net);
    auto* overflow=r.userOverflow[node]; size_t size=overflow?overflow->size():0;
    unsigned distinct=r.ownerNet[node]>=0 ? 1:0;
    B_OWNER_REQUIRE(count==b.count+(op==1?1:-1));
    if (r.ownerNet[node]>=0) B_OWNER_REQUIRE(r.ownerCnt[node]>0);
    peak("max_primary_refs",r.ownerCnt[node]);
    if (overflow) for (const auto& kv:*overflow) {
        B_OWNER_REQUIRE(kv.first>=0 && kv.first!=r.ownerNet[node] && kv.second>0 && kv.second<=65535);
        ++distinct; peak("max_overflow_refs",kv.second);
    }
    B_OWNER_REQUIRE(distinct==r.occCnt[node]);
    const auto& h=r.hot[node];
    B_OWNER_REQUIRE(h.ownerNet==r.ownerNet[node] && h.ownerCnt==r.ownerCnt[node] && h.occCnt==std::min(255,int(distinct)));
    ++stats["events"]; ++stats[op==1?"increments":"decrements"];
    if (op==1) ++stats[b.count?"same_net_increments":"new_net_increments"];
    if (op==2 && b.count==1) ++stats["net_removals"];
    if (op==2 && b.owner==net && b.count==1 && b.overflow) ++stats["promotions"];
    stats["live_overflow_entries"] += size; stats["live_overflow_entries"] -= b.overflow;
    stats["live_overflow_nodes"] += size!=0; stats["live_overflow_nodes"] -= b.overflow!=0;
    peak("max_overflow_entries",stats["live_overflow_entries"]);
    peak("max_overflow_nodes",stats["live_overflow_nodes"]);
    peak("max_overflow_per_node",size); peak("max_occupancy",distinct);
    peak("max_same_net_refs",count);
    std::array<uint32_t,8> record{{op,uint32_t(node),uint32_t(net),uint32_t(count),distinct,uint32_t(r.ownerNet[node]),r.ownerCnt[node],uint32_t(size)}};
    for (uint32_t word:record) for (unsigned shift=0;shift<32;shift+=8) events.put(char(word>>shift));
    B_OWNER_REQUIRE(bool(events));
}
template<class R> void begin_route(const R& r) {
    if (!events.is_open()) start(r);
    stats["load_events"]=stats["events"];
    uint64_t owned=0;
    for (int owner:r.ownerNet) owned += owner>=0;
    stats["load_owned_nodes"]=owned;
    std::array<uint32_t,8> marker{{0,uint32_t(r.ownerNet.size()),0,0,0,0,0,0}};
    for(uint32_t word:marker) for(unsigned shift=0;shift<32;shift+=8) events.put(char(word>>shift));
    B_OWNER_REQUIRE(bool(events));
}
template<class R> void finish(const R& r) {
    uint64_t entries=0,nodes=0,used=0;
    for (size_t i=0;i<r.ownerNet.size();++i) {
        if(r.ownerNet[i]>=0) ++used;
        if(r.userOverflow[i]) {++nodes;entries+=r.userOverflow[i]->size();}
    }
    B_OWNER_REQUIRE(entries==stats["live_overflow_entries"] && nodes==stats["live_overflow_nodes"]);
    stats["final_owned_nodes"]=used;
    events.flush(); B_OWNER_REQUIRE(bool(events)); events.close();
    std::ofstream out(prefix+".json"); out<<"{\n"; bool first=true;
    for(const auto& kv:stats) {if(!first)out<<",\n";first=false;out<<"  \""<<kv.first<<"\": "<<kv.second;}
    out<<"\n}\n";out.flush();B_OWNER_REQUIRE(bool(out));
}
}

#undef B_OWNER_REQUIRE
