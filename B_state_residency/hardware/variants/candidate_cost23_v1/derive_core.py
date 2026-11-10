from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_postprev_query_core','module candidate_cost23_query_core',1)
 ports=''' input wire cost_c_req_valid,output wire cost_c_req_ready,input wire [31:0] cost_c_req_cookie,cost_c_req_node,
 input wire [1:0] cost_c_req_query,cost_c_req_op,input wire [3:0] cost_c_req_price,
 output wire cost_c_rsp_valid,input wire cost_c_rsp_ready,output wire [3:0] cost_c_rsp_status,
 output wire [31:0] cost_c_rsp_cookie,cost_c_rsp_node,cost_c_rsp_y,cost_c_rsp_slr,cost_c_rsp_next,cost_c_rsp_prev_column,
 output wire [255:0] cost_c_rsp_attrs,output wire [1:0] cost_c_rsp_op,cost_c_rsp_query,output wire [3:0] cost_c_rsp_price,
'''
 s=s.replace(' input wire post_l_valid,',ports+' input wire post_l_valid,',1)
 s=s.replace('wire [1:0] pc_rv,pc_rr,pc_sv,pc_sr;wire [143:0] pc_rd;wire [989:0] pc_sd;', 'wire [2:0] pc_rv,pc_rr,pc_sv,pc_sr;wire [215:0] pc_rd;wire [1484:0] pc_sd;')
 for a,b in [('{post_c_req_valid,c_req_valid}','{cost_c_req_valid,post_c_req_valid,c_req_valid}'),('{post_c_req_ready,c_req_ready}','{cost_c_req_ready,post_c_req_ready,c_req_ready}'),('{post_c_rsp_valid,c_rsp_valid}','{cost_c_rsp_valid,post_c_rsp_valid,c_rsp_valid}'),('{post_c_rsp_ready,c_rsp_ready}','{cost_c_rsp_ready,post_c_rsp_ready,c_rsp_ready}')]:s=s.replace(a,b)
 logic=''' wire [31:0] cost_c_rsp_label_prev;wire cost_c_rsp_north,cost_c_rsp_prev_read,cost_c_rsp_prev_present;
 assign pc_rd[144+:72]={cost_c_req_op,cost_c_req_query,cost_c_req_price,cost_c_req_cookie,cost_c_req_node};
 assign {cost_c_rsp_status,cost_c_rsp_op,cost_c_rsp_query,cost_c_rsp_price,cost_c_rsp_cookie,cost_c_rsp_node,cost_c_rsp_y,cost_c_rsp_slr,cost_c_rsp_next,cost_c_rsp_prev_column,cost_c_rsp_label_prev,cost_c_rsp_north,cost_c_rsp_prev_read,cost_c_rsp_prev_present,cost_c_rsp_attrs}=pc_sd[990+:495];
'''
 s=s.replace(' assign {mc_req_op,mc_req_query',logic+' assign {mc_req_op,mc_req_query',1)
 s=s.replace('.CLIENTS(2),.REQUEST_BITS(72),.RESPONSE_BITS(495)', '.CLIENTS(3),.REQUEST_BITS(72),.RESPONSE_BITS(495)',1)
 return s
if __name__=='__main__':Path(__file__).with_name('candidate_cost23_query_core.sv').write_text(derive((ROOT/'hardware/variants/candidate_postprev_v1/candidate_postprev_query_core.sv').read_text()))
