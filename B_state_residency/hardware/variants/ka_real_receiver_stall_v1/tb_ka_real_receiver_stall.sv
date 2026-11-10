`timescale 1ns/1ps
// Receiver-only test. The top-level lease normally excludes this overlap.
// A deliberate identity mismatch checks transport completion without AXI data.
module tb_ka_real_receiver_stall;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cfg_valid=0,cfg_rsp_ready=0,req_valid=0,rsp_ready=0;
 wire cfg_ready,cfg_rsp_valid,configured,req_ready,rsp_valid,fault,drained;
 wire[2:0]cfg_status;wire[3:0]rsp_status;
 wire[31:0]rsp_cookie,rsp_checkpoint;wire[63:0]rsp_design,rsp_generation;
 wire m_arvalid,m_awvalid,m_wvalid;
 integer stalls=0,transfers=0,ticks=0;
 checkpoint_authority_reader dut(
 .clk(clk),.rst(rst),.abort(1'b0),.cfg_permit(1'b1),.cfg_valid(cfg_valid),.cfg_ready(cfg_ready),
 .cfg_design(64'h1234),.cfg_generation(64'd9),.cfg_primary(64'h1000),.cfg_pool(64'h2000),.cfg_allocator(64'h3000),
 .cfg_checkpoint(32'd17),.cfg_nodes(32'd4),.cfg_nets(32'd4),.cfg_capacity(32'd4),
 .rearm_valid(1'b0),.cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(cfg_rsp_ready),.cfg_status(cfg_status),.configured(configured),
 .req_valid(req_valid),.req_ready(req_ready),.req_design(64'h1235),.req_generation(64'd9),.req_checkpoint(32'd17),
 .req_node(32'd0),.req_net(32'd0),.req_cookie(32'hcafef00d),
 .rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_design(rsp_design),.rsp_generation(rsp_generation),.rsp_checkpoint(rsp_checkpoint),.rsp_cookie(rsp_cookie),
 .fault(fault),.drained(drained),.m_arvalid(m_arvalid),.m_arready(1'b1),
 .m_rdata(512'd0),.m_rid(4'd0),.m_rresp(2'd0),.m_rlast(1'b0),.m_rvalid(1'b0),
 .m_awvalid(m_awvalid),.m_awready(1'b1),.m_wvalid(m_wvalid),.m_wready(1'b1),.m_bid(4'd0),.m_bresp(2'd0),.m_bvalid(1'b0));
 always @(posedge clk)begin
  ticks=ticks+1;if(ticks>100)$fatal(1,"KA_RECEIVER_WATCHDOG");
  if(!rst)begin
   if(fault||m_arvalid||m_awvalid||m_wvalid)$fatal(1,"KA_RECEIVER_FAULT_OR_UNEXPECTED_AXI");
   if(req_valid&&!req_ready)stalls=stalls+1;
   if(req_valid&&req_ready)transfers=transfers+1;
   if(cfg_rsp_valid&&!cfg_rsp_ready&&req_ready)$fatal(1,"KA_RECEIVER_EARLY_READY");
  end
 end
 initial begin
  repeat(5)@(negedge clk);rst=0;cfg_valid=1;
  do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
  wait(cfg_rsp_valid);@(negedge clk);
  if(cfg_status!==0||!configured)$fatal(1,"KA_RECEIVER_CONFIG");req_valid=1;
  repeat(7)@(negedge clk);cfg_rsp_ready=1;
  do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;
  wait(rsp_valid);@(negedge clk);
  repeat(3)begin
   if(rsp_status!==1||rsp_design!==64'h1234||rsp_generation!==64'd9||rsp_checkpoint!==32'd17||rsp_cookie!==32'hcafef00d||!rsp_valid||!drained)$fatal(1,"KA_RECEIVER_IDENTITY_REJECTION");
   @(negedge clk);
  end
  rsp_ready=1;@(negedge clk);rsp_ready=0;@(negedge clk);
  if(stalls!=8||transfers!=1||rsp_valid||!req_ready)$fatal(1,"KA_RECEIVER_COUNTS stalls=%0d transfers=%0d",stalls,transfers);
  $display("KA_REAL_RECEIVER_STALL_PASS stalls=%0d transfers=%0d response_status=1",stalls,transfers);$finish;
 end
endmodule
