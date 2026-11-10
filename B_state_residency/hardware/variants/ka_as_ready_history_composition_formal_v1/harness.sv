module ka_as_ready_history_composition_formal(input wire clk);
(* anyseq *) reg cfg_stage;
(* anyseq *) reg publish_valid;
(* anyseq *) reg publish_permit;
(* anyseq *) reg discard_valid;
(* anyseq *) reg cold_rst;
(* anyseq *) reg abort;
(* anyseq *) reg backend_drained;
(* anyseq *) reg normal_retired;
(* anyseq *) reg retry_safe;
(* anyseq *) reg cfg_valid;
wire cfg_ready;
(* anyseq *) reg cfg_authoritative;
(* anyseq *) reg [63:0] cfg_design;
(* anyseq *) reg [31:0] cfg_checkpoint;
(* anyseq *) reg [31:0] cfg_version;
(* anyseq *) reg [1:0] cfg_query;
(* anyseq *) reg [3:0] cfg_price;
(* anyseq *) reg cfg_rsp_ready;
(* anyseq *) reg j_valid;
(* anyseq *) reg [31:0] j_node;
(* anyseq *) reg [31:0] j_net;
(* anyseq *) reg [2:0] j_op;
(* anyseq *) reg recover_valid;
(* anyseq *) reg [31:0] recover_cookie;
(* anyseq *) reg [31:0] recover_checkpoint;
(* anyseq *) reg [31:0] recover_version;
(* anyseq *) reg [63:0] recover_design;
(* anyseq *) reg [1:0] recover_query;
(* anyseq *) reg [3:0] recover_price;
(* anyseq *) reg reconfigure_done;
(* anyseq *) reg labels_done;
(* anyseq *) reg rsp_ready;
wire busy;
wire a_valid;
(* anyseq *) reg a_ready;
(* anyseq *) reg a_rsp_valid;
wire a_rsp_ready;
(* anyseq *) reg [3:0] a_status;
(* anyseq *) reg [31:0] a_rsp_cookie;
(* anyseq *) reg [31:0] a_rsp_checkpoint;
(* anyseq *) reg [31:0] a_refs;
(* anyseq *) reg [31:0] a_occupancy;
(* anyseq *) reg [63:0] a_rsp_design;
(* anyseq *) reg o_ready;
(* anyseq *) reg o_rsp_valid;
(* anyseq *) reg [3:0] o_status;
(* anyseq *) reg [31:0] o_rsp_cookie;
(* anyseq *) reg [31:0] o_count;
(* anyseq *) reg [31:0] o_occupancy;
wire configured;
wire [3:0] f_state;
(* anyseq *) reg f_authority_quiet;
recovery_coordinator dut(
.cfg_stage(cfg_stage),
.publish_valid(publish_valid),
.publish_permit(publish_permit),
.discard_valid(discard_valid),
.clk(clk),
.cold_rst(cold_rst),
.abort(abort),
.backend_drained(backend_drained),
.normal_retired(normal_retired),
.retry_safe(retry_safe),
.cfg_valid(cfg_valid),
.cfg_ready(cfg_ready),
.cfg_authoritative(cfg_authoritative),
.cfg_design(cfg_design),
.cfg_checkpoint(cfg_checkpoint),
.cfg_version(cfg_version),
.cfg_query(cfg_query),
.cfg_price(cfg_price),
.cfg_rsp_ready(cfg_rsp_ready),
.j_valid(j_valid),
.j_node(j_node),
.j_net(j_net),
.j_op(j_op),
.recover_valid(recover_valid),
.recover_cookie(recover_cookie),
.recover_checkpoint(recover_checkpoint),
.recover_version(recover_version),
.recover_design(recover_design),
.recover_query(recover_query),
.recover_price(recover_price),
.reconfigure_done(reconfigure_done),
.labels_done(labels_done),
.rsp_ready(rsp_ready),
.busy(busy),
.a_valid(a_valid),
.a_ready(a_ready),
.a_rsp_valid(a_rsp_valid),
.a_rsp_ready(a_rsp_ready),
.a_status(a_status),
.a_rsp_cookie(a_rsp_cookie),
.a_rsp_checkpoint(a_rsp_checkpoint),
.a_refs(a_refs),
.a_occupancy(a_occupancy),
.a_rsp_design(a_rsp_design),
.o_ready(o_ready),
.o_rsp_valid(o_rsp_valid),
.o_status(o_status),
.o_rsp_cookie(o_rsp_cookie),
.o_count(o_count),
.o_occupancy(o_occupancy),
.configured(configured),
.f_state(f_state));
reg past_valid=0,seen_aw_response=0;
initial assume(cold_rst);
always @(posedge clk)begin
 past_valid<=1;
 if(cold_rst)seen_aw_response<=0;
 else if(f_state==5 && a_rsp_valid && a_rsp_ready)seen_aw_response<=1;
 if(past_valid && !cold_rst)begin
  if(f_state==1 && backend_drained && normal_retired && !abort) assume(f_authority_quiet);
  if($past(!cold_rst && f_authority_quiet && !a_valid && f_state>=1 && f_state<=9)) assume(f_authority_quiet);
  if($past(!cold_rst && f_state==5 && a_rsp_valid && a_rsp_ready && !abort)) assume(f_authority_quiet);
  if(a_valid && f_authority_quiet) assume(a_ready);
  assert(f_state<=12);
  if(f_state==2 || f_state==3 || f_state==4 || f_state==6 || f_state==7 || f_state==8 || f_state==9) assert(f_authority_quiet);
  if(a_valid) assert(f_authority_quiet);
  if(a_valid) assert(a_ready);
  if(f_state==5) assert(a_rsp_ready);
  if(f_state!=0) assert(configured);
 end
 cover(past_valid && !cold_rst && a_valid && a_ready && f_authority_quiet);
 cover(past_valid && !cold_rst && seen_aw_response && a_valid && a_ready && f_authority_quiet);
end
endmodule
