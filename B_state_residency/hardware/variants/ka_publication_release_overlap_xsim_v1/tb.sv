`timescale 1ns/1ps
module tb;
reg clk=0;always #5 clk=~clk;
reg rst=1,acquire_valid=0,release_valid=0,start_valid=0;
wire jp_done;wire [1:0]jp_status;
wire pc_owned,jp_owned,acquire_ready,release_ready,start_ready,prepare_allowed;
checkpoint_lease_guard lease(.clk(clk),.rst(rst),.acquire_valid(acquire_valid),.acquire_ready(acquire_ready),.release_valid(release_valid),.release_ready(release_ready),.owned(pc_owned),.healthy(1'b1),.retired(1'b1),.route_retired(1'b1),.no_offers(1'b1),.command_busy(jp_owned),.command_valid(1'b0),.test_reset(1'b0));
checkpoint_publish_barrier publication(.clk(clk),.rst(rst),.lease_owned(pc_owned),.retired(1'b1),.stage_busy(1'b0),.fault(1'b0),.manifest_ready(1'b1),.start_valid(start_valid),.start_ready(start_ready),.start_design(64'd1),.start_generation(64'd2),.start_checkpoint(32'd2),.start_version(32'd1),.start_query(2'd0),.start_price(4'd1),.commit_valid(1'b0),.cancel_valid(1'b0),.owned(jp_owned),.prepare_allowed(prepare_allowed),.done_ready(1'b0),.done_valid(jp_done),.done_status(jp_status),.prepared(3'd0),.publish_ready(3'd0),.discard_ready(3'd0),.a_design(64'd1),.a_generation(64'd1),.k_design(64'd1),.c_design(64'd1),.a_checkpoint(32'd1),.k_checkpoint(32'd1),.c_checkpoint(32'd1),.k_version(32'd1),.c_version(32'd1),.journal_count(32'd0),.k_query(2'd0),.k_price(4'd1),.sa_design(64'd1),.sa_generation(64'd2),.sa_checkpoint(32'd2),.sk_design(64'd1),.sc_design(64'd1),.sk_checkpoint(32'd2),.sc_checkpoint(32'd2),.sk_version(32'd1),.sc_version(32'd1),.sk_query(2'd0),.sk_price(4'd1));
initial begin
 repeat(3) @(negedge clk);
 rst=0;acquire_valid=1;
 @(posedge clk);if(acquire_ready!==1'b1)$fatal(1,"acquire not admitted");
 @(negedge clk);acquire_valid=0;if(pc_owned!==1'b1||jp_owned!==1'b0)$fatal(1,"bad acquired state");
 @(negedge clk);start_valid=1;release_valid=1;
 #1;if(start_ready!==1'b1||release_ready!==1'b1)$fatal(1,"overlap not admitted");
 @(posedge clk);$display("SIMULTANEOUS_ACCEPT time=%0t start=%b release=%b",$time,start_ready,release_ready);
 #1;if(jp_owned!==1'b1||pc_owned!==1'b0)$fatal(1,"expected ownership split absent");
 $display("OWNERSHIP_SPLIT time=%0t publication=%b lease=%b",$time,jp_owned,pc_owned);
 @(negedge clk);start_valid=0;release_valid=0;
 @(posedge clk);#1;if(jp_done!==1'b1||jp_status!==2'd3||jp_owned!==1'b1||pc_owned!==1'b0)$fatal(1,"expected halt output absent");
 $display("REPRODUCTION_OBSERVED time=%0t status=%0d publication=%b lease=%b",$time,jp_status,jp_owned,pc_owned);
 $finish;
end
initial begin #1000;$fatal(1,"watchdog");end
endmodule
