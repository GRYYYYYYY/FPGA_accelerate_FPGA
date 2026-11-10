#pragma once
// Host runtime for full search only. Outer negotiation remains on the CPU.
#include "search_xrt_v1/transport.hpp"
#include <filesystem>
#include <iomanip>

namespace full_search_xrt {
inline std::string quote(const std::string& s) {
    std::ostringstream out;out<<'"';
    for(unsigned char c:s){if(c=='"' || c=='\\')out<<'\\'<<c;else if(c<32)out<<"\\u"<<std::hex<<std::setw(4)<<std::setfill('0')<<unsigned(c)<<std::dec;else out<<c;}
    out<<'"';return out.str();
}
class Runtime {
    std::filesystem::path directory;
    std::string layout;
    std::unique_ptr<search_xrt::Transport> backend;
    std::unique_ptr<search_xrt::Session<search_xrt::Transport>> session;
    double open_ms=0;
    unsigned mode;
    void summary(const std::string& name,bool complete)const {
        const auto& s=session->stats();
        std::ofstream out(directory/name);search_xrt::require(bool(out),"cannot write transport evidence");
        out<<std::setprecision(17)<<"{\"backend\":\"xrt_hardware_full_search_cpu_negotiation\",\"complete\":"<<(complete?"true":"false")
           <<",\"mode\":"<<quote(mode?"compact":"csr")<<",\"layout\":"<<quote(layout)
           <<",\"device_bdf\":"<<quote(backend->bdf())<<",\"device_name\":"<<quote(backend->device_name())<<",\"xclbin_uuid\":"<<quote(backend->uuid())
           <<",\"open_ms\":"<<open_ms<<",\"setup_ms\":"<<s.setup_ms<<",\"setup_h2d_bytes\":"<<s.setup_h2d_bytes
           <<",\"attempts\":"<<s.attempts<<",\"completed\":"<<s.completed<<",\"h2d_bytes\":"<<s.h2d_bytes<<",\"d2h_bytes\":"<<s.d2h_bytes
           <<",\"h2d_ms\":"<<s.h2d_ms<<",\"d2h_ms\":"<<s.d2h_ms<<",\"kernel_wall_ms\":"<<s.kernel_wall_ms<<",\"argument_groups\":[";
        for(unsigned i=0;i<15;++i){if(i)out<<',';out<<backend->memory().argument_groups[i];}
        out<<"],\"scope\":\"Full search on device; snapshots/negotiation/occupancy on host; sync bytes are API spans, not physical bus traffic\"}\n";
        out.close();search_xrt::require(bool(out),"cannot finish transport evidence");
    }
public:
    Runtime(const kernel_route::LoadedImage& image,const std::string& binary,const std::string& device,const std::string& memory,const std::string& evidence):
        directory(evidence),layout(memory),mode(image.config[0]) {
        search_xrt::require(!std::filesystem::exists(directory),"transport directory already exists");
        auto start=search_xrt::Clock::now();
        std::ifstream file(binary,std::ios::binary|std::ios::ate);search_xrt::require(bool(file),"cannot open xclbin");
        const auto length=file.tellg();search_xrt::require(length>0 && uint64_t(length)<=1024ull*1024*1024,"invalid xclbin size");
        std::vector<char> bytes(static_cast<size_t>(length));file.seekg(0);file.read(bytes.data(),length);search_xrt::require(bool(file),"truncated xclbin");
        backend=std::make_unique<search_xrt::Transport>(bytes,device,layout,image.image,image.config,mode);
        open_ms=search_xrt::elapsed(start);
        session=std::make_unique<search_xrt::Session<search_xrt::Transport>>(*backend,image.image.data(),unsigned(image.image.size()),image.config.data());
        search_xrt::require(std::filesystem::create_directories(directory),"cannot create new transport directory");summary("opened.json",false);
    }
    const search_xrt::Statistics& stats()const{return session->stats();}
    search_xrt::Output search(const uint32_t* roots,size_t count,const uint64_t* packet,size_t words){return session->search(roots,count,packet,words);}
    void finish()const{search_xrt::require(!session->failed(),"transport failed");summary("complete.json",true);}
};
} // namespace full_search_xrt
