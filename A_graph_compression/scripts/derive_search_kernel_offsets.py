#!/usr/bin/env python3
"""Remove pointer-bearing object state, keeping the frozen packet/search ABI."""
from pathlib import Path
from derive_search_kernel_inline import derive as inlined
from derive_search_flat_controller import replace_once as one
from search_kernel_hls_pipeline import ROOT,NAMES
OUT=ROOT/'hardware/vitis/search_kernel_offsets_v3'

def cost():
    s=inlined('search_cost_snapshot.hpp').replace('#include "search_site_state.hpp"','#include "search_cost_snapshot.hpp"')
    s=one(s,'enum class CostStatus : uint8_t {ok,invalid,capacity_exhausted,overflow};\n','')
    s=s.replace('SearchCostSnapshot','SearchOffsetCost')
    s=one(s,'const uint64_t *owners,*history,*fixed;','uint64_t owners,history,fixed; // word offsets into the explicit packet argument')
    s=one(s,'CostStatus bind(View v)','CostStatus bind(const uint64_t* packet,View v)')
    for name in ['compatible','penalty','step_cost']:
        s=one(s,'CostStatus '+name+'(uint32_t net,','CostStatus '+name+'(const uint64_t* packet,uint32_t net,')
    s=one(s,'penalty(net,before,after,present,site)','penalty(packet,net,before,after,present,site)')
    s=one(s,'if ((v.owner_count && !v.owners) || (v.history_count && !v.history) || (v.fixed_count && !v.fixed)) return CostStatus::invalid;','if (!packet) return CostStatus::invalid;')
    # Convert every buffer use explicitly, preserving the count/index logic.
    for old,new in [
        ('v.owners+4*i','packet+v.owners+4*i'),('v.fixed+4*i','packet+v.fixed+4*i'),
        ('v.history[2*i]','packet[v.history+2*i]'),('v.history[2*(i-1)]','packet[v.history+2*(i-1)]'),
        ('lower_key<4>(view_.fixed,','lower_key<4>(packet+view_.fixed,'),('view_.fixed[4*at]','packet[view_.fixed+4*at]'),('view_.fixed+4*at','packet+view_.fixed+4*at'),
        ('lower_key<4>(view_.owners,','lower_key<4>(packet+view_.owners,'),('view_.owners+4*(start+j)','packet+view_.owners+4*(start+j)'),
        ('lower_key<2>(view_.history,','lower_key<2>(packet+view_.history,'),('view_.history[2*h]','packet[view_.history+2*h]'),('view_.history[2*h+1]','packet[view_.history+2*h+1]')]:
        if old not in s:raise ValueError('Missing cost anchor '+old)
        s=s.replace(old,new)
    # The pointer-arithmetic replacement must not affect an already converted
    # array subscript; fix the one overlapping fixed-record token explicitly.
    s=s.replace('packet[packet+view_.fixed+4*at]','packet[view_.fixed+4*at]')
    return s

def adjacency():
    s=inlined('search_graph_adjacency.hpp');s=s[s.index('template<unsigned Mode> class ImageAdjacency'):]
    s=s.replace('ImageAdjacency','OffsetImageAdjacency')
    s=one(s,'    const uint32_t* image_=nullptr;\n','')
    s=one(s,'        image_=image;ready_=true;return RowStatus::known;','        ready_=true;return RowStatus::known;')
    s=one(s,'RowStatus neighbors(uint32_t node,','RowStatus neighbors(const uint32_t* image,uint32_t node,')
    s=one(s,'decode<Mode>(image_,','decode<Mode>(image,')
    return '#pragma once\n#include "search_graph_adjacency.hpp"\nnamespace fpga_search {\n'+s

def provider():
    s=inlined('search_snapshot_provider.hpp').replace('#include "search_cost_snapshot.hpp"','#include "search_offset_cost.hpp"')
    s=s.replace('SearchSnapshotProvider','SearchOffsetProvider').replace('using Cost=SearchCostSnapshot<','using Cost=SearchOffsetCost<')
    s=one(s,'const uint64_t *forbidden,*node_costs;','uint64_t forbidden,node_costs;')
    s=one(s,'        const uint8_t *pseudo_attributes,*blocked_attributes;\n','')
    s=one(s,'const uint64_t *protected_pips,*semantics_keys;','uint64_t protected_pips,semantics_keys;')
    s=one(s,'        const State* requirements;\n','')
    s=one(s,'    Adjacency& adjacency_;\n','')
    s=one(s,'    explicit SearchOffsetProvider(Adjacency& adjacency):adjacency_(adjacency){\n#pragma HLS INLINE\n}\n','')
    s=one(s,'CostStatus bind(View v)','CostStatus bind(const uint64_t* packet,View v,unsigned graph_nodes,const uint8_t* pseudo,const uint8_t* blocked,const State* requirements)')
    s=one(s,'v.nodes!=adjacency_.node_count() || !v.forbidden || !v.node_costs || !v.pseudo_attributes || !v.blocked_attributes ||\n           (v.protected_count && !v.protected_pips) || (v.semantics_count && (!v.semantics_keys || !v.requirements))','v.nodes!=graph_nodes || !packet || !pseudo || !blocked || (v.semantics_count && !requirements)')
    s=s.replace('v.pseudo_attributes[i]','pseudo[i]').replace('v.blocked_attributes[i]','blocked[i]').replace('v.requirements[i]','requirements[i]')
    s=s.replace('v.protected_pips[i]','packet[v.protected_pips+i]').replace('v.protected_pips[i-1]','packet[v.protected_pips+i-1]')
    s=s.replace('v.semantics_keys[i]','packet[v.semantics_keys+i]').replace('v.semantics_keys[i-1]','packet[v.semantics_keys+i-1]')
    s=one(s,'cost_.bind(v.cost)','cost_.bind(packet,v.cost)')
    s=one(s,'bool blocked_node(uint32_t node)','bool blocked_node(const uint64_t* packet,uint32_t node)')
    s=one(s,'view_.forbidden[node/64]','packet[view_.forbidden+node/64]')
    s=one(s,'bool blocked(uint32_t,const LabelEdge& e)','bool blocked(const uint64_t* packet,const uint8_t* blocked_flags,uint32_t,const LabelEdge& e)')
    s=s.replace('lower(view_.protected_pips,','lower(packet+view_.protected_pips,').replace('view_.protected_pips[at]','packet[view_.protected_pips+at]').replace('view_.blocked_attributes[e.attr]','blocked_flags[e.attr]')
    begin=s.index('    RowStatus neighbors(');end=s.index('    SemanticsStatus semantics(',begin)
    s=s[:begin]+s[end:]
    s=one(s,'SemanticsStatus semantics(uint32_t,const LabelEdge& e,State& out)','SemanticsStatus semantics(const uint64_t* packet,const uint8_t* pseudo_flags,const State* requirements,uint32_t,const LabelEdge& e,State& out)')
    s=s.replace('lower(view_.semantics_keys,','lower(packet+view_.semantics_keys,').replace('view_.semantics_keys[at]','packet[view_.semantics_keys+at]').replace('view_.pseudo_attributes[e.attr]','pseudo_flags[e.attr]').replace('view_.requirements[at]','requirements[at]')
    s=one(s,'bool compatible(const State& s)','bool compatible(const uint64_t* packet,const State& s)')
    s=one(s,'cost_.compatible(view_.net,','cost_.compatible(packet,view_.net,')
    s=one(s,'bool step_cost(uint32_t,const LabelEdge& e,','bool step_cost(const uint64_t* packet,uint32_t,const LabelEdge& e,')
    s=one(s,'cost_.step_cost(view_.net,','cost_.step_cost(packet,view_.net,')
    s=s.replace('view_.node_costs[2*e.dst]','packet[view_.node_costs+2*e.dst]').replace('view_.node_costs[2*e.dst+1]','packet[view_.node_costs+2*e.dst+1]')
    return s

def controller():
    s=inlined('search_controller_flat.hpp').replace('#include "search_controller.hpp"','#include "search_controller_flat.hpp"').replace('struct FlatSearchController','struct OffsetSearchController')
    s=one(s,'template<class Provider>\n    static Result run(Provider& provider,Workspace& w,','template<class Provider,class Adjacency>\n    static Result run(Provider& provider,Adjacency& adjacency,const uint32_t* image,const uint64_t* packet,const uint8_t* pseudo,const uint8_t* blocked_flags,const State* requirements,Workspace& w,')
    s=s.replace('provider.blocked_node(','provider.blocked_node(packet,').replace('provider.compatible(','provider.compatible(packet,').replace('provider.blocked(','provider.blocked(packet,blocked_flags,').replace('provider.semantics(','provider.semantics(packet,pseudo,requirements,').replace('provider.step_cost(','provider.step_cost(packet,')
    s=one(s,'provider.neighbors(current.node,','adjacency.neighbors(image,current.node,')
    return s

def kernel():
    s=inlined('search_kernel.hpp').replace('#include "search_controller_flat.hpp"','#include "search_controller_offsets.hpp"\n#include "search_offset_provider.hpp"').replace('#include "search_graph_adjacency.hpp"','#include "search_offset_adjacency.hpp"')
    s=one(s,'using Core=FlatSearchController<L>;','using Core=OffsetSearchController<L>;')
    s=one(s,'using Adjacency=ImageAdjacency<Mode>;','using Adjacency=OffsetImageAdjacency<Mode>;')
    anchor='    static constexpr unsigned ResultWords='
    s=one(s,anchor,'    using OffsetProvider=SearchOffsetProvider<L,Adjacency,M::semantics,M::attributes,M::protected_pips,M::owners,M::history,M::fixed>;\n'+anchor)
    s=one(s,'        Provider provider(adjacency);','        OffsetProvider provider;')
    s=one(s,'typename Provider::View view{nodes,attributes,packet+forbidden_at,packet+costs_at,pseudo,blocked,packet+protected_at,packet+semantics_at,requirements,nprotected,nsem,\n            {packet+owners_at,packet+history_at,packet+fixed_at,nowners,nhistory,nfixed},uint32_t(h[4]),h[5]};',
        'typename OffsetProvider::View view{nodes,attributes,forbidden_at,costs_at,protected_at,semantics_at,nprotected,nsem,\n            {owners_at,history_at,fixed_at,nowners,nhistory,nfixed},uint32_t(h[4]),h[5]};')
    s=one(s,'provider.bind(view)','provider.bind(packet,view,adjacency.node_count(),pseudo,blocked,requirements)')
    s=one(s,'Core::run(provider,workspace,','Core::run(provider,adjacency,image,packet,pseudo,blocked,requirements,workspace,')
    return s

EXTRA={'search_offset_cost.hpp':cost,'search_offset_adjacency.hpp':adjacency,'search_offset_provider.hpp':provider,'search_controller_offsets.hpp':controller}

def bodies():
    result={name:((ROOT/('src/native' if name=='search_kernel_packet.hpp' else 'hardware/vitis')/name).read_text()) for name in NAMES+['search_kernel_packet.hpp']}
    result['search_kernel.hpp']=kernel()
    result.update({name:fn() for name,fn in EXTRA.items()})
    return result

def verify():
    for name,body in bodies().items():
        if (OUT/name).read_text()!=body:raise ValueError('Different offset derivation '+name)

if __name__=='__main__':
    content=bodies();OUT.mkdir(exist_ok=False)
    for name,body in content.items():
        with (OUT/name).open('x') as f:f.write(body)
    verify();print('OFFSET_DERIVATION_PASS files='+str(len(content)))
