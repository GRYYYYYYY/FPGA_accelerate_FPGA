"""Abort a real held success reply, or its exact consumption edge."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_shared_last_v1/sources/tb_query_fault.sv')
def make():
 s=BASE.read_text()
 s=s.replace('reg wm_enable=0;', '''reg late_started=0;reg[31:0]retry_cookie=32'hc0010001;integer late_mode=0;
initial begin if($value$plusargs("latemode=%d",late_mode))begin end if(late_mode<0||late_mode>1)$fatal(1,"late mode");end
reg wm_enable=0;''')
 s=s.replace(".recover_cookie(32'hc0010001)",'.recover_cookie(retry_cookie)')
 start=s.index('task warm_fault_and_restore;')
 a=s.index(' $fdisplay(trace,"WARM_COMPLETE',start)
 b=s.index(' // Restore only verification cursors',a)
 # Real successful restore body, reused after higher native attempt acceptance.
 r0=s.index(' recovering=1;armed=0;',start)
 r1=s.index(' $fdisplay(trace,"WARM_COMPLETE',r0)
 second=s[r0:r1]
 # The second attempt has J0: no owner repair requests are expected or invented.
 second=second.replace('system.controller.last_version!=5','system.controller.last_version!=6')
 second=second.replace('k_rsp_status||k_count||!wm_joined','k_rsp_status||k_rsp_cookie!=retry_cookie||k_corrected||k_count||!wm_joined')
 injected=''' $fdisplay(trace,"LATE_SUCCESS_HELD %0d %0d %0d %08h %0d %0d",cycles,k_rsp_status,k_count,k_rsp_cookie,late_mode,k_corrected);
 late_started=1;@(negedge clk);abort=1;
 if(late_mode==0)begin
  repeat(8)begin @(negedge clk);
   $fdisplay(trace,"LATE_ABORT_HELD %0d %0d %08h %0d %0d %0d",cycles,k_rsp_valid,k_rsp_cookie,k_rsp_status,k_count,k_corrected);
   if(!k_rsp_valid||k_rsp_cookie!=retry_cookie||k_rsp_status||k_corrected!=6||k_count||!wm_owned||!wm_fault||recover_open||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"late abort changed held success or opened work");
  end
 end
 k_rsp_ready=1;@(posedge clk);
 $fdisplay(trace,"LATE_SUCCESS_CONSUME %0d %0d %0d %08h %0d",cycles,abort,k_rsp_status,k_rsp_cookie,k_corrected);
 if(!k_rsp_valid||k_rsp_status||k_corrected!=6||k_rsp_cookie!=retry_cookie)$fatal(1,"late success consumption");
 @(negedge clk);k_rsp_ready=0;abort=0;
 repeat(12)begin @(negedge clk);if(!wm_owned||!wm_fault||recover_open||k_permit||qc_cmd_ready||rc_req_ready||pc_acquire_ready)$fatal(1,"late success lost quarantine");end
 $fdisplay(trace,"LATE_QUARANTINE %0d %0d %0d %0d",cycles,k_count,query_version,system.inner.backend.recovery_ctl.attempt_version);
 if(k_count||query_version!=5||system.inner.backend.recovery_ctl.attempt_version!=5)$fatal(1,"late success committed state/floor");
 // Already committed attempt5 remains rejected even though J is now zero.
 retry_cookie=32'hc0020000;k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=1||k_rsp_cookie!=retry_cookie||k_count||!wm_owned||!wm_fault)$fatal(1,"late same attempt rejection");end
 $fdisplay(trace,"RETRY_REJECT %0d %0d %0d %08h",cycles,k_rsp_status,k_count,k_rsp_cookie);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)@(negedge clk);
 as_recover_version=6;as_recover_query=0;retry_cookie=32'hc0020001;
 $fdisplay(trace,"RETRY_START %0d %0d %0d %08h",cycles,as_recover_version,k_count,retry_cookie);
'''
 finish=''' $fdisplay(trace,"WARM_COMPLETE %0d %0d %0d %0d %0d",cycles,k_rsp_status,k_corrected,rc_slots,system.controller.last_sequence);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;wait(recover_open);if(wm_owned||wm_fault||!k_permit||query_version!=6||p_active_query!=0||p_active_price!=6)$fatal(1,"late retry release");
'''
 s=s[:a]+injected+second+finish+s[b:]
 s=s.replace('if(wm_owned&&(wm_fault||qc_cmd_ready||rc_req_ready||pc_acquire_ready))', 'if(wm_owned&&((wm_fault&&!late_started)||qc_cmd_ready||rc_req_ready||pc_acquire_ready))')
 s=s.replace('endmodule','''always @(posedge clk)if(late_started&&(k_cold_rst||bench_rst))$fatal(1,"late retry cold reset");
endmodule''')
 return s
if __name__=='__main__':(HERE/'tb_late.sv').write_text(make())
