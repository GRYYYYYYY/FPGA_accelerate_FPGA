#!/usr/bin/env python3
"""Execute exact generated trace guard with legal and violating AXI requests."""
import json,os,subprocess
from pathlib import Path
from check_vitis_kernel import digest
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
    out=BASE/'compressed_axi_guard_tests_v1';out.mkdir(exist_ok=False)
    source=BASE/'compressed_batch_rtl_guarded_v1/sim/verilog/AESL_axi_master_trace_mem.v'
    text=source.read_text();guard=text.split('// Independent conservative read-only AXI burst guard.\n')[1].rsplit('endmodule',1)[0]
    tb=out/'tb.sv'
    tb.write_text('''`timescale 1ns/1ps
module tb;
reg clk=0;
always #5 clk=~clk;
reg TRAN_trace_mem_AWVALID=0, TRAN_trace_mem_AWREADY=1;
reg [63:0] TRAN_trace_mem_AWADDR=128;
reg [7:0] TRAN_trace_mem_AWLEN=0;
reg [2:0] TRAN_trace_mem_AWSIZE=6;
reg [1:0] TRAN_trace_mem_AWBURST=1;
integer test_case;
'''+guard+'''
initial begin
if (!$value$plusargs("CASE=%d",test_case)) $fatal(1,"MISSING_CASE");
#1;
case(test_case)
0: TRAN_trace_mem_AWADDR=64;
1: begin TRAN_trace_mem_AWADDR=128; TRAN_trace_mem_AWLEN=7; end
2: TRAN_trace_mem_AWADDR=0;
3: begin TRAN_trace_mem_AWADDR=63; TRAN_trace_mem_AWSIZE=0; end
4: TRAN_trace_mem_AWADDR='hx;
5: TRAN_trace_mem_AWBURST=2;
6: begin TRAN_trace_mem_AWADDR=0; TRAN_trace_mem_AWVALID=0; end
7: begin TRAN_trace_mem_AWADDR=64; TRAN_trace_mem_AWBURST=0; TRAN_trace_mem_AWLEN=255; end
8: begin TRAN_trace_mem_AWADDR=32; TRAN_trace_mem_AWSIZE=6; end
endcase
if(test_case != 6) TRAN_trace_mem_AWVALID=1;
#20;
$display("A_GUARD_LEGAL_PASS case=%0d",test_case);$finish;
end
endmodule
''')
    env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
    records=[]
    def run(name,command):
        log=out/(name+'.log')
        with log.open('x') as f:code=subprocess.run(command,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
        records.append(dict(name=name,command=command,exit_code=code,log_sha256=digest(log)))
        return code,log.read_text(errors='replace')
    code,text=run('compile',[str(BIN/'xvlog'),'--sv',str(tb)]);assert code==0,text
    code,text=run('elaborate',[str(BIN/'xelab'),'xil_defaultlib.tb','-s','guard_test','-mt','off']);assert code==0,text
    tcl=out/'run.tcl';tcl.write_text('run 100ns\nquit\n')
    expected={0:None,1:None,2:'A_RO_WRITE_VIOLATION',3:'A_RO_WRITE_VIOLATION',4:'A_RO_UNKNOWN_ADDRESS',5:'A_RO_UNSUPPORTED_BURST',6:None,7:None,8:'A_RO_WRITE_VIOLATION'}
    for case,marker in expected.items():
        code,text=run('case_'+str(case),[str(BIN/'xsim'),'guard_test','-testplusarg','CASE='+str(case),'-tclbatch',str(tcl)])
        if marker is None:assert code==0 and 'A_GUARD_LEGAL_PASS' in text and 'A_RO_' not in text,(case,text)
        else:assert marker in text and 'A_GUARD_LEGAL_PASS' not in text,(case,text)
    target=ROOT/'results/compressed_axi_ro_guard_tests_20261025_v1.json';assert not target.exists()
    report=dict(status='exact_trace_ro_guard_nine_xsim_cases_passed',cases=9,records=records,files={str(p):digest(p) for p in [source,tb,tcl,Path(__file__).resolve()]},limits=['Exact trace_mem guard isolated test, not whole design proof','Conservative AW request protection ignores WSTRB; invalid and unsupported bursts rejected'])
    tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(target)
    print(report['status'])
if __name__=='__main__':main()
