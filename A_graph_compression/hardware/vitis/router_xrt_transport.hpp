#pragma once
#include "router_exchange.hpp"
#include <xrt/xrt_device.h>
#include <xrt/xrt_kernel.h>
#include <xrt/xrt_bo.h>
#include <experimental/xrt_xclbin.h>
#include <filesystem>
#include <iomanip>

namespace kernel_router {
inline std::string json_text(const std::string& text) {
    std::ostringstream out;out<<'"';
    for(unsigned char c:text) {
        if(c=='"'||c=='\\')out<<'\\'<<c;
        else if(c<32)out<<"\\u"<<std::hex<<std::setw(4)<<std::setfill('0')<<unsigned(c)<<std::dec;
        else out<<c;
    }
    out<<'"';return out.str();
}
class DeviceBuffer {
public:
    xrt::bo bo;
    DeviceBuffer(xrt::device& device,size_t bytes,int group):bo(device,bytes,group){}
    void write(const void* p,size_t bytes){bo.write(p,bytes,0);}
    void read(void* p,size_t bytes){bo.read(p,bytes,0);}
    void sync(SyncDirection direction,size_t bytes){bo.sync(direction==SyncDirection::to_device?
        XCL_BO_SYNC_BO_TO_DEVICE:XCL_BO_SYNC_BO_FROM_DEVICE,bytes,0);}
};
class XrtTransport {
    std::vector<uint32_t> image,config;
    const uint32_t* bound_image=nullptr;
    const uint32_t* bound_config=nullptr;
    std::unique_ptr<xrt::device> device;
    std::unique_ptr<xrt::kernel> kernel;
    std::array<std::unique_ptr<DeviceBuffer>,6> buffers;
    std::array<int,6> groups;
    std::filesystem::path directory;
    std::string bdf,device_name,uuid,memory;
    double setup_ms=0,graph_h2d_ms=0;
    ExchangeStats measurements;
public:
    XrtTransport(const std::string& graph,const std::string& descriptor,const std::string& binary,
                 const std::string& device_id,const std::string& tag,const std::string& output):directory(output),memory(tag) {
        using Clock=std::chrono::steady_clock;auto start=Clock::now();
        auto elapsed=[](Clock::time_point t){return std::chrono::duration<double,std::milli>(Clock::now()-t).count();};
        board_graph::require(tag=="DDR[0]"||tag=="HBM[0]","Explicit DDR[0] or HBM[0] required");
        board_graph::require(!std::filesystem::exists(directory),"Transport evidence directory already exists");
        image=board_graph::words(graph,board_graph::image_words);config=board_graph::words(descriptor,32);
        board_graph::require(config.size()==32&&config[0]<=1,"Invalid graph descriptor");
        board_graph::descriptor(image,config,config[0]);
        xrt::xclbin xclbin(binary);
        board_graph::require(xclbin.get_target_type()==xrt::xclbin::target_type::hw,"Real hardware xclbin required");
        device=std::make_unique<xrt::device>(device_id);auto loaded=device->load_xclbin(xclbin);
        kernel=std::make_unique<xrt::kernel>(*device,loaded,"graph_accel");
        for(int i=0;i<6;++i) {
            groups[i]=kernel->group_id(i);bool found=false;
            for(const auto& mem:xclbin.get_mems())if(mem.get_index()==groups[i]) {
                board_graph::require(mem.get_used()&&mem.get_tag()==tag,"Actual kernel memory group differs");
                auto type=mem.get_type();
                board_graph::require(tag=="HBM[0]"?type==xrt::xclbin::mem::memory_type::hbm:
                    (type==xrt::xclbin::mem::memory_type::ddr4||type==xrt::xclbin::mem::memory_type::ddr3||
                     type==xrt::xclbin::mem::memory_type::dram),"Actual memory type differs");found=true;
            }
            board_graph::require(found,"Kernel argument memory group missing");
        }
        const size_t sizes[]={image.size()*4,128,128*4,(board_graph::output_words+8)*4,(128*3+8)*4,40};
        for(unsigned i=0;i<6;++i)buffers[i]=std::make_unique<DeviceBuffer>(*device,sizes[i],groups[i]);
        bdf=device->get_info<xrt::info::device::bdf>();device_name=device->get_info<xrt::info::device::name>();uuid=loaded.to_string();
        setup_ms=elapsed(start);start=Clock::now();
        buffers[0]->write(image.data(),image.size()*4);buffers[1]->write(config.data(),128);
        buffers[0]->sync(SyncDirection::to_device,image.size()*4);buffers[1]->sync(SyncDirection::to_device,128);
        graph_h2d_ms=elapsed(start);
        std::filesystem::create_directories(directory);write_summary(false);
    }
    void operator()(const uint32_t* im,const uint32_t* cf,const uint32_t* rq,uint32_t* out,
                    uint32_t* result,uint32_t* counts,uint32_t n,uint32_t capacity) {
        exchange_shape(n,capacity);
        board_graph::require(im&&cf&&rq&&out&&result&&counts,"Null transport buffer");
        if(!bound_image) {
            board_graph::require(std::equal(image.begin(),image.end(),im)&&std::equal(config.begin(),config.end(),cf),
                                 "Provider image differs from resident device image");bound_image=im;bound_config=cf;
        } else board_graph::require(im==bound_image&&cf==bound_config&&std::equal(config.begin(),config.end(),cf),
                                    "Resident image/config identity changed");
        exchange(buffers,rq,out,result,counts,n,capacity,[&](uint32_t count,uint32_t words) {
            auto run=(*kernel)(buffers[0]->bo,buffers[1]->bo,buffers[2]->bo,buffers[3]->bo,
                              buffers[4]->bo,buffers[5]->bo,count,words);
            return run.wait()==ERT_CMD_STATE_COMPLETED;
        },measurements);
    }
    const ExchangeStats& stats() const {return measurements;}
    void write_summary(bool complete) const {
        std::ofstream out(directory/(complete?"complete.json":"opened.json"));
        board_graph::require(bool(out),"Cannot write transport evidence");
        out<<std::setprecision(17)<<"{\"backend\":\"xrt_hardware\",\"complete\":"<<(complete?"true":"false")
           <<",\"device_bdf\":"<<json_text(bdf)<<",\"device_name\":"<<json_text(device_name)
           <<",\"xclbin_uuid\":"<<json_text(uuid)<<",\"memory\":"<<json_text(memory)<<",\"groups\":[";
        for(unsigned i=0;i<6;++i){if(i)out<<',';out<<groups[i];}
        out<<"],\"setup_ms\":"<<setup_ms<<",\"graph_h2d_ms\":"<<graph_h2d_ms
           <<",\"calls\":"<<measurements.calls<<",\"requests\":"<<measurements.requests
           <<",\"h2d_bytes\":"<<measurements.h2d_bytes<<",\"d2h_bytes\":"<<measurements.d2h_bytes
           <<",\"h2d_ms\":"<<measurements.h2d_ms<<",\"kernel_wall_ms\":"<<measurements.kernel_wall_ms
           <<",\"d2h_ms\":"<<measurements.d2h_ms
           <<",\"scope\":\"CPU search and negotiation with device adjacency; kernel wall is host-observed, not device profiling\"}\n";
        out.close();board_graph::require(bool(out),"Cannot finish transport evidence");
    }
};
}
