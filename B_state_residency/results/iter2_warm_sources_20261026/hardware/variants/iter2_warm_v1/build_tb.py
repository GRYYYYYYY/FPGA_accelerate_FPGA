from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/iter2_lifecycle_full_v5/sources/tb_query_fault.sv')
def make():
 s=BASE.read_text().replace('.ENABLE_WARM_RECOVERY(1))system(','.ENABLE_WARM_RECOVERY(1),.RESTORE_RECORDS(1024))system(')
 s=s.replace('.wm_source_version(32\'d4),.wm_source_query(2\'d2),.wm_source_price(4\'d4)',".wm_source_version(32'd3),.wm_source_query(2'd1),.wm_source_price(4'd3)")
 s=s.replace(".recover_checkpoint(wm_enable?32'd18:32'd17)",".recover_checkpoint(32'd17)").replace(".snapshot_checkpoint(wm_enable?32'd18:32'd17)",".snapshot_checkpoint(32'd17)")
 s=s.replace(".snapshot_count(32'd328)",".snapshot_count(32'd822)").replace(".snapshot_probe(32'd150697)",".snapshot_probe(32'd204279)")
 marker="ap_get(558358,23916,64'h100000001,0,1,2);"
 assert s.count(marker)==1;s=s.replace(marker,marker+'\n iter2_capture_initial;')
 marker=' query_index=0;replayed=1;armed=0;\n autonomous_query;'
 assert s.count(marker)==1;s=s.replace(marker,''' query_index=0;replayed=0;armed=1;fault_case=5;wm_enable=1;warm_fault_node=558358;
 fault_query;
 iter2_warm_restore;
 autonomous_query;''')
 s=s.replace('system.controller.last_version!=3||p_active_query!=1||p_active_price!=3','system.controller.last_version!=4||p_active_query!=2||p_active_price!=4')
 # Duplicate-command check belongs to the new storage attempt after recovery.
 s=s.replace("qc_cmd_query=1;qc_cmd_price=3;", "qc_cmd_query=2;qc_cmd_price=4;")
 s=s.replace("qc_cmd_expand={32'd3,32'd291", "qc_cmd_expand={32'd4,32'd291")
 s=s.replace('ITER2_LIFECYCLE_PASS','ITER2_WARM_PASS')
 extra='''task iter2_capture_initial;begin
 qc_cp_generation=64'h100000001;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"initial query capture boundary");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 wait(qc_cp_rsp_valid);@(negedge clk);if(qc_cp_status)$fatal(1,"initial query capture status");warm_qcrc=qc_cp_crc;qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==77))$fatal(1,"initial path capture boundary");cap_path_image[x]=cap_path_m_data;cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"initial path status");warm_pcrc=cap_path_crc;cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 $fdisplay(trace,"ITER2_INITIAL_CAPTURE %0d %08h %08h %0d %0d",cycles,warm_pcrc,warm_qcrc,rc_slots,system.controller.last_sequence);
end endtask

task iter2_warm_restore;begin
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;host_ctrl_valid=0;host_design_req_valid=0;host_io_valid=0;host_owner_req_valid=0;cc_req_valid=0;expand_valid=0;seed_valid=0;cs_req_valid=0;k_cfg_valid=0;cf_load_valid=0;rc_req_valid=0;
 recovering=1;armed=0;as_recover_version=4;as_recover_query=2;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(k_labels_valid);@(negedge clk);if(k_count!=2||k_corrected!=2||!wm_owned||wm_fault||as_bound_generation!=64'h100000001)$fatal(1,"iter2 warm owner repair");
 $fdisplay(trace,"ITER2_OWNER_REPAIRED %0d %0d %0d",cycles,k_corrected,k_count);
 rc=$fseek(imports_fd,0,0);if(rc)$fatal(1,"iter2 label rewind");
 for(integer x=0;x<822;x=x+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"warm import node");
  for(integer f=0;f<5;f=f+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"warm import field");import_record[f*32+:32]=word;end
  @(negedge clk);lr_s_valid=1;lr_s_node=import_node;lr_s_payload=import_record;lr_s_last=x==821;do @(posedge clk);while(!lr_s_ready);@(negedge clk);lr_s_valid=0;
 end
 wait(wm_receipts[0]);if(lr_written!=822||lr_verified!=822||wm_joined||k_rsp_valid)$fatal(1,"iter2 label receipt");
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==77;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||wm_receipts!=1||wm_joined||k_rsp_valid)$fatal(1,"iter2 path held");end cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 qc_cp_restore=1;qc_cp_expected_crc=warm_qcrc;qc_cp_valid=1;do @(posedge clk);while(!qc_cp_ready);@(negedge clk);qc_cp_valid=0;
 for(integer x=0;x<10;x=x+1)begin @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];qc_cp_s_last=x==9;qc_cp_s_valid=1;do @(posedge clk);while(!qc_cp_s_ready);@(negedge clk);qc_cp_s_valid=0;end
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);if(qc_cp_status||wm_receipts!=3||wm_joined||k_rsp_valid)$fatal(1,"iter2 query held");end qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status||k_count||!wm_owned||!wm_joined||wm_fault||recover_open)$fatal(1,"iter2 warm complete");end
 $fdisplay(trace,"ITER2_WARM_COMPLETE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,rc_slots,system.controller.last_sequence);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);
 if(wm_owned||query_version!=4||p_active_query!=2||p_active_price!=4||rc_slots)$fatal(1,"iter2 warm release");
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count1=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;replayed=1;
 $fdisplay(trace,"ITER2_RETRY %0d %0d %0d",cycles,restore_epoch,restore_version);
end endtask
'''
 s=s.replace('endmodule',extra+'endmodule');return s
if __name__=='__main__':(HERE/'tb_warm.sv').write_text(make())
