#pragma once
#include "host_contract.hpp"
#include <chrono>
#include <memory>

namespace kernel_router {
enum class SyncDirection {to_device,from_device};
struct ExchangeShape {size_t requests,output,result,counts;};
inline ExchangeShape exchange_shape(uint32_t n,uint32_t capacity) {
    board_graph::require(n>0&&n<=128&&capacity<=board_graph::output_words,"Router exchange bounds");
    return {size_t(n)*4,(size_t(capacity)+8)*4,(size_t(n)*3+8)*4,40};
}
struct ExchangeStats {
    uint64_t calls=0,requests=0,h2d_bytes=0,d2h_bytes=0;
    double h2d_ms=0,kernel_wall_ms=0,d2h_ms=0;
};
template<class Buffer,class Launch>
void exchange(std::array<std::unique_ptr<Buffer>,6>& buffers,const uint32_t* requests,
              uint32_t* output,uint32_t* result,uint32_t* counts,uint32_t n,uint32_t capacity,
              Launch launch,ExchangeStats& stats) {
    using Clock=std::chrono::steady_clock;
    auto elapsed=[](Clock::time_point t){return std::chrono::duration<double,std::milli>(Clock::now()-t).count();};
    const auto shape=exchange_shape(n,capacity);
    auto start=Clock::now();
    buffers[2]->write(requests,shape.requests);buffers[3]->write(output,shape.output);
    buffers[4]->write(result,shape.result);buffers[5]->write(counts,shape.counts);
    buffers[2]->sync(SyncDirection::to_device,shape.requests);buffers[3]->sync(SyncDirection::to_device,shape.output);
    buffers[4]->sync(SyncDirection::to_device,shape.result);buffers[5]->sync(SyncDirection::to_device,shape.counts);
    stats.h2d_ms+=elapsed(start);start=Clock::now();
    board_graph::require(launch(n,capacity),"XRT kernel did not complete successfully");
    stats.kernel_wall_ms+=elapsed(start);start=Clock::now();
    buffers[5]->sync(SyncDirection::from_device,shape.counts);
    buffers[4]->sync(SyncDirection::from_device,shape.result);
    buffers[3]->sync(SyncDirection::from_device,shape.output);
    buffers[5]->read(counts,shape.counts);buffers[4]->read(result,shape.result);buffers[3]->read(output,shape.output);
    stats.d2h_ms+=elapsed(start);++stats.calls;stats.requests+=n;
    stats.h2d_bytes+=shape.requests+shape.output+shape.result+shape.counts;
    stats.d2h_bytes+=shape.output+shape.result+shape.counts;
}
}
