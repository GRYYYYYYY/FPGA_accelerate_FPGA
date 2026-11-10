#!/usr/bin/env python3
"""Keep frozen negotiation snapshot construction, replace search with real top."""
from pathlib import Path
from derive_search_flat_controller import ROOT,replace_once as one
TARGET=ROOT/'src/native/search_kernel_route_adapter.hpp'

def derive():
    s=(ROOT/'src/native/search_word_snapshot_route_adapter.hpp').read_text()
    s=s.replace('word_snapshot_route','kernel_route').replace('word_controller_adapter','flat_controller_adapter').replace('search_word_controller_adapter.hpp','search_flat_controller_adapter.hpp').replace('WordSearchController','FlatSearchController')
    s=one(s,'#include "search_snapshot_provider.hpp"','#include "search_snapshot_provider.hpp"\n#include "search_kernel_binding.hpp"\n#include "search_kernel_packet.hpp"')
    s=one(s,'    std::vector<uint64_t> forbidden_,nodes_,owners_,history_;','    std::vector<uint64_t> forbidden_,nodes_,owners_,history_,packet_;\n    ImageView image_{};')
    s=one(s,'        if(graph.node_count()>Limits::nodes)fail(true,"snapshot node domain exceeds capacity");',
        '        if(!active_image)fail(false,"no production kernel image bound");\n        image_=*active_image;\n        if(image_.config[2]!=graph.node_count())fail(false,"kernel/native node domains differ");\n        if(graph.node_count()>Limits::nodes)fail(true,"snapshot node domain exceeds capacity");')
    s=one(s,'        counters.node_occupied+=occupied;',
        '        packet_=search_kernel_host::packet<Limits>(view,0,1,1,{});\n'
        '        ++kernel_counters.packets;kernel_counters.serialized_words+=packet_.size();\n'
        '        kernel_counters.max_packet_words=std::max(kernel_counters.max_packet_words,unsigned(packet_.size()));\n'
        '        counters.node_occupied+=occupied;')
    s=one(s,'        auto r=Core::run(provider_,w,sorted_roots.data(),unsigned(sorted_roots.size()),target,state,budget);',
        '''        if(packet_.size()<32+Core::Index::Storage::Words)fail(false,"kernel search before snapshot bind");
        packet_[6]=target;packet_[7]=sorted_roots.size();packet_[8]=budget;
        const typename Core::Key initial_key{0,state};
        if(!Core::Index::Storage::store(packet_.data()+32,0,initial_key))fail(false,"invalid kernel initial key");
        kernel_counters.max_roots=std::max(kernel_counters.max_roots,unsigned(sorted_roots.size()));
        uint64_t meta[2]={w.epoch,w.key_count},result[81]{};
        invoke<Limits>(image_,sorted_roots.data(),packet_.data(),unsigned(packet_.size()),w.heap,w.slots,w.records,w.keys,w.unknown_nodes,w.unknown_pips,w.path,meta,result);
        if(result[15]!=1 || result[0]>uint64_t(fpga_search::SearchStatus::invalid_input) || meta[0]>UINT32_MAX || meta[1]>Limits::labels || result[7]>Limits::path || result[8]>Limits::nodes || result[9]>Limits::unknown_pips || result[10]>Limits::labels || result[11]>Limits::heap || result[12]>Limits::slots)fail(false,"malformed kernel result");
        if(result[13]){if(result[13]!=meta[0] || result[14]!=meta[1])fail(false,"kernel metadata/result mismatch");}
        else if(meta[0]!=w.epoch || meta[1]!=w.key_count)fail(false,"kernel preflight mutated metadata");
        w.epoch=unsigned(meta[0]);w.key_count=unsigned(meta[1]);
        typename Core::Result r;r.status=fpga_search::SearchStatus(result[0]);r.cost=result[1];r.expanded=result[2];r.blocked=result[3];
        r.pushes=result[4];r.pops=result[5];r.improvements=result[6];r.path_length=unsigned(result[7]);r.unknown_node_count=unsigned(result[8]);r.unknown_pip_count=unsigned(result[9]);r.label_count=unsigned(result[10]);r.max_heap=unsigned(result[11]);r.max_probes=unsigned(result[12]);
        if(r.status==fpga_search::SearchStatus::found){typename Core::Key key{};if(!Core::Index::Storage::load(result+16,0,key) || key.node!=target)fail(false,"invalid kernel demand state");r.demands=key.state;}
        else for(unsigned i=16;i<81;++i)if(result[i])fail(false,"failed kernel result contains demand state");''')
    s=one(s,'for(unsigned i=0;i<r.path_length;++i)out.path.emplace_back(w.path[i].source,flat_controller_adapter::native_edge(w.path[i].edge));',
        'for(unsigned i=0;i<r.path_length;++i){const uint32_t* p=w.path+uint64_t(i)*8;out.path.emplace_back(p[0],Edge{p[1],p[2],p[3],p[4],p[5],p[6],p[7]});}')
    s=one(s,'w.unknown_pips[i].tile,w.unknown_pips[i].pip','uint32_t(w.unknown_pips[i]>>32),uint32_t(w.unknown_pips[i])')
    s=s.replace('// CPU integration of the static provider. Snapshot construction, native\n// adjacency, negotiation, occupancy updates and result retention remain host work.',
        '// CPU integration of the actual production search top. Snapshot construction,\n// negotiation, occupancy updates and result retention remain host work.\n// Adjacency and the entire search execute inside the kernel C model.')
    return s

if __name__=='__main__':
    with TARGET.open('x') as f:f.write(derive())
