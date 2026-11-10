from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_params_engine','module candidate_cost23_engine',1)
 ports='''output wire out_cost_valid,output wire [3:0] out_cost_status,output wire [159:0] out_cost_words,output wire [735:0] out_cost_packet,
output wire [415:0] out_cost_geometry,output wire [127:0] out_cost_geometry_result,
'''
 s=s.replace('input wire [31:0] expand_connection,',ports+'input wire [31:0] expand_connection,',1)
 decl='''wire k_busy,k_fault,k_ready,k_req_valid;reg k_started;
wire [31:0] k_cookie,k_child,k_version;wire [1:0] k_query;wire [3:0] k_price;wire [63:0] k_design;
wire kc_valid,kc_ready,kc_rsp_valid,kc_rsp_ready;wire [31:0] kc_cookie,kc_node,kc_rsp_cookie,kc_rsp_node,kc_y,kc_slr,kc_next,kc_prev;
wire [1:0] kc_query,kc_op,kc_rsp_op,kc_rsp_query;wire [3:0] kc_price,kc_status,kc_rsp_price;wire [255:0] kc_attrs;
wire k_identity_error;
'''
 s=s.replace('wire q_req_ready,',decl+'wire q_req_ready,',1)
 s=s.replace('||q_lease','||q_lease||k_busy')
 s=s.replace('assign out_valid=q_meta_valid&&raw_seen&&raw_out_valid&&(out_action==0||(out_prep_valid&&out_post_valid));','assign out_valid=q_meta_valid&&raw_seen&&raw_out_valid&&(out_action==0||(out_prep_valid&&out_post_valid&&out_cost_valid));',1)
 s=s.replace('assign fault=','assign fault=k_fault||k_identity_error||',1)
 s=s.replace('if(q_fault||q_stopped||q_identity_error||post_fault','if(k_fault||k_identity_error||q_fault||q_stopped||q_identity_error||post_fault',1)
 logic='''assign k_identity_error=out_cost_valid&&(k_cookie!=out_sequence||k_child!=out_node||k_query!=p_active_query||k_price!=p_active_price||k_version!=query_version||k_design!=design_id);
assign k_req_valid=q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_prep_valid&&out_post_valid&&!k_started;
always @(posedge clk)begin
 if(rst)k_started<=0;
 else if(raw_out_valid&&raw_out_ready)k_started<=0;
 else if(k_req_valid&&k_ready)k_started<=1;
end
cost23_inputs cost_inputs(.clk(clk),.rst(rst),.abort(abort||fence_stopped),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(k_req_valid),.req_ready(k_ready),.req_cookie(out_sequence),.req_child(out_node),.req_sink(q_sink),.req_params(q_meta),.req_config(out_config),.req_attrs(out_post_attrs),
 .req_count(out_prep_count),.req_history(out_prep_history),.req_price_value(out_prep_price_value),.req_x(out_post_x),.req_y(out_post_y),.req_upstream(out_post_upstream),.req_center(out_post_distance),.req_net(out_prep_net_data),
 .rsp_valid(out_cost_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),.rsp_status(out_cost_status),.rsp_cookie(k_cookie),.rsp_child(k_child),.rsp_version(k_version),.rsp_query(k_query),.rsp_price(k_price),.rsp_design(k_design),.rsp_packet(out_cost_packet),.rsp_cost(out_cost_words),.rsp_geometry(out_cost_geometry),.rsp_geometry_result(out_cost_geometry_result),.busy(k_busy),.fault(k_fault),
 .c_req_valid(kc_valid),.c_req_ready(kc_ready),.c_req_cookie(kc_cookie),.c_req_node(kc_node),.c_req_query(kc_query),.c_req_op(kc_op),.c_req_price(kc_price),
 .c_rsp_valid(kc_rsp_valid),.c_rsp_ready(kc_rsp_ready),.c_rsp_status(kc_status),.c_rsp_cookie(kc_rsp_cookie),.c_rsp_node(kc_rsp_node),.c_rsp_y(kc_y),.c_rsp_slr(kc_slr),.c_rsp_next(kc_next),.c_rsp_prev_column(kc_prev),.c_rsp_attrs(kc_attrs),.c_rsp_op(kc_rsp_op),.c_rsp_query(kc_rsp_query),.c_rsp_price(kc_rsp_price));
'''
 s=s.replace('assign all_configured=',logic+'assign all_configured=',1)
 s=s.replace('candidate_postprev_query_core #','candidate_cost23_query_core #',1)
 s=s.replace(' core(\n',''' core(
.cost_c_req_valid(kc_valid),.cost_c_req_ready(kc_ready),.cost_c_req_cookie(kc_cookie),.cost_c_req_node(kc_node),.cost_c_req_query(kc_query),.cost_c_req_op(kc_op),.cost_c_req_price(kc_price),
.cost_c_rsp_valid(kc_rsp_valid),.cost_c_rsp_ready(kc_rsp_ready),.cost_c_rsp_status(kc_status),.cost_c_rsp_cookie(kc_rsp_cookie),.cost_c_rsp_node(kc_rsp_node),.cost_c_rsp_y(kc_y),.cost_c_rsp_slr(kc_slr),.cost_c_rsp_next(kc_next),.cost_c_rsp_prev_column(kc_prev),.cost_c_rsp_attrs(kc_attrs),.cost_c_rsp_op(kc_rsp_op),.cost_c_rsp_query(kc_rsp_query),.cost_c_rsp_price(kc_rsp_price),
''',1)
 return s
if __name__=='__main__':
 Path(__file__).with_name('candidate_cost23_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_params_v1/candidate_params_engine.sv').read_text()))
