from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PAIR=ROOT/'hardware/variants/iter2_pair_v1/build_tb.py'
def make():
 s=runpy.run_path(str(PAIR))['make']()
 start=s.index(' for(import_i=0;import_i<822;')
 end=s.index('\n\n\n control(1);',start)
 s=s[:start]+' $fdisplay(trace,"BASELINE_NO_PRELOAD %0d",cycles);\n'+s[end:]
 for marker,stop in [(' for(final_index=0;final_index<822;', ' if(commits!=421'),(' for(final_index=0;final_index<822;', ' if(commits!=302')]:
  start=s.index(marker);end=s.index(stop,start);s=s[:start]+s[end:]
 s=s.replace(' if(!$value$plusargs("imports=%s",path))$fatal(1,"import path");imports_fd=$fopen(path,"r");','')
 s=s.replace('||!imports_fd','')
 s=s.replace('query_residency_system #(', 'query_residency_system #(.ENABLE_BASELINE(1),',1)
 s=s.replace(')system(.wm_enable', ''')system(.baseline_permit(1'b1),.baseline_epoch(64'h300010003),.baseline_req_valid(baseline_req_valid),.baseline_req_ready(baseline_req_ready),.baseline_req_node(baseline_req_node),.baseline_req_epoch(baseline_req_epoch),.baseline_rsp_valid(baseline_rsp_valid),.baseline_rsp_ready(baseline_rsp_ready),.baseline_rsp_status(baseline_rsp_status),.baseline_rsp_node(baseline_rsp_node),.baseline_rsp_epoch(baseline_rsp_epoch),.baseline_rsp_payload(baseline_rsp_payload),.wm_enable''',1)
 s=s.replace(' control(0);\n $fdisplay(trace,"BASELINE_NO_PRELOAD', ' baseline_configure;control(0);\n $fdisplay(trace,"BASELINE_NO_PRELOAD',1)
 s=s.replace(' iter2_next_query;\n $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS', ' iter2_next_query;control(1);\n $fdisplay(trace,"BASELINE_PAIR_DONE %0d",cycles);\n $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS',1)
 extra='''
reg bcfg_valid=0,bcfg_ready=0;wire bcfg_accept,bcfg_reply;wire[3:0]bcfg_status;wire baseline_idle,baseline_configured;
wire baseline_req_valid,baseline_req_ready,baseline_rsp_valid,baseline_rsp_ready;
wire[31:0]baseline_req_node,baseline_rsp_node;wire[63:0]baseline_req_epoch,baseline_rsp_epoch;wire[3:0]baseline_rsp_status;wire[159:0]baseline_rsp_payload;
wire[63:0]ba;wire[7:0]bl;wire[2:0]bz;wire[1:0]bb;wire[3:0]bi;wire bv,by,brv,brr,brlast;wire[511:0]bd;wire[3:0]brid;wire[1:0]bresp;
label_baseline_reader baseline(.clk(clk),.rst(bench_rst),.cfg_valid(bcfg_valid),.cfg_ready(bcfg_accept),.cfg_permit(1'b1),.cfg_base(64'hb000000000),.cfg_epoch(64'h300010003),.cfg_count(32'd9089009),.cfg_rsp_valid(bcfg_reply),.cfg_rsp_ready(bcfg_ready),.cfg_status(bcfg_status),.req_valid(baseline_req_valid),.req_ready(baseline_req_ready),.req_node(baseline_req_node),.req_epoch(baseline_req_epoch),.rsp_valid(baseline_rsp_valid),.rsp_ready(baseline_rsp_ready),.rsp_status(baseline_rsp_status),.rsp_node(baseline_rsp_node),.rsp_epoch(baseline_rsp_epoch),.rsp_payload(baseline_rsp_payload),.idle(baseline_idle),.configured(baseline_configured),.araddr(ba),.arlen(bl),.arsize(bz),.arburst(bb),.arid(bi),.arvalid(bv),.arready(by),.rdata(bd),.rid(brid),.rresp(bresp),.rlast(brlast),.rvalid(brv),.rready(brr));
axi_file_memory #(.READ_ONLY(1),.TAG("baseline")) baseline_mem(.clk(clk),.rst(bench_rst),.base0(64'hb000000000),.size0(64'd290848320),.base1(64'b0),.size1(64'b0),.base2(64'b0),.size2(64'b0),.araddr(ba),.arlen(bl),.arsize(bz),.arburst(bb),.arid(bi),.arvalid(bv),.arready(by),.rdata(bd),.rid(brid),.rresp(bresp),.rlast(brlast),.rvalid(brv),.rready(brr),.awaddr(64'b0),.awlen(8'b0),.awsize(3'd6),.awburst(2'd1),.awid(4'b0),.awvalid(1'b0),.wdata(512'b0),.wstrb(64'b0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b1),.inject_r(1'b0),.inject_b(1'b0));
task baseline_configure;begin
 @(negedge clk);bcfg_valid=1;do @(posedge clk);while(!bcfg_accept);@(negedge clk);bcfg_valid=0;
 wait(bcfg_reply);@(negedge clk);if(bcfg_status)$fatal(1,"baseline config");bcfg_ready=1;@(negedge clk);bcfg_ready=0;
end endtask
always @(posedge clk)if(!bench_rst)begin
 if(baseline_req_valid&&baseline_req_ready)$fdisplay(trace,"BM %0d %0d %h",cycles,baseline_req_node,baseline_req_epoch);
 if(baseline_rsp_valid&&baseline_rsp_ready)$fdisplay(trace,"BR %0d %0d %0d %040h",cycles,baseline_rsp_node,baseline_rsp_status,baseline_rsp_payload);
end
'''
 path='system.inner.backend.dut.core.p'
 extra+='always @(posedge clk)if(!bench_rst)begin\n'
 extra+=f' if({path}.native_cmd_valid&&{path}.native_cmd_ready)$fdisplay(trace,"NB %0d %0d %0d %0d %0d %0d %0d %08h %0d %0d",cycles,'+','.join(path+'.native_cmd_'+n for n in ['op','slot','page','generation','offset','field','value','query','price'])+');\n'
 extra+=f' if({path}.native_rsp_valid&&{path}.native_rsp_ready)$fdisplay(trace,"NR %0d %0d %0d %040h",cycles,{path}.native_rsp_status,{path}.native_rsp_present,{path}.native_rsp_payload);\nend\n'
 return s.replace('query_residency_system #(',extra+'\nquery_residency_system #(',1)
def make_disabled():
 s=runpy.run_path(str(PAIR))['make']()
 s=s.replace('query_residency_system #(', 'query_residency_system #(.ENABLE_BASELINE(0),',1)
 ties=".baseline_permit(1'b0),.baseline_epoch(64'b0),.baseline_req_valid(),.baseline_req_ready(1'b0),.baseline_req_node(),.baseline_req_epoch(),.baseline_rsp_valid(1'b0),.baseline_rsp_ready(),.baseline_rsp_status(4'b0),.baseline_rsp_node(32'b0),.baseline_rsp_epoch(64'b0),.baseline_rsp_payload(160'b0),"
 return s.replace(')system(',')system('+ties,1)
if __name__=='__main__':(HERE/'tb_pair.sv').write_text(make())
