from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def make():
 s=runpy.run_path(str(ROOT/'hardware/variants/label_baseline_cancel_v1/build_tb.py'))['make']()
 s=s.replace('.host_release_ready(pc_release_ready),.root_release_valid(snap_root_release_valid)', '.host_release_valid_UNUSED(pc_release_valid),.host_release_ready(pre_g3_pc_release_ready),.root_release_valid(snap_root_release_valid)',1)
 s=s.replace('.host_release_valid(pc_release_valid),.root_release_ready(label_gate_ready),.host_release_valid_UNUSED(pc_release_valid),', '.host_release_valid(pc_release_valid&&!g3_block),.root_release_ready(label_gate_ready),',1)
 s=s.replace(' $fdisplay(trace,"BASELINE_WARM_DONE %0d",cycles);', ' $fdisplay(trace,"BASELINE_WARM_DONE %0d",cycles);\n cumulative_g3_copy;',1)
 extra='''
assign pc_release_ready=pre_g3_pc_release_ready&&!g3_block;
reg g3_cmd=0,g3_ack=0;reg[1:0]g3_op=0;
wire g3_ready,g3_busy,g3_rsp,g3_receipt,g3_bound,g3_data_error,g3_coverage_error,g3_manifest;
wire[3:0]g3_status;wire[31:0]g3_cookie,g3_dirty,g3_verified;
wire[63:0]g3_floor,g3_cpfloor,g3_rd,g3_rb,g3_rg,g3_rc,g3_rdst;
wire[63:0]g3_ar,g3_aw;wire g3_av,g3_aq,g3_rv,g3_rr,g3_rl,g3_wav,g3_waq,g3_wv,g3_wq,g3_bv,g3_bq;
wire[511:0]g3_data,g3_wdata;wire[3:0]g3_rid,g3_bid;wire[1:0]g3_rresp,g3_bresp;
wire g3_healthy=system.pc_safe&&!wm_owned&&!wm_fault&&recover_open&&!qc_busy&&!rc_busy&&!f_fault;
cumulative_owner_snapshot #(.MAX_DIRTY(64)) g3_writer(
 .clk(clk),.rst(k_cold_rst),.lease(pc_owned),.source_drained(f_all_drained&&f_backend_idle&&f_normal_retired&&owner_drained),.source_healthy(g3_healthy),.source_protocol_ok(!owner_watch_fault),
 .cmd_op(g3_op),.cmd_design(design_id),.cmd_baseline(64'h100000001),.cmd_generation(64'h100000003),.cmd_checkpoint(g3_op==0 ? 64'd17 : 64'd19),
 .bank0_base(64'ha000000000),.bank1_base(64'hc000000000),.active_destination(as_bound_generation==64'h100000001 ? 64'h91fffff000 : 64'ha000000000),.active_generation(as_bound_generation),
 .obs_bid(owner_m_bid),.obs_awid(owner_m_awid),.obs_awsize(owner_m_awsize),.obs_awburst(owner_m_awburst),
 .bound(g3_bound),.data_error(g3_data_error),.coverage_error(g3_coverage_error),.generation_floor(g3_floor),.checkpoint_floor(g3_cpfloor),
 .receipt_design(g3_rd),.receipt_baseline(g3_rb),.receipt_generation(g3_rg),.receipt_checkpoint(g3_rc),.receipt_destination(g3_rdst),
 .publish_design(design_id),.publish_baseline(64'h100000001),.publish_generation(64'h100000003),.publish_checkpoint(64'd19),.publish_destination(64'hc000000000),.manifest_ready(g3_manifest),.release_blocked(g3_block),
 .obs_awvalid(owner_m_awvalid),.obs_awready(owner_m_awready),.obs_awaddr(owner_m_awaddr),.obs_awlen(owner_m_awlen),.obs_bvalid(owner_m_bvalid),.obs_bready(owner_m_bready),.obs_bresp(owner_m_bresp),
 .cmd_valid(g3_cmd),.cmd_ready(g3_ready),.source_base(64'h61fffff000),.destination_base(64'hc000000000),.span_bytes(64'd146284032),.cmd_cookie(32'h5a000019),
 .busy(g3_busy),.rsp_valid(g3_rsp),.rsp_ready(g3_ack),.status(g3_status),.rsp_cookie(g3_cookie),.receipt_valid(g3_receipt),.dirty_count(g3_dirty),.verified_count(g3_verified),
 .m_araddr(g3_ar),.m_arvalid(g3_av),.m_arready(g3_aq),.m_rdata(g3_data),.m_rid(g3_rid),.m_rresp(g3_rresp),.m_rlast(g3_rl),.m_rvalid(g3_rv),.m_rready(g3_rr),
 .m_awaddr(g3_aw),.m_awvalid(g3_wav),.m_awready(g3_waq),.m_wdata(g3_wdata),.m_wvalid(g3_wv),.m_wready(g3_wq),.m_bid(g3_bid),.m_bresp(g3_bresp),.m_bvalid(g3_bv),.m_bready(g3_bq));
axi_file_memory #(.READ_ONLY(0),.MAX_BEATS(1),.TERTIARY_WRITABLE(1),.TAG("g3copy")) g3_memory(
 .clk(clk),.rst(k_cold_rst),.base0(64'h61fffff000),.base1(64'ha000000000),.base2(64'hc000000000),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd146284032),.inject_r(1'b0),.inject_b(1'b0),.hold_r(1'b0),
 .araddr(g3_ar),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(g3_av),.arready(g3_aq),.rdata(g3_data),.rid(g3_rid),.rresp(g3_rresp),.rlast(g3_rl),.rvalid(g3_rv),.rready(g3_rr),
 .awaddr(g3_aw),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(g3_wav),.awready(g3_waq),.wdata(g3_wdata),.wstrb(64'hffffffffffffffff),.wlast(1'b1),.wvalid(g3_wv),.wready(g3_wq),.bid(g3_bid),.bresp(g3_bresp),.bvalid(g3_bv),.bready(g3_bq));
task cumulative_command(input integer op);begin
 @(negedge clk);g3_op=op;g3_cmd=1;do @(posedge clk);while(!g3_ready);@(negedge clk);g3_cmd=0;
end endtask
task cumulative_result(input integer op,expected,n);begin
 wait(g3_rsp);repeat(8)begin @(negedge clk);
  if(g3_status!=expected||g3_cookie!=32'h5a000019||g3_verified!=n||!pc_owned||pc_release_ready||g3_manifest)$fatal(1,"cumulative held response op=%0d status=%0d",op,g3_status);
 end
 $fdisplay(trace,"CUMULATIVE_RESULT %0d %0d %0d %0d %0d %0d %0d %016h %0d",cycles,op,g3_status,g3_dirty,g3_verified,g3_data_error,g3_coverage_error,g3_floor,g3_cpfloor);
 g3_ack=1;@(negedge clk);g3_ack=0;wait(!g3_busy);
end endtask
initial begin
 @(negedge bench_rst);wait(pc_owned&&g3_healthy&&f_all_drained&&f_backend_idle&&f_normal_retired&&owner_drained);
 cumulative_command(0);cumulative_result(0,0,0);
 if(!g3_bound||g3_dirty||g3_floor!=64'h100000001)$fatal(1,"pre-work cumulative bind");
end
task cumulative_g3_copy;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 $fdisplay(trace,"CUMULATIVE_PRECONDITION %0d %0d %0d %0d %0d %0d %0d %016h %0d %0d %0d",cycles,pc_owned,g3_healthy,g3_bound,g3_data_error,g3_coverage_error,g3_dirty,as_bound_generation,k_saved_checkpoint,rc_slots,system.controller.last_sequence);
 if(!pc_owned||!g3_healthy||!g3_bound||!g3_data_error||g3_coverage_error||g3_dirty!=4||as_bound_generation!=64'h100000002||k_saved_checkpoint!=18||rc_slots!=3||system.controller.last_sequence!=180328)$fatal(1,"actual G3 rearm preconditions");
 $fdisplay(trace,"CUMULATIVE_REARM_SOURCE %0d %0d %0d %0d %0d %0d %0d",cycles,pc_owned,g3_healthy,owner_drained,f_all_drained,g3_data_error,g3_dirty);
 cumulative_command(1);cumulative_result(1,0,0);
 if(g3_data_error||g3_coverage_error||g3_dirty!=4)$fatal(1,"cumulative rearm lost coverage");
 cumulative_command(2);cumulative_result(2,0,4);
 if(!g3_manifest||!g3_receipt||g3_rd!=design_id||g3_rb!=64'h100000001||g3_rg!=64'h100000003||g3_rc!=19||g3_rdst!=64'hc000000000||g3_dirty!=4||as_bound_generation!=64'h100000002||k_saved_checkpoint!=18)$fatal(1,"G3 candidate descriptor/current G2");
 $fdisplay(trace,"CUMULATIVE_G3_CANDIDATE %0d %016h %0d %016h %0d",cycles,g3_rg,g3_rc,g3_rdst,g3_dirty);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(g3_coverage_error)$fatal(1,"real owner cumulative coverage lost");
 if(g3_busy&&(!pc_owned||pc_release_ready||owner_m_awvalid))$fatal(1,"cumulative native lease");
 if(g3_cmd&&g3_ready)$fdisplay(trace,"CUMULATIVE_ACCEPT %0d %0d %0d %0d",cycles,g3_op,g3_dirty,g3_data_error);
end
'''
 s=s.replace('owner_snapshot_checkpoint_adapter #(', 'wire pre_g3_pc_release_ready,g3_block;\nowner_snapshot_checkpoint_adapter #(',1)
 return s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':(HERE/'tb_cumulative_system.sv').write_text(make())
