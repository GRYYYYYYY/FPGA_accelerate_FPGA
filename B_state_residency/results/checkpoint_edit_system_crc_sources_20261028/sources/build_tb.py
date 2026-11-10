from pathlib import Path
import runpy
HOST=[('input', 1, 'jp_start'), ('output', 1, 'jp_start_ready'), ('input', 1, 'jp_commit'), ('output', 1, 'jp_commit_ready'), ('input', 1, 'jp_cancel'), ('output', 1, 'jp_cancel_ready'), ('output', 1, 'jp_owned'), ('output', 1, 'jp_done'), ('input', 1, 'jp_done_ready'), ('output', 2, 'jp_result'), ('input', 1, 'jp_manifest_ready'), ('input', 64, 'jp_generation'), ('input', 64, 'jp_design'), ('input', 32, 'jp_checkpoint'), ('input', 32, 'jp_version'), ('input', 2, 'jp_query'), ('input', 4, 'jp_price'), ('input', 2, 'jp_load'), ('input', 2, 'jp_ack'), ('output', 2, 'jp_ready'), ('output', 2, 'jp_reply'), ('output', 2, 'jp_status'), ('input', 1, 'jp_authority_stage')]
HERE=Path(__file__).parent
TASK='''
reg ap_valid=0,ap_rsp_ready=0;wire ap_ready,ap_rsp_valid;wire[3:0]ap_status;wire[31:0]ap_refs,ap_occ,ap_rsp_cookie,ap_rsp_checkpoint;wire[63:0]ap_rsp_generation,ap_rsp_design;
reg[31:0]ap_node=0,ap_net=0,ap_cookie=0;reg[63:0]ap_generation=64'h100000002;
reg jp_start=0,jp_commit=0,jp_cancel=0,jp_done_ready=0,jp_authority_stage=0;integer joint_pulses=0,joint_watch=0;reg joint_started=0;
reg[1:0]jp_load=0,jp_ack=0;
wire jp_start_ready,jp_commit_ready,jp_cancel_ready,jp_owned,jp_done;
wire[1:0]jp_result,jp_ready,jp_reply,jp_status;
task joint_cancel_check;reg[1:0]accepted;begin
 if(!pc_owned||k_count!=6||k_saved_checkpoint!=17)$fatal(1,"joint baseline");
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 if(!jp_owned)$fatal(1,"joint ownership");
 @(negedge clk);jp_load=3;
 while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=6||k_saved_checkpoint!=17)$fatal(1,"held stage reply");end
 jp_ack=3;@(negedge clk);jp_ack=0;
 wait(system.jp_prepared==3);
 if(k_permit||pc_release_ready||!pc_owned||system.jp_commit_ready)$fatal(1,"stage admission");
 // Native stream request must remain unaccepted while metadata transaction owns lease.
 cap_path_valid=1;qc_cp_valid=1;
 repeat(8)begin @(negedge clk);if(cap_path_ready||qc_cp_ready||cap_path_busy||qc_cp_busy)$fatal(1,"stream overlap accepted");end
 cap_path_valid=0;qc_cp_valid=0;
 jp_cancel=1;do @(posedge clk);while(!jp_cancel_ready);@(negedge clk);jp_cancel=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result!=2||pc_release_ready||k_count!=6||k_saved_checkpoint!=17||system.jp_prepared||system.as_bound_generation!=64'h100000001)$fatal(1,"cancel did not preserve state");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;
 wait(!jp_owned);if(!k_permit||!system.pc_safe)$fatal(1,"cancel work permission not restored");
 $fdisplay(trace,"JOINT_SYSTEM_CANCEL %0d %0d %0d",cycles,k_count,k_saved_checkpoint);
 $display("JOINT_SYSTEM_CANCEL_PASS journal=%0d checkpoint=%0d",k_count,k_saved_checkpoint);
end endtask
'''
def make(s):
 ties=''
 for d,w,n in HOST:
  if n in ['jp_start','jp_commit','jp_cancel','jp_done_ready','jp_load','jp_ack','jp_start_ready','jp_commit_ready','jp_cancel_ready','jp_owned','jp_done','jp_result','jp_ready','jp_reply','jp_status','jp_authority_stage']:v=n
  else:v={'jp_design':'design_id','jp_checkpoint':"32'd18",'jp_generation':"64'h100000002",'jp_version':'query_version','jp_query':'p_active_query','jp_price':'p_active_price','jp_manifest_ready':"1'b1",'jp_authority_stage':"1'b0"}[n]
  ties+=f'.{n}({v}),'
 needle=')system(.cp_ready';assert s.count(needle)==1;s=s.replace(needle,')system('+ties+'.cp_ready')
 needle=' // Reject decreasing generation; capture the later transaction from its handshake.';assert s.count(needle)==1;s=s.replace(needle,' joint_cancel_check;\n'+needle)
 s=patch_commit(s)
 s=s.replace('.cp_ready(cap_path_ready)', ''.join(f'.{n}({n}),'for n in ['ap_valid','ap_ready','ap_rsp_valid','ap_rsp_ready','ap_status','ap_refs','ap_occ','ap_rsp_cookie','ap_rsp_checkpoint','ap_rsp_generation','ap_rsp_design','ap_node','ap_net','ap_cookie','ap_generation'])+".ap_design(design_id),.ap_checkpoint(32'd18),.cp_ready(cap_path_ready)")
 at=s.index(';',s.index('module '))+1
 decl,task=TASK.split('task joint_cancel_check',1)
 return (s[:at]+decl+s[at:]).replace('endmodule','task joint_cancel_check'+task+OBSERVE+'\nendmodule')

OBSERVE="""
always @(posedge clk)if(!rst&&!k_cold_rst)begin
 if(joint_started)begin joint_watch=joint_watch+1;if(joint_watch>600000)$fatal(1,"joint watchdog state=%0d cp=%0d j=%0d prepared=%b ready=%b lease=%b",system.publication.state,k_saved_checkpoint,k_count,{system.jp_prepared,system.jp_ap},{system.jp_pubready,system.jp_apr},pc_owned);end
 if(jp_start&&jp_start_ready)$fdisplay(trace,"JS %0d %0d %0d %0d %0d %0d",cycles,k_saved_checkpoint,k_count,query_version,system.jp_cver,pc_owned);
 if(system.jp_prepare&&system.jp_load[0]&&system.inner.backend.jp_kr)$fdisplay(trace,"JK %0d %0d %0d",cycles,system.jp_checkpoint,system.jp_version);
 if(system.jp_prepare&&system.jp_load[1]&&system.inner.backend.jp_cr)$fdisplay(trace,"JC %0d %0d %0d",cycles,system.jp_checkpoint,system.jp_version);
 if(jp_reply[0]&&jp_ack[0])$fdisplay(trace,"JKR %0d %0d %0d %0d",cycles,jp_status[0],k_saved_checkpoint,k_count);
 if(jp_reply[1]&&jp_ack[1])$fdisplay(trace,"JCR %0d %0d %0d",cycles,jp_status[1],system.jp_ccp);
 if(jp_cancel&&jp_cancel_ready)$fdisplay(trace,"JX %0d %0d",cycles,system.jp_prepared);
 if(|system.jp_dv)$fdisplay(trace,"JD %0d %0d %0d",cycles,system.jp_dv,{system.jp_dropready,system.jp_adr});
 if(|system.jp_pv)begin joint_pulses=joint_pulses+1;$fdisplay(trace,"JP %0d %0d %0d %0d %0d %016h",cycles,system.jp_pv,k_saved_checkpoint,system.jp_ccp,k_count,as_bound_generation);end
 if(authority_bind&&as_cfg_ready)$fdisplay(trace,"JAS %0d %0d %016h %0d",cycles,jp_authority_stage,system.as_cfg_generation,system.as_cfg_checkpoint);
 if(as_cfg_rsp_valid&&authority_ack)$fdisplay(trace,"JAR %0d %0d %016h",cycles,as_cfg_status,as_bound_generation);
 if(jp_done&&jp_done_ready)$fdisplay(trace,"JE %0d %0d %0d %0d %0d %0d",cycles,jp_result,k_saved_checkpoint,k_count,system.jp_ccp,pc_owned);
 if(jp_owned&&(!pc_owned||pc_release_ready))$fatal(1,"unexpected publication or lost lease in cancel case");
end
"""

COMMIT_TASK="""
task joint_commit_check;reg[1:0]accepted;begin
 joint_started=1;
 @(negedge clk);jp_start=1;do @(posedge clk);while(!jp_start_ready);@(negedge clk);jp_start=0;
 jp_authority_stage=1;authority_bind=1;do @(posedge clk);while(!as_cfg_ready);@(negedge clk);authority_bind=0;
 wait(as_cfg_rsp_valid);repeat(8)begin @(negedge clk);if(as_cfg_status||system.jp_ap||as_bound_generation!=64'h100000001||k_count!=6||pc_release_ready)$fatal(1,"held authority candidate");end
 authority_ack=1;@(negedge clk);authority_ack=0;wait(system.jp_ap);
 jp_load=3;while(jp_load!=0)begin @(posedge clk);accepted=jp_load&jp_ready;@(negedge clk);jp_load=jp_load&~accepted;end
 wait(jp_reply==3);repeat(8)begin @(negedge clk);if(jp_status||pc_release_ready||system.jp_prepared||k_count!=6||k_saved_checkpoint!=17)$fatal(1,"held commit stage reply");end
 jp_ack=3;@(negedge clk);jp_ack=0;wait(system.jp_prepared==3);
 if(as_bound_generation!=64'h100000001||k_count!=6||k_saved_checkpoint!=17||system.jp_ccp!=17)$fatal(1,"prepared metadata changed baseline");
 jp_commit=1;do @(posedge clk);while(!jp_commit_ready);@(negedge clk);jp_commit=0;
 wait(jp_done);repeat(8)begin @(negedge clk);if(jp_result||pc_release_ready||k_count||k_saved_checkpoint!=18||system.jp_ccp!=18||as_bound_generation!=64'h100000002||joint_pulses!=1)$fatal(1,"joint publication mismatch");end
 jp_done_ready=1;@(negedge clk);jp_done_ready=0;wait(!jp_owned);jp_authority_stage=0;
 if(!k_permit||!system.pc_safe||rc_slots!=1||system.controller.last_sequence!=1)$fatal(1,"publication lost working state");
 ap_get(0,4754,64'h100000001,1,0,0);
 for(integer x=0;x<6;x=x+1)ap_get(cap_path_image[7+x],2717,64'h100000002,0,1,1);
 ap_get(0,4754,64'h100000002,0,1,1);
 // Old-generation ledger cannot be imported under newly active authority.
 qc_cp_expected_crc=qc_cp_crc;qcp_load(1);if(!qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"stale ledger accepted");
 qc_cp_generation=0;qcp_start(0);
 for(integer x=0;x<10;x=x+1)begin
  wait(qc_cp_m_valid);@(negedge clk);if(qc_cp_m_index!=x||qc_cp_m_last!=(x==9))$fatal(1,"new ledger boundary");qcp_image[x]=qc_cp_m_data;qc_cp_m_ready=1;@(negedge clk);qc_cp_m_ready=0;
 end
 qcp_result(0);if({qcp_image[5],qcp_image[4]}!=64'h100000002||qcp_image[8]!=1)$fatal(1,"new ledger identity");
 qc_cp_expected_crc=qc_cp_crc;qcp_load(0);if(qc_restore_pending||system.controller.last_sequence!=1)$fatal(1,"new ledger restore");
 @(negedge clk);pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 $fdisplay(trace,"JOINT_SYSTEM_COMMIT %0d %0d %0d %016h",cycles,k_saved_checkpoint,k_count,as_bound_generation);$fflush(trace);$display("JOINT_PUBLICATION_OBSERVED checkpoint=%0d",k_saved_checkpoint);
"""
COMMIT_TASK+=' // Continue from the restored first branch using the existing independent q2 oracle.\n count1=6;for(integer x=0;x<6;x=x+1)saved1[x]=cap_path_image[7+x];stage_no=0;probe_owners;\n $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);\n if(!$value$plusargs("cost2=%s",path))$fatal(1,"cost2");fd_gold=$fopen(path,"r");\n if(!$value$plusargs("candidates2=%s",path))$fatal(1,"candidates2");candidates_fd=$fopen(path,"r");\n if(!$value$plusargs("polls2=%s",path))$fatal(1,"polls2");polls_fd=$fopen(path,"r");\n if(!$value$plusargs("finals2=%s",path))$fatal(1,"finals2");finals_fd=$fopen(path,"r");\n if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"q2 oracle open");\n poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;physical_expands=0;metadata_calls=0;visited_reads=0;\n query_index=1;selected_sink=128009;selected_connection=16497;selected_sequence=2;stopped=0;\n autonomous_query;\n for(final_index=0;final_index<328;final_index=final_index+1)begin\n  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");\n  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end\n  if(final_node_id==selected_sink)gold_final[159:128]=0;\n  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"q2 final label %0d",final_node_id);\n end\n stage_no=1;probe_owners;\n stage_no=2;route_command(1,0,150697,1);probe_owners;\n stage_no=3;route_command(1,1,128009,2);probe_owners;\n if(rc_slots!=0||count1!=6||count2!=6||rc_fault||poll_i!=43||expand_i!=42||candidate_i!=176)$fatal(1,"cold q2 final totals");\n control(1);control(2);wait(f_normal_retired&&f_backend_idle&&f_all_drained&&f_phase==0);\n'
COMMIT_TASK+=' $fdisplay(trace,"JOINT_SYSTEM_Q2_PASS %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i);$display("JOINT_SYSTEM_COMMIT_PASS reads=%0d polls=%0d expands=%0d candidates=%0d",as_rbeats,poll_i,expand_i,candidate_i);\nend endtask\n'

def patch_commit(s):
 for a,b in [(".as_cfg_generation(64'h100000001)",".as_cfg_generation(jp_authority_stage?64'h100000002:64'h100000001)"),(".as_cfg_checkpoint(32'd17)",".as_cfg_checkpoint(jp_authority_stage?32'd18:32'd17)"),(".as_cfg_primary(64'h91fffff000)",".as_cfg_primary(jp_authority_stage?64'ha000000000:64'h91fffff000)"),(".as_cfg_pool(64'h9208aaef40)",".as_cfg_pool(jp_authority_stage?64'ha008aaff40:64'h9208aaef40)"),(".as_cfg_allocator(64'h9208aaef40)",".as_cfg_allocator(jp_authority_stage?64'ha008aaff40:64'h9208aaef40)"),(".base1(64'h9208aaef40),.base2(64'h9208aaef40),.size0(64'd145424192),.size1(64'd0)",".base1(64'ha000000000),.base2(64'h9208aaef40),.size0(64'd145424192),.size1(64'd145424256)")]:
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 assert s.count('\n bundle_capture;\n')==1
 s=s.replace('\n bundle_capture;\n','\n bundle_capture;\n joint_commit_check;\n')
 return s.replace('endmodule',COMMIT_TASK+'\nendmodule')

AP_TASK="""
task ap_get(input[31:0]node,net,input[63:0]generation,input[3:0]status,input[31:0]refs,occ);begin
 @(negedge clk);ap_node=node;ap_net=net;ap_generation=generation;ap_cookie=ap_cookie+1;ap_valid=1;
 do @(posedge clk);while(!ap_ready);@(negedge clk);ap_valid=0;
 wait(ap_rsp_valid);repeat(8)begin @(negedge clk);if(!ap_rsp_valid||ap_status!=status||ap_refs!=refs||ap_occ!=occ||ap_rsp_cookie!=ap_cookie||ap_rsp_checkpoint!=18||ap_rsp_generation!=64'h100000002||ap_rsp_design!=design_id||pc_release_ready||!pc_owned)$fatal(1,"native authority inspection");end
 ap_rsp_ready=1;@(negedge clk);ap_rsp_ready=0;
end endtask
always @(posedge clk)if(!rst&&!k_cold_rst)begin
 if(ap_valid&&ap_ready)$fdisplay(trace,"APQ %0d %0d %0d %016h %0d",cycles,ap_node,ap_net,ap_generation,ap_cookie);
 if(ap_rsp_valid&&ap_rsp_ready)$fdisplay(trace,"APR %0d %0d %0d %0d %016h %0d",cycles,ap_status,ap_refs,ap_occ,ap_rsp_generation,ap_rsp_cookie);
end
"""
# Read-only public interface; no hierarchical writes to DUT state.
COMMIT_TASK=AP_TASK+COMMIT_TASK
