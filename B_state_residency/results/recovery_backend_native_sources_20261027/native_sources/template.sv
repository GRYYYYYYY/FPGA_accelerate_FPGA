`timescale 1ns/1ps
module tb_capacity_bound;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,cfg_valid=0,cfg_rsp_ready=0,j_valid=0,recover_valid=0,rsp_ready=0;
 wire cfg_ready,cfg_rsp_valid,cfg_status,j_ready,recover_ready,rsp_valid,labels_valid,target_reset,attempt_reset,permit_work,busy,fault;
 wire[3:0]rsp_status;wire[31:0]journal_count,rsp_corrected,rsp_cookie;
 wire a_valid,a_rsp_ready,o_valid,o_rsp_ready;wire[2:0]o_op;wire[31:0]a_node,a_net,a_cookie,a_checkpoint,o_node,o_net,o_cookie;wire[63:0]a_design;
 reg a_rsp_valid=0,o_rsp_valid=0;reg[31:0]a_rsp_cookie=0,o_rsp_cookie=0;reg[3:0]o_status=0;
 integer caps=0,gets=0,authority=0;
 recovery_coordinator dut(.cfg_stage(1'b0),.publish_valid(1'b0),.publish_permit(1'b0),.discard_valid(1'b0),
 .clk(clk),.cold_rst(rst),.abort(1'b0),.backend_drained(1'b1),.normal_retired(!a_rsp_valid&&!o_rsp_valid),.retry_safe(1'b1),.attempt_reset(attempt_reset),
 .cfg_valid(cfg_valid),.cfg_ready(cfg_ready),.cfg_authoritative(1'b1),.cfg_design(64'h1234),.cfg_checkpoint(32'd18),.cfg_version(32'd4),.cfg_query(2'd2),.cfg_price(4'd4),.cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(cfg_rsp_ready),.cfg_status(cfg_status),
 .j_valid(j_valid),.j_ready(j_ready),.j_node(32'd208292),.j_net(32'd6632),.j_op(3'd2),.journal_count(journal_count),.permit_work(permit_work),
 .recover_valid(recover_valid),.recover_ready(recover_ready),.recover_cookie(32'h1001),.recover_checkpoint(32'd18),.recover_version(32'd5),.recover_design(64'h1234),.recover_query(2'd3),.recover_price(4'd5),.target_reset(target_reset),.reconfigure_done(1'b1),.labels_valid(labels_valid),.labels_done(1'b1),
 .rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.rsp_corrected(rsp_corrected),.busy(busy),.fault(fault),
 .a_valid(a_valid),.a_ready(!a_rsp_valid),.a_node(a_node),.a_net(a_net),.a_cookie(a_cookie),.a_checkpoint(a_checkpoint),.a_design(a_design),.a_rsp_valid(a_rsp_valid),.a_rsp_ready(a_rsp_ready),.a_status(4'd0),.a_rsp_cookie(a_rsp_cookie),.a_rsp_checkpoint(32'd18),.a_rsp_design(64'h1234),.a_refs(32'd1),.a_occupancy(32'd2),
 .o_valid(o_valid),.o_ready(!o_rsp_valid),.o_op(o_op),.o_node(o_node),.o_net(o_net),.o_cookie(o_cookie),.o_rsp_valid(o_rsp_valid),.o_rsp_ready(o_rsp_ready),.o_status(o_status),.o_rsp_cookie(o_rsp_cookie),.o_count(32'd0),.o_occupancy(32'd1));
 always @(posedge clk)if(rst)begin a_rsp_valid<=0;o_rsp_valid<=0;end else begin
  if(labels_valid)$fatal(1,"capacity refusal cannot complete labels");
  if(a_rsp_valid&&a_rsp_ready)a_rsp_valid<=0;
  if(o_rsp_valid&&o_rsp_ready)o_rsp_valid<=0;
  if(a_valid&&!a_rsp_valid)begin a_rsp_cookie<=a_cookie;a_rsp_valid<=1;authority<=authority+1;end
  if(o_valid&&!o_rsp_valid)begin
   o_rsp_cookie<=o_cookie;o_rsp_valid<=1;
   if(o_op==0)begin o_status<=0;gets<=gets+1;end
   else if(o_op==1)begin o_status<=5;caps<=caps+1;end
   else $fatal(1,"unexpected capacity unit operation");
  end
 end
 initial begin #10000;$fatal(1,"bounded capacity retry watchdog");end
 initial begin
  repeat(3)@(negedge clk);rst=0;cfg_valid=1;do @(posedge clk);while(!cfg_ready);@(negedge clk);cfg_valid=0;
  wait(cfg_rsp_valid);@(negedge clk);if(cfg_status)$fatal(1,"cfg");cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;
  j_valid=1;do @(posedge clk);while(!j_ready);@(negedge clk);j_valid=0;
  recover_valid=1;do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;
  wait(rsp_valid);repeat(8)begin @(negedge clk);
   if(rsp_status!=3||rsp_cookie!=32'h1001||rsp_corrected||journal_count!=1||permit_work||!fault||caps!=2||gets!=2||authority!=2)$fatal(1,"unavailable capacity did not fail closed within one extra pass");
  end
  rsp_ready=1;@(negedge clk);rsp_ready=0;
  if(!fault||permit_work||journal_count!=1)$fatal(1,"failure released work");
  $display("CAPACITY_BOUND_PASS refusals=%0d gets=%0d authority=%0d journal=%0d",caps,gets,authority,journal_count);$finish;
 end
endmodule
