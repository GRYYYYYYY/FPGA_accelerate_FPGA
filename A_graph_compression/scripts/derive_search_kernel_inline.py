#!/usr/bin/env python3
"""Isolated HLS-only inline directives; strip them to recover frozen CPU code."""
from pathlib import Path
from search_kernel_hls_pipeline import ROOT,NAMES
OUT=ROOT/'hardware/vitis/search_kernel_inline_v2'
ANCHORS={
 'search_kernel.hpp':['uint64_t* meta,uint64_t* result) {'],
 'search_controller_flat.hpp':['static bool add_unknown_pip(Workspace& w,Result& out,PipIdentity pip) {','uint32_t target,const State& initial,uint64_t budget) {'],
 'search_graph_adjacency.hpp':['RowStatus bind(const uint32_t* image,const uint32_t* config,uint32_t image_words) {','unsigned node_count()const{','RowStatus neighbors(uint32_t node,LabelEdge* out,unsigned capacity,unsigned& count) {'],
 'search_cost_snapshot.hpp':['CostStatus bind(View v) {','CostStatus compatible(uint32_t net,const State& requested,bool& output) const {','CostStatus penalty(uint32_t net,const State& before,const State& after,uint64_t present,uint64_t& output) const {','uint64_t other_node_owners,uint64_t node_history,uint64_t& output) const {'],
 'search_snapshot_provider.hpp':['explicit SearchSnapshotProvider(Adjacency& adjacency):adjacency_(adjacency){','CostStatus bind(View v) {','unsigned node_count()const{','bool blocked_node(uint32_t node)const{','bool blocked(uint32_t,const LabelEdge& e)const {','RowStatus neighbors(uint32_t node,LabelEdge* out,unsigned capacity,unsigned& count) {','SemanticsStatus semantics(uint32_t,const LabelEdge& e,State& out)const {','bool compatible(const State& s)const {','bool step_cost(uint32_t,const LabelEdge& e,const State& before,const State& after,uint64_t& out)const {']}
INSERT='\n#pragma HLS INLINE\n'

def source(name):
    return ROOT/('src/native' if name=='search_kernel_packet.hpp' else 'hardware/vitis')/name

def derive(name):
    body=source(name).read_text()
    for anchor in ANCHORS.get(name,[]):
        if body.count(anchor)!=1:raise ValueError('Ambiguous function scope '+anchor)
        body=body.replace(anchor,anchor+INSERT)
    if body.replace(INSERT,'')!=source(name).read_text():raise ValueError('Unexpected behavior change')
    return body

def verify():
    for name in NAMES+['search_kernel_packet.hpp']:
        if (OUT/name).read_text()!=derive(name):raise ValueError('Different inline derivation '+name)

if __name__=='__main__':
    OUT.mkdir(exist_ok=False)
    for name in NAMES+['search_kernel_packet.hpp']:
        with (OUT/name).open('x') as f:f.write(derive(name))
    verify()
    print('INLINE_DERIVATION_PASS directives='+str(sum(map(len,ANCHORS.values()))))
