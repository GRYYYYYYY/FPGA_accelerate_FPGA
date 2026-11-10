#include "search_kernel_packet.hpp"
#include <array>
#include <cassert>
#include <cstdio>
struct L:fpga_search::SearchRegionLimits {
    static constexpr unsigned nodes=4,degree=2,roots=4,unknown_pips=4,path=8,expansions=8,slots=16,labels=8,heap=8;
};
struct M {static constexpr unsigned semantics=2,attributes=2,protected_pips=2,owners=4,history=4,fixed=4;};
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
template<unsigned Mode> void check(){
    using K=fpga_search::SearchKernel<Mode,L,M>;using P=typename K::Provider;
    using W=typename K::StateWords;using Core=typename K::Core;
    std::array<uint64_t,24> heap{};std::array<uint64_t,16> slots{};
    std::array<uint64_t,80> records{};std::array<uint64_t,8*W::Words> keys{};
    std::array<uint64_t,1> unknown{};std::array<uint64_t,4> pips{};std::array<uint32_t,64> path{};
    std::array<uint64_t,2> meta{};std::array<uint64_t,83> result{};result[0]=result[82]=0x123456789abcdef0ULL;
    uint32_t roots[1]={0};Image image(Mode);
    uint64_t forbidden[1]{},node_costs[8]={0,0,2,1,0,2,0,0};uint8_t pseudo[2]={0,1},blocked[2]{};
    uint64_t sem_keys[1]={3};typename Core::State requirements[1]{};
    requirements[0].signals.count=1;requirements[0].signals.data[0]=3;
    requirements[0].bits.count=1;requirements[0].bits.data[0]={4,1,1};
    requirements[0].values.count=1;requirements[0].values.data[0]={5,2};
    uint64_t owners[12]={3,9,0,0,(uint64_t(1)<<32)|4,9,1,0,(uint64_t(2)<<32)|5,9,0,3};
    uint64_t history[6]={3,2,(uint64_t(1)<<32)|4,3,(uint64_t(2)<<32)|5,5};
    uint64_t fixed[4]={(uint64_t(1)<<32)|4,0,1,1};
    typename P::View view{4,2,forbidden,node_costs,pseudo,blocked,nullptr,sem_keys,requirements,0,1,{owners,history,fixed,3,3,1},7,4};
    auto packet=search_kernel_host::packet<L>(view,2,1,8,{});
    // Independent literal offsets for the production 65-word state schema.
    assert(W::Words==65 && packet.size()==196 && packet[0]==0x4153454152434831ULL && packet[1]==196);
    for(unsigned i=32;i<98;++i)assert(packet[i]==0);
    assert(packet[100]==2 && packet[101]==1 && packet[103]==2 && packet[106]==256 && packet[107]==0 && packet[108]==3);
    assert(packet[109]==0x0001010100000000ULL && packet[110]==3 && packet[126]==4 && packet[134]==1 && packet[150]==1 && packet[166]==0x200000005ULL);
    for(unsigned i=0;i<12;++i)assert(packet[174+i]==owners[i]);
    for(unsigned i=0;i<6;++i)assert(packet[186+i]==history[i]);
    for(unsigned i=0;i<4;++i)assert(packet[192+i]==fixed[i]);
    auto call=[&](unsigned length){K::run(image.data.data(),image.config.data(),unsigned(image.data.size()),roots,packet.data(),length,heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta.data(),result.data()+1);assert(result[0]==0x123456789abcdef0ULL && result[82]==result[0]);};
    call(unsigned(packet.size()));
    assert(result[1]==uint64_t(fpga_search::SearchStatus::found) && result[2]==35 && result[8]==2 && result[16]==1);
    const uint32_t literal[16]={0,1,0,3,10,11,1,0,1,2,0,7,11,12,0,0};
    for(unsigned i=0;i<16;++i)assert(path[i]==literal[i]);
    typename W::Key demand{};assert(W::load(result.data()+17,0,demand) && demand.node==2 && demand.state.signals.count==1 && demand.state.bits.count==1 && demand.state.values.count==1);
    const auto good=packet;const auto good_config=image.config;
    unsigned rejected=0;
    auto reject=[&](fpga_search::SearchStatus status,unsigned length){
        const auto oldheap=heap;const auto oldslots=slots;const auto oldrecords=records;const auto oldkeys=keys;
        const auto oldunknown=unknown;const auto oldpips=pips;const auto oldpath=path;const auto oldmeta=meta;
        call(length);assert(result[1]==uint64_t(status));for(unsigned i=2;i<16;++i)assert(result[i]==0);for(unsigned i=17;i<82;++i)assert(result[i]==0);
        assert(heap==oldheap && slots==oldslots && records==oldrecords && keys==oldkeys && unknown==oldunknown && pips==oldpips && path==oldpath && meta==oldmeta);
        ++rejected;packet=good;image.config=good_config;
    };
    const auto invalid=fpga_search::SearchStatus::invalid_input,capacity=fpga_search::SearchStatus::capacity_exhausted;
    for(unsigned word:{0u,1u,14u,31u}){packet[word]^=1;reject(invalid,unsigned(packet.size()));}
    for(unsigned word:{2u,3u,7u,8u,9u,10u,11u,12u,13u}){packet[word]=UINT64_MAX;reject(capacity,unsigned(packet.size()));}
    for(unsigned word:{2u,3u,5u,7u,8u}){packet[word]=0;reject(invalid,unsigned(packet.size()));}
    packet[4]=uint64_t(UINT32_MAX)+1;reject(invalid,unsigned(packet.size()));
    packet[6]=4;reject(invalid,unsigned(packet.size()));
    for(unsigned word:{106u,107u}){packet[word]=2;reject(invalid,unsigned(packet.size()));packet[word]=uint64_t(1)<<63;reject(invalid,unsigned(packet.size()));}
    for(unsigned word:{32u,109u}){packet[word]|=1;reject(invalid,unsigned(packet.size()));packet[word]|=uint64_t(1)<<63;reject(invalid,unsigned(packet.size()));}
    packet[108]=3;packet[109]=uint64_t(33)<<32;reject(invalid,unsigned(packet.size()));
    packet[177]=1;reject(invalid,unsigned(packet.size())); // nonzero value on exclusive signal owner
    packet[195]=2;reject(invalid,unsigned(packet.size())); // value outside fixed bit mask
    image.config[fpga_search::graph_decode::MODE]=1-Mode;reject(invalid,unsigned(packet.size()));
    image.config[fpga_search::graph_decode::ATTR_COUNT]=1;reject(invalid,unsigned(packet.size()));
    reject(invalid,31);reject(invalid,unsigned(packet.size()-1));reject(capacity,fpga_search::SearchPacketMaxWords+1);
    const auto saved_meta=meta;meta[0]=uint64_t(UINT32_MAX)+1;reject(invalid,unsigned(packet.size()));meta=saved_meta;
    meta[1]=9;reject(invalid,unsigned(packet.size()));meta=saved_meta;
    // Unknown PIP, fixed conflict, exhausted budget, unknown adjacency and reset.
    view.semantics_count=0;packet=search_kernel_host::packet<L>(view,2,1,8,{});call(unsigned(packet.size()));
    assert(result[1]==uint64_t(fpga_search::SearchStatus::unknown_site_semantics) && result[10]==1 && pips[0]==3);
    view.semantics_count=1;fixed[3]=0;packet=search_kernel_host::packet<L>(view,2,1,8,{});call(unsigned(packet.size()));
    assert(result[1]==uint64_t(fpga_search::SearchStatus::no_path) && result[4]==1);fixed[3]=1;
    packet=search_kernel_host::packet<L>(view,2,1,1,{});call(unsigned(packet.size()));assert(result[1]==uint64_t(fpga_search::SearchStatus::budget_exhausted));
    roots[0]=3;packet=search_kernel_host::packet<L>(view,2,1,8,{});call(unsigned(packet.size()));assert(result[1]==uint64_t(fpga_search::SearchStatus::incomplete_domain) && result[9]==1 && unknown[0]==8);
    roots[0]=0;meta[0]=UINT32_MAX;packet=search_kernel_host::packet<L>(view,2,1,8,{});call(unsigned(packet.size()));assert(result[1]==uint64_t(fpga_search::SearchStatus::found) && meta[0]==1);
    std::printf("KERNEL_PACKET_PASS mode=%u successful_transactions=6 rejected_preflight=%u literal_offsets=pass guards=pass\n",Mode,rejected);
}
int main(){check<0>();check<1>();}
