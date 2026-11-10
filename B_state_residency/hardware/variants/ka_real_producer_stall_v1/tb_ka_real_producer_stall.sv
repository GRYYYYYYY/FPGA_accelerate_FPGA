`timescale 1ns/1ps
module tb_ka_real_producer_stall;
 reg clk=0; always #5 clk=~clk;
 reg cold_rst=1,cfg_valid=0,j_valid=0,recover_valid=0;
 wire cfg_ready,cfg_rsp_valid,cfg_status,j_ready,recover_ready;
 wire reconfigure_valid,labels_valid,rsp_valid,fault;
 wire [3:0]rsp_status; wire[31:0]rsp_corrected;
 wire a_valid,a_rsp_ready,o_valid,o_rsp_ready;
 wire[31:0]a_node,a_net,a_cookie,a_checkpoint,o_cookie;
 wire[63:0]a_design;
 reg a_ready=0,a_rsp_valid=0,o_rsp_valid=0;
 reg[31:0]a_rsp_cookie=0,o_rsp_cookie=0;
 integer stalled=0,transfers=0,owner_transfers=0,ticks=0;
 reg held=0;reg[191:0]payload;
 recovery_coordinator #(.ENTRIES(32),.RESET_HOLD(5),.MAX_CYCLES(1024),.EXCLUSIVE_BACKEND_RESPONSES(1)) dut(
 .clk(clk),.cold_rst(cold_rst),.abort(1'b0),.backend_drained(1'b1),.normal_retired(1'b1),.retry_safe(1'b1),
 .cfg_stage(1'b0),.publish_valid(1'b0),.publish_permit(1'b0),.discard_valid(1'b0),
 .cfg_valid(cfg_valid),.cfg_ready(cfg_ready),.cfg_authoritative(1'b1),.cfg_design(64'h123456789abcdef0),
 .cfg_checkpoint(32'd17),.cfg_version(32'd3),.cfg_query(2'd1),.cfg_price(4'd3),
 .cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(1'b1),.cfg_status(cfg_status),
 .j_valid(j_valid),.j_ready(j_ready),.j_node(32'd100),.j_net(32'd2),.j_op(3'd1),
 .recover_valid(recover_valid),.recover_ready(recover_ready),.recover_cookie(32'hcafef00d),
 .recover_checkpoint(32'd17),.recover_version(32'd4),.recover_design(64'h123456789abcdef0),.recover_query(2'd2),.recover_price(4'd4),
 .reconfigure_valid(reconfigure_valid),.reconfigure_done(reconfigure_valid),.labels_valid(labels_valid),.labels_done(labels_valid),
 .rsp_valid(rsp_valid),.rsp_ready(1'b0),.rsp_status(rsp_status),.rsp_corrected(rsp_corrected),.fault(fault),
 .a_valid(a_valid),.a_ready(a_ready),.a_node(a_node),.a_net(a_net),.a_cookie(a_cookie),.a_checkpoint(a_checkpoint),.a_design(a_design),
 .a_rsp_valid(a_rsp_valid),.a_rsp_ready(a_rsp_ready),.a_status(4'd0),.a_rsp_cookie(a_rsp_cookie),
 .a_rsp_checkpoint(32'd17),.a_rsp_design(64'h123456789abcdef0),.a_refs(32'd0),.a_occupancy(32'd0),
 .o_valid(o_valid),.o_ready(1'b1),.o_cookie(o_cookie),.o_rsp_valid(o_rsp_valid),.o_rsp_ready(o_rsp_ready),
 .o_status(4'd0),.o_rsp_cookie(o_rsp_cookie),.o_count(32'd0),.o_occupancy(32'd0));
 always @(posedge clk)begin
  ticks=ticks+1;if(ticks>300)$fatal(1,"KA_UNIT_WATCHDOG");
  if(!cold_rst)begin
   if(held&&(!a_valid||{a_design,a_checkpoint,a_node,a_net,a_cookie}!==payload))$fatal(1,"KA_UNIT_HOLD_MISMATCH");
   held<=a_valid&&!a_ready;payload<={a_design,a_checkpoint,a_node,a_net,a_cookie};
   if(a_valid)begin
    if($isunknown({a_design,a_checkpoint,a_node,a_net,a_cookie}))$fatal(1,"KA_UNIT_UNKNOWN");
    if(a_node!==32'd100||a_net!==32'd2||a_checkpoint!==32'd17||a_design!==64'h123456789abcdef0)$fatal(1,"KA_UNIT_PAYLOAD");
    if(a_ready)begin
     if(a_cookie!==(transfers==0?32'hcafef00d:32'h4afef00d))$fatal(1,"KA_UNIT_COOKIE");
     transfers=transfers+1;a_rsp_cookie<=a_cookie;a_rsp_valid<=1;a_ready<=0;
    end else stalled=stalled+1;
   end
   if(a_rsp_valid&&a_rsp_ready)begin a_rsp_valid<=0;a_ready<=1;end
   if(o_valid)begin owner_transfers=owner_transfers+1;o_rsp_cookie<=o_cookie;o_rsp_valid<=1;end
   if(o_rsp_valid&&o_rsp_ready)o_rsp_valid<=0;
   if(fault)$fatal(1,"KA_UNIT_DUT_FAULT");
  end
 end
 initial begin
  repeat(5)@(negedge clk);cold_rst=0;
  @(negedge clk);cfg_valid=1;do @(posedge clk);while(!cfg_ready);
  @(negedge clk);cfg_valid=0;if(!cfg_rsp_valid||cfg_status!==0)$fatal(1,"KA_UNIT_CONFIG");
  repeat(2)@(negedge clk);j_valid=1;do @(posedge clk);while(!j_ready);
  @(negedge clk);j_valid=0;recover_valid=1;do @(posedge clk);while(!recover_ready);
  @(negedge clk);recover_valid=0;wait(a_valid);
  repeat(7)@(negedge clk);a_ready=1;
  wait(rsp_valid);@(negedge clk);
  if(rsp_status!==0||rsp_corrected!==0||transfers!=2||owner_transfers!=2||stalled<6)$fatal(1,"KA_UNIT_RESULT stalled=%0d transfers=%0d owner=%0d status=%0d",stalled,transfers,owner_transfers,rsp_status);
  $display("KA_REAL_PRODUCER_STALL_PASS stalled=%0d transfers=%0d owner=%0d",stalled,transfers,owner_transfers);$finish;
 end
endmodule
