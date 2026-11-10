#include "router_provider.hpp"
#include <filesystem>
extern "C" void graph_accel(const uint32_t*,const uint32_t*,const uint32_t*,uint32_t*,uint32_t*,uint32_t*,uint32_t,uint32_t);
int main(int argc,char** argv) {try {
    namespace bg=board_graph;
    bg::require(argc==4,"Usage: provider_test image config full_manifest");
    int mutation=0;uint32_t mutation_node=0,other_node=0;bool found=false,other=false;
    kernel_router::KernelCall invoke=[&](const uint32_t* im,const uint32_t* cf,const uint32_t* rq,
        uint32_t* out,uint32_t* result,uint32_t* count,uint32_t n,uint32_t capacity) {
        graph_accel(im,cf,rq,out,result,count,n,capacity);
        switch(mutation) {
        case 1:count[0]=capacity/8+1;break;
        case 2:count[1]=n+1;break;
        case 3:result[0]=1;break;
        case 4:result[1]=1025;break;
        case 5:result[2]=2;break;
        case 6:result[2]=3;break;
        case 7:result[2]=4;break;
        case 8:result[2]=1;break;
        case 9:out[0]=rq[0]+1;break;
        case 10:out[1]=cf[2];break;
        case 11:out[2]=cf[4];break;
        case 12:out[3]=cf[25];break;
        case 13:out[4]=cf[25];break;
        case 14:out[5]=cf[25];break;
        case 15:out[6]=cf[26];break;
        case 16:out[7]=2;break;
        case 17:out[8*count[0]]=0;break;
        case 18:result[3*n]=0;break;
        case 19:count[2]=0;break;
        case 20:for(unsigned k=0;k<8;++k)std::swap(out[k],out[8+k]);break;
        }
    };
    kernel_router::Provider provider(argv[1],argv[2],1,invoke);
    std::ifstream manifest(argv[3]);std::string image,config,case_path;
    std::vector<std::string> cases;
    while(manifest>>image>>config>>case_path)
        if(std::filesystem::path(case_path).filename().string().rfind("full_",0)==0)cases.push_back(case_path);
    bg::require(cases.size()==9,"Expected nine full-graph golden chunks");
    uint64_t checked=0,records=0,unknown=0;
    for(const auto& path:cases) {
        auto c=bg::fixture(path);
        for(uint32_t begin=0;begin<c.count;begin+=128) {
            uint32_t end=std::min(c.count,begin+128);
            std::vector<uint32_t> requests(c.requests.begin()+begin,c.requests.begin()+end);
            auto rows=provider.decode_batch(requests);
            for(uint32_t index=begin;index<end;++index) {
                auto& row=rows[index-begin];uint32_t start=c.results[3*index],degree=c.results[3*index+1],status=c.results[3*index+2];
                bg::require(row.known==(status==0)&&row.edges.size()==degree,"Golden row status/degree differs");
                for(uint32_t i=0;i<degree;++i) {
                    auto p=c.output.data()+8*(start+i);const auto& edge=row.edges[i];
                    bg::require(p[0]==requests[index-begin]&&std::memcmp(&edge,p+1,sizeof(Edge))==0,"Golden full edge differs");
                }
                if(degree>=2&&!found){mutation_node=c.requests[index];found=true;}
                else if(degree>0&&found&&!other){other_node=c.requests[index];other=true;}
                ++checked;records+=degree;unknown+=status==1;
            }
        }
    }
    bg::require(checked==274732&&records==1100754&&unknown==53759&&found&&other,"Full graph coverage differs");
    std::vector<Edge> edges;auto calls=provider.kernel_calls;
    provider.neighbors(mutation_node,edges);provider.neighbors(mutation_node,edges);
    bg::require(provider.kernel_calls==calls+1&&provider.hits==1,"Cache reuse failed");
    provider.neighbors(other_node,edges);provider.neighbors(mutation_node,edges);
    bg::require(provider.kernel_calls==calls+3,"Cache eviction failed");
    auto repeated=provider.decode_batch({mutation_node,mutation_node});
    bg::require(repeated[0].edges.size()==repeated[1].edges.size()&&
        std::memcmp(repeated[0].edges.data(),repeated[1].edges.data(),repeated[0].edges.size()*sizeof(Edge))==0,"Duplicate requests differ");
    for(mutation=1;mutation<=20;++mutation) {
        bool rejected=false;try{provider.decode_batch({mutation_node});}catch(const std::runtime_error&){rejected=true;}
        bg::require(rejected,"Malformed kernel reply accepted");
    }
    mutation=0;provider.materialize_all();calls=provider.kernel_calls;
    for(const auto& path:cases) {
        auto c=bg::fixture(path);
        for(uint32_t i=0;i<c.count;++i) {
            bool known=provider.neighbors(c.requests[i],edges);uint32_t start=c.results[3*i],degree=c.results[3*i+1];
            bg::require(known==(c.results[3*i+2]==0)&&edges.size()==degree,"Resident row differs");
            for(uint32_t j=0;j<degree;++j)
                bg::require(std::memcmp(&edges[j],c.output.data()+8*(start+j)+1,sizeof(Edge))==0,"Resident edge differs");
        }
    }
    bg::require(provider.kernel_calls==calls,"Resident graph unexpectedly invokes decoder");
    bool invalid=false;try{provider.neighbors(uint32_t(provider.node_count()),edges);}catch(const std::runtime_error&){invalid=true;}
    bg::require(invalid,"Invalid canonical node accepted");
    std::cout<<"KERNEL_PROVIDER_PASS nodes="<<checked<<" edges="<<records<<" unknown="<<unknown<<" mutations=20 cache_and_materialization=pass\n";
    return 0;
}catch(const std::exception& error){std::cerr<<"KERNEL_PROVIDER_FAIL "<<error.what()<<'\n';return 1;}}
