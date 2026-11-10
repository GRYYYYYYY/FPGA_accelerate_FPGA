from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/search_fault_retire_matrix_v6/sources/tb_query_fault.sv'
def make():
 s=BASE.read_text();needle=')system(.qc_cmd_valid';assert s.count(needle)==1
 pins={n:"1'b0"for n in ['pc_acquire_valid','pc_release_valid','cp_valid','cp_restore','cp_rsp_ready','cp_s_valid','cp_s_last','cp_m_ready','cp_test_reset']}
 pins.update({n:"32'd0"for n in ['cp_nodes','cp_nets','cp_expected_crc','cp_s_index','cp_s_data']});pins['cp_design']="64'd0"
 return s.replace(needle,')system('+','.join('.'+n+'('+v+')'for n,v in pins.items())+',.qc_cmd_valid')
if __name__=='__main__':(HERE/'tb_query_fault.sv').write_text(make())
