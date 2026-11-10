from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_cost23_query_core','module candidate_commit_query_core',1)
 ports=''' input wire commit_l_valid,output wire commit_l_ready,input wire commit_l_write,
 input wire [31:0] commit_l_node,commit_l_value,input wire [2:0] commit_l_field,
 output wire commit_l_rsp_valid,input wire commit_l_rsp_ready,output wire [3:0] commit_l_status,output wire [159:0] commit_l_payload,output wire commit_l_present,
'''
 s=s.replace(' input wire cost_c_req_valid,',ports+' input wire cost_c_req_valid,',1)
 for n in ['req_valid','req_ready','rsp_valid','rsp_ready']:s=s.replace('wire [3:0] arb_io_c_'+n,'wire [4:0] arb_io_c_'+n)
 s=s.replace('wire [271:0] arb_io_c_req_data','wire [339:0] arb_io_c_req_data').replace('wire [659:0] arb_io_c_rsp_data','wire [824:0] arb_io_c_rsp_data')
 logic=''' assign arb_io_c_req_valid[4]=commit_l_valid;
 assign commit_l_ready=arb_io_c_req_ready[4];
 assign arb_io_c_req_data[272+:68]={commit_l_write,commit_l_node,commit_l_value,commit_l_field};
 assign commit_l_rsp_valid=arb_io_c_rsp_valid[4];
 assign arb_io_c_rsp_ready[4]=commit_l_rsp_ready;
 assign {commit_l_status,commit_l_payload,commit_l_present}=arb_io_c_rsp_data[660+:165];
'''
 s=s.replace(' assign {p_io_write,p_io_node,p_io_value,p_io_field}',logic+' assign {p_io_write,p_io_node,p_io_value,p_io_field}',1)
 s=s.replace('.CLIENTS(4),.REQUEST_BITS(68),.RESPONSE_BITS(165)', '.CLIENTS(5),.REQUEST_BITS(68),.RESPONSE_BITS(165)',1)
 return s
if __name__=='__main__':Path(__file__).with_name('candidate_commit_query_core.sv').write_text(derive((ROOT/'hardware/variants/candidate_cost23_v1/candidate_cost23_query_core.sv').read_text()))
