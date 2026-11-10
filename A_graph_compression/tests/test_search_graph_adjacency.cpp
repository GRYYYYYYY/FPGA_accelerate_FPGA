#include "../src/native/packed_graph.hpp"
#include "host_contract.hpp"
#include "search_graph_adjacency.hpp"
#include <cassert>
#include <cstring>
#include <iostream>
template<unsigned Mode> void check(const std::string& path,const std::vector<uint32_t>& image,const std::vector<uint32_t>& config) {
    Graph reference(path,0);fpga_search::ImageAdjacency<Mode> candidate;
    assert(candidate.bind(image.data(),config.data(),image.size())==fpga_search::RowStatus::known);
    assert(candidate.node_count()==reference.node_count());
    std::array<fpga_search::LabelEdge,1026> out{},before{};
    std::memset(out.data(),0xa5,sizeof(out));std::vector<Edge> edges;
    unsigned known=0,unknown=0,max_degree=0;uint64_t total=0;bool checked_capacity=false;
    for(unsigned node=0;node<reference.node_count();++node) {
        const bool expected=reference.neighbors(node,edges);
        std::stable_sort(edges.begin(),edges.end(),[](const Edge& a,const Edge& b){return std::make_tuple(a.dst,a.tile,a.pip,a.dir,a.dir?a.down:a.up,a.dir?a.up:a.down)<std::make_tuple(b.dst,b.tile,b.pip,b.dir,b.dir?b.down:b.up,b.dir?b.up:b.down);});
        before=out;unsigned count=UINT32_MAX;
        const auto status=candidate.neighbors(node,out.data(),1024,count);
        if(!expected){assert(status==fpga_search::RowStatus::unknown && count==0 && std::memcmp(out.data(),before.data(),sizeof(out))==0);++unknown;continue;}
        assert(status==fpga_search::RowStatus::known && count==edges.size());++known;total+=count;max_degree=std::max(max_degree,count);
        for(unsigned i=0;i<count;++i){const auto& a=edges[i];const auto& b=out[i];assert(std::tie(a.dst,a.tile,a.pip,a.up,a.down,a.attr,a.dir)==std::tie(b.dst,b.tile,b.pip,b.up,b.down,b.attr,b.dir));}
        assert(std::memcmp(out.data()+count,before.data()+count,(out.size()-count)*sizeof(out[0]))==0);
        if(count && !checked_capacity){before=out;unsigned rejected=UINT32_MAX;assert(candidate.neighbors(node,out.data(),count-1,rejected)==fpga_search::RowStatus::capacity_exhausted && rejected==0 && std::memcmp(out.data(),before.data(),sizeof(out))==0);checked_capacity=true;}
    }
    assert(known==220973 && unknown==53759 && total==1100754 && checked_capacity);
    unsigned count=UINT32_MAX;before=out;
    assert(candidate.neighbors(reference.node_count(),out.data(),1024,count)==fpga_search::RowStatus::invalid && count==0 && std::memcmp(out.data(),before.data(),sizeof(out))==0);
    auto bad=config;bad[0]=1-Mode;assert(candidate.bind(image.data(),bad.data(),image.size())==fpga_search::RowStatus::invalid && candidate.node_count()==0);
    bad=config;bad[1]=UINT32_MAX;assert(candidate.bind(image.data(),bad.data(),image.size())==fpga_search::RowStatus::invalid);
    bad=config;bad[2]=UINT32_MAX;assert(candidate.bind(image.data(),bad.data(),image.size())==fpga_search::RowStatus::invalid);
    assert(candidate.bind(nullptr,config.data(),image.size())==fpga_search::RowStatus::invalid);
    assert(candidate.bind(image.data(),config.data(),image.size()-1)==fpga_search::RowStatus::invalid);
    assert(candidate.bind(image.data(),config.data(),image.size())==fpga_search::RowStatus::known);
    std::cout<<"SEARCH_GRAPH_FULL_PASS mode="<<Mode<<" nodes="<<reference.node_count()<<" known="<<known<<" unknown="<<unknown<<" edges="<<total<<" max_degree="<<max_degree<<"\nSEARCH_GRAPH_REJECTION_GUARDS_PASS\n";
}
int main(int argc,char** argv) {
    assert(argc==3);auto image=board_graph::words(argv[1],board_graph::image_words);auto config=board_graph::words(argv[2],32);
    assert(config.size()==32);board_graph::descriptor(image,config,config[0]);
    if(config[0]==0)check<0>(argv[1],image,config);else check<1>(argv[1],image,config);
}
