from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/authority_query_v4/sources');CORE=ROOT/'results/query_checkpoint_sources_20261025/query_lifecycle.sv'
PORTS='''input wire qc_cp_valid,qc_cp_restore,qc_cp_rsp_ready,qc_cp_s_valid,qc_cp_s_last,qc_cp_m_ready,qc_cp_test_reset,
output wire qc_cp_ready,qc_cp_busy,qc_cp_rsp_valid,qc_cp_s_ready,qc_cp_m_valid,qc_cp_m_last,qc_restore_pending,
input wire[31:0]qc_cp_expected_crc,qc_cp_s_index,qc_cp_s_data,
output wire[31:0]qc_cp_crc,qc_cp_m_index,qc_cp_m_data,output wire[3:0]qc_cp_status,
'''
NAMES=['valid','restore','rsp_ready','s_valid','s_last','m_ready','ready','busy','rsp_valid','s_ready','m_valid','m_last','expected_crc','s_index','s_data','crc','m_index','m_data','status']
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=(BASE/'query_residency_system.sv').read_text();at=s.index(')(\n')+3;s=s[:at]+PORTS+s[at:]
 s=rep(s,'wire pc_safe;','')
 decl='''wire pc_safe;wire qc_core_cp_ready,cp_inner_ready;reg qc_reset_held,qc_pending,qc_import_held;
assign qc_restore_pending=qc_pending;
assign qc_cp_ready=pc_owned&&!cp_busy&&!qc_reset_held&&qc_core_cp_ready;
assign cp_ready=!qc_cp_valid&&!qc_cp_busy&&!qc_reset_held&&cp_inner_ready;
always @(posedge clk)begin
 if(k_cold_rst)begin qc_reset_held<=0;qc_pending<=0;qc_import_held<=0;end
 else begin
  qc_reset_held<=ENABLE_TEST_INJECTION&&qc_cp_test_reset&&pc_owned&&pc_safe&&!qc_busy&&!cp_busy&&!cp_valid&&!qc_cp_valid&&!qc_cp_busy;
  if(ENABLE_TEST_INJECTION&&qc_cp_test_reset&&pc_owned&&pc_safe&&!qc_busy&&!cp_busy&&!cp_valid&&!qc_cp_valid&&!qc_cp_busy)qc_pending<=1;
  if(qc_cp_valid&&qc_cp_ready)begin qc_import_held<=qc_cp_restore;if(qc_cp_restore)qc_pending<=1;end
  if(qc_cp_rsp_valid&&qc_cp_rsp_ready)begin
   if(qc_import_held&&qc_cp_status==0)qc_pending<=0;
   qc_import_held<=0;
  end
 end
end
'''
 at=s.index(');\n')+3;s=s[:at]+decl+s[at:]
 s=rep(s,'.command_busy(cp_busy),.command_valid(cp_valid),.test_reset(cp_test_reset)', '.command_busy(cp_busy||qc_cp_busy||qc_pending),.command_valid(cp_valid||qc_cp_valid),.test_reset(cp_test_reset||qc_cp_test_reset||qc_reset_held)')
 s=rep(s,'&&!qc_busy&&!ss_busy&&!qc_fault', '&&(!qc_busy||qc_cp_busy)&&!ss_busy&&!qc_fault')
 s=rep(s,'.cp_valid(cp_valid&&pc_owned)', '.cp_valid(cp_valid&&pc_owned&&!qc_cp_valid&&!qc_cp_busy&&!qc_reset_held)')
 s=rep(s,'.cp_ready(cp_ready)', '.cp_ready(cp_inner_ready)')
 s=rep(s,'.admit(!as_cfg_lease&&', '.admit(!qc_pending&&!as_cfg_lease&&')
 start=s.index('query_lifecycle controller(');tail=s[start:]
 tail=rep(tail,'.rst(rst)', '.rst(rst||qc_reset_held)')
 pins=','.join('.cp_'+n+'('+('qc_core_cp_ready'if n=='ready'else'qc_cp_'+n)+')'for n in NAMES)
 tail=rep(tail,'query_lifecycle controller(', 'query_lifecycle controller('+pins+',.cp_safe(pc_owned&&pc_safe&&!qc_reset_held),.active_generation(as_bound_generation),')
 s=s[:start]+tail
 return {'query_residency_system.sv':s,'query_lifecycle.sv':CORE.read_text()}
if __name__=='__main__':
 for n,s in make().items():(HERE/n).write_text(s)
