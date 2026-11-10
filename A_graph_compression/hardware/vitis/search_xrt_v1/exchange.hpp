#pragma once
// Host-only resident full-search exchange. Backend writes/reads include sync.
#include "abi.hpp"
#include <algorithm>
#include <chrono>
#include <limits>
#include <stdexcept>
#include <vector>

namespace search_xrt {
inline void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
struct Statistics {
    uint64_t attempts=0,completed=0,setup_h2d_bytes=0,h2d_bytes=0,d2h_bytes=0;
    double setup_ms=0,h2d_ms=0,kernel_wall_ms=0,d2h_ms=0;
};
struct Output {
    std::array<uint64_t,81> result{};
    std::array<uint64_t,2> meta{};
    std::vector<uint32_t> path;
    std::vector<uint64_t> unknown_nodes,unknown_pips;
};
using Clock=std::chrono::steady_clock;
inline double elapsed(Clock::time_point start){return std::chrono::duration<double,std::milli>(Clock::now()-start).count();}

template<class Backend> class Session {
    Backend& backend;
    unsigned image_words,nodes;
    std::array<uint64_t,2> previous{};
    bool poisoned=false;
    Statistics measurements;
    void validate_header(const Output& out,uint32_t target) {
        const auto& r=out.result;const auto& m=out.meta;
        require(r[15]==1 && r[0]<=6 && m[0]<=UINT32_MAX && m[1]<=524288,"invalid result version/status/metadata");
        require(r[7]<=524288 && r[8]<=nodes && r[9]<=1100754 && r[10]<=524288 &&
                r[11]<=131072 && r[12]<=1048576,"result exceeds production capacities");
        if(r[13]) {
            const uint64_t next=previous[0]==UINT32_MAX?1:previous[0]+1;
            require(r[13]==m[0] && r[14]==m[1],"resident workspace metadata mismatch");
            if(m==previous) {
                // Core preflight (e.g. forbidden target) can reject after the
                // packet loader, before resetting the resident search epoch.
                require(r[0]==5 || r[0]==6,"unchanged epoch on executed search");
                for(unsigned i=1;i<13;++i)require(r[i]==0,"rejected search exposes partial result");
            }else require(m[0]==next,"resident workspace epoch mismatch");
        }else {
            require(m==previous && (r[0]==5 || r[0]==6),"rejected preflight mutated metadata");
            for(unsigned i=1;i<15;++i)require(r[i]==0,"preflight exposes partial result");
        }
        if(r[0]==0)require(uint32_t(r[16])==target,"returned target differs");
        else {
            require(r[7]==0,"failed search contains a path");
            for(unsigned i=16;i<81;++i)require(r[i]==0,"failed search contains demand state");
        }
    }
public:
    // Caller must validate the complete AGRAPH01 descriptor before constructing
    // a real backend. This shape check also permits explicit synthetic tests.
    Session(Backend& device,const uint32_t* image,unsigned words,const uint32_t* config):
        backend(device),image_words(words),nodes(config?config[2]:0) {
        require(image && config && words>0 && uint64_t(words)*4<=arguments[0].bytes &&
                nodes>0 && nodes<=1048576 && config[0]<=1,"invalid resident image shape");
        auto start=Clock::now();
        backend.write(0,image,size_t(words)*4);backend.write(1,config,128);
        // Initial epoch=0 makes the production kernel initialize the slot
        // table on its first valid search. No uninitialized slot is consulted.
        backend.write(13,previous.data(),16);
        measurements.setup_h2d_bytes=size_t(words)*4+128+16;
        measurements.setup_ms=elapsed(start);
    }
    Session(const Session&)=delete;Session& operator=(const Session&)=delete;
    const Statistics& stats()const{return measurements;}
    bool failed()const{return poisoned;}
    Output search(const uint32_t* roots,size_t root_count,const uint64_t* packet,size_t packet_words) {
        require(!poisoned,"workspace unusable after transport failure");
        require(roots && packet && root_count>0 && root_count<=1048576 && packet_words>=32 &&
                packet_words<=4194304,"query buffer bounds");
        require(packet[1]==packet_words && packet[2]==nodes && packet[7]==root_count &&
                packet[6]<nodes,"query header/buffer mismatch");
        for(size_t i=0;i<root_count;++i)require(roots[i]<nodes && (!i || roots[i-1]<roots[i]),"roots must be sorted unique nodes");
        Output out;
        try {
            ++measurements.attempts;auto start=Clock::now();
            backend.write(3,roots,root_count*4);measurements.h2d_bytes+=root_count*4;
            backend.write(4,packet,packet_words*8);measurements.h2d_bytes+=packet_words*8;
            measurements.h2d_ms+=elapsed(start);start=Clock::now();
            require(backend.launch(image_words,unsigned(packet_words)),"kernel did not complete successfully");
            measurements.kernel_wall_ms+=elapsed(start);start=Clock::now();
            backend.read(14,out.result.data(),648);measurements.d2h_bytes+=648;
            backend.read(13,out.meta.data(),16);measurements.d2h_bytes+=16;
            validate_header(out,uint32_t(packet[6]));
            out.path.resize(size_t(out.result[7])*8);
            out.unknown_pips.resize(size_t(out.result[9]));
            if(out.result[8])out.unknown_nodes.resize((nodes+63)/64);
            if(!out.path.empty()){backend.read(12,out.path.data(),out.path.size()*4);measurements.d2h_bytes+=out.path.size()*4;}
            if(!out.unknown_pips.empty()){backend.read(11,out.unknown_pips.data(),out.unknown_pips.size()*8);measurements.d2h_bytes+=out.unknown_pips.size()*8;}
            if(!out.unknown_nodes.empty()) {
                backend.read(10,out.unknown_nodes.data(),out.unknown_nodes.size()*8);
                measurements.d2h_bytes+=out.unknown_nodes.size()*8;
                if(nodes%64)require((out.unknown_nodes.back()>>(nodes%64))==0,"unknown bitmap outside node domain");
                uint64_t count=0;for(auto word:out.unknown_nodes)count+=unsigned(__builtin_popcountll(word));
                require(count==out.result[8],"unknown bitmap count mismatch");
            }
            if(!out.path.empty()) {
                require(std::binary_search(roots,roots+root_count,out.path[0]) &&
                        out.path[out.path.size()-7]==packet[6],"path endpoints differ");
                for(size_t i=0;i<out.path.size();i+=8) {
                    require(out.path[i]<nodes && out.path[i+1]<nodes && out.path[i+7]<=1,"invalid path node/direction");
                    if(i)require(out.path[i]==out.path[i-7],"discontinuous path");
                }
            }else if(out.result[0]==0)require(std::binary_search(roots,roots+root_count,uint32_t(packet[6])),"empty path target is not root");
            auto unique_pips=out.unknown_pips;std::sort(unique_pips.begin(),unique_pips.end());
            require(std::adjacent_find(unique_pips.begin(),unique_pips.end())==unique_pips.end(),"duplicate unknown PIP");
            previous=out.meta;measurements.d2h_ms+=elapsed(start);++measurements.completed;
            return out;
        }catch(...){poisoned=true;throw;}
    }
};
} // namespace search_xrt
