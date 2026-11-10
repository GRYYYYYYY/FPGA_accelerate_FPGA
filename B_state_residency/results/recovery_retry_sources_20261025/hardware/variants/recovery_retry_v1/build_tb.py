"""Two recovery attempts, then complete real CPU-matched query replay."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/recovery_fault_matrix_v2/sources'
SUCCESS=ROOT/'results/search_fault_retire_matrix_v6/sources/tb_query_fault.sv'
def rep(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def make():
 s=(BASE/'tb_recovery_fault.sv').read_text();good=SUCCESS.read_text()
 decl="""reg[31:0]retry_cookie=32'hc0010001,retry_version=4,stream_cookie=32'he0010001;
reg[1:0]retry_query=2;reg[3:0]retry_price=4;
integer soft_resets=0,reset_cycles=0,cold_cycles=0;reg[2303:0]descriptor_before;
always @(posedge clk)begin
 if(k_cold_rst)cold_cycles<=cold_cycles+1;
 if(k_target_reset)reset_cycles<=reset_cycles+1;
 if(system.inner.backend.k_attempt_reset)begin
  soft_resets<=soft_resets+1;
  if(k_count!=1||!f_all_drained||!f_backend_idle||!f_normal_retired||f_pending!=0||lr_busy||cf_busy||lr_rsp_valid||cf_rsp_valid||system.inner.backend.config_restore.descriptor!==descriptor_before)$fatal(1,"unsafe retry transient reset");
  $fdisplay(trace,"SOFT %0d %0d %0d %0d",cycles,k_count,k_new_query,k_new_version);
 end
end
"""
 a=decl.index('always @(posedge clk)');monitor=decl[a:];decl=decl[:a]
 s=rep(s,'wire recovery_inject;', 'wire recovery_inject;\n'+decl)
 s=rep(s,'endmodule',monitor+'\nendmodule')
 for port,literal,value in [('recover_cookie',"32'hc0010001",'retry_cookie'),('recover_version',"32'd4",'retry_version'),('recover_query',"2'd2",'retry_query'),('recover_price',"4'd4",'retry_price'),('snapshot_cookie',"32'he0010001",'stream_cookie'),('lr_s_cookie',"32'he0010001",'stream_cookie')]:s=rep(s,f'.{port}({literal})',f'.{port}({value})')
 s=rep(s,'initial begin wait(recovering);','initial begin:first_stream wait(recovering);')
 a=s.index(' k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;k_rec_valid=1;')
 b=s.index('\nend\n\nassign recovery_inject',a)
 tail=""" k_rsp_ready=1;@(negedge clk);k_rsp_ready=0;
 recovery_done=1;disable first_stream;lr_s_valid=0;
 descriptor_before=system.inner.backend.config_restore.descriptor;
 repeat(16)begin @(negedge clk);if(recover_open||k_permit||f_sr!=0||rc_req_ready||qc_cmd_ready||k_target_reset||!k_fault||k_count!=1||!f_all_drained||f_pending!=0)$fatal(1,"failed recovery reopened or dropped journal");end
 $fdisplay(trace,"RF_CLOSED %0d %0d %0d",cycles,k_count,f_phase);
 retry_cookie=32'hc0020001;retry_version=5;retry_query=3;retry_price=5;stream_cookie=32'he0020001;
 k_rec_valid=1;do @(posedge clk);while(!k_rec_ready);@(negedge clk);k_rec_valid=0;
 wait(k_rcfg_valid);@(negedge clk);restore_epoch=k_new_query;restore_version=k_new_version;
 wait(!k_rcfg_valid);
"""
 c=good.index(' wait(k_labels_valid);@(negedge clk);');d=good.index('\n replayed=1;',c)
 tail+=good[c:d].replace("32'he0010001","32'he0020001").replace("32'hc0010001","32'hc0020001")
 tail+='\n if(soft_resets!=1||reset_cycles!=10||cold_cycles!=5||system.inner.backend.config_restore.descriptor!==descriptor_before||k_new_query!=3||k_new_version!=5)$fatal(1,"retry reset/config identity");\n'
 e=good.index('\nend\nendmodule',d)
 tail+=good[d:e].replace('QUERY_FAULT_OBSERVED case=%0d outcome=recovered_retry','RECOVERY_RETRY_OBSERVED case=%0d outcome=recovered_retry').replace('fault_case,cycles,k_corrected','recovery_fault,cycles,k_corrected')
 s=s[:a]+tail+s[b:]
 return s
if __name__=='__main__':(HERE/'tb_recovery_retry.sv').write_text(make())
