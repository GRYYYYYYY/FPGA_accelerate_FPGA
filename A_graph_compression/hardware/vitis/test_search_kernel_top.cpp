#include "search_kernel_packet.hpp"
#include <array>
#include <algorithm>
#include <cassert>
#include <cstdio>
#ifndef SEARCH_GRAPH_MODE
#define SEARCH_GRAPH_MODE 0
#endif
extern "C" void search_kernel_top(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
struct Image {
    std::vector<uint32_t> data;std::array<uint32_t,32> config{};
    Image(unsigned mode){
        using namespace fpga_search::graph_decode;
        config[MODE]=mode;config[STRING_COUNT]=13;config[ATTR_COUNT]=2;
        auto section=[&](unsigned index,unsigned count,std::initializer_list<uint32_t> words){config[index]=unsigned(data.size());config[index+1]=count;data.insert(data.end(),words);};
        section(NODE_BASE,4,{0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,UINT32_MAX});
        section(TILE_BASE,1,{0,0,0,0,0,0});section(GRID_BASE,1,{0,0,0});
        section(ALIAS_BASE,3,{0,10,0,0,11,1,0,12,2});
        if(mode==0){section(CSR_OFF_BASE,4,{0,0,1,0,2,0,2,0});section(CSR_EDGE_BASE,2,{1,0,3,10,11,1,0,2,0,7,11,12,0,0});}
        else {section(INSTANCE_BASE,3,{UINT32_MAX,0,0,0,1,0,0,UINT32_MAX,0,0,1,1,0,0,UINT32_MAX,0,0,2,0,0,0});section(ADD_BASE,2,{0,0,3,10,11,1,0,0,0,7,11,12,0,0});}
        config[IMAGE_WORDS]=unsigned(data.size());
    }
};

int main(){
    using L=fpga_search::SearchRegionLimits;using K=fpga_search::SearchKernel<SEARCH_GRAPH_MODE>;
    using P=K::Provider;using W=K::StateWords;
    Image fixture(SEARCH_GRAPH_MODE);const unsigned image_words=unsigned(fixture.data.size());fixture.data.resize(33554432);
    std::vector<uint64_t> heap(3*L::heap),slots(L::slots),records(10*L::labels),keys(L::labels*W::Words),unknown((L::nodes+63)/64),pips(L::unknown_pips,0xbadc0ffeeULL);
    std::vector<uint32_t> path(8*L::path,0xabcdef01u),roots(L::roots);uint64_t meta[2]{},result[81]{};
    uint64_t forbidden[1]{},costs[8]={0,0,2,1,0,2,0,0};uint8_t pseudo[2]={0,1},blocked[2]{};
    uint64_t sem_keys[1]={3};K::State requirement[1]{};
    requirement[0].signals.count=1;requirement[0].signals.data[0]=3;
    requirement[0].bits.count=1;requirement[0].bits.data[0]={4,1,1};
    requirement[0].values.count=1;requirement[0].values.data[0]={5,2};
    uint64_t owners[12]={3,9,0,0,(uint64_t(1)<<32)|4,9,1,0,(uint64_t(2)<<32)|5,9,0,3};
    uint64_t history[6]={3,2,(uint64_t(1)<<32)|4,3,(uint64_t(2)<<32)|5,5};uint64_t fixed[4]={(uint64_t(1)<<32)|4,0,1,1};
    P::View view{4,2,forbidden,costs,pseudo,blocked,nullptr,sem_keys,requirement,0,1,{owners,history,fixed,3,3,1},7,4};
    for(unsigned transaction=0;transaction<2;++transaction){
        view.semantics_count=transaction?0:1;
        auto packet=search_kernel_host::packet<L>(view,2,1,8,{});const unsigned packet_words=unsigned(packet.size());packet.resize(fpga_search::SearchPacketMaxWords);
        search_kernel_top(fixture.data.data(),fixture.config.data(),image_words,roots.data(),packet.data(),packet_words,heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta,result);
        assert(result[15]==1 && meta[0]==transaction+1 && result[13]==meta[0] && result[14]==meta[1]);
        if(!transaction){
            assert(result[0]==0 && result[1]==35 && result[2]==2 && result[3]==0 && result[4]==3 && result[5]==3 && result[6]==0 && result[7]==2 && result[8]==0 && result[9]==0 && result[10]==3 && result[11]==1);
            const uint32_t literal[16]={0,1,0,3,10,11,1,0,1,2,0,7,11,12,0,0};for(unsigned i=0;i<16;++i)assert(path[i]==literal[i]);
            assert(std::all_of(path.begin()+16,path.end(),[](uint32_t v){return v==0xabcdef01u;}));
            assert(std::all_of(pips.begin(),pips.end(),[](uint64_t v){return v==0xbadc0ffeeULL;}));
            W::Key demand{};assert(W::load(result+16,0,demand) && demand.node==2);
            assert(demand.state.signals.count==1 && demand.state.signals.data[0]==3 && demand.state.bits.count==1 && demand.state.bits.data[0].field==4 && demand.state.bits.data[0].mask==1 && demand.state.bits.data[0].value==1 && demand.state.values.count==1 && demand.state.values.data[0].field==5 && demand.state.values.data[0].value==2);
        }else{
            assert(result[0]==3 && result[1]==0 && result[2]==1 && result[3]==0 && result[4]==1 && result[5]==1 && result[6]==0 && result[7]==0 && result[8]==0 && result[9]==1 && result[10]==1 && result[11]==1 && pips[0]==3);
            for(unsigned i=16;i<81;++i)assert(result[i]==0);
            assert(std::all_of(pips.begin()+1,pips.end(),[](uint64_t v){return v==0xbadc0ffeeULL;}));
        }
        assert(unknown[0]==0);
        std::printf("SEARCH_KERNEL_TOP_TRANSACTION_PASS mode=%u transaction=%u status=%llu cost=%llu path=%llu\n",SEARCH_GRAPH_MODE,transaction,(unsigned long long)result[0],(unsigned long long)result[1],(unsigned long long)result[7]);
    }
    std::puts("SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1");
}
