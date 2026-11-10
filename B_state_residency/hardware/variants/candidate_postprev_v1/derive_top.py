from pathlib import Path
s=Path('hardware/variants/candidate_prefetch_v1/candidate_prefetch_engine.sv').read_text().replace('module candidate_prefetch_engine #(','module candidate_postprev_engine #(',1).replace('candidate_prefetch_query_core #','candidate_postprev_query_core #')
ports='''output wire out_post_valid,output wire [3:0] out_post_status,
output wire [31:0] out_post_x,out_post_y,out_post_upstream,out_post_distance,
output wire [255:0] out_post_attrs,output wire out_post_prev_read,
input wire seed_valid,output wire seed_ready,input wire [31:0] seed_op,seed_key,seed_id,seed_cookie,seed_version,
output wire seed_rsp_valid,input wire seed_rsp_ready,output wire [31:0] seed_rsp_status,seed_rsp_cookie,seed_rsp_size,
'''
s=s.replace('output wire out_prep_valid,',ports+'output wire out_prep_valid,',1)
s=s.replace('wire  core_busy;','').replace('reg query_owned,fence_stopped;','wire core_busy,state_lease;\nreg query_owned,fence_stopped;',1)
s=s.replace('wire state_lease=cost_lease||cc_busy||prefetch_busy;','assign state_lease=cost_lease||cc_busy||prefetch_busy||post_busy;')
s=s.replace('assign out_valid=raw_seen&&raw_out_valid&&(out_action==0||out_prep_valid);','assign out_valid=raw_seen&&raw_out_valid&&(out_action==0||(out_prep_valid&&out_post_valid));')
s=s.replace('reg prep_started,raw_seen;reg [31:0] held_net;','reg prep_started,raw_seen,post_started;reg [31:0] held_net,held_parent;',1)
s=s.replace('prep_started<=0;raw_seen<=0;held_net<=0;','prep_started<=0;raw_seen<=0;held_net<=0;held_parent<=0;post_started<=0;',1)
s=s.replace('if(expand_valid&&expand_ready)held_net<=expand_net;','if(expand_valid&&expand_ready)begin held_net<=expand_net;held_parent<=expand_parent;end\n  if(raw_out_valid&&raw_out_ready)post_started<=0;\n  else if(post_req_valid&&post_req_ready)post_started<=1;',1)
s=s.replace('assign permit_expand=!state_lease&&','assign permit_expand=frontier_expand_ready&&!state_lease&&',1)
s=s.replace('assign permit_control=!state_lease&&','assign permit_control=(host_ctrl_op!=2||frontier_close_ready)&&!frontier_busy&&!state_lease&&',1)
s=s.replace('assign query_ready=all_configured&&','assign query_ready=frontier_initialized&&!frontier_busy&&all_configured&&',1)
s=s.replace('assign fault=prefetch_fault||','assign fault=post_fault||post_identity_error||frontier_fault||prefetch_fault||',1)
s=s.replace('assign busy=core_busy||cs_busy||state_lease;','assign busy=core_busy||cs_busy||state_lease||frontier_busy;',1)
s=s.replace('if(prefetch_fault||core_fault||','if(post_fault||post_identity_error||frontier_fault||prefetch_fault||core_fault||',1)
s=s.replace('!(cc_busy||prefetch_busy)','!(cc_busy||prefetch_busy||post_busy)')
logic='''
wire post_busy,post_fault,post_req_ready,post_req_valid;
wire frontier_expand_ready,frontier_close_ready,frontier_initialized,frontier_busy,frontier_fault;
wire [31:0] frontier_size;
wire pf_valid,pf_ready,pf_rsp_valid,pf_rsp_ready;wire [31:0] pf_cookie,pf_rsp_status,pf_rsp_cookie,pf_rsp_size;
wire [1:0] pf_query,pf_rsp_query;wire [3:0] pf_price,pf_rsp_price;
wire pl_valid,pl_ready,pl_write,pl_rsp_valid,pl_rsp_ready,pl_present;
wire [31:0] pl_node,pl_value;wire [2:0] pl_field;wire [3:0] pl_status;wire [159:0] pl_payload;
wire pc2_valid,pc2_ready,pc2_rsp_valid,pc2_rsp_ready,pc2_prev_read;
wire [31:0] pc2_cookie,pc2_node,pc2_rsp_cookie,pc2_rsp_node,pc2_y,pc2_label_prev;
wire [1:0] pc2_query,pc2_rsp_query,pc2_rsp_op;wire [3:0] pc2_price,pc2_rsp_price,pc2_status;wire [255:0] pc2_attrs;
wire [31:0] post_cookie,post_parent,post_child,post_version;wire [63:0] post_design;wire [1:0] post_query;wire [3:0] post_price;
wire post_identity_error=out_post_valid&&(post_cookie!=out_sequence||post_parent!=held_parent||post_child!=out_node||post_query!=p_active_query||post_price!=p_active_price||post_version!=query_version||post_design!=design_id);
assign post_req_valid=raw_seen&&raw_out_valid&&out_action!=0&&out_prep_valid&&!post_started;
postprev_inputs post_inputs(
 .clk(clk),.rst(rst),.abort(abort||fence_stopped),.active(p_active),.decision_lock(operation_pending),.active_query(p_active_query),.active_price(p_active_price),.active_version(query_version),.active_design(design_id),
 .req_valid(post_req_valid),.req_ready(post_req_ready),.req_early(out_bits[2]),.req_cookie(out_sequence),.req_parent(held_parent),.req_child(out_node),.req_centers(out_prep_net_data[63:0]),
 .rsp_valid(out_post_valid),.rsp_ready(raw_out_valid&&raw_out_ready&&out_action!=0),.rsp_status(out_post_status),.rsp_cookie(post_cookie),.rsp_parent(post_parent),.rsp_child(post_child),
 .rsp_x(out_post_x),.rsp_y(out_post_y),.rsp_upstream(out_post_upstream),.rsp_distance(out_post_distance),.rsp_attrs(out_post_attrs),.rsp_prev_read(out_post_prev_read),.rsp_query(post_query),.rsp_price(post_price),.rsp_version(post_version),.rsp_design(post_design),.busy(post_busy),.fault(post_fault),
 .f_req_valid(pf_valid),.f_req_ready(pf_ready),.f_req_cookie(pf_cookie),.f_req_query(pf_query),.f_req_price(pf_price),.f_rsp_valid(pf_rsp_valid),.f_rsp_ready(pf_rsp_ready),.f_rsp_status(pf_rsp_status),.f_rsp_cookie(pf_rsp_cookie),.f_rsp_size(pf_rsp_size),.f_rsp_query(pf_rsp_query),.f_rsp_price(pf_rsp_price),
 .l_valid(pl_valid),.l_ready(pl_ready),.l_write(pl_write),.l_node(pl_node),.l_value(pl_value),.l_field(pl_field),.l_rsp_valid(pl_rsp_valid),.l_rsp_ready(pl_rsp_ready),.l_status(pl_status),.l_payload(pl_payload),.l_present(pl_present),
 .c_req_valid(pc2_valid),.c_req_ready(pc2_ready),.c_req_cookie(pc2_cookie),.c_req_node(pc2_node),.c_req_query(pc2_query),.c_req_price(pc2_price),.c_rsp_valid(pc2_rsp_valid),.c_rsp_ready(pc2_rsp_ready),.c_rsp_status(pc2_status),.c_rsp_cookie(pc2_rsp_cookie),.c_rsp_node(pc2_rsp_node),.c_rsp_y(pc2_y),.c_rsp_label_prev(pc2_label_prev),.c_rsp_attrs(pc2_attrs),.c_rsp_op(pc2_rsp_op),.c_rsp_query(pc2_rsp_query),.c_rsp_price(pc2_rsp_price),.c_rsp_prev_read(pc2_prev_read));
query_frontier frontier(
 .clk(clk),.rst(rst),.abort(abort||fence_stopped),.query_active(p_active),.query_owned(query_owned),.decision_lock(operation_pending),.close_requested(host_ctrl_valid&&host_ctrl_op==2),.may_close(!core_busy&&!state_lease),
 .query_id(p_active_query),.price(p_active_price),.version(query_version),.ready_for_expand(frontier_expand_ready),.ready_for_close(frontier_close_ready),.initialized(frontier_initialized),.busy(frontier_busy),.fault(frontier_fault),
 .clear_valid(pf_valid),.clear_ready(pf_ready),.clear_cookie(pf_cookie),.clear_query(pf_query),.clear_price(pf_price),.clear_rsp_valid(pf_rsp_valid),.clear_rsp_ready(pf_rsp_ready),.clear_rsp_status(pf_rsp_status),.clear_rsp_cookie(pf_rsp_cookie),.clear_rsp_size(pf_rsp_size),.clear_rsp_query(pf_rsp_query),.clear_rsp_price(pf_rsp_price),
 .seed_valid(seed_valid),.seed_ready(seed_ready),.seed_op(seed_op),.seed_key(seed_key),.seed_id(seed_id),.seed_cookie(seed_cookie),.seed_version(seed_version),.seed_rsp_valid(seed_rsp_valid),.seed_rsp_ready(seed_rsp_ready),.seed_rsp_status(seed_rsp_status),.seed_rsp_cookie(seed_rsp_cookie),.seed_rsp_size(seed_rsp_size),.heap_size(frontier_size));
'''
anchor='reg prep_started,raw_seen,post_started;reg [31:0] held_net,held_parent;';assert anchor in s;s=s.replace(anchor,anchor+'\n'+logic,1)
portslist=['post_l_valid(pl_valid)','post_l_ready(pl_ready)','post_l_write(pl_write)','post_l_node(pl_node)','post_l_value(pl_value)','post_l_field(pl_field)','post_l_rsp_valid(pl_rsp_valid)','post_l_rsp_ready(pl_rsp_ready)','post_l_status(pl_status)','post_l_payload(pl_payload)','post_l_present(pl_present)',
'post_c_req_valid(pc2_valid)','post_c_req_ready(pc2_ready)','post_c_req_cookie(pc2_cookie)','post_c_req_node(pc2_node)','post_c_req_query(pc2_query)','post_c_req_price(pc2_price)','post_c_rsp_valid(pc2_rsp_valid)','post_c_rsp_ready(pc2_rsp_ready)','post_c_rsp_status(pc2_status)','post_c_rsp_cookie(pc2_rsp_cookie)','post_c_rsp_node(pc2_rsp_node)','post_c_rsp_y(pc2_y)','post_c_rsp_label_prev(pc2_label_prev)','post_c_rsp_attrs(pc2_attrs)','post_c_rsp_op(pc2_rsp_op)','post_c_rsp_query(pc2_rsp_query)','post_c_rsp_price(pc2_rsp_price)','post_c_rsp_prev_read(pc2_prev_read)']
s=s.replace('core(\n','core(\n'+''.join('.'+p+',\n'for p in portslist),1)
Path('hardware/variants/candidate_postprev_v1/candidate_postprev_engine.sv').write_text(s)
