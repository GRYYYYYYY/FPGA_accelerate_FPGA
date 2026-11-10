task fourth_path_snapshot(input integer capture);begin
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==155))$fatal(1,"fourth snapshot framing");
  cap_path_image[x]=cap_path_m_data;$fdisplay(trace,"FOURTH_PATH_WORD %0d %0d %0d %08h",cycles,capture,x,cap_path_m_data);
  cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"fourth snapshot status");
 $fdisplay(trace,"FOURTH_PATH_DONE %0d %0d %08h %0d",cycles,capture,cap_path_crc,rc_slots);
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
end endtask

task fourth_query;begin
 $fdisplay(trace,"FOURTH_BEGIN %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 fourth_path_snapshot(0);
 if(rc_slots!=7||cap_path_image[117]!=0||k_count||k_saved_checkpoint!=20)$fatal(1,"fourth initial paths");
 cap_path_image[117]=1;cap_path_image[118]=3;cap_path_image[119]=26422;cap_path_image[120]=66893;cap_path_image[121]=6954;
 cap_path_image[122]=design_id[31:0];cap_path_image[123]=design_id[63:32];cap_path_image[124]=990178;cap_path_image[125]=558358;cap_path_image[126]=265324;
 prep_crc=32'hffffffff;for(integer x=0;x<156;x=x+1)prep_crc=prep_crc_word(prep_crc,cap_path_image[x]);warm_pcrc=~prep_crc;
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<156;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==155;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"FOURTH_PATH_IMPORT %0d %08h",x,cap_path_image[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_crc!=warm_pcrc||rc_slots!=15||k_count||!pc_owned)$fatal(1,"fourth metadata registration");end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 stage_no=7;owner_op(0,990178,1,1);owner_op(0,558358,4,2);owner_op(0,265324,5,1);
 route_command(1,3,6954,180330);
 owner_op(0,990178,0,0);owner_op(0,558358,3,2);owner_op(0,265324,4,1);owner_op(0,339193,1,1);owner_op(0,990179,2,2);iter2_foreign_probe;
 if(rc_slots!=7||system.controller.last_sequence!=180329||k_saved_checkpoint!=20||k_count!=3||fault||rc_fault||k_fault)$fatal(1,"fourth preparation continuity");
 $fdisplay(trace,"FOURTH_PREPARED %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost4=%s",path))$fatal(1,"cost4");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates4=%s",path))$fatal(1,"candidates4");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls4=%s",path))$fatal(1,"polls4");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals4=%s",path))$fatal(1,"finals4");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"fourth oracle files");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=3;selected_sink=6954;selected_connection=170791;selected_sequence=180330;stopped=0;armed=0;replayed=1;warm_running=0;
 autonomous_query;
 if(commits!=231||candidate_i!=402||expand_i!=82||poll_i!=83||rc_slots!=15||system.controller.last_sequence!=180330||query_version!=6||p_active_query!=0||p_active_price!=6||k_count!=3||k_saved_checkpoint!=20)$fatal(1,"fourth aggregate/context");
 owner_op(0,990178,1,1);owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 fourth_path_snapshot(1);
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"fourth query export");qcp_image[x]=qc_cp_m_data;
  $fdisplay(trace,"FOURTH_QUERY_WORD %0d %0d %08h",cycles,x,qc_cp_m_data);qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if(qcp_image[8]!=180330||qcp_image[6]!=6||qcp_image[7]!=32'h58||{qcp_image[5],qcp_image[4]}!=64'h100000004)$fatal(1,"fourth ledger floor");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"FOURTH_PASS %0d %0d %0d %0d %0d %0d %0d %08h",cycles,poll_i,expand_i,candidate_i,commits,rc_slots,system.controller.last_sequence,qc_cp_crc);
 $display("FOURTH_PASS polls=83 expands=82 candidates=402 costs=231");
end endtask
