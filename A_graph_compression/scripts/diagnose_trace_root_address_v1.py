#!/usr/bin/env python3
"""Isolated arithmetic/AXI diagnostic; never a full-kernel acceptance report.

Extract the first roots-read address cone verbatim from each frozen trace
module. The cone's one register is clocked without its surrounding FSM enable;
this intentionally tests address arithmetic, not state reachability. Feed it
through the unchanged production AXI adapter and address guard.
"""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import observe, abort_reason, POLICY

ROOT = Path(__file__).resolve().parents[1]
TRIAL = Path('/tmp/A_graph_compression_recovery_20261025_v1/compact_nonzero_native_rtl_v2')
RTL = TRIAL/'sim/verilog'
BIN = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
OUT = ROOT/'data/derived/trace_root_address_diagnostic_20261030_v1'
REPORT = ROOT/'results/trace_root_address_diagnostic_20261030_v1.json'


def cone(kind, index, output):
    source = RTL/('search_batch_trace_top_v2_'+kind+'.v')
    text = source.read_text()
    declarations = dict((m[2], m[0]) for m in re.finditer(
        r'^(wire|reg|input)\s+(?:signed\s+)?(?:\[[^\]]+\]\s*)?(\w+)\s*;', text, re.M))
    assignments = dict((m[1], m[0]) for m in re.finditer(r'^assign (\w+) = ([^;]+);', text, re.M))
    statements = {}; seen = set(); bridges = []

    def visit(name):
        if name in seen:
            return
        require(name in declarations, 'Missing declaration '+name)
        seen.add(name)
        if name in ('roots_x', index):
            return
        if name in assignments:
            statement = assignments[name]
        else:
            matches = set(re.findall(r'\b'+re.escape(name)+r' <= [^;]+;', text))
            require(len(matches) == 1, 'Not a unique register expression: '+name)
            statement = matches.pop(); bridges.append(name)
        statements[name] = statement
        # Match known identifiers, not Verilog numeric literals or system tasks.
        for dep in re.findall(r'\b\w+\b', statement.split('=', 1)[1]):
            if dep in declarations:
                visit(dep)

    visit(output)
    require(len(bridges) == 1 and len(statements) == 6, 'Unexpected address cone')
    lines = [f'module cone_{kind}(input wire clk,input wire [63:0] roots_x,',
             f'input wire [20:0] {index},output wire [63:0] address);']
    lines += [declarations[n] for n in sorted(seen-{'roots_x', index})]
    lines += [s if n not in bridges else 'always @(posedge clk) '+s for n, s in statements.items()]
    lines += [f'assign address={output};', 'endmodule']
    return '\n'.join(lines), dict(source=str(source), source_sha256=digest(source),
                                  statements=statements, declarations={n: declarations[n] for n in seen},
                                  register_enable_omitted_for_arithmetic_diagnostic=bridges)


def execute(phase, args, expected=None):
    command = ['prlimit', '--as=8589934592:8589934592', '--stack=67108864:67108864',
               '--core=0:0', '--', *args]
    start = time.monotonic(); initial = observe(); reason = None
    log = OUT/(phase+'.log')
    with log.open('x') as stream:
        child = subprocess.Popen(command, cwd=OUT, stdout=stream, stderr=subprocess.STDOUT,
                                 start_new_session=True,
                                 env={**os.environ, 'LD_PRELOAD': '/lib/x86_64-linux-gnu/libudev.so.1'})
        while child.poll() is None:
            current = observe()
            reason = abort_reason(initial, current)
            if time.monotonic()-start > 120:
                reason = 'diagnostic_120s_timeout'
            if reason:
                os.killpg(child.pid, signal.SIGTERM)
                try: child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL); child.wait()
                break
            time.sleep(.2)
    receipt = dict(command=command, exit_code=child.returncode,
                   elapsed_seconds=time.monotonic()-start, expected_failure=expected,
                   resource_policy=POLICY, initial_memory=initial, final_memory=observe(),
                   abort_reason=reason, log_sha256=digest(log))
    (OUT/(phase+'.receipt.json')).write_text(json.dumps(receipt, indent=2)+'\n')
    text = log.read_text(errors='replace')
    require(reason is None and child.returncode in (0, 1), 'Diagnostic execution failed '+phase)
    if expected:
        require(expected in text and 'Fatal:' in text and 'UNEXPECTED_ACCEPTANCE' not in text,
                'Wrong negative result '+phase)
    else:
        require(child.returncode == 0 and not any(x in text for x in ('ERROR:', 'Fatal:', 'FATAL', 'UNEXPECTED_ACCEPTANCE')),
                'Diagnostic failure '+phase)
    return text


def main():
    require(not OUT.exists() and not REPORT.exists(), 'Refuse overwrite')
    search, a = cone('search', 'i_52_fu_320', 'sext_ln36_fu_2584_p1')
    net, b = cone('net', 'i_fu_540', 'sext_ln23_fu_4677_p1')
    parents = [RTL/'search_batch_trace_top_v2_sink_loop_worker.v', RTL/'search_batch_trace_top_v2_batch_worker.v']
    for parent in parents:
        require(parent.read_text().count(".roots_x(64'd0)") == 1, 'Different frozen pointer connection')
    adapter = RTL/'search_batch_trace_top_v2_input_mem_m_axi.v'
    guard = RTL/'axi_model_rebase_guard_v1.sv'
    top = (RTL/'search_batch_trace_top_v2.v').read_text()
    block = re.search(r'search_batch_trace_top_v2_input_mem_m_axi #\((.*?)\)\s*input_mem_m_axi_U\(', top, re.S)
    require(block is not None, 'Missing actual adapter instance')
    params = block[1]
    # Resolve each actual top parameter from its frozen declaration, retaining
    # the complete parameter set used by the full-kernel instance.
    for name in set(re.findall(r'\bC_M_AXI_INPUT_MEM_\w+\b', params)):
        match = re.search(r'parameter\s+'+name+r'\s*=\s*([^;,\n]+)', top)
        require(match is not None, 'Missing top parameter '+name)
        params = params.replace(name, match[1].strip())
    OUT.mkdir()
    tb = OUT/'trace_address_tb.sv'
    tb.write_text('`timescale 1ns/1ps\n'+search+'\n'+net+'''
module tb;
reg clk=0; always #5 clk=~clk;
reg rst=1, request=0;
reg [63:0] roots=4224; reg [20:0] idx=0;
wire [63:0] search_address,net_address,ARADDR;
wire ARVALID,I_ARREADY; wire [7:0] ARLEN; wire [2:0] ARSIZE; wire [1:0] ARBURST;
reg choose_net=0; integer mode=0,read_mode,n,k,passes=0;
reg [63:0] expected_address;
cone_search s(clk,roots,idx,search_address);
cone_net n0(clk,roots,idx,net_address);
search_batch_trace_top_v2_input_mem_m_axi #('''+params+''') adapter(
 .ACLK(clk),.ARESET(rst),.ACLK_EN(1'b1),
 .AWREADY(1'b1),.WREADY(1'b1),.BID(1'b0),.BRESP(2'd0),.BUSER(1'b0),.BVALID(1'b0),
 .ARADDR(ARADDR),.ARVALID(ARVALID),.ARREADY(1'b1),.ARLEN(ARLEN),.ARSIZE(ARSIZE),.ARBURST(ARBURST),
 .RID(1'b0),.RDATA(512'd0),.RRESP(2'd0),.RLAST(1'b0),.RUSER(1'b0),.RVALID(1'b0),
 .I_AWADDR(64'd0),.I_AWLEN(32'd0),.I_AWVALID(1'b0),.I_WDATA(512'd0),.I_WSTRB(64'd0),
 .I_WVALID(1'b0),.I_BREADY(1'b1),.I_ARADDR(choose_net?net_address:search_address),
 .I_ARLEN(32'd1),.I_ARVALID(request),.I_ARREADY(I_ARREADY),.I_RREADY(1'b1));
a_axi_model_rebase_guard_v1 #(.BASE(4096),.DEPTH(589826),.DATA_BITS(512),.NAME("input_mem")) guard(
 .clk(clk),.awvalid(1'b0),.awready(1'b0),.awaddr(64'd0),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),
 .arvalid(ARVALID),.arready(1'b1),.araddr(ARADDR),.arlen(ARLEN),.arsize(ARSIZE),.arburst(ARBURST));
task issue;
begin
 rst=1; request=0; repeat(5) @(negedge clk); rst=0;
 repeat(3) @(negedge clk);
 expected_address=((roots+4*idx)>>6)<<6;
 if(search_address !== (expected_address>>6) || net_address !== (expected_address>>6))
   $fatal(1,"CONE_ARITHMETIC_MISMATCH");
 request=1;
 @(posedge clk); while(!I_ARREADY) @(posedge clk);
 @(negedge clk); request=0;
 while(!ARVALID) @(negedge clk);
 if(ARADDR !== expected_address || ARLEN!==0 || ARSIZE!==6 || ARBURST!==1)
   $fatal(1,"ADAPTER_ADDRESS_MISMATCH");
 $display("TRACE_ADDRESS mode=%0d net=%0d roots=%0d index=%0d address=%0d len=%0d size=%0d",mode,choose_net,roots,idx,ARADDR,ARLEN,ARSIZE);
 @(negedge clk); passes=passes+1;
end endtask
initial begin
 read_mode=$value$plusargs("CASE=%d",mode); if(read_mode!=1)$fatal(1,"MISSING_CASE");
 if(mode==0)begin
   for(n=0;n<2;n=n+1)begin
     choose_net=n;
     for(k=0;k<6;k=k+1)begin
       case(k) 0:idx=0;1:idx=1;2:idx=15;3:idx=16;4:idx=1023;5:idx=1048575;endcase
       issue;
     end
   end
   if(passes!=12)$fatal(1,"WRONG_COUNT");
   $display("TRACE_ADDRESS_DIAGNOSTIC_PASS positive_requests=12");$finish;
 end else if(mode==1 || mode==2)begin
   roots=0;idx=0;choose_net=(mode==2);issue;
   $display("UNEXPECTED_ACCEPTANCE");$finish;
 end else $fatal(1,"BAD_MODE");
end
initial begin #100000;$fatal(1,"DIAGNOSTIC_TIMEOUT");end
endmodule
''')
    run = OUT/'run.tcl'; run.write_text('run all\nquit\n')
    sources = [Path(__file__).resolve(), adapter, guard, tb, run, *parents,
               RTL/'search_batch_trace_top_v2.v', Path(a['source']), Path(b['source']),
               TRIAL/'rtl.log', TRIAL/'rtl.receipt.json',
               ROOT/'results/native_nonzero_address_failure_20261030_v1.json']
    files = {str(p): digest(p) for p in sources}
    plan = dict(status='diagnostic_only_not_full_kernel', cones=[a,b], files=files,
                constant_parent_connections=[str(p) for p in parents], adapter_parameters=params,
                positive_requests=12, negative_requests=2, full_kernel_accepted=False)
    (OUT/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    execute('xvlog', [str(BIN/'xvlog'),'--sv',str(adapter),str(guard),str(tb)])
    execute('xelab', [str(BIN/'xelab'),'tb','-s','trace_address','--O0','-mt','off'])
    logs = []
    for case in range(3):
        log = execute('case_'+str(case), [str(BIN/'xsim'),'trace_address','-tclbatch',str(run),
                                        '--testplusarg','CASE='+str(case)],
                      'A_REBASE_BELOW_BASE input_mem write=0' if case else None)
        require(('TRACE_ADDRESS_DIAGNOSTIC_PASS positive_requests=12' in log) if case==0 else
                ('roots=0 index=0 address=0 len=0 size=6' in log), 'Missing measured result')
        logs.append(log)
    for n,h in files.items(): require(digest(n)==h,'Input changed during diagnostic '+n)
    for p in OUT.iterdir():
        if p.is_file() and p.suffix in ('.log','.json','.tcl','.sv'):
            files[str(p)]=digest(p)
    result = dict(status='trace_root_constant_zero_address_cones_reproduce_guard_failure_diagnostic_only',
                  files=files, cones=[a,b], positive_requests=12, negative_requests=2,
                  full_kernel_accepted=False, actual_first_failed_request_source_proven=False,
                  conclusions=['Both frozen parents connect roots_x to literal zero.',
                               'Both extracted first-read arithmetic cones, followed by the unchanged full AXI adapter, issue address zero for index zero and trip the unchanged guard.',
                               'Driving 4224 into the diagnostic cones yields expected aligned addresses for all12 requests. This does not modify or validate the production DUT.'],
                  limits=['Original FSM reachability/enables, full memory contents and full kernel were not simulated.',
                          'The full-run log has no numeric failing address or caller; the exact first failing source remains to be captured.',
                          'No production source, original trial, frozen checker or downstream prerequisite modified.'])
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])


if __name__=='__main__': main()
