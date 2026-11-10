// Test the actual generated helper against original binary lookup.
#include "graph_body.cpp"
#include <cassert>
#include <iostream>
#include <climits>
int main() {
    uint32_t cfg[CFG_WORDS]={};
    cfg[GRID_BASE]=0;cfg[GRID_COUNT]=5;cfg[TILE_COUNT]=8;
    uint32_t im[15]={uint32_t(INT_MIN),uint32_t(INT_MIN),0,
                    uint32_t(-1),2,1,0,0,2,0,1,3,
                    uint32_t(INT_MAX),uint32_t(INT_MAX),4};
    const int32_t xy[][2]={{INT_MIN,INT_MIN},{-1,2},{0,0},{0,1},
                          {INT_MAX,INT_MAX},{-1,1},{1,0},{INT_MAX,0}};
    unsigned checked=0;
    for(unsigned pattern=0;pattern<3;pattern++) {
        TileCache cache={false,0,0,0};
        for(unsigned i=0;i<128;i++) {
            unsigned key=pattern==0?0:(pattern==1?(i/4)%8:i%8);
            for(unsigned prior_error=0;prior_error<2;prior_error++) {
                bool a=!prior_error,b=a;
                uint32_t expected=tile_lookup(im,cfg,xy[key][0],xy[key][1],a);
                uint32_t actual=cached_tile_lookup(im,cfg,xy[key][0],xy[key][1],b,cache);
                assert(actual==expected && a==b);checked++;
            }
        }
    }
    // Invalid tile identifiers must never become cache hits.
    im[8]=99;TileCache invalid={false,0,0,0};
    for(unsigned i=0;i<2;i++) {
        bool ok=true;assert(cached_tile_lookup(im,cfg,0,0,ok,invalid)==99);
        assert(!ok && !invalid.valid);checked++;
    }
    // An unsuccessful lookup invalidates the preceding successful entry.
    im[8]=2;TileCache cache={false,0,0,0};bool ok=true;
    assert(cached_tile_lookup(im,cfg,0,0,ok,cache)==2 && cache.valid);
    cached_tile_lookup(im,cfg,1,0,ok,cache);assert(!ok && !cache.valid);checked++;
    // Fresh per-node state observes a changed image even with identical coordinates.
    im[8]=7;TileCache fresh={false,0,0,0};ok=true;
    assert(cached_tile_lookup(im,cfg,0,0,ok,fresh)==7 && ok);checked++;
    cfg[GRID_COUNT]=0;fresh.valid=false;ok=true;
    assert(cached_tile_lookup(im,cfg,0,0,ok,fresh)==0 && !ok && !fresh.valid);checked++;
    std::cout<<"TILE_CACHE_HELPER_PASS checks="<<checked<<"\n";
}
