"""Three-slot full hierarchy: preserve G3 source, register/ripup q3, execute q3."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=Path('/tmp/B_state_residency_offer_20261025/owner_g3_retired_full_v3/sources/tb_query_fault.sv')

TASK=r'''
task third_path_snapshot(input bit capture);begin
 cap_path_restore=0;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<117;x=x+1)begin
  wait(cap_path_m_valid);@(negedge clk);if(cap_path_m_index!=x||cap_path_m_last!=(x==116))$fatal(1,"third snapshot framing");
  cap_path_image[x]=cap_path_m_data;$fdisplay(trace,"THIRD_PATH_WORD %0d %0d %0d %08h",cycles,capture,x,cap_path_m_data);
  cap_path_m_ready=1;@(negedge clk);cap_path_m_ready=0;
 end
 wait(cap_path_rsp_valid);@(negedge clk);if(cap_path_status)$fatal(1,"third snapshot status");
 $fdisplay(trace,"THIRD_PATH_DONE %0d %0d %08h %0d",cycles,capture,cap_path_crc,rc_slots);
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
end endtask
task third_query;begin
 $fdisplay(trace,"THIRD_BEGIN %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 third_path_snapshot(0);
 if(rc_slots!=3||cap_path_image[78]!=0||k_count)$fatal(1,"third initial paths");
 cap_path_image[78]=1;cap_path_image[79]=3;cap_path_image[80]=26422;cap_path_image[81]=66893;cap_path_image[82]=151354;
 cap_path_image[83]=design_id[31:0];cap_path_image[84]=design_id[63:32];cap_path_image[85]=990179;cap_path_image[86]=558358;cap_path_image[87]=265324;
 prep_crc=32'hffffffff;for(integer x=0;x<117;x=x+1)prep_crc=prep_crc_word(prep_crc,cap_path_image[x]);warm_pcrc=~prep_crc;
 cap_path_restore=1;cap_path_valid=1;do @(posedge clk);while(!cap_path_ready);@(negedge clk);cap_path_valid=0;
 for(integer x=0;x<117;x=x+1)begin
  @(negedge clk);warm_pi=x;warm_pd=cap_path_image[x];warm_plast=x==116;warm_psv=1;do @(posedge clk);while(!system.cp_s_ready);@(negedge clk);warm_psv=0;
  $fdisplay(trace,"THIRD_PATH_IMPORT %0d %08h",x,cap_path_image[x]);
 end
 wait(cap_path_rsp_valid);repeat(8)begin @(negedge clk);if(cap_path_status||cap_path_crc!=warm_pcrc||rc_slots!=7||k_count||!pc_owned)$fatal(1,"third metadata registration");end
 cap_path_rsp_ready=1;@(negedge clk);cap_path_rsp_ready=0;
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 stage_no=6;owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);
 route_command(1,2,151354,180329);
 owner_op(0,990179,1,2);owner_op(0,558358,3,2);owner_op(0,265324,4,1);owner_op(0,339193,1,1);iter2_foreign_probe;
 if(rc_slots!=3||system.controller.last_sequence!=180328||k_saved_checkpoint!=19||k_count!=3||fault||rc_fault||k_fault)$fatal(1,"third preparation continuity");
 $fdisplay(trace,"THIRD_PREPARED %0d %0d %0d %0d",cycles,rc_slots,k_count,system.controller.last_sequence);
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost3=%s",path))$fatal(1,"cost3");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates3=%s",path))$fatal(1,"candidates3");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls3=%s",path))$fatal(1,"polls3");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals3=%s",path))$fatal(1,"finals3");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"third oracle files");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=2;selected_sink=151354;selected_connection=170785;selected_sequence=180329;stopped=0;armed=0;replayed=1;warm_running=0;
 autonomous_query;
 if(commits!=302||candidate_i!=565||expand_i!=113||poll_i!=114||rc_slots!=7||system.controller.last_sequence!=180329||query_version!=5||p_active_query!=3||p_active_price!=5||k_count!=3||k_saved_checkpoint!=19)$fatal(1,"third aggregate/context");
 owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
 control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 third_path_snapshot(1);
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"third query export");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if(qcp_image[8]!=180329||qcp_image[6]!=5||qcp_image[7]!=32'h57)$fatal(1,"third ledger floor");
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"THIRD_PASS %0d %0d %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits,rc_slots,system.controller.last_sequence);
 $display("THIRD_QUERY_PASS polls=114 expands=113 candidates=565 costs=302");
end endtask
'''

def make():
 s=BASE.read_text()
 s=s.replace('reg qc_cmd_slot=0;', 'reg[1:0]qc_cmd_slot=0;')
 s=s.replace('rc_req_op=0,rc_req_slot=0,rc_rsp_ready=0;', 'rc_req_op=0,rc_rsp_ready=0;reg[1:0]rc_req_slot=0;')
 s=s.replace('wire[1:0]rc_slots;', 'wire[2:0]rc_slots;').replace('reg[1:0]qcp_slots;', 'reg[2:0]qcp_slots;')
 s=s.replace("assign f_route_payload={30'd0,", "assign f_route_payload={29'd0,")
 s=s.replace('query_residency_system #(', 'query_residency_system #(.PATH_SLOTS(3),',1)
 s=s.replace('export_manifest g3_exports(', 'export_manifest #(.PATH_SLOTS(3)) g3_exports(',1)
 s=s.replace('cap_path_image[0:77]', 'cap_path_image[0:116]').replace('x<78;', 'x<117;').replace('x==77', 'x==116')
 s=s.replace('ss_candidates!=(query_index==0?849:564)', 'ss_candidates!=(query_index==0?849:(query_index==1?564:565))')
 s=s.replace('cycles>3000000', 'cycles>4000000')
 assert s.count('\n publish_g3;\n')==1
 s=s.replace('\n publish_g3;\n', '\n publish_g3;\n third_query;\n',1)
 s=s.replace('\nendmodule', TASK+'\nendmodule',1)
 return s

if __name__=='__main__':(HERE/'tb_third.sv').write_text(make())
