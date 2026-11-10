from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/recovery_retry_normal_v1/sources/tb_query_lifecycle_join.sv'
def rep(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def make():
 s=BASE.read_text()
 decl='''
`ifdef PC_BYPASS
localparam PC_ENABLED=0;
`else
localparam PC_ENABLED=1;
`endif
reg pc_acquire_valid=0,pc_release_valid=0;wire pc_acquire_ready,pc_release_ready,pc_owned;
reg cp_valid=0,cp_restore=0,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0,cp_test_reset=0;
wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;
reg[63:0]cp_design=64'h123456789abcdef0;reg[31:0]cp_nodes=9089009,cp_nets=27960,cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;
reg[31:0]pc_image[0:77],pc_saved_crc;integer pc_waits=0,pc_checks=0,pc_owned_cycles=0,pc_loss_cycles=0,pc_contend_cycles=0;
reg[31:0]pc_saved_sequence,pc_saved_journal;reg[2303:0]pc_saved_descriptor;integer pc_axi_before[0:11];
'''
 s=rep(s,'module tb_candidate_offer;', 'module tb_candidate_offer;\n'+decl)
 s=rep(s,'.ENABLE_TEST_INJECTION(0))system(','.ENABLE_TEST_INJECTION(PC_ENABLED))system(')
 names=['pc_acquire_valid','pc_acquire_ready','pc_release_valid','pc_release_ready','pc_owned','cp_valid','cp_restore','cp_ready','cp_busy','cp_rsp_valid','cp_rsp_ready','cp_status','cp_crc','cp_design','cp_nodes','cp_nets','cp_expected_crc','cp_s_valid','cp_s_ready','cp_s_index','cp_s_data','cp_s_last','cp_m_valid','cp_m_ready','cp_m_index','cp_m_data','cp_m_last','cp_test_reset']
 s=rep(s,')system(.qc_cmd_valid',')system('+','.join('.'+n+'('+n+')'for n in names)+',.qc_cmd_valid')
 tasks='''
function automatic[31:0]pc_crc_word(input[31:0]old,input[31:0]word);
reg[31:0]v;begin v=old^word;for(integer z=0;z<32;z=z+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;pc_crc_word=v;end endfunction
task pc_cmd(input integer restore);begin
 @(negedge clk);cp_restore=restore;cp_valid=1;do @(posedge clk);while(!cp_ready);@(negedge clk);cp_valid=0;
end endtask
task pc_result(input integer expected);reg[35:0]hold;begin
 wait(cp_rsp_valid);@(negedge clk);if(cp_status!=expected)$fatal(1,"real path checkpoint status %0d/%0d",cp_status,expected);
 hold={cp_status,cp_crc};repeat(7)begin @(negedge clk);if(!pc_owned||!cp_rsp_valid||pc_release_ready||{cp_status,cp_crc}!==hold)$fatal(1,"checkpoint held completion/release");end
 $fdisplay(trace,"PCDONE %0d %0d %0d %08h %0d",cycles,pc_checks,cp_status,cp_crc,rc_slots);pc_checks=pc_checks+1;
 cp_rsp_ready=1;@(negedge clk);cp_rsp_ready=0;repeat(2)@(negedge clk);
end endtask
task pc_save(input integer compare);reg[64:0]hold;reg[31:0]crc;begin
 pc_cmd(0);crc=32'hffffffff;
 for(integer x=0;x<78;x=x+1)begin
  wait(cp_m_valid);@(negedge clk);hold={cp_m_last,cp_m_index,cp_m_data};
  repeat(2)begin @(negedge clk);if(!cp_m_valid||{cp_m_last,cp_m_index,cp_m_data}!==hold)$fatal(1,"checkpoint export changed under backpressure");end
  if(cp_m_index!=x||cp_m_last!=(x==77))$fatal(1,"checkpoint export framing");
  if(compare)begin if(cp_m_data!==pc_image[x])$fatal(1,"restored route checkpoint differs word=%0d",x);end else pc_image[x]=cp_m_data;
  crc=pc_crc_word(crc,cp_m_data);cp_m_ready=1;@(negedge clk);cp_m_ready=0;
 end
 pc_result(0);if(cp_crc!==~crc)$fatal(1,"checkpoint export CRC");
 if(!compare)pc_saved_crc=cp_crc;
end endtask
task pc_load(input integer bad);begin
 cp_expected_crc=pc_saved_crc^bad;pc_cmd(1);
 for(integer x=0;x<78;x=x+1)begin
  @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=pc_image[x];cp_s_last=x==77;
  do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;
 end
 pc_result(bad?1:0);
end endtask
task path_checkpoint_roundtrip;begin
 wait(pc_owned);@(negedge clk);pc_acquire_valid=0;
 if(pc_waits<7||rc_slots!=3||k_count!=10||system.controller.last_sequence!=2)$fatal(1,"checkpoint acquired before query completion");
 pc_saved_sequence=system.controller.last_sequence;pc_saved_journal=k_count;pc_saved_descriptor=system.inner.backend.config_restore.descriptor;
 pc_axi_before[0]=g_reads;pc_axi_before[1]=d_reads;pc_axi_before[2]=d_writes;pc_axi_before[3]=p_reads;pc_axi_before[4]=p_writes;pc_axi_before[5]=owner_reads;pc_axi_before[6]=owner_writes;pc_axi_before[7]=cs_reads;pc_axi_before[8]=q_reads;pc_axi_before[9]=t_reads;
 q_cfg_valid=1;g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;host_ctrl_valid=1;host_design_req_valid=1;host_io_valid=1;host_owner_req_valid=1;cc_req_valid=1;expand_valid=1;seed_valid=1;cs_req_valid=1;k_cfg_valid=1;cf_load_valid=1;rc_req_valid=1;qc_cmd_valid=1;k_rec_valid=1;
 pc_save(0);
 @(negedge clk);cp_test_reset=1;repeat(4)@(negedge clk);cp_test_reset=0;repeat(3)@(negedge clk);
 if(rc_slots!=0||cp_busy||k_target_reset||k_cold_rst||rst)$fatal(1,"diagnostic saved-path reset scope");
 $fdisplay(trace,"PCLOSS %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 pc_load(1);if(rc_slots!=0)$fatal(1,"corrupt checkpoint published paths");
 pc_load(0);if(rc_slots!=3)$fatal(1,"valid checkpoint did not restore paths");
 pc_save(1);
 if(system.controller.last_sequence!=pc_saved_sequence||k_count!=pc_saved_journal||system.inner.backend.config_restore.descriptor!==pc_saved_descriptor)$fatal(1,"path reset changed other resident state");
 if(g_reads!=pc_axi_before[0]||d_reads!=pc_axi_before[1]||d_writes!=pc_axi_before[2]||p_reads!=pc_axi_before[3]||p_writes!=pc_axi_before[4]||owner_reads!=pc_axi_before[5]||owner_writes!=pc_axi_before[6]||cs_reads!=pc_axi_before[7]||q_reads!=pc_axi_before[8]||t_reads!=pc_axi_before[9])$fatal(1,"checkpoint issued physical traffic or admitted contender");
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;qc_cmd_valid=0;k_rec_valid=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;
 if(pc_owned||pc_checks!=4||pc_loss_cycles<3||pc_contend_cycles<78)$fatal(1,"checkpoint lease did not retire");
 $fdisplay(trace,"PCEND %0d %0d %0d %0d %0d %0d",cycles,pc_owned_cycles,pc_loss_cycles,k_count,system.controller.last_sequence,pc_contend_cycles);
end endtask
'''
 s=rep(s,'task autonomous_query;begin',tasks+'\ntask autonomous_query;begin')
 s=rep(s,'q_cfg_valid=1;\ng_cfg_valid=1;', 'if(PC_ENABLED&&query_index==1)pc_acquire_valid=1;\nq_cfg_valid=1;\ng_cfg_valid=1;')
 s=rep(s,' autonomous_query;\n for(final_index', ' autonomous_query;\n if(PC_ENABLED&&query_index==1)path_checkpoint_roundtrip;\n for(final_index')
 monitor='''
always @(posedge clk)if(!k_cold_rst)begin
 if(pc_acquire_valid&&!pc_acquire_ready&&!pc_owned)pc_waits<=pc_waits+1;
 if(pc_acquire_valid&&pc_acquire_ready)begin
  if(!f_all_drained||!f_backend_idle||!f_normal_retired||f_phase!=0||qc_busy||ss_busy||rc_busy||f_sv!=0||qc_cmd_valid||rc_req_valid||k_rec_valid)$fatal(1,"checkpoint acquire without retirement");
  $fdisplay(trace,"PCBEGIN %0d %0d %0d %0d",cycles,pc_waits,k_count,system.controller.last_sequence);
 end
 if(pc_owned)begin
  pc_owned_cycles<=pc_owned_cycles+1;
  if(f_sv==16'hffff&&qc_cmd_valid&&rc_req_valid&&k_rec_valid)pc_contend_cycles<=pc_contend_cycles+1;
  if(f_sr!=0||rc_req_ready||qc_cmd_ready||k_rec_ready||system.b_f_sv!=0||system.b_rc_req_valid||system.b_k_rec_valid||system.ss_start_valid)$fatal(1,"checkpoint normal entry leak");
  if(!f_all_drained||!f_normal_retired||!f_backend_idle||f_phase!=0||f_pending!=0||k_target_reset)$fatal(1,"checkpoint backend no longer retired");
 end
 if(system.inner.backend.route_join.cp_reset_held)begin pc_loss_cycles<=pc_loss_cycles+1;$fdisplay(trace,"PCRESET %0d %0d",cycles,rc_slots);end
 if(cp_valid&&cp_ready)$fdisplay(trace,"PCCMD %0d %0d %0d %08h",cycles,pc_checks,cp_restore,cp_expected_crc);
 if(cp_m_valid&&cp_m_ready)$fdisplay(trace,"PCOUT %0d %0d %0d %08h %0d",cycles,pc_checks,cp_m_index,cp_m_data,cp_m_last);
 if(cp_s_valid&&cp_s_ready)$fdisplay(trace,"PCIN %0d %0d %0d %08h %0d",cycles,pc_checks,cp_s_index,cp_s_data,cp_s_last);
end
'''
 s=rep(s,'endmodule',monitor+'\nendmodule')
 return s
if __name__=='__main__':(HERE/'tb_query_lifecycle_join.sv').write_text(make())
