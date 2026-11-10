#include "../hardware/vitis/search_xrt_v1/exchange.hpp"
#include "search_xrt_fixture_v1.hpp"
#include <cstring>
#include <functional>
#include <map>
#include <memory>
#include <iostream>
extern "C" void search_kernel_csr(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
extern "C" void search_kernel_compact(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
using namespace search_xrt;
struct CpuBackend {
    std::array<std::unique_ptr<uint32_t[]>,15> narrow;
    std::array<std::unique_ptr<uint64_t[]>,15> wide;
    std::array<unsigned,15> writes{},reads{};
    unsigned mode;
    explicit CpuBackend(unsigned m):mode(m) {
        for(unsigned id=0;id<15;++id)if(arguments[id].bytes) {
            if(id==0 || id==1 || id==3 || id==12)narrow[id].reset(new uint32_t[allocation_size(id)/4]());
            else wide[id].reset(new uint64_t[allocation_size(id)/8]());
        }
    }
    void* data(unsigned id){return narrow[id]?static_cast<void*>(narrow[id].get()):wide[id].get();}
    void write(unsigned id,const void* ptr,size_t size){assert(size<=arguments[id].bytes);std::memcpy(data(id),ptr,size);++writes[id];}
    void read(unsigned id,void* ptr,size_t size){assert(size<=arguments[id].bytes);std::memcpy(ptr,data(id),size);++reads[id];}
    bool launch(unsigned image_words,unsigned packet_words) {
        auto fn=mode?search_kernel_compact:search_kernel_csr;
        fn(narrow[0].get(),narrow[1].get(),image_words,narrow[3].get(),wide[4].get(),packet_words,
           wide[6].get(),wide[7].get(),wide[8].get(),wide[9].get(),wide[10].get(),wide[11].get(),
           narrow[12].get(),wide[13].get(),wide[14].get());
        return true;
    }
};
struct FaultBackend {
    std::array<uint64_t,81> result{};
    std::array<uint64_t,2> meta{1,1};
    std::array<unsigned,15> reads{};
    bool success=true;
    std::vector<uint64_t> unknown{0};
    FaultBackend(){result[0]=1;result[10]=1;result[13]=1;result[14]=1;result[15]=1;}
    void write(unsigned,const void*,size_t){}
    bool launch(unsigned,unsigned){return success;}
    void read(unsigned id,void* dest,size_t size){
        ++reads[id];
        if(id==14)std::memcpy(dest,result.data(),size);
        else if(id==13)std::memcpy(dest,meta.data(),size);
        else if(id==10)std::memcpy(dest,unknown.data(),size);
        else std::memset(dest,0,size);
    }
};
int main(){
    using K=fpga_search::SearchKernel<0>;using L=fpga_search::SearchRegionLimits;
    unsigned transactions=0;
    for(unsigned mode=0;mode<2;++mode) {
        Image image(mode);CpuBackend backend(mode);Session<CpuBackend> session(backend,image.data.data(),unsigned(image.data.size()),image.config.data());
        uint32_t root=0;uint64_t forbidden[1]{},costs[8]{},sem_keys[2]={3,7};uint8_t pseudo[2]={0,1},blocked[2]{};
        K::State requirements[2]{};auto& full=requirements[0];
        full.signals.count=32;for(unsigned i=0;i<32;++i)full.signals.data[i]=i+1;
        full.bits.count=16;for(unsigned i=0;i<16;++i)full.bits.data[i]={201+i,1,1};
        full.values.count=8;for(unsigned i=0;i<8;++i)full.values.data[i]={301+i,11+i};
        K::Provider::View view{4,2,forbidden,costs,pseudo,blocked,nullptr,sem_keys,requirements,0,2,{nullptr,nullptr,nullptr,0,0,0},7,1};
        const unsigned statuses[11]={0,5,5,5,0,1,1,0,6,6,0};
        uint64_t last_epoch=0;
        for(unsigned tx=0;tx<11;++tx) {
            auto& second=requirements[1];second={};
            if(tx==1){second.signals.count=1;second.signals.data[0]=100;}
            if(tx==2){second.bits.count=1;second.bits.data[0]={500,1,1};}
            if(tx==3){second.values.count=1;second.values.data[0]={600,1};}
            if(tx==4){second=full;for(unsigned i=0;i<16;++i)second.bits.data[i]={201+i,2,2};}
            if(tx==5){second.bits.count=1;second.bits.data[0]={216,1,0};}
            if(tx==6){second.values.count=1;second.values.data[0]={308,99};}
            forbidden[0]=tx==9?4:0;
            auto packet=search_kernel_host::packet<L>(view,2,1,8,{});
            if(tx==8)packet[0]=0;
            auto output=session.search(&root,1,packet.data(),packet.size());
            const auto& r=output.result;assert(r[0]==statuses[tx]);
            if(tx!=8 && tx!=9)++last_epoch;
            assert(output.meta[0]==last_epoch);
            if(r[0]==0) {
                const std::vector<uint32_t> path={0,1,0,3,10,11,1,0,1,2,0,7,11,12,1,0};
                assert(output.path==path && r[1]==2 && r[7]==2);
                uint64_t expected[65]{};expected[0]=2|(uint64_t(32)<<32)|(uint64_t(16)<<40)|(uint64_t(8)<<48);
                for(unsigned i=0;i<16;++i)expected[1+i]=(2*i+1)|(uint64_t(2*i+2)<<32);
                for(unsigned i=0;i<8;++i)expected[17+i]=(201+2*i)|(uint64_t(202+2*i)<<32);
                for(unsigned i=0;i<16;++i)expected[25+i]=expected[41+i]=tx==4?3:1;
                for(unsigned i=0;i<8;++i)expected[57+i]=(301+i)|(uint64_t(11+i)<<32);
                for(unsigned i=0;i<65;++i)assert(r[16+i]==expected[i]);
            }else assert(output.path.empty());
            assert(output.unknown_nodes.empty() && output.unknown_pips.empty());++transactions;
        }
        assert(backend.writes[0]==1 && backend.writes[1]==1 && backend.writes[13]==1 && backend.writes[3]==11 && backend.writes[4]==11);
        for(unsigned id:{6,7,8,9,10,11,12,14})assert(backend.writes[id]==0);
        assert(session.stats().completed==11 && !session.failed());
        std::cout<<"RESIDENT_CMODEL_PASS mode="<<mode<<" transactions=11 full_state=32,16,8 full_workspace=1 hardware_executed=false\n";
    }
    std::vector<std::function<void(FaultBackend&)>> faults={
        [](auto& b){b.success=false;},[](auto& b){b.result[15]=0;},[](auto& b){b.result[0]=7;},
        [](auto& b){b.result[7]=524289;},[](auto& b){b.result[8]=5;},[](auto& b){b.result[9]=1100755;},
        [](auto& b){b.meta[0]=2;},[](auto& b){b.result[13]=0;},
        [](auto& b){b.result[16]=1;},[](auto& b){b.result[7]=1;},
        [](auto& b){b.result[8]=1;b.unknown[0]=0;},[](auto& b){b.result[8]=1;b.unknown[0]=16;}
    };
    Image image(0);uint32_t root=0;uint64_t packet[32]{};packet[1]=32;packet[2]=4;packet[6]=2;packet[7]=1;
    for(size_t index=0;index<faults.size();++index) {
        FaultBackend backend;faults[index](backend);Session<FaultBackend> session(backend,image.data.data(),unsigned(image.data.size()),image.config.data());
        bool rejected=false;try{session.search(&root,1,packet,32);}catch(const std::runtime_error&){rejected=true;}
        assert(rejected && session.failed() && session.stats().completed==0);
        if(index<10)assert(backend.reads[10]==0 && backend.reads[11]==0 && backend.reads[12]==0);
        const auto reads=backend.reads;rejected=false;
        try{session.search(&root,1,packet,32);}catch(const std::runtime_error&){rejected=true;}
        assert(rejected && reads==backend.reads);
    }
    {FaultBackend backend;Session<FaultBackend> session(backend,image.data.data(),unsigned(image.data.size()),image.config.data());
     bool rejected=false;try{session.search(&root,0,packet,32);}catch(const std::runtime_error&){rejected=true;}
     assert(rejected && !session.failed() && session.stats().attempts==0);
     auto out=session.search(&root,1,packet,32);assert(out.result[0]==1 && session.stats().completed==1);}
    std::cout<<"SEARCH_EXCHANGE_ALL_PASS production_transactions="<<transactions<<" transport_faults="<<faults.size()<<" host_preflight_recovery=1 hardware_executed=false\n";
}
