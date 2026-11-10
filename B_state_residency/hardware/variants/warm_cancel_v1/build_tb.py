from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_shared_last_v1/sources/tb_query_fault.sv')
def make():
 s=BASE.read_text();s=s.replace('reg wm_enable=0;', 'reg cancel_started=0;\nreg wm_enable=0;')
 a='for(integer x=0;x<10;x=x+1)begin\n  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];'
 b='for(integer x=0;x<9;x=x+1)begin\n  @(negedge clk);qc_cp_s_index=x;qc_cp_s_data=qcp_image[x];'
 assert s.count(a)==1;s=s.replace(a,b)
 i=s.index(' wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);if(qc_cp_status||wm_receipts!=3')
 j=s.index('end endtask',i)
 s=s[:i]+''' cancel_started=1;@(negedge clk);abort=1;
 wait(qc_cp_rsp_valid);repeat(8)begin @(negedge clk);
  $fdisplay(trace,"CANCEL_HELD %0d %0d %0d %0d %0d %0d",cycles,qc_cp_status,k_rsp_valid,k_rsp_status,wm_owned,wm_fault);
  if(qc_cp_status!=2||!wm_owned||!wm_fault||k_rsp_valid||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"warm failure completed before query reply retirement");
 end
 qc_cp_rsp_ready=1;@(negedge clk);qc_cp_rsp_ready=0;
 for(integer waited=0;waited<2048&&!k_rsp_valid;waited=waited+1)@(negedge clk);
 if(!k_rsp_valid)begin $fflush(trace);$fatal(1,"cancel completion stuck coordinator=%0d wm_retired=%0d query_busy=%0d",system.inner.backend.recovery_ctl.state,system.wm_retired,qc_cp_busy);end
 repeat(8)begin @(negedge clk);if(k_rsp_status==0||!wm_owned||!wm_fault||recover_open||!system.wm_retired)$fatal(1,"cancel completion quarantine");end
 $fdisplay(trace,"CANCEL_COMPLETE %0d %0d %0d %0d",cycles,k_rsp_status,k_count,k_saved_checkpoint);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;abort=0;repeat(8)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"cancel opened work");end
 $fdisplay(trace,"WARM_CANCEL_PASS %0d",cycles);$fflush(trace);$display("WARM_CANCEL_PASS");$finish;
'''+s[j:]
 s=s.replace('if(wm_owned&&(wm_fault||qc_cmd_ready||rc_req_ready||pc_acquire_ready))', 'if(wm_owned&&((wm_fault&&!cancel_started)||qc_cmd_ready||rc_req_ready||pc_acquire_ready))')
 return s
if __name__=='__main__':(HERE/'tb_cancel.sv').write_text(make())
