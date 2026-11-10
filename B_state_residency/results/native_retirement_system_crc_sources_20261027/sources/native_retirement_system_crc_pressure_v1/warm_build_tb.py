from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/checkpoint_commit_v6/sources/tb_query_fault.sv')
DECL='''
reg wm_enable=0;wire wm_owned,wm_fault,wm_joined;wire[2:0]wm_receipts;
reg warm_psv=0,warm_plast=0;reg[31:0]warm_pi=0,warm_pd=0;reg[31:0]warm_pcrc,warm_qcrc;
reg warm_running=0;integer warm_fd,warm_rc;string warm_path;reg[31:0]warm_word;reg[31:0]warm_nodes[0:327];reg[159:0]warm_values[0:327];
'''
CLEAR='''q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;'''
TASK='''
task warm_fault_and_restore;begin
 wm_enable=1;as_recover_version=5;as_recover_query=3;recovering=0;replayed=0;injection_seen=0;armed=1;warm_running=1;
 $fdisplay(trace,"WARM_FAULT_START %0d %0d %0d",cycles,k_saved_checkpoint,k_count);
 fault_query;
 CLEAR
 recovering=1;armed=0;injected_abort=0;injected_drift=0;as_inject=0;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);if(k_saved_checkpoint!=18||as_bound_generation!=64'h100000002||!wm_owned||wm_fault||pc_owned)$fatal(1,"warm repair binding");
 $fdisplay(trace,"WARM_OWNER_REPAIRED %0d %0d %0d",cycles,k_corrected,k_count);
 for(integer x=0;x<328;x=x+1)begin
  @(negedge clk);lr_s_valid=1;lr_s_node=warm_nodes[x];lr_s_payload=warm_values[x];lr_s_last=x==327;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(wm_receipts[0]);repeat(12)begin @(negedge clk);if(wm_joined||k_rsp_valid||k_permit||!wm_owned||wm_fault||lr_busy)$fatal(1,"label-only completion admitted work");end
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==77;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||wm_receipts!=1||wm_joined||k_rsp_valid||pc_owned)$fatal(1,"warm path held");end cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=warm_qcrc;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;
 end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);if(qc_cp_status||wm_receipts!=3||wm_joined||k_rsp_valid||pc_owned)$fatal(1,"warm query held");end qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status||k_count||!wm_joined||!wm_owned||wm_fault||recover_open||rc_slots!=1||system.controller.last_sequence!=1||system.controller.last_version!=5)$fatal(1,"warm complete join");end
 $fdisplay(trace,"WARM_COMPLETE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,rc_slots,system.controller.last_sequence);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);if(wm_owned||wm_fault||!k_permit||query_version!=5||p_active_query!=3||p_active_price!=5)$fatal(1,"warm release");
 // Restore only verification cursors, never DUT path/owner state.
 count1=6;count2=0;for(integer x=0;x<6;x=x+1)saved1[x]=cap_path_image[7+x];
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");rc=$fseek(finals_fd,0,0);if(rc)$fatal(1,"final rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;physical_expands=0;metadata_calls=0;visited_reads=0;stopped=0;replayed=1;warm_running=0;
 $fdisplay(trace,"WARM_RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);$fflush(trace);$display("WARM_RESTORE_OBSERVED checkpoint=%0d",k_saved_checkpoint);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(system.wm_rec_accept&&wm_enable)$fdisplay(trace,"WA %0d %0d %0d",cycles,system.wm_on,pc_owned);
 if(system.wm_label_done&&wm_owned)$fdisplay(trace,"WL %0d %0d %0d %0d",cycles,lr_rsp_status,lr_written,lr_verified);
 if(wm_owned&&(wm_fault||qc_cmd_ready||rc_req_ready||pc_acquire_ready))$fatal(1,"warm exclusive owner");
 if(wm_owned&&cap_path_valid&&cap_path_ready)$fdisplay(trace,"WP %0d",cycles);
 if(wm_owned&&cap_path_rsp_valid&&cap_path_rsp_ready)$fdisplay(trace,"WPR %0d %0d %08h",cycles,cap_path_status,cap_path_crc);
 if(wm_owned&&qc_cp_valid&&qc_cp_ready)$fdisplay(trace,"WQ %0d",cycles);
 if(wm_owned&&qc_cp_rsp_valid&&qc_cp_rsp_ready)$fdisplay(trace,"WQR %0d %0d %08h",cycles,qc_cp_status,qc_cp_crc);
end
initial begin
 if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"warm imports");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"warm imports open");
 for(integer x=0;x<328;x=x+1)begin
  warm_rc=$fscanf(warm_fd,"%d",warm_nodes[x]);if(warm_rc!=1)$fatal(1,"warm node");
  for(integer f=0;f<5;f=f+1)begin warm_rc=$fscanf(warm_fd,"%h",warm_word);if(warm_rc!=1)$fatal(1,"warm value");warm_values[x][f*32+:32]=warm_word;end
 end
 $fclose(warm_fd);if(!$value$plusargs("warmpcrc=%h",warm_pcrc)||!$value$plusargs("warmqcrc=%h",warm_qcrc))$fatal(1,"warm crcs");
end
'''.replace(' CLEAR', ' '+CLEAR)
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=BASE.read_text();i=s.index(';',s.index('module '))+1;s=s[:i]+DECL+s[i:]
 s=rep(s,'.ENABLE_TEST_INJECTION(DIAG_ENABLED))system(','.ENABLE_TEST_INJECTION(DIAG_ENABLED),.ENABLE_WARM_RECOVERY(1))system(.wm_enable(wm_enable),.wm_source_version(32\'d4),.wm_source_query(2\'d2),.wm_source_price(4\'d4),.wm_path_crc(warm_pcrc),.wm_query_crc(warm_qcrc),.wm_owned(wm_owned),.wm_fault(wm_fault),.wm_joined(wm_joined),.wm_receipts(wm_receipts),')
 for port,old,new in [('cp_s_valid',"1'b0",'warm_psv'),('cp_s_last',"1'b0",'warm_plast'),('cp_s_index',"32'd0",'warm_pi'),('cp_s_data',"32'd0",'warm_pd'),('cp_expected_crc',"32'd0",'warm_pcrc'),('recover_checkpoint',"32'd17","wm_enable?32'd18:32'd17"),('snapshot_checkpoint',"32'd17","wm_enable?32'd18:32'd17")]:s=rep(s,f'.{port}({old})',f'.{port}({new})')
 # New context does not alter numeric prices/cost inputs: retain independent CPU oracle.
 s=rep(s,'query_index=1;selected_sink=128009;selected_connection=16497;selected_sequence=2;stopped=0;\n autonomous_query;', 'query_index=1;selected_sink=128009;selected_connection=16497;selected_sequence=2;stopped=0;\n warm_fault_and_restore;\n autonomous_query;')
 s=s.replace('joint_watch>600000','joint_watch>1800000')
 return s.replace('endmodule',TASK+'\nendmodule')
if __name__=='__main__':(HERE/'tb_warm.sv').write_text(make())
