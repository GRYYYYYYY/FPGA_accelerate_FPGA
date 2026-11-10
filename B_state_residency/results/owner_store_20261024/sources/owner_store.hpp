#pragma once
#include <array>
#include <cstdint>
#include <limits>
#include <vector>

// Executable memory-layout specification, not HLS or an AXI implementation.
// Primary: net+1, refs16|occupancy16, overflow_head+1, reserved.
// Pool: net+1, refs32, next+1, reserved. Free entries have net=refs=0.
// Allocator: next_unused, free_head+1, live_entries, reserved.
namespace owner_state {
using Record = std::array<uint32_t,4>;
enum Status : uint32_t { OK=0, RANGE=1, UNDERFLOW=2, REF_LIMIT=3,
    OCC_LIMIT=4, CAPACITY=5, CORRUPT=6, BAD_OP=7, STALE=8 };
enum Op : uint32_t { GET=0, INC=1, DEC=2 };
struct Write { uint32_t region,index; Record before,after; };
struct Plan {
    uint64_t generation=0;
    Status status=OK;
    uint32_t count=0,occupancy=0,will_overuse=0;
    std::vector<Write> writes;
};
class Store {
public:
    std::vector<Record> primary,pool;
    Record allocator{};
    uint64_t generation=0;
    Store(uint32_t nodes,uint32_t entries):primary(nodes),pool(entries) {}
    Record& record(uint32_t region,uint32_t index) {
        return region==0?primary.at(index):region==1?pool.at(index):allocator;
    }
    Plan prepare(uint32_t op,uint32_t node,uint32_t net) const {
        Plan p; p.generation=generation;
        auto error=[&](Status s){p.status=s;p.writes.clear();return p;};
        if(op>DEC)return error(BAD_OP);
        if(node>=primary.size() || net>uint32_t(INT32_MAX))return error(RANGE);
        if(allocator[3] || allocator[0]>pool.size() || allocator[1]>allocator[0] || allocator[2]>allocator[0])return error(CORRUPT);
        Record a=primary[node],meta=allocator;
        uint32_t refs=a[1]&65535,occ=a[1]>>16,key=net+1;
        if(a[3] || (a[0]==0 ? (a[1]!=0 || a[2]!=0) : (a[0]>uint32_t(INT32_MAX)+1u || refs==0 || occ==0)))return error(CORRUPT);
        uint32_t ptr=a[2],found=0,previous=0,found_previous=0,hops=0;
        std::vector<uint32_t> keys;
        while(ptr) {
            if(ptr>allocator[0] || ++hops>pool.size())return error(CORRUPT);
            const auto& r=pool[ptr-1];
            if(r[3] || !r[0] || r[0]>uint32_t(INT32_MAX)+1u || !r[1] || r[1]>65535 || r[0]==a[0])return error(CORRUPT);
            for(auto old:keys)if(old==r[0])return error(CORRUPT);
            keys.push_back(r[0]);
            if(r[0]==key){found=ptr;found_previous=previous;}
            previous=ptr;ptr=r[2];
        }
        if(occ!=hops+uint32_t(a[0]!=0) || hops>allocator[2])return error(CORRUPT);
        uint32_t count=a[0]==key?refs:found?pool[found-1][1]:0;
        p.count=count;p.occupancy=occ;p.will_overuse=occ>1 || (occ==1 && count==0);
        if(op==GET)return p;
        if(generation==UINT64_MAX)return error(STALE);
        auto write=[&](uint32_t region,uint32_t index,Record value) {
            const auto& old=region==0?primary[index]:region==1?pool[index]:allocator;
            if(old!=value)p.writes.push_back({region,index,old,value});
        };
        auto release=[&](uint32_t entry) {
            write(1,entry-1,Record{{0,0,meta[1],0}});
            meta[1]=entry;--meta[2];
        };
        if(op==INC) {
            if(count==65535)return error(REF_LIMIT);
            if(count) {
                if(a[0]==key){++refs;a[1]=(occ<<16)|refs;write(0,node,a);}
                else {auto r=pool[found-1];++r[1];write(1,found-1,r);}
            } else {
                if(occ==65535)return error(OCC_LIMIT);
                if(!a[0]){a[0]=key;a[1]=0x10001;write(0,node,a);}
                else {
                    uint32_t entry=meta[1];
                    if(entry) {
                        if(entry>meta[0])return error(CORRUPT);
                        const auto& free=pool[entry-1];
                        if(free[0] || free[1] || free[3] || free[2]>meta[0] || free[2]==entry)return error(CORRUPT);
                        meta[1]=free[2];
                    } else {
                        if(meta[0]==pool.size())return error(CAPACITY);
                        entry=++meta[0];
                        if(pool[entry-1]!=Record{})return error(CORRUPT);
                    }
                    ++meta[2];
                    write(1,entry-1,Record{{key,1,a[2],0}});
                    a[2]=entry;a[1]=((occ+1)<<16)|refs;write(0,node,a);write(2,0,meta);
                }
            }
            ++count;if(p.count==0)++occ;
        } else {
            if(!count)return error(UNDERFLOW);
            if(a[0]==key) {
                if(refs>1){--refs;a[1]=(occ<<16)|refs;write(0,node,a);}
                else {
                    --occ;
                    if(a[2]) {
                        auto r=pool[a[2]-1];
                        if(!meta[2])return error(CORRUPT);
                        release(a[2]);a=Record{{r[0],(occ<<16)|r[1],r[2],0}};
                        write(2,0,meta);
                    } else a=Record{};
                    write(0,node,a);
                }
            } else {
                auto r=pool[found-1];
                if(r[1]>1){--r[1];write(1,found-1,r);}
                else {
                    if(!meta[2])return error(CORRUPT);
                    if(found_previous){auto prev=pool[found_previous-1];prev[2]=r[2];write(1,found_previous-1,prev);}
                    else a[2]=r[2];
                    release(found);--occ;a[1]=(occ<<16)|refs;
                    write(0,node,a);write(2,0,meta);
                }
            }
            --count;
        }
        p.count=count;p.occupancy=occ;p.will_overuse=occ>1 || (occ==1 && count==0);
        return p;
    }
    Status commit(const Plan& p) {
        if(p.status!=OK)return p.status;
        if(p.generation!=generation)return STALE;
        for(const auto& w:p.writes)if(record(w.region,w.index)!=w.before)return STALE;
        for(const auto& w:p.writes)record(w.region,w.index)=w.after;
        if(!p.writes.empty())++generation;
        return OK;
    }
};
}
