from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_cost23_engine','module candidate_commit_engine',1)
 ports='''output wire out_commit_valid,output wire [3:0] out_commit_status,output wire [2:0] out_commit_acked,output wire [159:0] out_commit_payload,
'''
 s=s.replace('output wire out_cost_valid,',ports+'output wire out_cost_valid,',1)
 decl='''wire commit_busy,commit_fault,commit_ready,commit_req_valid;reg commit_started;
wire [31:0] commit_cookie,commit_parent,commit_child,commit_sequence,commit_version;wire [1:0] commit_query;wire [3:0] commit_price;wire [63:0] commit_design;
wire cl_valid,cl_ready,cl_write,cl_rsp_valid,cl_rsp_ready,cl_present;wire [31:0] cl_node,cl_value;wire [2:0] cl_field;wire [3:0] cl_status;wire [159:0] cl_payload;
wire commit_identity_error;
'''
 s=s.replace('wire k_busy,',decl+'wire k_busy,',1)
 s=s.replace('||q_lease||k_busy','||q_lease||k_busy||commit_busy')
 s=s.replace('out_prep_valid&&out_post_valid&&out_cost_valid));','out_prep_valid&&out_post_valid&&out_cost_valid&&out_commit_valid));',1)
 s=s.replace('assign fault=','assign fault=commit_fault||commit_identity_error||',1)
 s=s.replace('if(k_fault||k_identity_error||q_fault','if(commit_fault||commit_identity_error||k_fault||k_identity_error||q_fault',1)
 logic='''assign commit_identity_error=out_commit_valid&&(commit_cookie!=out_sequence||commit_parent!=held_parent||commit_child!=out_node||commit_sequence!=out_config[31:0]||commit_query!=p_active_query||commit_price!=p_active_price||commit_version!=query_version||commit_design!=design_id);
assign commit_req_valid=q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_cost_valid&&!commit_started;
always @(posedge clk)begin
 if(rst)commit_started<=0;
 else if(raw_out_valid&&raw_out_ready)commit_started<=0;
 else if(commit_req_valid&&commit_ready)commit_started<=1;
end
cost_label_commit commit_inputs(.clk(clk),.rst(rst),.abort(abort||fence_stopped),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(commit_req_valid),.req_ready(commit_ready),.req_cookie(out_sequence),.req_parent(held_parent),.req_child(out_node),.req_sequence(out_config[31:0]),.req_partial(out_cost_words[95:64]),.req_total(out_cost_words[159:128]),
 .rsp_valid(out_commit_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),.rsp_status(out_commit_status),.rsp_acked(out_commit_acked),.rsp_cookie(commit_cookie),.rsp_parent(commit_parent),.rsp_child(commit_child),.rsp_sequence(commit_sequence),.rsp_version(commit_version),.rsp_query(commit_query),.rsp_price(commit_price),.rsp_design(commit_design),.rsp_payload(out_commit_payload),.busy(commit_busy),.fault(commit_fault),
 .l_valid(cl_valid),.l_ready(cl_ready),.l_write(cl_write),.l_node(cl_node),.l_value(cl_value),.l_field(cl_field),.l_rsp_valid(cl_rsp_valid),.l_rsp_ready(cl_rsp_ready),.l_status(cl_status),.l_payload(cl_payload),.l_present(cl_present));
'''
 s=s.replace('assign all_configured=',logic+'assign all_configured=',1)
 s=s.replace('candidate_cost23_query_core #','candidate_commit_query_core #',1).replace(' core(\n',''' core(
.commit_l_valid(cl_valid),.commit_l_ready(cl_ready),.commit_l_write(cl_write),.commit_l_node(cl_node),.commit_l_value(cl_value),.commit_l_field(cl_field),.commit_l_rsp_valid(cl_rsp_valid),.commit_l_rsp_ready(cl_rsp_ready),.commit_l_status(cl_status),.commit_l_payload(cl_payload),.commit_l_present(cl_present),
''',1)
 return s
if __name__=='__main__':Path(__file__).with_name('candidate_commit_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_cost23_v1/candidate_cost23_engine.sv').read_text()))
