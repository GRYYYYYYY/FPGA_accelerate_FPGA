#!/usr/bin/env python3
"""Conservative FSM cycle floor for the reference first transaction; not a live-state proof."""
import collections
import json
from pathlib import Path
import re

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
LIVE = BASE/'collision_safe_native_owner_recovery_v2'
SRC = BASE/'collision_safe_batch_hls_v1/source'
REPORT = ROOT/'results/native_trace_cycle_floor_20261102_v1.json'


def state_graph(text):
    matches = list(re.finditer(r'^        ap_ST_fsm_state(\d+) : begin', text, re.M))
    require(matches, 'Missing generated FSM case')
    blocks = {}
    for i, match in enumerate(matches):
        n = int(match[1])
        require(n not in blocks, 'Duplicate FSM case')
        end = matches[i+1].start() if i+1 < len(matches) else text.index('endcase', match.start())
        blocks[n] = text[match.start():end]
    graph = {n: set(map(int, re.findall(r'ap_NS_fsm = ap_ST_fsm_state(\d+);', b)))
             for n, b in blocks.items()}
    require(all(graph.values()), 'Unparsed FSM transition')
    return blocks, graph


def shortest(graph, start, end, allowed):
    queue = collections.deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        if path[-1] == end:
            return path
        for n in sorted(graph[path[-1]]):
            if n in allowed and n not in seen:
                seen.add(n)
                queue.append(path+[n])
    raise AssertionError('No counter-update path')


def analyze():
    require(not REPORT.exists(), 'Refuse overwrite')
    rtl = LIVE/'sim/verilog'
    trace_file = rtl/'search_batch_trace_top_v2_a_write_net_trace_record.v'
    batch_file = rtl/'search_batch_trace_top_v2_batch_worker.v'
    tb_file = rtl/'search_batch_trace_top_v2.autotb.v'
    plan = json.loads((LIVE/'plan.json').read_text())
    for p in [trace_file,batch_file,tb_file]:
        require(digest(p) == plan['copies'][str(p)]['sha256'], 'Live RTL differs from original copied input')
    text = trace_file.read_text()
    blocks, graph = state_graph(text)
    require('always @ (posedge ap_clk) begin\n    if (ap_rst' in text and
            'ap_CS_fsm <= ap_NS_fsm;' in text, 'Unexpected FSM clocking')
    loops = []
    entries = 2097152
    for line, head, boundary, fast, update, exit_state, counter, add, compare, low in [
        (29,3314,3315,3387,3459,3460,'i_105_fu_596','add_ln29_7_reg_11660',
         'icmp_ln29_fu_5605_p2','trunc_ln29_18_fu_5601_p1'),
        (45,5328,5329,5401,5543,5544,'i_117_fu_676','add_ln45_4_reg_12933',
         'icmp_ln45_fu_8632_p2','trunc_ln45_fu_8628_p1')]:
        require(f'assign {compare} = (({counter} == 22\'d2097152)' in text, 'Unexpected loop limit')
        require(f'assign {low} = {counter}[3:0];' in text, 'Unexpected group size')
        require(re.search(r'assign \w+ = \(\('+low+r" == 4'd0\)",text), 'Missing modulo-16 predicate')
        assignments = re.findall(r'\b'+counter+r' <= ([^;]+);',text)
        require(sorted(assignments) == sorted(["22'd0",add]), 'Unexpected counter writers')
        require(re.search(r'assign \w+ = \('+counter+r" \+ 22'd1\);",text), 'Counter does not increment by one')
        require(graph[head] == {boundary,fast,exit_state}, 'Unexpected head branches')
        require(graph[update]-{update} == {head}, 'Unexpected update return')
        allowed = set(range(head,exit_state))
        require(all(graph[n] <= allowed|({exit_state} if n==head else set())
                    for n in allowed), 'Unexpected loop escape')
        paths = {str(first):[head]+shortest(graph,first,update,allowed)+[head]
                 for first in [boundary,fast]}
        cycles = {k:len(v)-1 for k,v in paths.items()}
        require(cycles[str(boundary)]==75 and cycles[str(fast)]==3, 'Changed shortest schedule')
        per_group = cycles[str(boundary)] + 15*cycles[str(fast)]
        loops.append(dict(source_line=line,head=head,update=update,counter=counter,
                          entries=entries,group_entries=16,cycles_per_group_floor=per_group,
                          cycles_floor=entries//16*per_group,shortest_paths=paths))
    half = float(re.search(r'`define AUTOTB_CLOCK_PERIOD_DIV2 ([\d.]+)',tb_file.read_text())[1])
    require(half==2.5 and '`timescale 1ns/1ps' in tb_file.read_text(), 'Changed clock')
    # Confirm the reset loop schedule separately. Reset precedes the serial net loop.
    batch = batch_file.read_text(); _, bg = state_graph(batch)
    require(bg[1509]=={1510,1511} and bg[1510]=={1510,1509}, 'Changed reset schedule')
    require("i_135_fu_658 == 22'd2097152" in batch, 'Changed reset capacity')
    reset_floor=entries*2
    fixture=(SRC/'test_compressed_batch_rtl_full_depth.cpp').read_text()
    require('batch_control[16]={8,80,2,3,93,8,1,' in fixture, 'Changed reference first call')
    require('batch_result[3]==1 && batch_result[4]==2' in fixture, 'Changed reference first result')
    c=(SRC/'search_trace_records.hpp').read_text()
    require(c.count('for(unsigned i=0;i<Pairs;++i)if(flags[i]==1')==2, 'Changed full scans')
    caller=(SRC/'search_batch_trace_top_v2.cpp').read_text()
    require(caller.index('if(batch_control[6])') < caller.index('for(unsigned iteration=0;'), 'Reset order changed')
    require('for(unsigned q=0;q<nets;++q)' in caller and '::a_write_net_trace_record(iteration,q,' in caller, 'Changed trace call structure')
    trace_floor=2*sum(x['cycles_floor'] for x in loops)
    files=[Path(__file__).resolve(),LIVE/'plan.json',trace_file,batch_file,tb_file,
           SRC/'test_compressed_batch_rtl_full_depth.cpp',SRC/'search_trace_records.hpp',
           SRC/'search_batch_trace_top_v2.cpp',SRC/'search_node_occupancy.hpp']
    result=dict(status='conditional_success_path_static_cycle_floor_derived_not_runtime_acceptance',
                loops=loops,reference_nets=2,clock_ns=2*half,
                trace_cycles_floor=trace_floor,trace_ms_floor=trace_floor*2*half/1e6,
                reset_cycles_floor=reset_floor,
                reset_plus_trace_cycles_floor=reset_floor+trace_floor,
                reset_plus_trace_ms_floor=(reset_floor+trace_floor)*2*half/1e6,
                assumptions=['Reference first-call success path, reset asserted, one round and two sequential net records',
                             'Reset remains deasserted during the transaction',
                             'Branches and AXI handshakes are relaxed to minimize cycles; additional stalls and matched-owner paths can only increase these loop costs'],
                exclusions=['Not a formal whole-design proof or measured latency',
                            'Does not establish the original running DUT state or absence of deadlock',
                            'Excludes search, startup, other loops, transfer and output costs',
                            'No transaction or functional acceptance'],
                files={str(p):digest(p) for p in files})
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k.endswith('_floor')},indent=2))


if __name__=='__main__':analyze()
