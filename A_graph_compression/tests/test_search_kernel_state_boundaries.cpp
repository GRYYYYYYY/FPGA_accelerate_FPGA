// Full production top: exact state capacities and overflow through real search.
#include "search_kernel_packet.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#ifndef SEARCH_GRAPH_MODE
#define SEARCH_GRAPH_MODE 0
#endif
#ifndef SEARCH_TOP_NAME
#define SEARCH_TOP_NAME search_kernel_top
#endif
extern "C" void SEARCH_TOP_NAME(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
struct Image {
    std::vector<uint32_t> data;std::array<uint32_t,32> config{};
    Image(unsigned mode){
        using namespace fpga_search::graph_decode;
        config[MODE]=mode;config[STRING_COUNT]=13;config[ATTR_COUNT]=2;
        auto section=[&](unsigned index,unsigned count,std::initializer_list<uint32_t> words){config[index]=unsigned(data.size());config[index+1]=count;data.insert(data.end(),words);};
        section(NODE_BASE,4,{0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,UINT32_MAX});
        section(TILE_BASE,1,{0,0,0,0,0,0});section(GRID_BASE,1,{0,0,0});
        section(ALIAS_BASE,3,{0,10,0,0,11,1,0,12,2});
        if(mode==0){section(CSR_OFF_BASE,4,{0,0,1,0,2,0,2,0});section(CSR_EDGE_BASE,2,{1,0,3,10,11,1,0,2,0,7,11,12,1,0});}
        else {section(INSTANCE_BASE,3,{UINT32_MAX,0,0,0,1,0,0,UINT32_MAX,0,0,1,1,0,0,UINT32_MAX,0,0,2,0,0,0});section(ADD_BASE,2,{0,0,3,10,11,1,0,0,0,7,11,12,1,0});}
        config[IMAGE_WORDS]=unsigned(data.size());
    }
};

template<class T> struct Guarded {
    std::vector<T> words;
    const T sentinel;
    explicit Guarded(size_t n,T fill=T{}):words(n+2,fill),sentinel(T(0xbaadf00d12345678ULL)) {words.front()=words.back()=sentinel;}
    T* data(){return words.data()+1;}
    void check()const {assert(words.front()==sentinel && words.back()==sentinel);}
};

int main(){
    using L=fpga_search::SearchRegionLimits;
    using K=fpga_search::SearchKernel<SEARCH_GRAPH_MODE>;
    using P=K::Provider;
    static_assert(L::signals==32 && L::bits==16 && L::values==8,"Production state capacities required");
    static_assert(L::heap==131072 && L::slots==1048576 && L::labels==524288,"Production workspace required");
    Image fixture(SEARCH_GRAPH_MODE);
    const unsigned image_words=unsigned(fixture.data.size());fixture.data.resize(33554432);
    Guarded<uint64_t> heap(3*L::heap),slots(L::slots),records(10*L::labels),keys(65*L::labels),unknown((L::nodes+63)/64),pips(L::unknown_pips,0xbadc0ffeeULL),meta(2),result(81);
    Guarded<uint32_t> path(8*L::path,0xabcdef01u),roots(L::roots);
    uint64_t forbidden[1]{},costs[8]{};uint8_t pseudo[2]={0,1},blocked[2]{};
    uint64_t sem_keys[2]={3,7};K::State requirements[2]{};
    auto& full=requirements[0];
    full.signals.count=32;for(unsigned i=0;i<32;++i)full.signals.data[i]=i+1;
    full.bits.count=16;for(unsigned i=0;i<16;++i)full.bits.data[i]={201+i,1,1};
    full.values.count=8;for(unsigned i=0;i<8;++i)full.values.data[i]={301+i,11+i};
    P::View view{4,2,forbidden,costs,pseudo,blocked,nullptr,sem_keys,requirements,0,2,{nullptr,nullptr,nullptr,0,0,0},7,1};
    const unsigned statuses[8]={0,5,5,5,0,1,1,0};
    for(unsigned transaction=0;transaction<8;++transaction){
        requirements[1]={};auto& second=requirements[1];
        if(transaction==1){second.signals.count=1;second.signals.data[0]=100;}
        if(transaction==2){second.bits.count=1;second.bits.data[0]={500,1,1};}
        if(transaction==3){second.values.count=1;second.values.data[0]={600,1};}
        if(transaction==4){second=full;for(unsigned i=0;i<16;++i)second.bits.data[i]={201+i,2,2};}
        if(transaction==5){second.bits.count=1;second.bits.data[0]={216,1,0};}
        if(transaction==6){second.values.count=1;second.values.data[0]={308,99};}
        auto packet=search_kernel_host::packet<L>(view,2,1,8,{});
        const unsigned packet_words=unsigned(packet.size());packet.resize(fpga_search::SearchPacketMaxWords);
        std::fill(path.words.begin()+1,path.words.end()-1,0xabcdef01u);
        SEARCH_TOP_NAME(fixture.data.data(),fixture.config.data(),image_words,roots.data(),packet.data(),packet_words,heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta.data(),result.data());
        const uint64_t* r=result.data();
        std::printf("STATE_BOUNDARY_OBSERVED mode=%u transaction=%u status=%llu cost=%llu expanded=%llu path=%llu\n",SEARCH_GRAPH_MODE,transaction,(unsigned long long)r[0],(unsigned long long)r[1],(unsigned long long)r[2],(unsigned long long)r[7]);std::fflush(stdout);
        assert(r[0]==statuses[transaction] && r[15]==1 && meta.data()[0]==transaction+1 && r[13]==meta.data()[0] && r[14]==meta.data()[1]);
        assert(r[2]==2 && r[6]==0 && r[8]==0 && r[9]==0 && r[11]==1 && r[12]>=1);
        const bool found=statuses[transaction]==0;
        assert(r[3]==unsigned(transaction==5 || transaction==6));
        assert(r[4]==unsigned(found?3:2) && r[5]==r[4] && r[10]==r[4]);
        if(found){
            assert(r[1]==2 && r[7]==2);
            const uint32_t literal[16]={0,1,0,3,10,11,1,0,1,2,0,7,11,12,1,0};
            for(unsigned i=0;i<16;++i)assert(path.data()[i]==literal[i]);
            // Literal output ABI oracle; no use of production state serializer/loader.
            uint64_t expected[65]{};
            expected[0]=2|(uint64_t(32)<<32)|(uint64_t(16)<<40)|(uint64_t(8)<<48);
            for(unsigned i=0;i<16;++i)expected[1+i]=(2*i+1)|(uint64_t(2*i+2)<<32);
            for(unsigned i=0;i<8;++i)expected[17+i]=(201+2*i)|(uint64_t(202+2*i)<<32);
            for(unsigned i=0;i<16;++i)expected[25+i]=expected[41+i]=transaction==4?3:1;
            for(unsigned i=0;i<8;++i)expected[57+i]=(301+i)|(uint64_t(11+i)<<32);
            for(unsigned i=0;i<65;++i)assert(r[16+i]==expected[i]);
        }else{
            assert(r[1]==0 && r[7]==0);
            for(unsigned i=16;i<81;++i)assert(r[i]==0);
        }
        assert(std::all_of(path.words.begin()+1+(found?16:0),path.words.end()-1,[](uint32_t x){return x==0xabcdef01u;}));
        assert(std::all_of(pips.words.begin()+1,pips.words.end()-1,[](uint64_t x){return x==0xbadc0ffeeULL;}));
        assert(unknown.data()[0]==0);
        heap.check();slots.check();records.check();keys.check();unknown.check();pips.check();path.check();roots.check();meta.check();result.check();
        std::printf("STATE_BOUNDARY_PASS mode=%u transaction=%u status=%u full_capacity=32,16,8 literal_output=1 guards=1\n",SEARCH_GRAPH_MODE,transaction,statuses[transaction]);
    }
    std::puts("STATE_BOUNDARY_ALL_PASS transactions=8 production_top=1 full_workspace_limits=1");
}
