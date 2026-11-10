from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/query_checkpoint_join_v3/sources/tb_query_fault.sv')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=BASE.read_text();decl='''
reg[63:0]qc_cp_generation=0;reg[31:0]bundle_query_crc;
reg cap_path_valid=0,cap_path_restore=0,cap_path_rsp_ready=0,cap_path_m_ready=0;
wire cap_path_ready,cap_path_busy,cap_path_rsp_valid,cap_path_m_valid,cap_path_m_last;wire[3:0]cap_path_status;wire[31:0]cap_path_crc,cap_path_m_index,cap_path_m_data;
reg[31:0]cap_path_image[0:77];
always @(posedge clk)if(!k_cold_rst&&cap_path_m_valid&&cap_path_m_ready)$fdisplay(trace,"BPATH %0d %08h %0d",cap_path_m_index,cap_path_m_data,cap_path_m_last);
task bundle_capture;begin
 qcp_active=1;
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 if(!pc_owned||!system.pc_safe||system.inner.backend.dut.frontier_size!=0||qc_busy||ss_busy||rc_busy||!f_all_drained||!f_backend_idle||!f_normal_retired)$fatal(1,"bundle capture not quiescent");
 // Reject decreasing generation; capture the later transaction from its handshake.
 qc_cp_generation=1;qcp_start(0);qcp_result(1);
 qc_cp_generation=64'h100000002;qcp_start(0);qc_cp_generation=~qc_cp_generation;
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"bundle query boundary");qcp_image[x]=qc_cp_m_data;repeat(2)@(negedge clk);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);bundle_query_crc=qc_cp_crc;if({qcp_image[5],qcp_image[4]}!==64'h100000002||qcp_image[8]!=1)$fatal(1,"pending capture identity not held");
 // Capturing a future identity does not activate it for a running import.
 qc_cp_expected_crc=bundle_query_crc;qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"future generation silently activated");
 // The default export remains bound to the running authority; re-import it to
 // retire the deliberately failed restore before freezing the healthy bundle.
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x)$fatal(1,"current generation boundary");qcp_image[x]=qc_cp_m_data;repeat(2)@(negedge clk);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if({qcp_image[5],qcp_image[4]}!==64'h100000001)$fatal(1,"default export changed identity");qc_cp_expected_crc=qc_cp_crc;qcp_load(0);

 @(negedge clk);cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==77))$fatal(1,"bundle path boundary");cap_path_image[x]=cap_path_m_data;repeat(2)@(negedge clk);cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"bundle path status");repeat(6)@(negedge clk);cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;wait(!cap_path_busy);
 if(system.as_bound_generation!==64'h100000001||system.controller.last_sequence!=1||qc_restore_pending||!pc_owned||!system.pc_safe||f_phase!=0||!f_all_drained||!f_backend_idle||!f_normal_retired)$fatal(1,"capture changed active binding/work state");
 $fdisplay(trace,"BCFG %0576h",system.inner.backend.config_restore.descriptor);
 $fdisplay(trace,"BCONTEXT %016h %016h %0d %0d %0d %0d %0d %0d %0d",design_id,64'h100000002,k_saved_checkpoint,query_version,p_active_query,p_active_price,cs_published_version,system.controller.last_sequence,rc_slots);
 $fdisplay(trace,"BFLOORS %0d %0d %0d %0d %0d",system.inner.backend.recovery_ctl.current_version,system.inner.backend.recovery_ctl.current_query,system.inner.backend.recovery_ctl.current_price,system.inner.backend.recovery_ctl.attempt_version,system.inner.backend.recovery_ctl.attempt_query);
 for(integer x=0;x<k_count;x=x+1)$fdisplay(trace,"BJ %0d %0d %0d",x,system.inner.backend.recovery_ctl.nodes[x],system.inner.backend.recovery_ctl.nets[x]);
 $fdisplay(trace,"BREADY %0d %08h %08h %0d %0d %0d %0d",cycles,bundle_query_crc,cap_path_crc,k_count,pc_owned,system.inner.backend.dut.frontier_size,f_phase);
end endtask
'''
 s=rep(s,'reg last_k_reset=0',decl+'\nreg last_k_reset=0')
 s=rep(s,')system(',')system(.qc_cp_generation(qc_cp_generation),')
 pins={'cp_valid':'cap_path_valid','cp_restore':'cap_path_restore','cp_rsp_ready':'cap_path_rsp_ready','cp_m_ready':'cap_path_m_ready','cp_design':'design_id','cp_nodes':"32'd9089009",'cp_nets':"32'd27960"}
 for n,v in pins.items():
  import re
  pat=r'\.'+n+r'\([^)]*\)';matches=list(re.finditer(pat,s));assert len(matches)==1,n;s=s[:matches[0].start()]+'.'+n+'('+v+')'+s[matches[0].end():]
 outputs={'cp_ready':'cap_path_ready','cp_busy':'cap_path_busy','cp_rsp_valid':'cap_path_rsp_valid','cp_status':'cap_path_status','cp_crc':'cap_path_crc','cp_m_valid':'cap_path_m_valid','cp_m_index':'cap_path_m_index','cp_m_data':'cap_path_m_data','cp_m_last':'cap_path_m_last'}
 s=rep(s,')system(',')system('+','.join('.'+n+'('+v+')'for n,v in outputs.items())+',')
 s=rep(s,' if(JOIN_ENABLED)query_checkpoint_join;', ' bundle_capture;')
 return s
if __name__=='__main__':(HERE/'tb_query_fault.sv').write_text(make())
