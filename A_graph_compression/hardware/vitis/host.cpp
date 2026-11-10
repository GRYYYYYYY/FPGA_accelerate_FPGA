#include "host_contract.hpp"
#include <xrt/xrt_device.h>
#include <xrt/xrt_kernel.h>
#include <xrt/xrt_bo.h>
#include <experimental/xrt_xclbin.h>
#include <chrono>
#include <filesystem>
#include <iomanip>
#include <iostream>
namespace bg=board_graph;
using Clock=std::chrono::steady_clock;
static double elapsed(Clock::time_point start){return std::chrono::duration<double,std::milli>(Clock::now()-start).count();}
static uint32_t mode_id(const std::string& mode){bg::require(mode=="csr"||mode=="compact","Expected csr or compact");return mode=="compact";}
static std::string quoted(const std::string& text){
    std::ostringstream out;out<<'"';
    for(unsigned char c:text){
        if(c=='"'||c=='\\')out<<'\\'<<c;
        else if(c<32)out<<"\\u"<<std::hex<<std::setw(4)<<std::setfill('0')<<unsigned(c)<<std::dec;
        else out<<c;
    }
    out<<'"';return out.str();
}
int main(int argc,char** argv){try{
    if(argc==4&&std::string(argv[1])=="--preflight"){
        auto work=bg::manifest(argv[2]);auto image=bg::words(work.image,bg::image_words),config=bg::words(work.config,32);
        bg::descriptor(image,config,mode_id(argv[3]));uint64_t requests=0,records=0,failed=0;
        for(const auto& path:work.cases){auto c=bg::fixture(path);requests+=c.count;records+=c.written;failed+=c.failed;}
        std::cout<<"{\"status\":\"host_shape_contract_passed_no_device_execution\",\"cases\":"<<work.cases.size()
            <<",\"requests\":"<<requests<<",\"records\":"<<records<<",\"expected_failed_requests\":"<<failed<<"}\n";return 0;
    }
    bg::require(argc==8,"Usage: host --preflight manifest mode OR host xclbin device mode DDR[0]|HBM[0] manifest NEW_output_dir repetitions");
    auto app_start=Clock::now();const std::string mode=argv[3],tag=argv[4];
    bg::require(tag=="DDR[0]"||tag=="HBM[0]","Unsupported memory comparison target");
    size_t consumed=0;auto repetitions=std::stoul(argv[7],&consumed);
    bg::require(consumed==std::strlen(argv[7])&&repetitions>0&&repetitions<=100,"Invalid repetitions");
    const std::filesystem::path directory=argv[6];bg::require(!std::filesystem::exists(directory),"Refusing existing result directory");
    auto work=bg::manifest(argv[5]);auto image=bg::words(work.image,bg::image_words),config=bg::words(work.config,32);
    bg::descriptor(image,config,mode_id(mode));
    // Check all fixture bounds before programming or allocating a device buffer.
    for(const auto& path:work.cases)bg::fixture(path);
    auto input_ms=elapsed(app_start);auto start=Clock::now();xrt::xclbin xclbin(argv[1]);
    bg::require(xclbin.get_target_type()==xrt::xclbin::target_type::hw,"This runner records real hardware only");
    xrt::device device{std::string(argv[2])};auto uuid=device.load_xclbin(xclbin);xrt::kernel kernel(device,uuid,"graph_accel");
    auto device_ms=elapsed(start);std::array<int,6> groups;
    for(int index=0;index<6;++index){
        groups[index]=kernel.group_id(index);bool found=false;
        for(const auto& memory:xclbin.get_mems())if(memory.get_index()==groups[index]){
            bg::require(memory.get_used()&&memory.get_tag()==tag,"Actual kernel memory mapping differs from requested backend");
            auto type=memory.get_type();
            bg::require(tag=="HBM[0]"?type==xrt::xclbin::mem::memory_type::hbm:
                (type==xrt::xclbin::mem::memory_type::ddr4||type==xrt::xclbin::mem::memory_type::ddr3||type==xrt::xclbin::mem::memory_type::dram),"Actual memory type differs");found=true;
        }
        bg::require(found,"Kernel memory group absent from topology");
    }
    std::filesystem::create_directories(directory);start=Clock::now();
    xrt::bo bi(device,image.size()*4,groups[0]),bc(device,128,groups[1]),bq(device,bg::request_words*4,groups[2]);
    xrt::bo bo(device,bg::output_words*4,groups[3]),br(device,bg::result_words*4,groups[4]),bn(device,8,groups[5]);
    auto allocation_ms=elapsed(start);start=Clock::now();bi.write(image.data());bc.write(config.data());
    bi.sync(XCL_BO_SYNC_BO_TO_DEVICE);bc.sync(XCL_BO_SYNC_BO_TO_DEVICE);auto graph_h2d_ms=elapsed(start);
    std::ofstream report(directory/"batches.jsonl");bg::require(bool(report),"Cannot create batch report");report<<std::setprecision(17);
    size_t completed=0;
    for(size_t repeat=0;repeat<repetitions;++repeat)for(size_t index=0;index<work.cases.size();++index){
        auto batch_start=Clock::now();auto c=bg::fixture(work.cases[index]);
        std::vector<uint32_t> output(bg::output_words,bg::sentinel),result(bg::result_words,bg::sentinel),requests(bg::request_words,0);
        std::copy(c.requests.begin(),c.requests.end(),requests.begin());uint32_t counts[2]={bg::sentinel,bg::sentinel};
        auto load_ms=elapsed(batch_start);start=Clock::now();
        bq.write(requests.data());bo.write(output.data());br.write(result.data());bn.write(counts);
        bq.sync(XCL_BO_SYNC_BO_TO_DEVICE);bo.sync(XCL_BO_SYNC_BO_TO_DEVICE);br.sync(XCL_BO_SYNC_BO_TO_DEVICE);bn.sync(XCL_BO_SYNC_BO_TO_DEVICE);
        auto batch_h2d_ms=elapsed(start);start=Clock::now();
        auto run=kernel(bi,bc,bq,bo,br,bn,c.count,c.capacity);
        bg::require(run.wait()==ERT_CMD_STATE_COMPLETED,"Kernel did not complete successfully");auto kernel_wall_ms=elapsed(start);start=Clock::now();
        bn.sync(XCL_BO_SYNC_BO_FROM_DEVICE);br.sync(XCL_BO_SYNC_BO_FROM_DEVICE);bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        bn.read(counts);br.read(result.data());bo.read(output.data());auto d2h_ms=elapsed(start);start=Clock::now();
        bg::compare(c,result,output,counts);auto validation_ms=elapsed(start);start=Clock::now();
        std::ofstream raw(directory/("batch_"+std::to_string(completed)+".bin"),std::ios::binary);
        uint32_t header[4]={counts[0],counts[1],c.count,c.capacity};raw.write(reinterpret_cast<char*>(header),16);
        raw.write(reinterpret_cast<char*>(result.data()),result.size()*4);raw.write(reinterpret_cast<char*>(output.data()),output.size()*4);
        raw.close();bg::require(bool(raw),"Cannot write readback evidence");auto export_ms=elapsed(start);
        report<<"{\"repeat\":"<<repeat<<",\"case\":"<<index<<",\"written\":"<<counts[0]<<",\"failed\":"<<counts[1]
            <<",\"fixture_load_ms\":"<<load_ms<<",\"batch_h2d_ms\":"<<batch_h2d_ms<<",\"kernel_wall_ms\":"<<kernel_wall_ms
            <<",\"d2h_ms\":"<<d2h_ms<<",\"validation_ms\":"<<validation_ms<<",\"export_ms\":"<<export_ms<<",\"batch_wall_ms\":"<<elapsed(batch_start)<<"}\n";
        report.flush();bg::require(bool(report),"Cannot write measurement");++completed;
    }
    std::ofstream summary(directory/"summary.json");summary<<std::setprecision(17)
        <<"{\"status\":\"hardware_batches_readback_verified\",\"mode\":\""<<mode<<"\",\"memory\":\""<<tag
        <<"\",\"device_bdf\":"<<quoted(device.get_info<xrt::info::device::bdf>())
        <<",\"device_name\":"<<quoted(device.get_info<xrt::info::device::name>())
        <<",\"xclbin_uuid\":"<<quoted(uuid.to_string())
        <<",\"argument_memory_groups\":["<<groups[0]<<','<<groups[1]<<','<<groups[2]<<','<<groups[3]<<','<<groups[4]<<','<<groups[5]<<']'
        <<",\"repetitions\":"<<repetitions<<",\"cases_per_repeat\":"<<work.cases.size()
        <<",\"completed_batches\":"<<completed<<",\"input_preflight_ms\":"<<input_ms<<",\"device_open_load_ms\":"<<device_ms
        <<",\"allocation_ms\":"<<allocation_ms<<",\"graph_h2d_ms\":"<<graph_h2d_ms<<",\"application_wall_ms\":"<<elapsed(app_start)
        <<",\"scope\":\"adjacency_kernel_only_with_full_output_guards; not_full_router_or_power\"}\n";
    summary.close();bg::require(bool(summary),"Cannot write summary");return 0;
}catch(const std::exception& e){std::cerr<<"BOARD_HOST_FAIL "<<e.what()<<'\n';return 1;}}
