from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_cancel_fixed_v2/sources/tb_query_fault.sv')
HEALTHY=Path('/tmp/B_state_residency_offer_20261025/warm_shared_last_v1/sources/tb_query_fault.sv')
def make():
 s=BASE.read_text();h=HEALTHY.read_text()
 s=s.replace('reg cancel_started=0;', "reg cancel_started=0;reg[31:0]retry_cookie=32'hc0010001;reg retry_started=0;")
 s=s.replace('.recover_cookie(32\'hc0010001)', '.recover_cookie(retry_cookie)')
 a=s.index(' $fdisplay(trace,"WARM_CANCEL_PASS %0d"')
 b=s.index('end endtask',a)
 start=h.index(' recovering=1;armed=0;',h.index('task warm_fault_and_restore;'))
 end=h.index('end endtask',start)
 positive=h[start:end]
 positive=positive.replace('system.controller.last_version!=5','system.controller.last_version!=6').replace('query_version!=5||p_active_query!=3||p_active_price!=5','query_version!=6||p_active_query!=0||p_active_price!=6')
 positive=positive.replace('k_rsp_status||k_count||!wm_joined','k_rsp_status||k_rsp_cookie!=retry_cookie||k_corrected!=0||k_count||!wm_joined')
 s=s[:a]+''' // Reject the already-used attempt through the real native reply path.
 retry_started=1;retry_cookie=32'hc0020000;k_rec_valid=1;
 do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rsp_valid);repeat(8)begin @(negedge clk);if(k_rsp_status!=1||k_rsp_cookie!=retry_cookie||k_count!=6||!wm_owned||!wm_fault)$fatal(1,"same-attempt native rejection");end
 $fdisplay(trace,"RETRY_REJECT %0d %0d %0d %08h",cycles,k_rsp_status,k_count,k_rsp_cookie);
 k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;repeat(8)@(negedge clk);
 as_recover_version=6;as_recover_query=0;retry_cookie=32'hc0020001;
 $fdisplay(trace,"RETRY_START %0d %0d %0d %08h",cycles,as_recover_version,k_count,retry_cookie);
'''+positive+s[b:]
 s=s.replace('endmodule','''always @(posedge clk)if(retry_started&&(k_cold_rst||bench_rst))$fatal(1,"retry performed cold reset");
endmodule''')
 return s
if __name__=='__main__':(HERE/'tb_retry.sv').write_text(make())
