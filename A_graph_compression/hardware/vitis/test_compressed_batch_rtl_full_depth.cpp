#include <cstdlib>
#include <cstdint>
#include <fstream>
#include "search_kernel_packet.hpp"
#include "search_resident_snapshot.hpp"
#include "search_retained_nodes.hpp"
#include "search_retained_edges.hpp"
#include <array>
#include <algorithm>
#include <cassert>
#include <cstdio>
#ifndef SEARCH_GRAPH_MODE
#define SEARCH_GRAPH_MODE 0
#endif
extern "C" void search_batch_trace_top_v2(const uint32_t* image,const uint32_t* config,unsigned image_words,
        uint32_t* root_nodes,uint64_t* packet,
        uint64_t* heap,uint64_t* slots,uint64_t* records,uint64_t* keys,
        uint64_t* unknown_nodes,uint64_t* unknown_pips,uint32_t* path,
        uint64_t* meta,uint64_t* result,
        uint64_t* tree_meta,uint64_t* tree_bits,uint64_t* tree_demands,
        uint64_t* edge_meta,uint32_t* edge_rows,uint64_t* control_result,const uint32_t* all_sinks,
        
        const uint64_t* static_image,
        uint64_t* node_meta,
        uint32_t* node_counts,
        uint64_t* node_history,
        uint64_t* node_keys,
        uint32_t* node_flags,
        uint64_t* site_meta,
        uint64_t* site_owners,
        uint64_t* site_history,
        uint64_t* site_request,
        uint64_t* retained_meta,
        uint64_t* retained_rows,
        uint32_t* old_nodes,
        uint64_t* net_result,
        const uint64_t* batch_control,
        const uint64_t* query_table,
        uint32_t* complete_flags,
        uint32_t* site_conflict_flags,
        uint64_t* site_summaries,
        uint64_t* round_result,
        uint64_t* batch_result,
        const uint64_t* trace_control,uint64_t* trace_meta,uint64_t* trace_data);
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
    (void)view;
    using Node=fpga_search::ProductionNodeOccupancy;using Site=fpga_search::ProductionSiteOccupancy;
    std::vector<uint64_t> static_image(4194304),node_history(1048576),node_keys(2097152),site_owners(524288),site_history(262144),site_request(196608),retained_rows(4194304);
    std::vector<uint32_t> node_counts(1048576),node_flags(2097152),old_nodes(1048576,0xdeadbeef),sinks(4194304,0xdeadbeef),edge_rows(37748736,0xdeadbeef);
    uint64_t node_meta[4]{},site_meta[6]{},retained_meta[6]{},edge_meta[6]{},tree_meta[5]{},tree_demands[65]{},control_result[8]{},net_result[8]{};
    std::vector<uint64_t> tree_bits(16384),packet(fpga_search::SearchPacketMaxWords);
    assert(Node::reset(4,node_meta,node_counts.data(),node_history.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);
    assert(Site::reset(site_meta)==fpga_search::SiteOccupancyStatus::ok);
    assert(fpga_search::RetainedNodes<>::reset(4,retained_meta)==fpga_search::RetainedStatus::ok);
    assert(fpga_search::RetainedEdges<>::reset(4,edge_meta)==fpga_search::RetainedEdgeStatus::ok);
    static_image[0]=UINT64_C(0x41534e4150535431);static_image[1]=89;static_image[2]=4;static_image[3]=2;static_image[5]=1;static_image[6]=1;
    static_image[17]=0x100;static_image[19]=3;typename W::Key requirement_key{};requirement_key.state=requirement[0];assert(W::store(static_image.data()+20,0,requirement_key));
    std::copy(fixed,fixed+4,static_image.begin()+85);
    std::vector<uint64_t> query_table(262144),site_summaries(131072);
    std::vector<uint32_t> complete_flags(65536,0xdeadbeef),site_conflict_flags(65536);
    uint64_t round_result[8]{},batch_result[12]{},batch_control[16]={8,80,2,3,93,8,1,0,0,0,0,0,0,0,0,0};
    const uint64_t schedule[8]={7,0,0,3,8,3,3,0};std::copy(schedule,schedule+8,query_table.begin());sinks[0]=1;sinks[1]=sinks[2]=2;
    std::fill(static_image.begin(),static_image.end(),0);static_image[0]=UINT64_C(0x41534e4150535431);static_image[1]=93;static_image[2]=4;static_image[3]=2;static_image[5]=1;static_image[6]=1;static_image[7]=4;
    for(unsigned i=0;i<4;++i)static_image[17+i]=(uint64_t(i)<<32)|(i==3?8:7);
    static_image[21]=0x100;static_image[23]=3;assert(W::store(static_image.data()+24,0,requirement_key));std::copy(fixed,fixed+4,static_image.begin()+89);
    uint64_t trace_meta[8]{},trace_control[8]={16777216,0,0,0,0,0,0,0};
    std::vector<uint64_t> trace_data(16777217,UINT64_C(0xdeadbeef));unsigned invocation=0;
    struct SnapshotPort {unsigned id,bytes;uint64_t depth,available;const void* data;};
    const SnapshotPort ports[]={
        {0,4,33554432,fixture.data.size(),fixture.data.data()},
        {1,4,32,fixture.config.size(),fixture.config.data()},
        {3,4,1048576,roots.size(),roots.data()},
        {4,8,4194304,packet.size(),packet.data()},
        {5,8,393216,heap.size(),heap.data()},
        {6,8,1048576,slots.size(),slots.data()},
        {7,8,5242880,records.size(),records.data()},
        {8,8,34078720,keys.size(),keys.data()},
        {9,8,16384,unknown.size(),unknown.data()},
        {10,8,1100754,pips.size(),pips.data()},
        {11,4,4194304,path.size(),path.data()},
        {12,8,2,sizeof(meta)/sizeof(meta[0]),meta},
        {13,8,81,sizeof(result)/sizeof(result[0]),result},
        {14,8,5,sizeof(tree_meta)/sizeof(tree_meta[0]),tree_meta},
        {15,8,16384,tree_bits.size(),tree_bits.data()},
        {16,8,65,sizeof(tree_demands)/sizeof(tree_demands[0]),tree_demands},
        {17,8,6,sizeof(edge_meta)/sizeof(edge_meta[0]),edge_meta},
        {18,4,37748736,edge_rows.size(),edge_rows.data()},
        {19,8,8,sizeof(control_result)/sizeof(control_result[0]),control_result},
        {20,4,4194304,sinks.size(),sinks.data()},
        {21,8,4194304,static_image.size(),static_image.data()},
        {22,8,4,sizeof(node_meta)/sizeof(node_meta[0]),node_meta},
        {23,4,1048576,node_counts.size(),node_counts.data()},
        {24,8,1048576,node_history.size(),node_history.data()},
        {25,8,2097152,node_keys.size(),node_keys.data()},
        {26,4,2097152,node_flags.size(),node_flags.data()},
        {27,8,6,sizeof(site_meta)/sizeof(site_meta[0]),site_meta},
        {28,8,524288,site_owners.size(),site_owners.data()},
        {29,8,262144,site_history.size(),site_history.data()},
        {30,8,196608,site_request.size(),site_request.data()},
        {31,8,6,sizeof(retained_meta)/sizeof(retained_meta[0]),retained_meta},
        {32,8,4194304,retained_rows.size(),retained_rows.data()},
        {33,4,1048576,old_nodes.size(),old_nodes.data()},
        {34,8,8,sizeof(net_result)/sizeof(net_result[0]),net_result},
        {35,8,16,sizeof(batch_control)/sizeof(batch_control[0]),batch_control},
        {36,8,262144,query_table.size(),query_table.data()},
        {37,4,65536,complete_flags.size(),complete_flags.data()},
        {38,4,65536,site_conflict_flags.size(),site_conflict_flags.data()},
        {39,8,131072,site_summaries.size(),site_summaries.data()},
        {40,8,8,sizeof(round_result)/sizeof(round_result[0]),round_result},
        {41,8,12,sizeof(batch_result)/sizeof(batch_result[0]),batch_result},
        {42,8,8,sizeof(trace_control)/sizeof(trace_control[0]),trace_control},
        {43,8,8,sizeof(trace_meta)/sizeof(trace_meta[0]),trace_meta},
        {44,8,16777216,trace_data.size(),trace_data.data()}
    };
    static_assert(sizeof(ports)/sizeof(ports[0])==44,"full pointer inventory");
    for(const auto& port:ports)assert(port.available>=port.depth);
    auto full_snapshot=[&](unsigned transaction){
        const char* prefix=std::getenv("A_BATCH_RTL_SNAPSHOT_PREFIX");assert(prefix && *prefix);
        const uint16_t endian=1;assert(*reinterpret_cast<const uint8_t*>(&endian)==1);
        const std::string name=std::string(prefix)+"_"+std::to_string(SEARCH_GRAPH_MODE)+"_"+std::to_string(transaction)+".bin";
        std::ofstream out(name,std::ios::binary);
        auto put=[&](uint64_t word){for(unsigned b=0;b<8;++b)out.put(char(word>>(8*b)));};
        put(UINT64_C(0x4142534e41503031));put(SEARCH_GRAPH_MODE);put(transaction);put(44);
        for(const auto& port:ports){put(port.id);put(port.bytes);put(port.depth);out.write(reinterpret_cast<const char*>(port.data),std::streamsize(port.depth*port.bytes));}
        out.close();assert(out);
    };
    auto invoke=[&](){search_batch_trace_top_v2(fixture.data.data(),fixture.config.data(),image_words,roots.data(),packet.data(),heap.data(),slots.data(),records.data(),keys.data(),unknown.data(),pips.data(),path.data(),meta,result,tree_meta,tree_bits.data(),tree_demands,edge_meta,edge_rows.data(),control_result,sinks.data(),static_image.data(),node_meta,node_counts.data(),node_history.data(),node_keys.data(),node_flags.data(),site_meta,site_owners.data(),site_history.data(),site_request.data(),retained_meta,retained_rows.data(),old_nodes.data(),net_result,batch_control,query_table.data(),complete_flags.data(),site_conflict_flags.data(),site_summaries.data(),round_result,batch_result,trace_control,trace_meta,trace_data.data());
        full_snapshot(invocation);
        assert(!trace_meta[4] && trace_meta[2] && trace_data.back()==UINT64_C(0xdeadbeef));
        const std::string name="trace_mode_"+std::to_string(SEARCH_GRAPH_MODE)+"_case_"+std::to_string(invocation++)+".bin";
        std::ofstream out(name,std::ios::binary);auto put=[&](uint64_t w){for(unsigned b=0;b<8;++b)out.put(char(w>>(8*b)));};
        for(auto w:trace_meta)put(w);
        for(unsigned i=0;i<trace_meta[2];++i)put(trace_data[i]);
        out.close();assert(out);
    };
    invoke();
    assert(!batch_result[0] && batch_result[1]==7 && batch_result[3]==1 && batch_result[4]==2 && batch_result[5]==3 && batch_result[6]==3 && batch_result[7]==1 && !batch_result[8] && !batch_result[9] && !batch_result[10] && !batch_result[11]);
    assert(complete_flags[0]==1 && complete_flags[1]==1 && round_result[3]==0 && round_result[6]==0);
    for(unsigned i=0;i<4;++i)assert(node_counts[i]==1 && node_history[i]==0);
    assert(retained_meta[2]==4 && retained_meta[4]==2 && edge_meta[2]==2 && site_meta[2]==3);
    // Explicit trusted component-state seed for an unsatisfiable persistent conflict.
    assert(Node::reset(4,node_meta,node_counts.data(),node_history.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);
    assert(Site::reset(site_meta)==fpga_search::SiteOccupancyStatus::ok);
    assert(fpga_search::RetainedNodes<>::reset(4,retained_meta)==fpga_search::RetainedStatus::ok);
    assert(fpga_search::RetainedEdges<>::reset(4,edge_meta)==fpga_search::RetainedEdgeStatus::ok);
    uint32_t occupied_node=1;
    assert(Node::update(77,nullptr,0,&occupied_node,1,node_meta,node_counts.data(),node_keys.data(),node_flags.data())==fpga_search::OccupancyStatus::ok);
    assert(fpga_search::RetainedNodes<>::replace(77,&occupied_node,1,retained_meta,retained_rows.data())==fpga_search::RetainedStatus::ok);
    batch_control[1]=2;batch_control[6]=0;invoke();
    assert(!batch_result[0] && batch_result[3]==2 && batch_result[4]==4 && batch_result[5]==6 && batch_result[6]==6 && !batch_result[7] && !batch_result[8] && batch_result[9]==1 && !batch_result[10] && batch_result[11]==2);
    assert(round_result[3]==1 && round_result[6]==1 && round_result[7]==2 && node_counts[1]==2 && node_history[1]==2 && retained_meta[2]==5 && retained_meta[4]==3);
    // No conflict + incomplete => terminate immediately with no history update.
    static_image[1]=27;static_image[5]=0;std::copy(fixed,fixed+4,static_image.begin()+23);
    batch_control[1]=80;batch_control[4]=27;batch_control[6]=1;invoke();
    assert(!batch_result[0] && batch_result[3]==1 && batch_result[4]==2 && batch_result[5]==3 && !batch_result[6] && !batch_result[7] && batch_result[8]==1 && !batch_result[9] && !batch_result[10] && !batch_result[11]);
    assert(complete_flags[0]==0 && complete_flags[1]==1 && round_result[3]==1 && round_result[6]==0 && retained_meta[2]==2 && edge_meta[2]==0);
    for(unsigned i=0;i<4;++i)assert(node_history[i]==0);
    const uint64_t version=node_meta[3],epoch=meta[0];batch_control[2]=0;invoke();assert(batch_result[0]==1 && !batch_result[1] && node_meta[3]==version && meta[0]==epoch);
    assert(std::all_of(complete_flags.begin()+2,complete_flags.end(),[](uint32_t v){return v==0xdeadbeef;}));
    assert(invocation==4);
    std::printf("FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=%u ports=44 transactions=4\n",SEARCH_GRAPH_MODE);
    std::printf("SEARCH_BATCH_PASS mode=%u routed=1 persistent_conflict_rounds=2 final_history_advance=1 incomplete_early_stop=1 invalid=1\n",SEARCH_GRAPH_MODE);
}
