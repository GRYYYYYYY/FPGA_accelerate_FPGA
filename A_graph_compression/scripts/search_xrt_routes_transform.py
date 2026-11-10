"""Derive new host-only bindings without modifying the frozen CPU router."""
from derive_search_flat_controller import replace_once as one


def binding(source):
    source = one(source, '#include <type_traits>', '#include <type_traits>\n#include <functional>\n#include "search_xrt_v1/exchange.hpp"')
    source = '\n'.join(line for line in source.splitlines() if not line.startswith('extern "C" void search_kernel_')) + '\n'
    source = one(source, 'inline thread_local KernelCounters kernel_counters;', '''inline thread_local KernelCounters kernel_counters;
using Exchange=std::function<search_xrt::Output(const uint32_t*,size_t,const uint64_t*,size_t)>;
inline thread_local Exchange active_exchange;
inline thread_local unsigned readback_epoch=0,readback_key_count=0;
struct ExchangeScope {
    explicit ExchangeScope(Exchange exchange) {
        if(active_exchange || !active_image || !exchange)throw std::logic_error("invalid/nested resident search transport");
        active_exchange=std::move(exchange);readback_epoch=readback_key_count=0;
    }
    ~ExchangeScope(){active_exchange={};readback_epoch=readback_key_count=0;}
    ExchangeScope(const ExchangeScope&)=delete;ExchangeScope& operator=(const ExchangeScope&)=delete;
};
template<class L> struct Readback {
    // Only returned data lives here; heap/index/records/keys stay in the backend.
    std::unique_ptr<uint64_t[]> unknown_store{new uint64_t[(L::nodes+63)/64]},pip_store{new uint64_t[L::unknown_pips]};
    std::unique_ptr<uint32_t[]> path_store{new uint32_t[size_t(8)*L::path]};
    uint64_t* unknown_nodes=unknown_store.get();uint64_t* unknown_pips=pip_store.get();uint32_t* path=path_store.get();
    unsigned& epoch=readback_epoch;unsigned& key_count=readback_key_count;
};
template<class L> Readback<L>& readback(){static thread_local Readback<L> value;return value;}''')
    source = one(source, 'uint64_t* heap,uint64_t* slots,uint64_t* records,uint64_t* keys,', '')
    begin = source.index('    ++kernel_counters.calls;')
    end = source.index('\n}', begin)
    source = source[:begin] + '''    if(!active_image || image.image!=active_image->image || image.config!=active_image->config || image.image_words!=active_image->image_words || !active_exchange)
        throw std::logic_error("no matching resident search transport");
    if(!packet || packet_words<32 || packet[7]>L::roots)throw std::invalid_argument("invalid resident query shape");
    ++kernel_counters.calls;kernel_counters.submitted_words+=packet_words;
    auto out=active_exchange(roots,size_t(packet[7]),packet,packet_words);
    if(out.result[7]>L::path || out.result[8]>L::nodes || out.result[9]>L::unknown_pips ||
       out.path.size()!=out.result[7]*8 || out.unknown_pips.size()!=out.result[9] ||
       out.unknown_nodes.size()!=(out.result[8]?(image.config[2]+63)/64:0))
        throw std::runtime_error("resident readback shape mismatch");
    std::copy(out.path.begin(),out.path.end(),path);
    std::copy(out.unknown_pips.begin(),out.unknown_pips.end(),unknown_pips);
    std::copy(out.unknown_nodes.begin(),out.unknown_nodes.end(),unknown_nodes);
    std::copy(out.meta.begin(),out.meta.end(),meta);
    std::copy(out.result.begin(),out.result.end(),result);''' + source[end:]
    source = source.replace('// Host-only binding for the exact production top C model.', '// Host-only binding for the resident full-search transport.')
    return source


def adapter(source):
    source = one(source, 'auto& w=flat_controller_adapter::storage<Limits>().workspace;', 'auto& w=readback<Limits>();')
    source = one(source, 'w.heap,w.slots,w.records,w.keys,', '')
    return source.replace('// CPU integration of the actual production search top.', '// Resident device transport integration of the production search top.').replace('// Adjacency and the entire search execute inside the kernel C model.', '// Adjacency and the entire search execute through the active transport.')


def runtime(source):
    source = one(source, '#include "site_inputs.hpp"', '#include "site_inputs.hpp"\n#include "search_xrt_runtime.hpp"')
    source = one(source, 'int main(int argc,char** argv) {try {', '''int main(int argc,char** argv) {try {
    if(argc==5 && std::string(argv[1])=="--preflight") {
        kernel_route::LoadedImage image(argv[2],argv[3]);
        const std::string mode=argv[4];
        require((mode=="csr" || mode=="compact") && image.config[0]==unsigned(mode=="compact"),"preflight mode mismatch");
        std::cout<<"FULL_SEARCH_XRT_IMAGE_PASS hardware_executed=false\\n";return 0;
    }''')
    source = one(source, 'require(argc==10,"usage: site_runtime image routing sites cache iterations budget cap kernel config");',
                 'require(argc==14,"usage: full_search_xrt image routing sites cache iterations budget cap kernel config xclbin device layout NEW_transport_dir (use audited Python launcher)");')
    source = one(source, '    kernel_route::ImageScope kernel_scope(kernel_image.view());', '''    kernel_route::ImageScope kernel_scope(kernel_image.view());
    full_search_xrt::Runtime device(kernel_image,argv[10],argv[11],argv[12],argv[13]);
    kernel_route::ExchangeScope exchange_scope([&](const uint32_t* roots,size_t count,const uint64_t* packet,size_t words){return device.search(roots,count,packet,words);});''')
    source = one(source, '    auto route_start=Clock::now();', '    const auto transport_start=device.stats();\n    auto route_start=Clock::now();')
    source = one(source, '    const auto sc=kernel_route::counters;', '''    const auto transport_end=device.stats();
    require(transport_end.completed-transport_start.completed==kc.calls,"not every search completed on the transport");
    const auto sc=kernel_route::counters;''')
    source = one(source, '<<",\\"peak_kib\\":"<<peak_kib', '''<<",\\"backend\\":\\"xrt_hardware_full_search_cpu_negotiation\\""
        <<",\\"xrt_calls\\":"<<(transport_end.completed-transport_start.completed)
        <<",\\"xrt_h2d_bytes\\":"<<(transport_end.h2d_bytes-transport_start.h2d_bytes)
        <<",\\"xrt_d2h_bytes\\":"<<(transport_end.d2h_bytes-transport_start.d2h_bytes)
        <<",\\"xrt_h2d_ms\\":"<<(transport_end.h2d_ms-transport_start.h2d_ms)
        <<",\\"xrt_d2h_ms\\":"<<(transport_end.d2h_ms-transport_start.d2h_ms)
        <<",\\"xrt_kernel_wall_ms\\":"<<(transport_end.kernel_wall_ms-transport_start.kernel_wall_ms)
        <<",\\"peak_kib\\":"<<peak_kib''')
    source = one(source, 'require(bool(std::cout),"write runtime result");return 0;',
                 'require(bool(std::cout),"write runtime result");device.finish();return 0;')
    return source
