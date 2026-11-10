"""Preserve negotiation; execute each search through the actual production ABI."""
from snapshot_routes_transform import transform_routes as snapshot_routes,transform_runtime as snapshot_runtime
from derive_search_flat_controller import replace_once as one

def transform_routes(text):
    return snapshot_routes(text).replace('search_snapshot_route_adapter.hpp','search_kernel_route_adapter.hpp').replace('snapshot_route::','kernel_route::')

def transform_runtime(text):
    text=snapshot_runtime(text).replace('snapshot_route::','kernel_route::').replace('controller_adapter::','flat_controller_adapter::')
    text=one(text,'argc==9','argc==10').replace('cap direct|expanded','cap kernel config')
    text=one(text,'    std::ifstream input(argv[2]);','    kernel_route::LoadedImage kernel_image(argv[1],argv[9]);\n    kernel_route::ImageScope kernel_scope(kernel_image.view());\n    std::ifstream input(argv[2]);')
    text=one(text,'execution=="direct"||execution=="expanded"','execution=="kernel"')
    text=one(text,'    if (execution=="expanded") graph.graph.materialize_all();','    // Image decoding is performed inside the production kernel.\n')
    begin=text.index('        if (!graph.neighbors(n,out)) return false;');end=text.index('        return true;',begin)+len('        return true;')
    text=text[:begin]+'        (void)n;(void)out;throw std::logic_error("kernel route attempted native adjacency fallback");'+text[end:]
    text=one(text,'flat_controller_adapter::counters={};kernel_route::counters={};','flat_controller_adapter::counters={};kernel_route::counters={};kernel_route::kernel_counters={};')
    anchor='    const auto sc=kernel_route::counters;'
    text=one(text,anchor,'''    const auto kc=kernel_route::kernel_counters;
    std::cerr<<"KERNEL_COUNTERS "<<batch<<' '<<kc.calls<<' '<<kc.packets<<' '<<kc.serialized_words<<' '<<kc.submitted_words<<' '<<kc.max_packet_words<<' '<<kc.max_roots<<'\\n';
    require(kc.calls==flat_controller_adapter::counters.searches && kc.packets==kernel_route::counters.snapshots,"not every search uses production kernel");
'''+anchor)
    return text
