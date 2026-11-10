"""Journal-preserving explicit recovery retry, derived from frozen v6 stack."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/recovery_fault_matrix_v2/sources'
def rep(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def make():
 out={};s=(BASE/'recovery_coordinator.sv').read_text()
 s=rep(s,'input wire clk,cold_rst,abort,backend_drained,normal_retired,','input wire clk,cold_rst,abort,backend_drained,normal_retired,retry_safe,output wire attempt_reset,')
 s=rep(s,'FAILWAIT=10,DONE=11;','FAILWAIT=10,DONE=11,REARM=12;')
 s=rep(s,'reg[1:0]current_query;','reg[31:0]attempt_version;reg[1:0]attempt_query;\n reg[1:0]current_query;')
 s=rep(s,'wire fail_now=abort||timeout||unexpected;', '''// Old callback fault latches are cleared only in a quiescent REARM cycle.
 wire fail_now=(abort&&state!=REARM)||timeout||unexpected;
 assign attempt_reset=!cold_rst&&state==REARM&&retry_safe&&!unexpected;''')
 s=rep(s,'assign recover_ready=!cold_rst&&configured&&!fault&&state==NORMAL&&!cfg_rsp_valid&&!cfg_valid&&!j_valid;', 'assign recover_ready=!cold_rst&&configured&&state==NORMAL&&!cfg_rsp_valid&&!cfg_valid&&!j_valid&&!unexpected&&(!fault||(stopped&&retry_safe&&backend_drained&&normal_retired));')
 s=rep(s,'state<=NORMAL;configured<=0;owned<=0;stopped<=0;', 'attempt_version<=0;attempt_query<=0;state<=NORMAL;configured<=0;owned<=0;stopped<=0;')
 s=rep(s,'current_price<=cfg_price;journal_count<=0;', 'current_price<=cfg_price;attempt_version<=cfg_version;attempt_query<=cfg_query;journal_count<=0;')
 s=rep(s,'recover_version<=current_version||recover_query==current_query', 'recover_version<=attempt_version||recover_query==current_query||recover_query==attempt_query')
 s=rep(s,'else begin new_version<=recover_version;new_query<=recover_query;new_price<=recover_price;state<=DRAIN;end', '''else begin
       new_version<=recover_version;new_query<=recover_query;new_price<=recover_price;
       attempt_version<=recover_version;attempt_query<=recover_query;
       if(stopped)begin stopped<=0;error_code<=0;state<=REARM;end else state<=DRAIN;
      end''')
 s=rep(s,'    DRAIN:if(backend_drained&&normal_retired)', '''    REARM:begin
     if(!retry_safe||unexpected||timeout)fail(6);
     else state<=DRAIN;
    end
    DRAIN:if(backend_drained&&normal_retired)''')
 out['recovery_coordinator.sv']=s
 s=(BASE/'config_restore_controller.sv').read_text()
 s=rep(s,'input wire clk,rst,abort,backend_drained,normal_retired,','input wire clk,rst,abort,backend_drained,normal_retired,attempt_reset,')
 s=rep(s,'assign load_ready=!rst&&!stopped', 'assign load_ready=!rst&&!attempt_reset&&!stopped')
 s=rep(s,'assign start_ready=!rst&&!stopped', 'assign start_ready=!rst&&!attempt_reset&&!stopped')
 s=rep(s,'  else begin\n   if(load_rsp_valid', '''  // A new recovery attempt may clear only retired transient state. The
  // authoritative descriptor, checkpoint and successful version survive.
  else if(attempt_reset&&state==IDLE&&!load_rsp_valid&&backend_drained&&normal_retired)begin
   stopped<=0;error_code<=0;elapsed<=0;tx_version<=0;sent<=0;retired<=0;
   rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;
  end else begin
   if(load_rsp_valid''')
 out['config_restore_controller.sv']=s
 s=(BASE/'residency_system.sv').read_text()
 s=rep(s,'wire k_labels_done;', 'wire k_labels_done;wire k_attempt_reset;wire k_retry_safe;')
 s=rep(s,'assign k_labels_done=lr_rsp_valid;', '''// The fence forwards a retry only after prior completion consumption and
// backend drain. Restore services and their responses must also be retired.
assign k_retry_safe=f_all_drained&&f_backend_idle&&f_normal_retired&&f_pending==0&&!cf_busy&&!lr_busy&&!cf_rsp_valid&&!lr_rsp_valid&&!f_fault;
assign k_labels_done=lr_rsp_valid;''')
 s=rep(s,'recovery_ctl(.clk(clk),.cold_rst(k_cold_rst)', 'recovery_ctl(.retry_safe(k_retry_safe),.attempt_reset(k_attempt_reset),.clk(clk),.cold_rst(k_cold_rst)')
 s=rep(s,'config_restore(.clk(clk),.rst(k_cold_rst)', 'config_restore(.attempt_reset(k_attempt_reset),.clk(clk),.rst(k_cold_rst)')
 s=rep(s,'label_restore(.clk(clk),.rst(k_cold_rst)', 'label_restore(.clk(clk),.rst(k_cold_rst||k_attempt_reset)')
 out['residency_system.sv']=s
 return out
if __name__=='__main__':
 for n,s in make().items():(HERE/n).write_text(s)
