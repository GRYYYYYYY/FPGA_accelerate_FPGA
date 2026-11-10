#pragma once
#include "search_key_words.hpp"

namespace fpga_search {
enum class RouteTreeStatus:unsigned {ok=0,invalid=1,capacity=2,overflow=3};

// Current multi-sink tree, separate from retained trace/physical edge output.
// meta=[magic,active_nodes,source,unique_nodes,version]; bits index canonical
// nodes. demands is the original 65-word site-state ABI with node field zero.
// Trusted state originates at reset. All buffers disjoint/exclusively owned.
template<unsigned Nodes=1048576,unsigned Path=524288> struct RouteTree {
    static_assert(Nodes>0 && Nodes<=1048576 && Path>0 && Path<=524288,"invalid production capacity");
    using Words=LabelKeyWords<1,32,16,8>;
    using Status=RouteTreeStatus;
    static constexpr uint64_t Magic=UINT64_C(0x4154524545535431);
    static bool valid(const uint64_t* meta) {
        return meta[0]==Magic && meta[1]>0 && meta[1]<=Nodes && meta[2]<meta[1] &&
               meta[3]>0 && meta[3]<=meta[1] && meta[4]>0;
    }
    static bool contains(const uint64_t* bits,uint32_t node){return ((bits[node/64]>>(node%64))&1)!=0;}
    static Status reset(unsigned nodes,uint32_t source,uint64_t* meta,uint64_t* bits,uint64_t* demands) {
        if(nodes>Nodes)return Status::capacity;
        if(!nodes || source>=nodes)return Status::invalid;
        for(unsigned i=0;i<(nodes+63)/64;++i)bits[i]=0;
        bits[source/64]|=uint64_t(1)<<(source%64);
        for(unsigned i=0;i<Words::Words;++i)demands[i]=0;
        meta[0]=Magic;meta[1]=nodes;meta[2]=source;meta[3]=1;meta[4]=1;return Status::ok;
    }
    static Status accept(uint32_t target,const uint64_t* search_result,const uint32_t* path,
                         uint64_t* meta,uint64_t* bits,uint64_t* demands,bool& applied) {
        applied=false;
        if(!valid(meta) || target>=meta[1] || search_result[15]!=1 || search_result[0]>6)return Status::invalid;
        if(search_result[7]>Path)return Status::capacity;
        if(search_result[0]!=0) {
            if(search_result[7])return Status::invalid;
            for(unsigned i=16;i<81;++i)if(search_result[i])return Status::invalid;
            return Status::ok; // Failed searches leave the accumulated tree intact.
        }
        if(meta[4]==UINT64_MAX)return Status::overflow;
        if(search_result[1]==UINT64_MAX)return Status::invalid;
        typename Words::Key before{},next{},combined{};
        if(!Words::load(demands,0,before) || before.node || !Words::load(search_result+16,0,next) || next.node!=target)return Status::invalid;
        if(merge_site_state(before.state,next.state,combined.state)!=StateStatus::ok)return Status::invalid;
        next.node=0;
        if(!equal_label_key(combined,next))return Status::invalid; // No prior resource may disappear or change incompatibly.
        const unsigned length=unsigned(search_result[7]);
        if(!length) {
            if(!contains(bits,target) || !equal_label_key(before,next))return Status::invalid;
        } else {
            uint32_t previous=path[0];
            if(previous>=meta[1] || !contains(bits,previous))return Status::invalid;
            for(unsigned i=0;i<length;++i) {
                const unsigned at=8*i;
                if(path[at]!=previous || path[at]>=meta[1] || path[at+1]>=meta[1] || path[at+7]>1)return Status::invalid;
                previous=path[at+1];
            }
            if(previous!=target)return Status::invalid;
        }
        // All failure checks precede state changes. Repeated canonical nodes
        // count once, even if a valid search path visits them more than once.
        for(unsigned i=0;i<length;++i) {
            const uint32_t n=path[8*i+1];
            if(!contains(bits,n)){bits[n/64]|=uint64_t(1)<<(n%64);++meta[3];}
        }
        Words::store(demands,0,next);++meta[4];applied=true;return Status::ok;
    }
    static Status roots(const uint64_t* meta,const uint64_t* bits,uint32_t* output,unsigned& count) {
        count=0;if(!valid(meta))return Status::invalid;
        for(unsigned n=0;n<unsigned(meta[1]);++n)if(contains(bits,n))output[count++]=n;
        return Status::ok;
    }
    static Status complete(const uint64_t* meta,const uint64_t* bits,const uint32_t* sinks,unsigned count,bool& done) {
        done=false;if(!valid(meta))return Status::invalid;
        if(count>Nodes)return Status::capacity;
        bool all=true;
        for(unsigned i=0;i<count;++i){if(sinks[i]>=meta[1])return Status::invalid;all=all && contains(bits,sinks[i]);}
        done=all;return Status::ok; // Empty/duplicate sinks retain native all_of semantics.
    }
};
using ProductionRouteTree=RouteTree<>;
} // namespace fpga_search
