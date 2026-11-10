#pragma once
// Host-only binding for the exact production top C model. The production image
// loader validates the full AGRAPH01 descriptor; raw views are used only by
// explicit synthetic test fixtures. No native search/adjacency fallback exists.
#include "host_contract.hpp"
#include "search_kernel.hpp"
#include <type_traits>
extern "C" void search_kernel_csr(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
extern "C" void search_kernel_compact(const uint32_t*,const uint32_t*,unsigned,const uint32_t*,const uint64_t*,unsigned,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint64_t*,uint32_t*,uint64_t*,uint64_t*);
namespace kernel_route {
struct ImageView {const uint32_t *image,*config;unsigned image_words;};
inline thread_local const ImageView* active_image=nullptr;
struct ImageScope {
    ImageView view;
    explicit ImageScope(ImageView v):view(v) {
        if(active_image || !view.image || !view.config || view.config[0]>1)throw std::invalid_argument("invalid/nested kernel image binding");
        active_image=&view;
    }
    ~ImageScope(){active_image=nullptr;}
    ImageScope(const ImageScope&)=delete;ImageScope& operator=(const ImageScope&)=delete;
};
struct LoadedImage {
    std::vector<uint32_t> image,config;
    LoadedImage(const std::string& image_path,const std::string& config_path):image(board_graph::words(image_path,board_graph::image_words)),config(board_graph::words(config_path,32)) {
        if(config.size()!=32 || config[0]>1)throw std::invalid_argument("invalid kernel descriptor");
        board_graph::descriptor(image,config,config[0]);
    }
    ImageView view()const{return {image.data(),config.data(),unsigned(image.size())};}
};
struct KernelCounters {
    uint64_t calls=0,packets=0,serialized_words=0,submitted_words=0;
    unsigned max_packet_words=0,max_roots=0;
};
inline thread_local KernelCounters kernel_counters;
template<class L> void invoke(ImageView image,const uint32_t* roots,const uint64_t* packet,unsigned packet_words,
        uint64_t* heap,uint64_t* slots,uint64_t* records,uint64_t* keys,uint64_t* unknown_nodes,uint64_t* unknown_pips,uint32_t* path,uint64_t* meta,uint64_t* result) {
    using P=fpga_search::SearchRegionLimits;using M=fpga_search::SearchMetadataLimits;
    static_assert(L::nodes==P::nodes && L::degree==P::degree && L::roots==P::roots && L::unknown_pips==P::unknown_pips && L::path==P::path && L::expansions==P::expansions,"production kernel search limits differ");
    static_assert(L::signals==P::signals && L::bits==P::bits && L::values==P::values && L::slots==P::slots && L::labels==P::labels && L::heap==P::heap,"production kernel storage limits differ");
    static_assert(L::semantics==M::semantics && L::attributes==M::attributes && L::protected_pips==M::protected_pips && L::config_owners==M::owners && L::config_history==M::history && L::fixed_records==M::fixed,"production kernel metadata limits differ");
    ++kernel_counters.calls;kernel_counters.submitted_words+=packet_words;
    if(image.config[0]==0)search_kernel_csr(image.image,image.config,image.image_words,roots,packet,packet_words,heap,slots,records,keys,unknown_nodes,unknown_pips,path,meta,result);
    else search_kernel_compact(image.image,image.config,image.image_words,roots,packet,packet_words,heap,slots,records,keys,unknown_nodes,unknown_pips,path,meta,result);
}
} // namespace kernel_route
