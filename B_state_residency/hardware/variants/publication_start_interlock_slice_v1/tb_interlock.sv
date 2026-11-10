`timescale 1ns/1ps
module tb_interlock;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,acquire=0,release_valid=0,jp_start=0,start_open=1;
 reg ap_valid=0,cp_valid=0,qc_cp_valid=0;
 reg other_busy=0,healthy=1,retired=1,route_retired=1,no_offers=1,test_reset=0;
 reg stage_busy=0,fault=0,manifest_ready=1,commit_valid=0,cancel_valid=0,done_ready=0;
 reg[2:0]prepared=0,publish_ready=7,discard_ready=7;
 reg[63:0]a_generation=1,start_generation=2;
 reg[31:0]a_checkpoint=1;
 wire acquire_ready,release_ready,pc_owned,safe,jp_owned,core_start_ready,start_ready,prepare_allowed,commit_ready,cancel_ready,done_valid;
 wire[1:0]done_status;wire[2:0]publish_valid,discard_valid;
 wire command_valid;
`ifdef ORIGINAL_WIRING
 assign command_valid=ap_valid||cp_valid||qc_cp_valid;
`else
 assign command_valid=jp_start||ap_valid||cp_valid||qc_cp_valid;
`endif
 assign start_ready=core_start_ready&&start_open;
 checkpoint_lease_guard lease(.clk(clk),.rst(rst),.acquire_valid(acquire),.release_valid(release_valid),
 .healthy(healthy),.retired(retired),.no_offers(no_offers),.route_retired(route_retired),
 .command_busy(other_busy||jp_owned),.command_valid(command_valid),.test_reset(test_reset),
 .acquire_ready(acquire_ready),.release_ready(release_ready),.safe(safe),.owned(pc_owned));
 checkpoint_publish_barrier publication(.clk(clk),.rst(rst),.lease_owned(pc_owned),.retired(retired&&route_retired),
 .stage_busy(stage_busy),.fault(fault),.manifest_ready(manifest_ready),.start_valid(jp_start&&start_open),.start_ready(core_start_ready),
 .start_design(64'd1),.start_generation(start_generation),.start_checkpoint(32'd2),.start_version(32'd3),.start_query(2'd0),.start_price(4'd3),
 .commit_valid(commit_valid),.cancel_valid(cancel_valid),.commit_ready(commit_ready),.cancel_ready(cancel_ready),
 .owned(jp_owned),.prepare_allowed(prepare_allowed),.done_valid(done_valid),.done_ready(done_ready),.done_status(done_status),
 .prepared(prepared),.publish_ready(publish_ready),.discard_ready(discard_ready),.publish_valid(publish_valid),.discard_valid(discard_valid),
 .a_design(64'd1),.a_generation(a_generation),.a_checkpoint(a_checkpoint),.k_design(64'd1),.c_design(64'd1),
 .k_checkpoint(a_checkpoint),.c_checkpoint(a_checkpoint),.k_version(32'd3),.c_version(32'd3),.k_query(2'd0),.k_price(4'd3),.journal_count(32'd0),
 .sa_design(64'd1),.sa_generation(64'd2),.sa_checkpoint(32'd2),.sk_design(64'd1),.sc_design(64'd1),
 .sk_checkpoint(32'd2),.sc_checkpoint(32'd2),.sk_version(32'd3),.sc_version(32'd3),.sk_query(2'd0),.sk_price(4'd3));
 integer checks=0,cycles=0,owned_checks=0,cases=0;integer fd;
 task automatic check(input logic ok,input string message);
  checks=checks+1;if(ok!==1'b1)$fatal(1,"INTERLOCK_CHECK %s",message);
 endtask
 task automatic step;begin @(posedge clk);#1;end endtask
 task automatic mark(input integer id,input string name);
  cases=cases+1;$display("INTERLOCK_CASE id=%0d name=%s time=%0t",id,name,$time);
 endtask
 task automatic reset_acquire;
  @(negedge clk);rst=1;acquire=0;release_valid=0;jp_start=0;start_open=1;
  other_busy=0;healthy=1;retired=1;route_retired=1;no_offers=1;test_reset=0;
  stage_busy=0;fault=0;manifest_ready=1;commit_valid=0;cancel_valid=0;done_ready=0;
  prepared=0;publish_ready=7;discard_ready=7;a_generation=1;a_checkpoint=1;start_generation=2;
  repeat(3)step();@(negedge clk);rst=0;acquire=1;#1;check(acquire_ready===1,"ACQUIRE_READY");
  step();check(pc_owned===1&&jp_owned===0,"ACQUIRE_OWNERSHIP");@(negedge clk);acquire=0;
 endtask
 task automatic start_transaction;
  @(negedge clk);jp_start=1;#1;check(start_ready===1,"START_READY");check(release_ready===0,"START_BLOCKS_RELEASE");
  step();check(pc_owned===1&&jp_owned===1,"START_OWNS_LEASE");@(negedge clk);jp_start=0;
 endtask
 task automatic cancel_transaction;
  @(negedge clk);cancel_valid=1;#1;check(cancel_ready===1,"CANCEL_READY");
  step();@(negedge clk);cancel_valid=0;step();check(done_valid===1&&done_status===2,"CANCEL_DONE");
 endtask
 task automatic finish_reply(input logic[1:0]expected,input integer record_cases);
  repeat(3)begin
   step();check(done_valid===1&&done_status===expected&&jp_owned===1&&pc_owned===1&&release_ready===0,"RESPONSE_HOLD");
  end
  if(record_cases)mark(3,"response_backpressure");
  @(negedge clk);done_ready=1;release_valid=1;#1;check(release_ready===0,"PRE_CONSUMPTION_RELEASE_BLOCKED");
  step();check(jp_owned===0&&pc_owned===1,"CONSUMPTION_RETAINS_LEASE");
  if(record_cases)mark(4,"release_on_consumption_edge");
  @(negedge clk);done_ready=0;#1;check(release_ready===1,"POST_CONSUMPTION_RELEASE_READY");
  step();check(pc_owned===0&&jp_owned===0,"POST_CONSUMPTION_RELEASE");@(negedge clk);release_valid=0;
  if(record_cases)mark(5,"release_after_consumption");
 endtask
 always @(posedge clk)begin
  cycles=cycles+1;
  $fdisplay(fd,"%0t,%b,%b,%b,%b,%b,%b,%b,%b,%b,%b",$time,rst,jp_start,start_ready,release_valid,release_ready,pc_owned,jp_owned,done_valid,done_ready,done_status[0]);
  #1;if(!rst&&jp_owned===1'b1)begin owned_checks=owned_checks+1;check(pc_owned===1,"PUBLICATION_LOST_LEASE");end
 end
 initial begin
  fd=$fopen("edges.csv","w");if(!fd)$fatal(1,"TRACE_OPEN");
  $fdisplay(fd,"time_ps,rst,start,start_ready,release,release_ready,lease_owned,publication_owned,done,done_ready,status_lsb");
  reset_acquire();@(negedge clk);release_valid=1;#1;check(release_ready===1,"RELEASE_ONLY_READY");
  step();check(pc_owned===0,"RELEASE_ONLY_ACCEPTED");mark(1,"release_only");
  reset_acquire();@(negedge clk);jp_start=1;release_valid=1;
  #1;check(start_ready===1,"SIMULTANEOUS_START_READY");check(release_ready===0,"SIMULTANEOUS_RELEASE_NOT_BLOCKED");
  step();check(pc_owned===1&&jp_owned===1,"SIMULTANEOUS_SINGLE_ACCEPT");
  @(negedge clk);jp_start=0;repeat(3)begin step();check(pc_owned===1&&release_ready===0,"HELD_RELEASE_DURING_OPEN");end
  mark(2,"simultaneous_start_held_release");cancel_transaction();finish_reply(2,1);
  reset_acquire();@(negedge clk);start_open=0;jp_start=1;release_valid=1;
  repeat(3)begin step();check(start_ready===0&&release_ready===0&&pc_owned===1&&jp_owned===0,"HELD_START_NOT_READY");end
  @(negedge clk);start_open=1;#1;check(start_ready===1&&release_ready===0,"HELD_START_BECOMES_READY");
  step();check(jp_owned===1&&pc_owned===1,"HELD_START_ACCEPTED");mark(6,"held_start_not_ready");
  @(negedge clk);jp_start=0;cancel_transaction();check(publish_valid===0,"CANCEL_NO_PUBLISH");mark(7,"cancel");finish_reply(2,0);
  reset_acquire();@(negedge clk);start_generation=1;start_transaction();
  check(done_valid===1&&done_status===1,"INVALID_START_REJECTION");mark(8,"invalid_start_payload");finish_reply(1,0);
  reset_acquire();start_transaction();@(negedge clk);prepared=7;commit_valid=1;
  #1;check(commit_ready===1&&publish_valid===7,"COMMIT_PUBLISH");step();
  @(negedge clk);commit_valid=0;prepared=0;a_generation=2;a_checkpoint=2;step();
  check(done_valid===1&&done_status===0,"COMMIT_DONE");mark(9,"normal_commit");finish_reply(0,0);
  reset_acquire();@(negedge clk);jp_start=1'bx;release_valid=1;#1;
  check(release_ready===1'bx,"UNKNOWN_START_PROPAGATES");step();check(pc_owned===1&&jp_owned===0,"UNKNOWN_NOT_ACCEPTED_IN_RTL_IF");
  @(negedge clk);jp_start=0;#1;check(release_ready===1,"UNKNOWN_WITHDRAWN");step();check(pc_owned===0,"RELEASE_AFTER_UNKNOWN_WITHDRAWN");mark(10,"unknown_start_observation");
  check(cases==10&&owned_checks>20,"COVERAGE");
  $display("INTERLOCK_SLICE_PASS cases=%0d checks=%0d cycles=%0d owned_checks=%0d time=%0t",cases,checks,cycles,owned_checks,$time);
  $fclose(fd);$finish;
 end
 initial begin #10000;$fatal(1,"INTERLOCK_SLICE_WATCHDOG");end
endmodule
