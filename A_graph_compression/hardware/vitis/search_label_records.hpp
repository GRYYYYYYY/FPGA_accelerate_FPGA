#pragma once
#include <stdint.h>

namespace fpga_search {
struct LabelEdge {uint32_t dst,tile,pip,up,down,attr,dir;};
struct LabelRecord {uint64_t cost;uint32_t parent;bool root;LabelEdge edge;};
enum class RecordStatus : uint8_t { ok, not_improved, capacity_exhausted, invalid };

// Explicit word ABI: cost,parent,root,dst,tile,pip,up,down,attr,dir.
// The key for record i is separately held at key index i by LabelIndex.
// Caller supplies count and Capacity*10 words; inactive storage is never read.
template<unsigned Capacity> struct LabelRecords {
    static_assert(Capacity>0 && Capacity<=0x19999999u,"label word offset overflow");
    static RecordStatus read(const uint64_t* words,unsigned count,unsigned index,LabelRecord& out) {
        if (count>Capacity || index>=count) return RecordStatus::invalid;
        const unsigned base=10*index;
        if (words[base+1]>UINT32_MAX || words[base+2]>1) return RecordStatus::invalid;
        for (unsigned j=3;j<10;++j) if (words[base+j]>UINT32_MAX) return RecordStatus::invalid;
        LabelRecord value{words[base],uint32_t(words[base+1]),words[base+2]!=0,
            {uint32_t(words[base+3]),uint32_t(words[base+4]),uint32_t(words[base+5]),
             uint32_t(words[base+6]),uint32_t(words[base+7]),uint32_t(words[base+8]),uint32_t(words[base+9])}};
        if (value.root) {
            if (value.cost || value.parent) return RecordStatus::invalid;
        } else if (!value.cost || value.cost==UINT64_MAX || value.parent>=count || value.parent==index) return RecordStatus::invalid;
        out=value;return RecordStatus::ok;
    }
    static RecordStatus cost(const uint64_t* words,unsigned count,unsigned index,uint64_t& out) {
        if (count>Capacity || index>=count) return RecordStatus::invalid;
        out=words[10*index];return RecordStatus::ok;
    }
    static void store(uint64_t* words,unsigned index,const LabelRecord& value) {
        const unsigned base=10*index;
        words[base]=value.cost;words[base+1]=value.parent;words[base+2]=value.root?1:0;
        words[base+3]=value.edge.dst;words[base+4]=value.edge.tile;words[base+5]=value.edge.pip;
        words[base+6]=value.edge.up;words[base+7]=value.edge.down;words[base+8]=value.edge.attr;words[base+9]=value.edge.dir;
    }
    static RecordStatus append_root(uint64_t* words,unsigned& count,unsigned& index) {
        if (count>Capacity) return RecordStatus::invalid;
        if (count==Capacity) return RecordStatus::capacity_exhausted;
        store(words,count,{0,0,true,{0,0,0,0,0,0,0}});index=count;++count;return RecordStatus::ok;
    }
    static RecordStatus append_child(uint64_t* words,unsigned& count,uint64_t new_cost,
                                      unsigned parent,const LabelEdge& edge,unsigned& index) {
        if (count>Capacity) return RecordStatus::invalid;
        if (count==Capacity) return RecordStatus::capacity_exhausted;
        LabelRecord p{};
        if (!new_cost || new_cost==UINT64_MAX || read(words,count,parent,p)!=RecordStatus::ok || p.cost>=new_cost) return RecordStatus::invalid;
        store(words,count,{new_cost,parent,false,edge});index=count;++count;return RecordStatus::ok;
    }
    static RecordStatus improve(uint64_t* words,unsigned count,unsigned index,uint64_t new_cost,
                                 unsigned parent,const LabelEdge& edge) {
        LabelRecord current{},p{};
        if (read(words,count,index,current)!=RecordStatus::ok || current.root) return RecordStatus::invalid;
        if (new_cost>=current.cost) return RecordStatus::not_improved;
        if (!new_cost || parent==index || read(words,count,parent,p)!=RecordStatus::ok || p.cost>=new_cost) return RecordStatus::invalid;
        store(words,index,{new_cost,parent,false,edge});return RecordStatus::ok;
    }
    // Validate a full parent chain without writing output or assuming that
    // parent IDs precede child IDs. Improvements can point to newer labels.
    static RecordStatus validate_path(const uint64_t* words,unsigned count,unsigned target,unsigned& edges) {
        if (count>Capacity || target>=count) return RecordStatus::invalid;
        unsigned cursor=target,n=0;
        for (unsigned step=0;step<Capacity;++step) {
            LabelRecord current{},p{};
            if (read(words,count,cursor,current)!=RecordStatus::ok) return RecordStatus::invalid;
            if (current.root) {edges=n;return RecordStatus::ok;}
            if (read(words,count,current.parent,p)!=RecordStatus::ok || p.cost>=current.cost) return RecordStatus::invalid;
            cursor=current.parent;++n;
        }
        return RecordStatus::invalid;
    }
};
} // namespace fpga_search
