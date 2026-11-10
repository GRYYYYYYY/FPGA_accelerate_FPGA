from pathlib import Path
from build import HOST
HERE=Path(__file__).parent
TASK='''
reg jp_start=0,jp_commit=0,jp_cancel=0,jp_done_ready=0;
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
  if n in ['jp_start','jp_commit','jp_cancel','jp_done_ready','jp_load','jp_ack','jp_start_ready','jp_commit_ready','jp_cancel_ready','jp_owned','jp_done','jp_result','jp_ready','jp_reply','jp_status']:v=n
  else:v={'jp_design':'design_id','jp_checkpoint':"32'd18",'jp_generation':"64'h100000002",'jp_version':'query_version','jp_query':'p_active_query','jp_price':'p_active_price','jp_manifest_ready':"1'b1",'jp_authority_stage':"1'b0"}[n]
  ties+=f'.{n}({v}),'
 needle=')system(.cp_ready';assert s.count(needle)==1;s=s.replace(needle,')system('+ties+'.cp_ready')
 needle=' // Reject decreasing generation; capture the later transaction from its handshake.';assert s.count(needle)==1;s=s.replace(needle,' joint_cancel_check;\n'+needle)
 at=s.index(';',s.index('module '))+1
 decl,task=TASK.split('task joint_cancel_check',1)
 return (s[:at]+decl+s[at:]).replace('endmodule','task joint_cancel_check'+task+OBSERVE+'\nendmodule')

OBSERVE="""
always @(posedge clk)if(!rst&&!k_cold_rst)begin
 if(jp_start&&jp_start_ready)$fdisplay(trace,"JS %0d %0d %0d %0d %0d %0d",cycles,k_saved_checkpoint,k_count,query_version,system.jp_cver,pc_owned);
 if(system.jp_prepare&&system.jp_load[0]&&system.inner.backend.jp_kr)$fdisplay(trace,"JK %0d %0d %0d",cycles,system.jp_checkpoint,system.jp_version);
 if(system.jp_prepare&&system.jp_load[1]&&system.inner.backend.jp_cr)$fdisplay(trace,"JC %0d %0d %0d",cycles,system.jp_checkpoint,system.jp_version);
 if(jp_reply[0]&&jp_ack[0])$fdisplay(trace,"JKR %0d %0d %0d %0d",cycles,jp_status[0],k_saved_checkpoint,k_count);
 if(jp_reply[1]&&jp_ack[1])$fdisplay(trace,"JCR %0d %0d %0d",cycles,jp_status[1],system.jp_ccp);
 if(jp_cancel&&jp_cancel_ready)$fdisplay(trace,"JX %0d %0d",cycles,system.jp_prepared);
 if(|system.jp_dv)$fdisplay(trace,"JD %0d %0d %0d",cycles,system.jp_dv,{system.jp_dropready,system.jp_adr});
 if(jp_done&&jp_done_ready)$fdisplay(trace,"JE %0d %0d %0d %0d %0d %0d",cycles,jp_result,k_saved_checkpoint,k_count,system.jp_ccp,pc_owned);
 if(jp_owned&&((|system.jp_pv)||!pc_owned||pc_release_ready))$fatal(1,"unexpected publication or lost lease in cancel case");
end
"""
