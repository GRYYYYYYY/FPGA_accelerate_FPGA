#pragma once
#include <cstdint>

namespace fpga_search {
enum class OccupancyStatus : uint64_t { ok=0, invalid=1, capacity=2, missing_owner=3, overflow=4 };

// Mutable canonical-node ownership, separate from the search label index.
// keys/flags form a bounded hash set of (net,node); 0=empty,1=live,2=tombstone.
// Per-node counts count distinct NETS, never sink paths or template instances.
// meta=[magic,node_count,live_pairs,version]. Only reset initializes storage.
// All buffers must be disjoint, exclusively owned and sufficiently allocated.
// The table is trusted state produced by these operations, not arbitrary input.
// No member stores an external pointer; top arguments are passed explicitly.
template<unsigned MaxNodes,unsigned Slots> struct NodeOccupancy {
    static_assert(MaxNodes>0 && MaxNodes<=0x3fffffffu,"invalid node capacity");
    static_assert(Slots>0 && Slots<=0x40000000u && (Slots&(Slots-1))==0,"slots must be power of two");
    static constexpr uint64_t Magic=0x414e4f44454f5731ULL;
    static uint64_t key(uint32_t net,uint32_t node) { return (uint64_t(net)<<32)|node; }
    static unsigned hash(uint64_t value) {
        value^=value>>33; value*=0xff51afd7ed558ccdULL; value^=value>>33;
        return unsigned(value)&(Slots-1);
    }
    static unsigned locate(const uint64_t* keys,const uint32_t* flags,uint64_t value,bool& found) {
        const unsigned start=hash(value);unsigned free_slot=Slots;found=false;
        for(unsigned i=0;i<Slots;++i) {
            const unsigned at=(start+i)&(Slots-1), flag=flags[at];
            if(flag==1 && keys[at]==value) {found=true;return at;}
            if(flag!=1 && free_slot==Slots) free_slot=at;
            if(flag==0) return free_slot;
        }
        return free_slot;
    }
    static bool valid_meta(const uint64_t* meta) {
        return meta[0]==Magic && meta[1]>0 && meta[1]<=MaxNodes && meta[2]<=Slots && meta[3]>0;
    }
    static bool valid_nodes(const uint32_t* data,unsigned count,unsigned nodes) {
        for(unsigned i=0;i<MaxNodes;++i) {
            if(i>=count)break;
            if(data[i]>=nodes || (i && data[i]<=data[i-1]))return false;
        }
        return true;
    }
    static bool contains(const uint32_t* data,unsigned count,uint32_t node) {
        unsigned lo=0,hi=count;
        for(unsigned i=0;i<32;++i) {
            if(lo>=hi)break;
            unsigned mid=lo+(hi-lo)/2;
            if(data[mid]<node)lo=mid+1;else hi=mid;
        }
        return lo<count && data[lo]==node;
    }
    static OccupancyStatus reset(unsigned nodes,uint64_t* meta,uint32_t* counts,
                                 uint64_t* history,uint32_t* flags) {
        if(nodes>MaxNodes)return OccupancyStatus::capacity;
        if(!nodes)return OccupancyStatus::invalid;
        for(unsigned i=0;i<Slots;++i)flags[i]=0;
        for(unsigned i=0;i<MaxNodes;++i) {if(i>=nodes)break;counts[i]=0;history[i]=0;}
        meta[0]=Magic;meta[1]=nodes;meta[2]=0;meta[3]=1;
        return OccupancyStatus::ok;
    }
    // Atomically release old_nodes and acquire new_nodes for net. Both lists
    // are sorted unique canonical IDs. Existing acquisitions are idempotent.
    // This is a set update; the caller supplies its complete old route when
    // replacing a route. Failures preserve all persistent state byte-for-byte.
    static OccupancyStatus update(uint32_t net,const uint32_t* old_nodes,unsigned old_count,
                                  const uint32_t* new_nodes,unsigned new_count,uint64_t* meta,
                                  uint32_t* counts,uint64_t* keys,uint32_t* flags) {
        if(old_count>MaxNodes || new_count>MaxNodes)return OccupancyStatus::capacity;
        if(!valid_meta(meta))return OccupancyStatus::invalid;
        if(meta[3]==UINT64_MAX)return OccupancyStatus::overflow;
        const unsigned nodes=unsigned(meta[1]);
        if(!valid_nodes(old_nodes,old_count,nodes) || !valid_nodes(new_nodes,new_count,nodes))
            return OccupancyStatus::invalid;
        if(old_count>meta[2])return OccupancyStatus::missing_owner;
        for(unsigned i=0;i<MaxNodes;++i) {
            if(i>=old_count)break;
            bool found=false;locate(keys,flags,key(net,old_nodes[i]),found);
            if(!found)return OccupancyStatus::missing_owner;
            if(!counts[old_nodes[i]])return OccupancyStatus::invalid;
        }
        uint64_t added=0;
        for(unsigned i=0;i<MaxNodes;++i) {
            if(i>=new_count)break;
            bool found=false;locate(keys,flags,key(net,new_nodes[i]),found);
            if(!found || contains(old_nodes,old_count,new_nodes[i]))++added;
            if(!found && counts[new_nodes[i]]==UINT32_MAX)return OccupancyStatus::overflow;
        }
        const uint64_t final_count=meta[2]-old_count+added;
        if(final_count>Slots)return OccupancyStatus::capacity;
        // After preflight, removals and additions cannot fail for owned state.
        for(unsigned i=0;i<MaxNodes;++i) {
            if(i>=old_count)break;
            bool found=false;unsigned at=locate(keys,flags,key(net,old_nodes[i]),found);
            flags[at]=2;--counts[old_nodes[i]];
        }
        for(unsigned i=0;i<MaxNodes;++i) {
            if(i>=new_count)break;
            bool found=false;const auto value=key(net,new_nodes[i]);unsigned at=locate(keys,flags,value,found);
            if(!found){keys[at]=value;flags[at]=1;++counts[new_nodes[i]];}
        }
        meta[2]=final_count;++meta[3];return OccupancyStatus::ok;
    }
    // Exactly the native round penalty: number of distinct owners minus one.
    // Check the complete active domain for overflow before changing history.
    static OccupancyStatus advance(uint64_t* meta,const uint32_t* counts,uint64_t* history,
                                   uint64_t& conflict_nodes) {
        if(!valid_meta(meta))return OccupancyStatus::invalid;
        if(meta[3]==UINT64_MAX)return OccupancyStatus::overflow;
        uint64_t conflicts=0;
        for(unsigned n=0;n<MaxNodes;++n) {
            if(n>=meta[1])break;
            if(counts[n]>1) {
                const uint64_t delta=uint64_t(counts[n])-1;
                if(history[n]>UINT64_MAX-delta)return OccupancyStatus::overflow;
                ++conflicts;
            }
        }
        for(unsigned n=0;n<MaxNodes;++n) {
            if(n>=meta[1])break;
            if(counts[n]>1)history[n]+=uint64_t(counts[n])-1;
        }
        ++meta[3];conflict_nodes=conflicts;return OccupancyStatus::ok;
    }
    // ABI-compatible [other_owner_count,history] words for the search packet.
    // A net owning multiple sink paths through one node is subtracted once.
    static OccupancyStatus snapshot(uint32_t net,const uint64_t* meta,const uint32_t* counts,
                                    const uint64_t* history,const uint64_t* keys,const uint32_t* flags,
                                    uint64_t* output) {
        if(!valid_meta(meta))return OccupancyStatus::invalid;
        for(unsigned n=0;n<MaxNodes;++n) {
            if(n>=meta[1])break;
            bool found=false;if(counts[n])locate(keys,flags,key(net,n),found);
            output[2*n]=uint64_t(counts[n])-(found?1:0);output[2*n+1]=history[n];
        }
        return OccupancyStatus::ok;
    }
};
using ProductionNodeOccupancy=NodeOccupancy<1048576,2097152>;
} // namespace fpga_search
