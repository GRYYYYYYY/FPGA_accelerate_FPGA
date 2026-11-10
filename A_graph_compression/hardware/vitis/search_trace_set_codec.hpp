#pragma once
#include <cstdint>
namespace fpga_search {
// Lossless maximal consecutive runs: unsigned LEB128(gap), LEB128(length).
// First gap is the absolute first key; later gaps are from the previous last.
// Canonical fallback to raw u64 when RLE does not strictly reduce byte count.
template<unsigned Max=1100754> struct TraceSetCodec {
    static_assert(Max>0 && Max<=1100754,"invalid sorted-set capacity");
    static unsigned leb_size(uint64_t value){unsigned n=1;for(unsigned i=0;i<9;++i){if(value<128)break;value>>=7;++n;}return n;}
    static bool measure(const uint64_t* keys,unsigned count,unsigned& encoding,uint64_t& bytes){
        if(count>Max)return false;
        for(unsigned i=1;i<count;++i)if(keys[i]<=keys[i-1])return false;
        uint64_t rle=0,previous=0;unsigned at=0;
        for(unsigned run=0;run<Max && at<count;++run){
            const unsigned first=at;const uint64_t start=keys[at];++at;
            for(unsigned step=0;step<Max && at<count;++step){if(keys[at-1]==UINT64_MAX || keys[at]!=keys[at-1]+1)break;++at;}
            rle+=leb_size(first?start-previous:start)+leb_size(at-first);previous=keys[at-1];
        }
        const uint64_t raw=uint64_t(count)*8;encoding=rle<raw?1:0;bytes=encoding?rle:raw;return true;
    }
    struct Bytes {
        uint64_t* out;unsigned at=0;uint64_t word=0;unsigned lane=0;
        void byte(unsigned value){word|=uint64_t(value)<<(8*lane);if(++lane==8){out[at++]=word;word=0;lane=0;}}
        void leb(uint64_t value){for(unsigned i=0;i<10;++i){const unsigned b=unsigned(value&127);value>>=7;byte(b|(value?128:0));if(!value)break;}}
        void finish(){if(lane)out[at]=word;}
    };
    // Caller pre-reserves ceil(bytes/8) disjoint words. Invalid input/capacity
    // rejection leaves all output words unchanged.
    static bool encode(const uint64_t* keys,unsigned count,unsigned capacity_words,uint64_t* out,unsigned& encoding,uint64_t& bytes){
        if(!measure(keys,count,encoding,bytes) || (bytes+7)/8>capacity_words)return false;
        if(!encoding){for(unsigned i=0;i<count;++i)out[i]=keys[i];return true;}
        Bytes writer{out};uint64_t previous=0;unsigned at=0;
        for(unsigned run=0;run<Max && at<count;++run){
            const unsigned first=at;const uint64_t start=keys[at];++at;
            for(unsigned step=0;step<Max && at<count;++step){if(keys[at-1]==UINT64_MAX || keys[at]!=keys[at-1]+1)break;++at;}
            writer.leb(first?start-previous:start);writer.leb(at-first);previous=keys[at-1];
        }
        writer.finish();return true;
    }
};
}
