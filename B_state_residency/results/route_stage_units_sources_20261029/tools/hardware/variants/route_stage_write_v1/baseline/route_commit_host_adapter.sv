`timescale 1ns/1ps
// Caller fences every other search/config/frontier entry with block_external.
module route_commit_host_adapter #(parameter integer PATH_SLOTS=2,PATH_SLOT_BITS=(PATH_SLOTS<=2?1:$clog2(PATH_SLOTS)),MAX_PATH=32,MAX_CYCLES=1048576)(
input wire cp_valid,cp_restore,
output wire cp_ready,cp_busy,cp_rsp_valid,input wire cp_rsp_ready,
output wire[3:0]cp_status,output wire[31:0]cp_crc,
input wire[63:0]cp_design,input wire[31:0]cp_nodes,cp_nets,cp_expected_crc,
input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,
input wire cp_test_reset,output wire pc_route_retired,
input wire pc_hold,pc_safe,
 input wire clk,rst,abort,active,admit,backend_drained,
 output wire j_valid,input wire j_ready,output wire[31:0]j_node,j_net,output wire[2:0]j_op,
 input wire[1:0]active_query,input wire[3:0]active_price,input wire[31:0]active_version,input wire[63:0]active_design,
 input wire req_valid,output wire req_ready,input wire req_op,input wire[PATH_SLOT_BITS-1:0]req_slot,input wire[31:0]req_cookie,req_source,req_sink,req_net,req_sequence,
 output wire rsp_valid,input wire rsp_ready,output wire[3:0]rsp_status,output wire[31:0]rsp_cookie,rsp_nodes,rsp_acked,
 output wire fault,busy,block_external,output wire[PATH_SLOTS-1:0]slot_valid,
 input wire h_l_valid,output wire h_l_ready,input wire h_l_write,input wire[31:0]h_l_node,h_l_value,input wire[2:0]h_l_field,
 output wire h_l_rsp_valid,input wire h_l_rsp_ready,output wire[3:0]h_l_status,output wire h_l_present,output wire[159:0]h_l_payload,
 input wire h_o_valid,output wire h_o_ready,input wire[2:0]h_o_op,input wire[31:0]h_o_node,h_o_net,h_o_cookie,
 output wire h_o_rsp_valid,input wire h_o_rsp_ready,output wire[3:0]h_o_status,output wire[31:0]h_o_rsp_cookie,h_o_count,h_o_occupancy,output wire h_o_will_overuse,
 output wire b_l_valid,input wire b_l_ready,output wire b_l_write,output wire[31:0]b_l_node,b_l_value,output wire[2:0]b_l_field,
 input wire b_l_rsp_valid,output wire b_l_rsp_ready,input wire[3:0]b_l_status,input wire b_l_present,input wire[159:0]b_l_payload,
 output wire b_o_valid,input wire b_o_ready,output wire[2:0]b_o_op,output wire[31:0]b_o_node,b_o_net,b_o_cookie,
 input wire b_o_rsp_valid,output wire b_o_rsp_ready,input wire[3:0]b_o_status,input wire[31:0]b_o_rsp_cookie,b_o_count,b_o_occupancy,input wire b_o_will_overuse
);
 reg held;wire core_rsp_valid;wire cp_core_ready;wire owner_pending;reg cp_reset_held;
 assign cp_ready=pc_hold&&!cp_reset_held&&cp_core_ready;
 always @(posedge clk)begin
  if(rst)cp_reset_held<=0;
  else cp_reset_held<=cp_test_reset&&pc_hold&&pc_safe&&!held&&!owner_pending&&!cp_busy&&!cp_valid;
 end
 wire c_ready,c_busy,c_fault,c_idle_fault,l_valid,l_ready,l_rsp_valid,l_rsp_ready,o_valid,o_ready,o_rsp_valid,o_rsp_ready;
 wire[31:0]l_node,o_node,o_net,o_cookie;wire[2:0]o_op;

 reg owner_send,owner_wait;reg[2:0]buffer_op;reg[31:0]buffer_node,buffer_net,buffer_cookie;
 assign owner_pending=owner_send||owner_wait;
 assign pc_route_retired=!held&&!owner_pending&&!c_busy&&!core_rsp_valid&&!l_valid&&!o_valid;
 assign j_valid=!rst&&held&&o_valid&&!owner_pending;
 assign j_node=o_node;assign j_net=o_net;assign j_op=o_op;
 always @(posedge clk)begin
  if(rst)begin owner_send<=0;owner_wait<=0;buffer_op<=0;buffer_node<=0;buffer_net<=0;buffer_cookie<=0;end
  else begin
   if(j_valid&&j_ready)begin owner_send<=1;buffer_op<=o_op;buffer_node<=o_node;buffer_net<=o_net;buffer_cookie<=o_cookie;end
   if(held&&owner_send&&b_o_ready)begin owner_send<=0;owner_wait<=1;end
   if(held&&b_o_rsp_valid&&b_o_rsp_ready)owner_wait<=0;
  end
 end
 assign rsp_valid=core_rsp_valid&&backend_drained;
 assign block_external=held||c_busy||c_idle_fault;
 assign busy=block_external;assign fault=c_fault;
 assign req_ready=c_ready&&admit&&!held&&backend_drained;
 route_commit_controller #(.FACTORED_PATH_WRITES(1),.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),.MAX_PATH(MAX_PATH),.MAX_CYCLES(MAX_CYCLES)) controller(
 .cp_valid(cp_valid&&pc_hold&&!cp_reset_held),.cp_restore(cp_restore),.cp_ready(cp_core_ready),.cp_busy(cp_busy),.cp_rsp_valid(cp_rsp_valid),.cp_rsp_ready(cp_rsp_ready),.cp_status(cp_status),.cp_crc(cp_crc),.cp_design(cp_design),.cp_nodes(cp_nodes),.cp_nets(cp_nets),.cp_expected_crc(cp_expected_crc),.cp_s_valid(cp_s_valid),.cp_s_ready(cp_s_ready),.cp_s_index(cp_s_index),.cp_s_data(cp_s_data),.cp_s_last(cp_s_last),.cp_m_valid(cp_m_valid),.cp_m_ready(cp_m_ready),.cp_m_index(cp_m_index),.cp_m_data(cp_m_data),.cp_m_last(cp_m_last),.cp_safe(pc_safe&&pc_hold&&backend_drained&&!held&&!owner_pending),
 .clk(clk),.rst(rst||cp_reset_held),.abort(abort),.active(active),.lease(held||admit||pc_hold),.active_query(active_query),.active_price(active_price),.active_version(active_version),.active_design(active_design),
 .req_valid(req_valid&&admit&&!held&&backend_drained),.req_ready(c_ready),.req_op(req_op),.req_slot(req_slot),.req_cookie(req_cookie),.req_source(req_source),.req_sink(req_sink),.req_net(req_net),.req_sequence(req_sequence),
 .rsp_valid(core_rsp_valid),.rsp_ready(rsp_ready&&backend_drained),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.rsp_nodes(rsp_nodes),.rsp_acked(rsp_acked),.busy(c_busy),.fault(c_fault),.idle_fault(c_idle_fault),.slot_valid(slot_valid),
 .l_valid(l_valid),.l_ready(l_ready),.l_node(l_node),.l_rsp_valid(l_rsp_valid),.l_rsp_ready(l_rsp_ready),.l_status(b_l_status),.l_present(b_l_present),.l_payload(b_l_payload),
 .o_valid(o_valid),.o_ready(o_ready),.o_op(o_op),.o_node(o_node),.o_net(o_net),.o_cookie(o_cookie),.o_rsp_valid(o_rsp_valid),.o_rsp_ready(o_rsp_ready),.o_status(b_o_status),.o_rsp_cookie(b_o_rsp_cookie));
 always @(posedge clk)begin
  if(rst)held<=0;
  else if(req_valid&&req_ready)held<=1;
  else if(held&&!c_busy&&!c_fault&&backend_drained&&!owner_pending)held<=0;
 end
 assign b_l_valid=held?l_valid:h_l_valid&&!block_external;
 assign b_l_write=held?1'b0:h_l_write;assign b_l_node=held?l_node:h_l_node;assign b_l_field=held?3'b0:h_l_field;assign b_l_value=held?32'b0:h_l_value;
 assign l_ready=held&&b_l_ready;assign l_rsp_valid=held&&b_l_rsp_valid;assign b_l_rsp_ready=held?l_rsp_ready:h_l_rsp_ready&&!block_external;
 assign h_l_ready=!block_external&&b_l_ready;assign h_l_rsp_valid=!block_external&&b_l_rsp_valid;
 assign h_l_status=b_l_status;assign h_l_present=b_l_present;assign h_l_payload=b_l_payload;
 assign b_o_valid=held?owner_send:h_o_valid&&!block_external;assign b_o_op=held?buffer_op:h_o_op;assign b_o_node=held?buffer_node:h_o_node;assign b_o_net=held?buffer_net:h_o_net;assign b_o_cookie=held?buffer_cookie:h_o_cookie;
 assign o_ready=held&&!owner_pending&&j_ready;assign o_rsp_valid=held&&b_o_rsp_valid;assign b_o_rsp_ready=held?o_rsp_ready:h_o_rsp_ready&&!block_external;
 assign h_o_ready=!block_external&&b_o_ready;assign h_o_rsp_valid=!block_external&&b_o_rsp_valid;
 assign h_o_status=b_o_status;assign h_o_rsp_cookie=b_o_rsp_cookie;assign h_o_count=b_o_count;assign h_o_occupancy=b_o_occupancy;assign h_o_will_overuse=b_o_will_overuse;
endmodule
