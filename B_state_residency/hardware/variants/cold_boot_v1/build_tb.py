from pathlib import Path
BASE=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3/sources')
HERE=Path(__file__).parent
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=(BASE/'tb_query_fault.sv').read_text()
 s=rep(s,'reg[1:0]restore_epoch=1;reg[31:0]restore_version=3;', 'reg[1:0]restore_epoch=2;reg[31:0]restore_version=4;')
 s=rep(s,'k_checkpoint=17,k_cfg_version=3;reg[1:0]k_cfg_query=1;reg[3:0]k_cfg_price=3;', 'k_checkpoint=18,k_cfg_version=4;reg[1:0]k_cfg_query=2;reg[3:0]k_cfg_price=4;')
 s=s.replace("64'h100000001","64'h100000002").replace('.as_cfg_checkpoint(32\'d17)',".as_cfg_checkpoint(32'd18)")
 at=s.index('initial begin\n trace=$fopen');pre=s[:at];old=s[at:]
 end=old.index(' if(!$value$plusargs("faultcase=')
 main=old[:end]
 main=main.replace('cs_cfg_version=3;', 'cs_cfg_version=4;')
 main=main.replace(' as_fault_mode=$value$plusargs', ''' if(cf_input!==boot_descriptor)$fatal(1,"effective config differs from bundle");
 @(negedge clk);boot_cfg_valid=1;do @(posedge clk);while(!boot_cfg_ready);@(negedge clk);boot_cfg_valid=0;
 as_fault_mode=$value$plusargs''')
 # Bundle logical labels are restored through real IO; never load old physical directory.
 main=main.replace(' control(1);',''' control(1);
 $fdisplay(trace,"BOOT_STAGE labels_written %0d",cycles);$fflush(trace);
 @(negedge clk);boot_verify_valid=1;do @(posedge clk);while(!boot_verify_ready);@(negedge clk);boot_verify_valid=0;
 rc=$rewind(imports_fd);
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);import_record[field_i*32+:32]=word;end
  label_read(import_node);if(host_record!==import_record)$fatal(1,"cold label mismatch %0d",import_node);
 end
 if(boot_verified_count!=328||boot_verify_status||!boot_receipts[2])$fatal(1,"cold label receipt %h %0d %0d",boot_receipts,boot_verified_count,boot_verify_status);
 $fdisplay(trace,"BOOT_STAGE labels_verified %0d %h",cycles,boot_receipts);$fflush(trace);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 $readmemh("paths.hex",cap_path_image);cap_path_restore=1;cap_path_valid=1;
 do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<78;x=x+1)begin
  @(negedge clk);boot_path_s_valid=1;boot_path_index=x;boot_path_data=cap_path_image[x];boot_path_last=x==77;
  do @(posedge clk);while(!boot_path_s_ready);@(negedge clk);boot_path_s_valid=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status||cap_path_crc!=boot_path_crc)$fatal(1,"cold path restore");cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 wait(!cap_path_busy);$readmemh("query.hex",qcp_image);qc_cp_expected_crc=boot_query_crc;qcp_load(0);
 $fdisplay(trace,"BOOT_STAGE imports %0d %h",cycles,boot_receipts);$fflush(trace);
 wait(boot_rsp_valid);@(negedge clk);
 pc_release_valid=1;
 repeat(8)begin @(negedge clk);if(!boot_pending||boot_status||pc_release_ready||qc_cmd_ready||rc_req_ready||f_sr!=0)$fatal(1,"cold completion escaped");end
 pc_release_valid=0;boot_rsp_ready=1;@(negedge clk);boot_rsp_ready=0;
 if(boot_pending)$fatal(1,"cold gate still pending");pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;
 // A valid old-sequence command in the free slot must reach native rejection.
 qc_cmd_slot=1;qc_cmd_cookie=32'hce000001;qc_cmd_source=65185;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;qc_cmd_design=design_id;qc_cmd_query=restore_epoch;qc_cmd_price=restore_version[3:0];
 qc_cmd_expand={restore_version,32'd295,32'd283,32'd46,32'd38,32'd260,32'd1,32'd2717,selected_sink,32'd0,32'd0,32'd0,32'd100,selected_connection};
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);@(negedge clk);if(qc_rsp_status!=1||qc_prepare_acked||qc_rsp_committed||qc_rsp_acked)$fatal(1,"cold stale sequence accepted");
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;
 // Continue from the restored first branch using the existing independent q2 oracle.
 count1=6;for(integer x=0;x<6;x=x+1)saved1[x]=cap_path_image[7+x];stage_no=0;probe_owners;
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost2=%s",path))$fatal(1,"cost2");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates2=%s",path))$fatal(1,"candidates2");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls2=%s",path))$fatal(1,"polls2");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals2=%s",path))$fatal(1,"finals2");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"q2 oracle open");
 query_index=1;selected_sink=128009;selected_connection=16497;selected_sequence=2;stopped=0;
 autonomous_query;
 for(final_index=0;final_index<328;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end
  if(final_node_id==selected_sink)gold_final[159:128]=0;
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"q2 final label %0d",final_node_id);
 end
 stage_no=1;probe_owners;
 stage_no=2;route_command(1,0,150697,1);probe_owners;
 stage_no=3;route_command(1,1,128009,2);probe_owners;
 if(rc_slots!=0||count1!=6||count2!=6||rc_fault||poll_i!=43||expand_i!=42||candidate_i!=176)$fatal(1,"cold q2 final totals");
 control(1);control(2);wait(f_normal_retired&&f_backend_idle&&f_all_drained&&f_phase==0);
 $fdisplay(trace,"COLD_Q2_PASS %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i);
 $fdisplay(trace,"COLD_BOOT_PASS cycles=%0d receipts=%h config=%h labels=%0d",cycles,boot_receipts,boot_config_receipts,boot_verified_count);$fflush(trace);
 $display("COLD_BOOT_PASS cycles=%0d labels=%0d",cycles,boot_verified_count);$finish;
end
endmodule
''')
 s=pre+main
 extra='''reg boot_cfg_valid=0,boot_verify_valid=0,boot_rsp_ready=0;
wire boot_cfg_ready,boot_verify_ready,boot_pending,boot_rsp_valid;wire[3:0]boot_status,boot_verify_status;
wire[4:0]boot_receipts;wire[7:0]boot_config_receipts;wire[31:0]boot_verified_count;
reg[31:0]boot_label_crc=0,boot_path_crc=0,boot_query_crc=0;
reg[31:0]boot_words[0:71];wire[2303:0]boot_descriptor;
generate for(genvar b=0;b<72;b=b+1)begin assign boot_descriptor[b*32+:32]=boot_words[b];end endgenerate
initial $readmemh("config_effective.hex",boot_words);
reg boot_path_s_valid=0,boot_path_last=0;reg[31:0]boot_path_index=0,boot_path_data=0;wire boot_path_s_ready;
initial begin
 if(!$value$plusargs("labelcrc=%h",boot_label_crc)||!$value$plusargs("pathcrc=%h",boot_path_crc)||!$value$plusargs("querycrc=%h",boot_query_crc))$fatal(1,"boot CRC arguments");
end
always @(posedge clk)if(!k_cold_rst&&boot_pending)begin
 if(qc_prepared_event||system.b_rc_req_valid||system.b_k_rec_valid)$fatal(1,"business escaped bootstrap");
end
'''
 idx=s.index('query_residency_system #');s=s[:idx]+extra+s[idx:]
 s=rep(s,')system(.cp_ready', ''')system(.boot_required(1'b1),.boot_cfg_valid(boot_cfg_valid),.boot_cfg_ready(boot_cfg_ready),.boot_design(design_id),.boot_generation(64'h100000002),.boot_checkpoint(32'd18),.boot_version(32'd4),.boot_nodes(32'd9089009),.boot_label_count(32'd328),.boot_label_crc(boot_label_crc),.boot_path_crc(boot_path_crc),.boot_query_crc(boot_query_crc),.boot_query(2'd2),.boot_slots(2'd1),.boot_price(4'd4),.boot_payload(boot_descriptor),.boot_pending(boot_pending),.boot_rsp_valid(boot_rsp_valid),.boot_rsp_ready(boot_rsp_ready),.boot_status(boot_status),.boot_verify_valid(boot_verify_valid),.boot_verify_ready(boot_verify_ready),.boot_verified_count(boot_verified_count),.boot_verify_status(boot_verify_status),.boot_receipts(boot_receipts),.boot_config_receipts(boot_config_receipts),.cp_ready''')
 s=rep(s,".cp_s_valid(1'b0),.cp_s_last(1'b0)",'.cp_s_valid(boot_path_s_valid),.cp_s_ready(boot_path_s_ready),.cp_s_last(boot_path_last)')
 s=rep(s,".cp_expected_crc(32'd0),.cp_s_index(32'd0),.cp_s_data(32'd0)",'.cp_expected_crc(boot_path_crc),.cp_s_index(boot_path_index),.cp_s_data(boot_path_data)')
 return s
if __name__=='__main__':(HERE/'tb_cold_boot.sv').write_text(make())
