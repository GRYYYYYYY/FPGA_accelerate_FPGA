#pragma once
#include "topology.hpp"
#include "../host_contract.hpp"
#include <xrt/xrt_device.h>
#include <xrt/xrt_kernel.h>
#include <xrt/xrt_bo.h>
#include <experimental/xrt_xclbin.h>
#include <memory>

namespace search_xrt {
class Transport {
    std::unique_ptr<xrt::device> device;
    std::unique_ptr<xrt::kernel> kernel;
    std::array<std::unique_ptr<xrt::bo>,15> buffers;
    Topology topology;
    std::string bdf_,name_,uuid_;
    static void metadata(const xrt::xclbin& binary) {
        require(binary.get_target_type()==xrt::xclbin::target_type::hw,"hardware xclbin required");
        require(binary.get_fpga_device_name().find("xcu280")==0,"U280 xclbin required");
        auto k=binary.get_kernel("search_kernel_top");
        require(k.get_args().size()==arguments.size(),"xclbin argument count differs");
        for(unsigned i=0;i<arguments.size();++i) {
            auto a=k.get_arg(int(i));const auto& expected=arguments[i];
            require(a.get_name()==expected.name && a.get_port()==expected.port &&
                    a.get_size()==expected.host_size && a.get_offset()==expected.offset,"xclbin argument ABI differs");
        }
    }
public:
    // Caller must bind the xclbin hash to the CSR/compact build report before
    // constructing this object: identical kernel XML cannot identify that mode.
    Transport(const std::vector<char>& raw_binary,const std::string& device_id,const std::string& layout,
              const std::vector<uint32_t>& image,const std::vector<uint32_t>& config,unsigned mode):topology(raw_binary,layout) {
        require(mode<=1 && config.size()==32 && config[0]==mode,"explicit image mode differs");
        board_graph::descriptor(image,config,mode);
        xrt::xclbin binary(raw_binary);metadata(binary);
        device=std::make_unique<xrt::device>(device_id);
        auto uuid=device->load_xclbin(binary);
        kernel=std::make_unique<xrt::kernel>(*device,uuid,"search_kernel_top:{search_kernel_top_1}",xrt::kernel::cu_access_mode::exclusive);
        for(unsigned id=0;id<arguments.size();++id)if(arguments[id].bytes) {
            const int actual=kernel->group_id(int(id));
            require(actual==topology.argument_groups[id],"runtime group ID differs from group connectivity");
            buffers[id]=std::make_unique<xrt::bo>(*device,allocation_size(id),actual);
        }
        bdf_=device->get_info<xrt::info::device::bdf>();name_=device->get_info<xrt::info::device::name>();uuid_=uuid.to_string();
    }
    const Topology& memory()const{return topology;}
    const std::string& bdf()const{return bdf_;}
    const std::string& device_name()const{return name_;}
    const std::string& uuid()const{return uuid_;}
    void write(unsigned id,const void* source,size_t bytes) {
        require(id<15 && buffers[id] && source && bytes>0 && bytes<=arguments[id].bytes,"invalid H2D span");
        buffers[id]->write(source,bytes,0);buffers[id]->sync(XCL_BO_SYNC_BO_TO_DEVICE,bytes,0);
    }
    void read(unsigned id,void* destination,size_t bytes) {
        require(id<15 && buffers[id] && destination && bytes>0 && bytes<=arguments[id].bytes,"invalid D2H span");
        buffers[id]->sync(XCL_BO_SYNC_BO_FROM_DEVICE,bytes,0);buffers[id]->read(destination,bytes,0);
    }
    bool launch(unsigned image_words,unsigned packet_words) {
        auto run=(*kernel)(*buffers[0],*buffers[1],image_words,*buffers[3],*buffers[4],packet_words,
                          *buffers[6],*buffers[7],*buffers[8],*buffers[9],*buffers[10],*buffers[11],
                          *buffers[12],*buffers[13],*buffers[14]);
        return run.wait()==ERT_CMD_STATE_COMPLETED;
    }
};
} // namespace search_xrt
