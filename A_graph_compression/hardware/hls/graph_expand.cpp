#include "graph_expand.hpp"
struct EdgeRecord { uint32_t w[7]; };

static uint32_t offset32(const uint32_t *image, uint32_t base, uint32_t index, bool &ok) {
    if (image[base+2*index+1] != 0) ok=false;
    return image[base+2*index];
}
static uint32_t tile_lookup(const uint32_t *im, const uint32_t *c, int32_t x, int32_t y, bool &ok) {
    uint32_t lo=0, hi=c[GRID_COUNT];
    while (lo<hi) {
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
    while (lo<hi) {
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
    while (lo<hi) {uint32_t mid=lo+(hi-lo)/2;if(im[base+width*mid]<key)lo=mid+1;else hi=mid;}
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
static uint32_t decode(const uint32_t *im, const uint32_t *c, uint32_t node,
                       EdgeRecord buffer[MAX_DEGREE], uint32_t &degree) {
    degree=0;
    if(node>=c[NODE_COUNT] || c[MODE]>1)return 4;
    uint32_t nbase=c[NODE_BASE]+4*node;
    int32_t row=(int32_t)im[nbase+3];
    if(row==-1)return 1;
    if(row<0)return 4;
    bool ok=true;
    if(c[MODE]==0) {
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
            while(j>0 && less_edge(value,buffer[j-1])) {buffer[j]=buffer[j-1];j--;}
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

extern "C" void graph_expand(const uint32_t image[IMAGE_DEPTH],
    const uint32_t config[CFG_WORDS], const uint32_t requests[MAX_REQUESTS],
    uint32_t output[OUTPUT_DEPTH], uint32_t result[RESULT_DEPTH],
    uint32_t request_count, uint32_t output_capacity_words,
    uint32_t &written_records, uint32_t &failed_requests) {
#pragma HLS INTERFACE m_axi port=image offset=slave bundle=graph depth=2097152
#pragma HLS INTERFACE m_axi port=config offset=slave bundle=control_data depth=32
#pragma HLS INTERFACE m_axi port=requests offset=slave bundle=control_data depth=65536
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=output_data depth=1048576
#pragma HLS INTERFACE m_axi port=result offset=slave bundle=output_data depth=196608
#pragma HLS INTERFACE s_axilite port=image bundle=control
#pragma HLS INTERFACE s_axilite port=config bundle=control
#pragma HLS INTERFACE s_axilite port=requests bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=result bundle=control
#pragma HLS INTERFACE s_axilite port=request_count bundle=control
#pragma HLS INTERFACE s_axilite port=output_capacity_words bundle=control
#pragma HLS INTERFACE s_axilite port=written_records bundle=control
#pragma HLS INTERFACE s_axilite port=failed_requests bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    uint32_t c[CFG_WORDS];
    EdgeRecord buffer[MAX_DEGREE];
#pragma HLS BIND_STORAGE variable=buffer type=ram_2p impl=bram
    for(unsigned i=0;i<CFG_WORDS;i++)c[i]=config[i];
    written_records=0;failed_requests=0;
    if(request_count>MAX_REQUESTS || output_capacity_words>OUTPUT_DEPTH) {failed_requests=request_count;return;}
    for(uint32_t q=0;q<request_count;q++) {
        uint32_t node=requests[q], degree=0, start=written_records;
        uint32_t status=decode(image,c,node,buffer,degree);
        if(status==0 && degree>output_capacity_words/8-written_records)status=2;
        if(status==0) {
            for(uint32_t i=0;i<degree;i++) {
                uint32_t out=8*(written_records+i);output[out]=node;
                for(unsigned k=0;k<7;k++)output[out+1+k]=buffer[i].w[k];
            }
            written_records+=degree;
        } else {failed_requests++;degree=0;}
        result[3*q]=start;result[3*q+1]=degree;result[3*q+2]=status;
    }
}
