from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/authority_query_v4/sources/tb_query_fault.sv')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=BASE.read_text()
 decl='''
`ifdef QC_NO_LOSS
localparam DIAG_ENABLED=0;
`else
localparam DIAG_ENABLED=1;
`endif
`ifdef QCP_BYPASS
localparam JOIN_ENABLED=0;
`else
localparam JOIN_ENABLED=1;
`endif
reg pc_acquire_valid=0,pc_release_valid=0;wire pc_acquire_ready,pc_release_ready,pc_owned;
reg qc_cp_valid=0,qc_cp_restore=0,qc_cp_rsp_ready=0,qc_cp_s_valid=0,qc_cp_s_last=0,qc_cp_m_ready=0,qc_cp_test_reset=0;
wire qc_cp_ready,qc_cp_busy,qc_cp_rsp_valid,qc_cp_s_ready,qc_cp_m_valid,qc_cp_m_last,qc_restore_pending;
reg[31:0]qc_cp_expected_crc=0,qc_cp_s_index=0,qc_cp_s_data=0;wire[31:0]qc_cp_crc,qc_cp_m_index,qc_cp_m_data;wire[3:0]qc_cp_status;
reg[31:0]qcp_image[0:9],qcp_crc;integer qcp_checks=0,qcp_rejected=0,qcp_pending_cycles=0;reg qcp_active=0;
reg[2303:0]qcp_descriptor;reg[31:0]qcp_journal;reg[1:0]qcp_slots;
always @(posedge clk)if(!k_cold_rst)begin
 if(qc_cp_s_valid&&qc_cp_s_ready)$fdisplay(trace,"QCS %0d %0d %08h %0d",qcp_checks,qc_cp_s_index,qc_cp_s_data,qc_cp_s_last);
 if(qc_cp_m_valid&&qc_cp_m_ready)$fdisplay(trace,"QCM %0d %0d %08h %0d",qcp_checks,qc_cp_m_index,qc_cp_m_data,qc_cp_m_last);
 if(qc_restore_pending)begin
  qcp_pending_cycles<=qcp_pending_cycles+1;
  if(pc_release_ready||qc_cmd_ready||rc_req_ready||expand_ready||seed_ready)$fatal(1,"partial query restore released work");
 end
end
function automatic[31:0]qcp_sum;reg[31:0]v;begin v=32'hffffffff;for(integer x=0;x<10;x=x+1)begin v=v^qcp_image[x];for(integer b=0;b<32;b=b+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;end qcp_sum=~v;end endfunction
 task qcp_result(input integer expected);reg[35:0]hold;begin
 wait(qc_cp_rsp_valid);@(negedge clk);if(qc_cp_status!=expected)$fatal(1,"query checkpoint result %d/%d",qc_cp_status,expected);hold={qc_cp_status,qc_cp_crc};
 pc_release_valid=1;
 repeat(6)begin @(negedge clk);if(!qc_cp_rsp_valid||{qc_cp_status,qc_cp_crc}!==hold||pc_release_ready||!pc_owned)$fatal(1,"held query checkpoint released lease");end
 pc_release_valid=0;$fdisplay(trace,"QCP %0d %0d %08h %0d %0d",qcp_checks,qc_cp_status,qc_cp_crc,qc_restore_pending,system.controller.last_sequence);qcp_checks=qcp_checks+1;
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;wait(!qc_cp_busy);
end endtask
task qcp_start(input integer restore);begin
 @(negedge clk);qc_cp_restore=restore;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
end endtask
task qcp_load(input integer expected);begin
 qcp_start(1);
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_valid=1;qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
 end
 qcp_result(expected);
end endtask
task query_checkpoint_join;begin
 qcp_active=1;qcp_descriptor=system.inner.backend.config_restore.descriptor;qcp_journal=k_count;qcp_slots=rc_slots;
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;if(!pc_owned)$fatal(1,"query checkpoint no lease");
 qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"query export boundary");qcp_image[x]=qc_cp_m_data;repeat(2)@(negedge clk);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);qcp_crc=qc_cp_crc;
 if(qcp_image[8]!=1||!qcp_image[7][6])$fatal(1,"query ledger did not capture consumed sequence");
 if(DIAG_ENABLED)begin
 @(negedge clk);qc_cp_test_reset=1;repeat(3)@(negedge clk);qc_cp_test_reset=0;repeat(3)@(negedge clk);
 if(!qc_restore_pending||system.controller.last_sequence!=0||system.controller.sequence_seen)$fatal(1,"query diagnostic loss");
 pc_release_valid=1;repeat(9)begin @(negedge clk);if(pc_release_ready||!pc_owned)$fatal(1,"unrestored query released lease");end pc_release_valid=0;
 end
 qc_cp_expected_crc=qcp_crc^1;qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=(DIAG_ENABLED?0:1))$fatal(1,"bad CRC opened recovery gate");
 qcp_image[5]=qcp_image[5]^1;qc_cp_expected_crc=qcp_sum();qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=(DIAG_ENABLED?0:1))$fatal(1,"wrong generation opened recovery gate");qcp_image[5]=qcp_image[5]^1;
 qc_cp_expected_crc=qcp_crc;qcp_load(0);if(qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"query ledger recovery missing");
 if(system.inner.backend.config_restore.descriptor!==qcp_descriptor||k_count!=qcp_journal||rc_slots!=qcp_slots||system.as_bound_generation!=64'h100000001)$fatal(1,"query reset changed retained services");
 @(negedge clk);pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 // A free slot and valid context ensure this is a sequence rejection.
 @(negedge clk);qc_cmd_slot=1;qc_cmd_cookie=32'hce000001;qc_cmd_source=65185;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];qc_cmd_expand={restore_version,32'd295,32'd283,32'd46,32'd38,32'd260,32'd1,32'd2717,selected_sink,32'd0,32'd0,32'd0,32'd100,selected_connection};
 if(rc_slots[1]||system.controller.label_state_dirty||qc_cmd_query!=p_active_query||qc_cmd_price!=p_active_price||qc_cmd_expand[447:416]!=query_version||!system.controller.sequence_seen)$fatal(1,"invalid sequence probe context");
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);@(negedge clk);if(qc_rsp_status!=1||qc_rsp_committed||qc_prepare_acked||qc_cleanup_acked||qc_fault||ss_busy||rc_slots!=qcp_slots)$fatal(1,"restored sequence replay admitted");
 $fdisplay(trace,"QCP_REJECT %0d %0d %0d %0d",cycles,qc_rsp_status,qc_prepare_acked,qc_rsp_committed);qcp_rejected=qcp_rejected+1;
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;wait(!qc_busy);
 $fdisplay(trace,"QCP_JOIN %0d %0d %0d %0d %0d",cycles,qcp_checks,qcp_rejected,qcp_pending_cycles,system.controller.last_sequence);
end endtask
'''
 s=rep(s,'reg last_k_reset=0',decl+'\nreg last_k_reset=0')
 s=s.replace('.ENABLE_TEST_INJECTION(0))system(','.ENABLE_TEST_INJECTION(DIAG_ENABLED))system(')
 for n in ['pc_acquire_valid','pc_release_valid']:
  s=rep(s,'.'+n+"(1'b0)",'.'+n+'('+n+')')
 pin=['pc_acquire_ready','pc_release_ready','pc_owned','qc_cp_valid','qc_cp_restore','qc_cp_rsp_ready','qc_cp_s_valid','qc_cp_s_last','qc_cp_m_ready','qc_cp_test_reset','qc_cp_ready','qc_cp_busy','qc_cp_rsp_valid','qc_cp_s_ready','qc_cp_m_valid','qc_cp_m_last','qc_restore_pending','qc_cp_expected_crc','qc_cp_s_index','qc_cp_s_data','qc_cp_crc','qc_cp_m_index','qc_cp_m_data','qc_cp_status']
 s=rep(s,')system(',')system('+','.join('.'+n+'('+n+')'for n in pin)+',')
 s=rep(s,' $fflush(trace);$fclose(trace);\n $display("QUERY_FAULT_OBSERVED', ' if(JOIN_ENABLED)query_checkpoint_join;\n $fflush(trace);$fclose(trace);\n $display("QUERY_FAULT_OBSERVED')
 # Existing lifecycle response monitor also observes the deliberate status1 probe.
 s=rep(s,'always @(posedge clk)if(!rst&&qc_rsp_valid)begin', 'always @(posedge clk)if(!rst&&qc_rsp_valid&&!qcp_active)begin')
 return s
if __name__=='__main__':(HERE/'tb_query_fault.sv').write_text(make())
