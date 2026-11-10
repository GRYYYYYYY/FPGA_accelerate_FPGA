#!/usr/bin/env python3
"""Reuse frozen decoder logic, adding bounded searches and routing edge order."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/derived/vitis_graph_kernel_20261023_v2/compact'
TARGET=ROOT/'hardware/vitis/search_graph_adjacency.hpp'

def derive():
    header=(BASE/'graph_body.hpp').read_text();header=header[header.index('enum GraphConfig'):header.index('// Host must validate')]
    body=(BASE/'graph_body.cpp').read_text();body=body[body.index('struct EdgeRecord'):body.index('extern "C" void graph_expand_body')]
    body=body.replace('static uint32_t decode(', 'template<unsigned Mode>\nstatic uint32_t decode(').replace('c[MODE]!=1','c[MODE]!=Mode').replace('if(false) {','if(Mode==0) {')
    if body.count('while (lo<hi) {')!=3:raise ValueError('Unknown binary search source')
    body=body.replace('while (lo<hi) {','for (unsigned search_step=0;search_step<32;++search_step) {if(lo>=hi)break;')
    old='while(j>0 && less_edge(value,buffer[j-1])) {buffer[j]=buffer[j-1];j--;}'
    if body.count(old)!=1:raise ValueError('Unknown stable decoder sort')
    body=body.replace(old,'for(unsigned shift=0;shift<MAX_DEGREE;++shift) {if(!j || !less_edge(value,buffer[j-1]))break;buffer[j]=buffer[j-1];j--;}')
    return '''#pragma once
#include "search_controller.hpp"
// Derived from the frozen full-image decoder. Host still validates the AGRAPH01
// image/descriptor identity. bind additionally checks every section address span.
namespace fpga_search { namespace graph_decode {
'''+header+body+'''} // namespace graph_decode

template<unsigned Mode> class ImageAdjacency {
    static_assert(Mode<=1,"unknown graph representation");
    const uint32_t* image_=nullptr;
    uint32_t config_[graph_decode::CFG_WORDS]{};
    graph_decode::EdgeRecord buffer_[graph_decode::MAX_DEGREE];
    bool ready_=false;
    static bool route_less(const graph_decode::EdgeRecord& a,const graph_decode::EdgeRecord& b) {
        // Native RoutingGraph stable order: dst,tile,pip,dir,src-wire,dst-wire.
        const unsigned order[4]={0,1,2,6};
        for(unsigned i=0;i<4;++i){const unsigned k=order[i];if(a.w[k]!=b.w[k])return a.w[k]<b.w[k];}
        const unsigned source_a=a.w[6]?4:3,source_b=b.w[6]?4:3;
        if(a.w[source_a]!=b.w[source_b])return a.w[source_a]<b.w[source_b];
        return a.w[7-source_a]<b.w[7-source_b];
    }
public:
    RowStatus bind(const uint32_t* image,const uint32_t* config,uint32_t image_words) {
        using namespace graph_decode;
        ready_=false;
        if(!image || !config || !image_words || image_words>IMAGE_DEPTH || config[IMAGE_WORDS]!=image_words || config[MODE]!=Mode || !config[NODE_COUNT] || !config[ATTR_COUNT])return RowStatus::invalid;
        const unsigned widths[12]={4,6,3,3,7,2,7,1,7,2,2,7};
        for(unsigned i=0;i<12;++i) {
            const uint64_t base=config[1+2*i],count=config[2+2*i];
            if(base>image_words || count*widths[i]>image_words-base)return RowStatus::invalid;
        }
        for(unsigned i=0;i<CFG_WORDS;++i)config_[i]=config[i];
        image_=image;ready_=true;return RowStatus::known;
    }
    unsigned node_count()const{return ready_?config_[graph_decode::NODE_COUNT]:0;}
    RowStatus neighbors(uint32_t node,LabelEdge* out,unsigned capacity,unsigned& count) {
        using namespace graph_decode;
        count=0;if(!ready_)return RowStatus::invalid;
        uint32_t degree=0;const uint32_t status=decode<Mode>(image_,config_,node,buffer_,degree);
        if(status==1)return RowStatus::unknown;
        if(status==2 || (status==0 && degree>capacity))return RowStatus::capacity_exhausted;
        if(status)return RowStatus::invalid;
        // Stable reordering preserves parallel edges and original tie order.
        for(unsigned i=1;i<MAX_DEGREE;++i) {
            if(i>=degree)break;
            const EdgeRecord value=buffer_[i];unsigned j=i;
            for(unsigned shift=0;shift<MAX_DEGREE;++shift){if(!j || !route_less(value,buffer_[j-1]))break;buffer_[j]=buffer_[j-1];--j;}
            buffer_[j]=value;
        }
        for(unsigned i=0;i<MAX_DEGREE;++i) {
            if(i>=degree)break;
            const auto& e=buffer_[i];out[i]={e.w[0],e.w[1],e.w[2],e.w[3],e.w[4],e.w[5],e.w[6]};
        }
        count=degree;return RowStatus::known;
    }
};
} // namespace fpga_search
'''

if __name__=='__main__':
    with TARGET.open('x') as f:f.write(derive())
    print(TARGET)
