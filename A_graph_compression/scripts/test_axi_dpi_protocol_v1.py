#!/usr/bin/env python3
"""Supplementary small-depth native vs transformed HLS AXI protocol test."""
import json,os,re,subprocess
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
LOCAL=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
 out=LOCAL/'axi_dpi_protocol_test_v1';out.mkdir(exist_ok=False)
 plan=json.loads((LOCAL/'search_axi_dpi_replay_v2/plan.json').read_text())
 name='AESL_axi_master_output_mem.v';original=Path(plan['original_sim'])/'verilog'/name
 converted=LOCAL/'search_axi_dpi_replay_v2/sim/verilog'/name
 item=next(x for x in plan['models'] if Path(x['path']).name==name)
 require(digest(original)==item['before_sha256'] and digest(converted)==item['after_sha256'],'Changed model')
 native=original.read_text();dpi=converted.read_text();module='AESL_axi_master_output_mem'
 for label,text in [('native',native),('dpi',dpi)]:
  (out/(label+'.sv')).write_text(text.replace('module '+module+' (','module '+module+'_'+label+' (',1))
 tv=out.parent/'tv/cdatafile'
 # Keep the generated fixture path isolated under this test, rather than shared parent.
 sim=out/'sim';sim.mkdir();tv=out/'tv/cdatafile';tv.mkdir(parents=True)
 (tv/'c.search_kernel_top.autotvin_output_mem.dat').write_bytes(bytes.fromhex('5a5aa5a50f0ff0f0'))
 widths={k:int(v) for k,v in re.findall(r'parameter\s+(\w+BITWIDTH)\s*=\s*32\x27d\s*(\d+)',native)}
 ports=[];decl=[];outputs=[]
 for direction,span,port in re.findall(r'^(input|output)\s*(\[[^\]\n]+\])?\s*(\w+)\s*;',native,re.M):
  for key,value in widths.items():span=re.sub(r'\b'+key+r'\b',str(value),span)
  ports.append((direction,port))
  if direction=='input':decl.append('reg '+span+' '+port+'=0;')
  else:
   outputs.append(port)
   for label in ['native','dpi']:decl.append('wire '+span+' '+label+'_'+port+';')
 require(len(ports)==53,'Unexpected generated port list')
 instances=[]
 for label in ['native','dpi']:
  connections=[f'.{port}({port if direction=="input" else label+"_"+port})' for direction,port in ports]
  instances.append(module+'_'+label+' #(.output_mem_mem_depth(64)) '+label+'_model('+','.join(connections)+');')
 compare=' || '.join(f'({"native_"+p} !== {"dpi_"+p})' for p in outputs)
 stimulus=r'''
reg[255:0] expected[0:3];reg[255:0] value;integer i,j,pass;
always #5 clk=~clk;
always @(negedge clk)if(reset && (COMPARE))$fatal(1,"AXI_NATIVE_DPI_SIGNAL_MISMATCH t=%0t",$time);
task write_burst(input integer partial);
 begin
  @(negedge clk);TRAN_output_mem_AWADDR=0;TRAN_output_mem_AWLEN=3;TRAN_output_mem_AWSIZE=5;TRAN_output_mem_AWBURST=1;TRAN_output_mem_AWVALID=1;
  @(posedge clk);while(!native_TRAN_output_mem_AWREADY)@(posedge clk);
  @(negedge clk);TRAN_output_mem_AWVALID=0;
  for(i=0;i<4;i=i+1)begin
   value=partial ? (256'hfedcba98765432100123456789abcdef0123456789abcdef9876543210abcdef00+i) : (256'h123456789abcdef00112233445566778899aabbccddeeff0a5a5a5a55a5a5a50+i);
   TRAN_output_mem_WDATA=value;TRAN_output_mem_WSTRB=partial ? 32'h5555aaaa : 32'hffffffff;
   TRAN_output_mem_WLAST=(i==3);TRAN_output_mem_WVALID=1;
   for(j=0;j<32;j=j+1)if(TRAN_output_mem_WSTRB[j])expected[i][j*8+:8]=value[j*8+:8];
   @(posedge clk);while(!native_TRAN_output_mem_WREADY)@(posedge clk);
   @(negedge clk);
  end
  TRAN_output_mem_WVALID=0;TRAN_output_mem_WLAST=0;
  while(!native_TRAN_output_mem_BVALID)@(negedge clk);
  repeat(3)begin @(negedge clk);if(!native_TRAN_output_mem_BVALID)$fatal(1,"BVALID_DROPPED_UNDER_STALL");end
  if(native_TRAN_output_mem_BRESP!==0)$fatal(1,"WRITE_RESPONSE_ERROR");
  TRAN_output_mem_BREADY=1;@(posedge clk);@(negedge clk);TRAN_output_mem_BREADY=0;
 end
endtask
task read_burst;
 begin
  @(negedge clk);TRAN_output_mem_ARADDR=0;TRAN_output_mem_ARLEN=3;TRAN_output_mem_ARSIZE=5;TRAN_output_mem_ARBURST=1;TRAN_output_mem_ARVALID=1;
  @(posedge clk);while(!native_TRAN_output_mem_ARREADY)@(posedge clk);
  @(negedge clk);TRAN_output_mem_ARVALID=0;
  for(i=0;i<4;i=i+1)begin
   while(!native_TRAN_output_mem_RVALID)@(negedge clk);
   value=native_TRAN_output_mem_RDATA;
   repeat(3)begin @(negedge clk);if(!native_TRAN_output_mem_RVALID || native_TRAN_output_mem_RDATA!==value)$fatal(1,"READ_STALL_INSTABILITY");end
   if(value!==expected[i] || native_TRAN_output_mem_RLAST!==(i==3) || native_TRAN_output_mem_RRESP!==0)$fatal(1,"READ_ORACLE_ERROR beat=%0d actual=%h expected=%h",i,value,expected[i]);
   TRAN_output_mem_RREADY=1;@(posedge clk);@(negedge clk);TRAN_output_mem_RREADY=0;
  end
 end
endtask
initial begin
 for(i=0;i<4;i=i+1)expected[i]=0;
 repeat(5)@(negedge clk);reset=1;
 write_burst(0);read_burst();write_burst(1);read_burst();
 $display("AXI_DPI_PROTOCOL_PASS bursts=4 beats=16 partial_byte_write=1 read_stall=3 response_stall=3");$finish;
end
initial begin #100000;$fatal(1,"AXI_PROTOCOL_TIMEOUT");end
'''.replace('COMPARE',compare)
 bench=out/'bench.sv';bench.write_text('`timescale 1ns/1ps\nmodule axi_dpi_protocol_test;\n'+'\n'.join(decl+instances)+stimulus+'\nendmodule\n')
 cpp=ROOT/'hardware/sim/axi_dpi_memory_v1.cpp';tcl=out/'run.tcl';tcl.write_text('run 100us\nquit\n')
 jobs=[('xsc',[str(BIN/'xsc'),'--cppversion','14',str(cpp)]),('xvlog',[str(BIN/'xvlog'),'--sv',str(out/'native.sv'),str(out/'dpi.sv'),str(bench)]),('xelab',[str(BIN/'xelab'),'work.axi_dpi_protocol_test','-s','axi_test','-mt','off','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc']),('xsim',[str(BIN/'xsim'),'axi_test','-tclbatch',str(tcl)])]
 rows=[];env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
 for phase,cmd in jobs:
  log=out/(phase+'.log')
  with log.open('x') as f:code=subprocess.run(cmd,cwd=sim,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
  text=log.read_text(errors='replace');rows.append(dict(phase=phase,command=cmd,exit_code=code,log_sha256=digest(log)))
  (out/'receipts.json').write_text(json.dumps(rows,indent=2)+'\n')
  require(code==0 and not re.search(r'ERROR:|Fatal:',text),'Phase failed '+phase)
  if phase=='xsim':require('AXI_DPI_PROTOCOL_PASS bursts=4 beats=16' in text,'Missing complete protocol oracle')
 result=dict(status='small_generated_axi_native_vs_dpi_protocol_and_data_oracle_passed',rows=rows,
  files={str(p):digest(p) for p in [original,converted,Path(item['ledger']),cpp,bench,out/'native.sv',out/'dpi.sv',tcl,tv/'c.search_kernel_top.autotvin_output_mem.dat',Path(__file__).resolve(),*[out/(phase+'.log') for phase,_ in jobs]]},
  limitations=['Supplementary unit at 64 declared words, same native/DPI parameters and original protocol/latency/four pages', 'One generated 256-bit output_mem model, page0 only, INCR bursts; no full protocol coverage claim','Original full-depth whole-DUT tests and complete transaction acceptance gates remain unchanged and pending'])
 target=ROOT/'results/axi_dpi_protocol_unit_20261025_v1.json';require(not target.exists(),'Refuse overwrite');tmp=target.with_suffix('.json.tmp')
 with tmp.open('x') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,target);print(result['status'])
if __name__=='__main__':main()
