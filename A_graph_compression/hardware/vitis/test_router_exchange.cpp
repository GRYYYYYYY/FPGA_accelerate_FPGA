#include "router_exchange.hpp"
#include <iostream>
namespace kr=kernel_router;
namespace bg=board_graph;
struct FakeBuffer {
    std::vector<uint8_t> host,device;
    unsigned writes=0,reads=0,to=0,from=0;
    explicit FakeBuffer(size_t n):host(n,0x42),device(n,0x17){}
    void write(const void* p,size_t n){bg::require(n<=host.size(),"fake write bounds");std::memcpy(host.data(),p,n);++writes;}
    void read(void* p,size_t n){bg::require(n<=host.size(),"fake read bounds");std::memcpy(p,host.data(),n);++reads;}
    void sync(kr::SyncDirection dir,size_t n) {
        bg::require(n<=host.size(),"fake sync bounds");
        if(dir==kr::SyncDirection::to_device){std::copy_n(host.begin(),n,device.begin());++to;}
        else {std::copy_n(device.begin(),n,host.begin());++from;}
    }
    uint32_t get(size_t i)const{uint32_t x;bg::require(i*4+4<=device.size(),"fake device load bounds");std::memcpy(&x,device.data()+4*i,4);return x;}
    void set(size_t i,uint32_t x){bg::require(i*4+4<=device.size(),"fake device store bounds");std::memcpy(device.data()+4*i,&x,4);}
};
int main(){try{
    unsigned checked=0;
    for(uint32_t n:{1u,2u,127u,128u})for(bool zero_capacity:{false,true}) {
        uint32_t cap=zero_capacity?0:n*8;
        auto shape=kr::exchange_shape(n,cap);
        std::array<std::unique_ptr<FakeBuffer>,6> buffers;
        size_t sizes[]={16,128,shape.requests,shape.output,shape.result,shape.counts};
        for(unsigned i=0;i<6;++i)buffers[i]=std::make_unique<FakeBuffer>(sizes[i]);
        std::vector<uint32_t> requests(n),output(shape.output/4,bg::sentinel),result(shape.result/4,bg::sentinel),counts(10,bg::sentinel);
        for(uint32_t i=0;i<n;++i)requests[i]=100+i;
        kr::ExchangeStats stats;
        kr::exchange(buffers,requests.data(),output.data(),result.data(),counts.data(),n,cap,
          [&](uint32_t count,uint32_t capacity){
            bg::require(count==n&&capacity==cap,"Wrong scalar ABI");
            for(uint32_t i=0;i<n;++i)bg::require(buffers[2]->get(i)==requests[i],"Requests not synchronized before launch");
            for(unsigned b:{3u,4u,5u})for(size_t i=0;i<sizes[b]/4;++i)
                bg::require(buffers[b]->get(i)==bg::sentinel,"Output guards not synchronized before launch");
            for(uint32_t i=0;i<n;++i) {
                buffers[4]->set(i*3,zero_capacity?0:i);buffers[4]->set(i*3+1,zero_capacity?0:1);buffers[4]->set(i*3+2,zero_capacity?2:0);
                if(!zero_capacity)for(unsigned k=0;k<8;++k)buffers[3]->set(i*8+k,1000+i*8+k);
            }
            buffers[5]->set(0,zero_capacity?0:n);buffers[5]->set(1,zero_capacity?n:0);return true;
          },stats);
        bg::require(stats.calls==1&&stats.requests==n,"Wrong call accounting");
        if(n==1&&!zero_capacity)bg::require(stats.h2d_bytes==152&&stats.d2h_bytes==148,"Wrong byte accounting");
        for(uint32_t i=0;i<n;++i) {
            bg::require(result[3*i]==(zero_capacity?0:i)&&result[3*i+1]==(zero_capacity?0:1)&&result[3*i+2]==(zero_capacity?2:0),"Result readback differs");
            if(!zero_capacity)for(unsigned k=0;k<8;++k)bg::require(output[i*8+k]==1000+i*8+k,"Output readback differs");
        }
        bg::require(counts[0]==(zero_capacity?0:n)&&counts[1]==(zero_capacity?n:0),"Count readback differs");
        for(size_t i=cap;i<output.size();++i)bg::require(output[i]==bg::sentinel,"Output guard differs");
        for(size_t i=n*3;i<result.size();++i)bg::require(result[i]==bg::sentinel,"Result guard differs");
        for(unsigned i=2;i<10;++i)bg::require(counts[i]==bg::sentinel,"Count guard differs");
        for(unsigned i=0;i<2;++i)bg::require(buffers[i]->writes==0&&buffers[i]->to==0&&buffers[i]->from==0,"Resident graph touched during exchange");
        for(unsigned i=3;i<6;++i)bg::require(buffers[i]->to==1&&buffers[i]->from==1&&buffers[i]->reads==1,"Incomplete transfer sequence");
        bool rejected=false;
        try{kr::exchange(buffers,requests.data(),output.data(),result.data(),counts.data(),n,cap,
                        [](uint32_t,uint32_t){return false;},stats);}catch(const std::runtime_error&){rejected=true;}
        bg::require(rejected&&stats.calls==1,"Failed launch accepted or counted complete");++checked;
    }
    for(auto args:{std::pair<uint32_t,uint32_t>{0,0},{129,0},{1,1048577}}) {
        bool rejected=false;try{kr::exchange_shape(args.first,args.second);}catch(const std::runtime_error&){rejected=true;}
        bg::require(rejected,"Invalid exchange bounds accepted");
    }
    std::cout<<"ROUTER_EXCHANGE_MOCK_PASS cases="<<checked<<" failed_launches=8 invalid_bounds=3 hardware_executed=false\n";
    return 0;
}catch(const std::exception& error){std::cerr<<"ROUTER_EXCHANGE_MOCK_FAIL "<<error.what()<<'\n';return 1;}}
