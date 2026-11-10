#pragma once
#include "search_controller.hpp"
// Derived from the frozen full-image decoder. Host still validates the AGRAPH01
// image/descriptor identity. bind additionally checks every section address span.
namespace fpga_search { namespace graph_decode {
enum GraphConfig { MODE, NODE_BASE, NODE_COUNT, TILE_BASE, TILE_COUNT,
    GRID_BASE, GRID_COUNT, ALIAS_BASE, ALIAS_COUNT, INSTANCE_BASE, INSTANCE_COUNT,
    TPL_BASE, TPL_COUNT, RULE_BASE, RULE_COUNT, REMOVE_BASE, REMOVE_COUNT,
    ADD_BASE, ADD_COUNT, PATCH_BASE, PATCH_COUNT, CSR_OFF_BASE, CSR_OFF_COUNT,
    CSR_EDGE_BASE, CSR_EDGE_COUNT, STRING_COUNT, ATTR_COUNT, IMAGE_WORDS, CFG_WORDS=32 };
enum { MAX_DEGREE=1024, MAX_REQUESTS=65536, IMAGE_DEPTH=33554432,
       OUTPUT_DEPTH=1048576, RESULT_DEPTH=3*MAX_REQUESTS };
struct EdgeRecord { uint32_t w[7]; };

static uint32_t offset32(const uint32_t *image, uint32_t base, uint32_t index, bool &ok) {
    if (image[base+2*index+1] != 0) ok=false;
    return image[base+2*index];
}
static uint32_t tile_lookup(const uint32_t *im, const uint32_t *c, int32_t x, int32_t y, bool &ok) {
    uint32_t lo=0, hi=c[GRID_COUNT];
    for (unsigned search_step=0;search_step<32;++search_step) {if(lo>=hi)break;
        uint32_t mid=lo+(hi-lo)/2, p=c[GRID_BASE]+3*mid;
        int32_t gx=(int32_t)im[p], gy=(int32_t)im[p+1];
        if (gx<x || (gx==x && gy<y)) lo=mid+1; else hi=mid;
    }
    if (lo>=c[GRID_COUNT]) {ok=false;return 0;}
    uint32_t p=c[GRID_BASE]+3*lo;
    if ((int32_t)im[p]!=x || (int32_t)im[p+1]!=y || im[p+2]>=c[TILE_COUNT]) ok=false;
    return im[p+2];
}
static uint32_t alias_lookup(const uint32_t *im, const uint32_t *c, uint32_t tile, uint32_t wire, bool &ok) {
    uint32_t lo=0, hi=c[ALIAS_COUNT];
    for (unsigned search_step=0;search_step<32;++search_step) {if(lo>=hi)break;
        uint32_t mid=lo+(hi-lo)/2, p=c[ALIAS_BASE]+3*mid;
        uint32_t at=im[p], aw=im[p+1];
        if (at<tile || (at==tile && aw<wire)) lo=mid+1; else hi=mid;
    }
    if (lo>=c[ALIAS_COUNT]) {ok=false;return 0;}
    uint32_t p=c[ALIAS_BASE]+3*lo;
    if (im[p]!=tile || im[p+1]!=wire || im[p+2]>=c[NODE_COUNT]) ok=false;
    return im[p+2];
}
static bool indexed_find(const uint32_t *im, uint32_t base, uint32_t count, uint32_t width,
                         uint32_t key, uint32_t &position) {
    uint32_t lo=0, hi=count;
    for (unsigned search_step=0;search_step<32;++search_step) {if(lo>=hi)break;uint32_t mid=lo+(hi-lo)/2;if(im[base+width*mid]<key)lo=mid+1;else hi=mid;}
    position=lo;
    return lo<count && im[base+width*lo]==key;
}
static bool less_edge(const EdgeRecord &a, const EdgeRecord &b) {
    for (unsigned i=0;i<7;i++) {if(a.w[i]<b.w[i])return true;if(a.w[i]>b.w[i])return false;}
    return false;
}
static EdgeRecord expand_rule(const uint32_t *im, const uint32_t *c, uint32_t src,
                               int32_t x, int32_t y, uint32_t base,
                               bool patch, uint32_t attr, bool &ok) {
    EdgeRecord e;
    int64_t tx=(int64_t)x+(int32_t)im[base], ty=(int64_t)y+(int32_t)im[base+1];
    if(tx < -2147483648LL || tx > 2147483647LL || ty < -2147483648LL || ty > 2147483647LL)ok=false;
    uint32_t tile=tile_lookup(im,c,(int32_t)tx,(int32_t)ty,ok);
    uint32_t up=im[base+3], down=im[base+4], dir=im[base+6];
    uint32_t sw=dir?down:up, dw=dir?up:down;
    if(dir>1 || alias_lookup(im,c,tile,sw,ok)!=src)ok=false;
    e.w[0]=alias_lookup(im,c,tile,dw,ok);e.w[1]=tile;e.w[2]=im[base+2];
    e.w[3]=up;e.w[4]=down;e.w[5]=patch?attr:im[base+5];e.w[6]=dir;
    return e;
}
template<unsigned Mode>
static uint32_t decode(const uint32_t *im, const uint32_t *c, uint32_t node,
                       EdgeRecord buffer[MAX_DEGREE], uint32_t &degree) {
    degree=0;
    if(node>=c[NODE_COUNT] || c[MODE]!=Mode)return 4;
    uint32_t nbase=c[NODE_BASE]+4*node;
    int32_t row=(int32_t)im[nbase+3];
    if(row==-1)return 1;
    if(row<0)return 4;
    bool ok=true;
    if(Mode==0) {
        if((uint32_t)row+1>=c[CSR_OFF_COUNT])return 4;
        uint32_t start=offset32(im,c[CSR_OFF_BASE],row,ok), end=offset32(im,c[CSR_OFF_BASE],row+1,ok);
        if(!ok || start>end || end>c[CSR_EDGE_COUNT])return 4;
        if(end-start>MAX_DEGREE)return 2;
        degree=end-start;
        for(uint32_t i=0;i<degree;i++)for(unsigned k=0;k<7;k++)buffer[i].w[k]=im[c[CSR_EDGE_BASE]+7*(start+i)+k];
    } else {
        uint32_t anchor=im[nbase+2];
        if((uint32_t)row>=c[INSTANCE_COUNT] || anchor>=c[TILE_COUNT])return 4;
        int32_t x=(int32_t)im[c[TILE_BASE]+6*anchor+2], y=(int32_t)im[c[TILE_BASE]+6*anchor+3];
        uint32_t b=c[INSTANCE_BASE]+7*row;
        int32_t tid=(int32_t)im[b];
        uint32_t rs=im[b+1],rc=im[b+2],as=im[b+3],ac=im[b+4],ps=im[b+5],pc=im[b+6];
        if(rs>c[REMOVE_COUNT] || rc>c[REMOVE_COUNT]-rs || as>c[ADD_COUNT] || ac>c[ADD_COUNT]-as
             || ps>c[PATCH_COUNT] || pc>c[PATCH_COUNT]-ps)return 4;
        if(tid>=0) {
            if((uint32_t)tid+1>=c[TPL_COUNT])return 4;
            uint32_t start=offset32(im,c[TPL_BASE],tid,ok), end=offset32(im,c[TPL_BASE],tid+1,ok);
            if(!ok || start>end || end>c[RULE_COUNT])return 4;
            for(uint32_t i=start;i<end;i++) {
                uint32_t pos=0;
                if(indexed_find(im,c[REMOVE_BASE]+rs,rc,1,i-start,pos))continue;
                bool patch=indexed_find(im,c[PATCH_BASE]+2*ps,pc,2,i-start,pos);
                uint32_t attr=patch?im[c[PATCH_BASE]+2*(ps+pos)+1]:0;
                if(degree>=MAX_DEGREE)return 2;
                buffer[degree++]=expand_rule(im,c,node,x,y,c[RULE_BASE]+7*i,patch,attr,ok);
            }
        } else if(tid!=-1 || rc || pc)return 4;
        for(uint32_t i=0;i<ac;i++) {
            if(degree>=MAX_DEGREE)return 2;
            buffer[degree++]=expand_rule(im,c,node,x,y,c[ADD_BASE]+7*(as+i),false,0,ok);
        }
        if(!ok)return 3;
        for(uint32_t i=1;i<degree;i++) {
            EdgeRecord value=buffer[i];uint32_t j=i;
            for(unsigned shift=0;shift<MAX_DEGREE;++shift) {if(!j || !less_edge(value,buffer[j-1]))break;buffer[j]=buffer[j-1];j--;}
            buffer[j]=value;
        }
    }
    for(uint32_t i=0;i<degree;i++) {
        const EdgeRecord &e=buffer[i];
        if(e.w[0]>=c[NODE_COUNT] || e.w[1]>=c[TILE_COUNT] || e.w[2]>=c[STRING_COUNT]
             || e.w[3]>=c[STRING_COUNT] || e.w[4]>=c[STRING_COUNT] || e.w[5]>=c[ATTR_COUNT] || e.w[6]>1)return 4;
    }
    return 0;
}

} // namespace graph_decode

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
