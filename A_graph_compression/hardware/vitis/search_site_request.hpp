#pragma once
#include "search_key_words.hpp"
namespace fpga_search {
// Convert a canonical node-zero state to sorted [kind/id,mask,value] requests.
// Caller provides disjoint buffers. All validation precedes any output write.
template<unsigned Requests=65536> struct SiteRequest {
    using Words=LabelKeyWords<1,32,16,8>;
    static unsigned run(const uint64_t* state,uint64_t* request,unsigned& count){
        count=0;typename Words::Key key{};
        if(!Words::load(state,0,key) || key.node)return 1;
        const unsigned n=key.state.signals.count+key.state.bits.count+key.state.values.count;
        if(n>Requests)return 2;
        unsigned at=0;
        for(unsigned i=0;i<key.state.signals.count;++i){request[3*at]=key.state.signals.data[i];request[3*at+1]=0;request[3*at+2]=0;++at;}
        for(unsigned i=0;i<key.state.bits.count;++i){const auto& b=key.state.bits.data[i];request[3*at]=(UINT64_C(1)<<32)|b.field;request[3*at+1]=b.mask;request[3*at+2]=b.value;++at;}
        for(unsigned i=0;i<key.state.values.count;++i){const auto& v=key.state.values.data[i];request[3*at]=(UINT64_C(2)<<32)|v.field;request[3*at+1]=0;request[3*at+2]=v.value;++at;}
        count=n;return 0;
    }
};
}
