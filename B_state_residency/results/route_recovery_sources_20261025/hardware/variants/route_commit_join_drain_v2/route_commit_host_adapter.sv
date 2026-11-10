`timescale 1ns/1ps
// Caller fences every other search/config/frontier entry with block_external.
module route_commit_host_adapter #(parameter integer MAX_PATH=32,MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,admit,backend_drained,
 input wire[1:0]active_query,input wire[3:0]active_price,input wire[31:0]active_version,input wire[63:0]active_design,
 input wire req_valid,output wire req_ready,input wire req_op,req_slot,input wire[31:0]req_cookie,req_source,req_sink,req_net,req_sequence,
 output wire rsp_valid,input wire rsp_ready,output wire[3:0]rsp_status,output wire[31:0]rsp_cookie,rsp_nodes,rsp_acked,
 output wire fault,busy,block_external,output wire[1:0]slot_valid,
 input wire h_l_valid,output wire h_l_ready,input wire h_l_write,input wire[31:0]h_l_node,h_l_value,input wire[2:0]h_l_field,
 output wire h_l_rsp_valid,input wire h_l_rsp_ready,output wire[3:0]h_l_status,output wire h_l_present,output wire[159:0]h_l_payload,
 input wire h_o_valid,output wire h_o_ready,input wire[2:0]h_o_op,input wire[31:0]h_o_node,h_o_net,h_o_cookie,
 output wire h_o_rsp_valid,input wire h_o_rsp_ready,output wire[3:0]h_o_status,output wire[31:0]h_o_rsp_cookie,h_o_count,h_o_occupancy,output wire h_o_will_overuse,
 output wire b_l_valid,input wire b_l_ready,output wire b_l_write,output wire[31:0]b_l_node,b_l_value,output wire[2:0]b_l_field,
 input wire b_l_rsp_valid,output wire b_l_rsp_ready,input wire[3:0]b_l_status,input wire b_l_present,input wire[159:0]b_l_payload,
 output wire b_o_valid,input wire b_o_ready,output wire[2:0]b_o_op,output wire[31:0]b_o_node,b_o_net,b_o_cookie,
 input wire b_o_rsp_valid,output wire b_o_rsp_ready,input wire[3:0]b_o_status,input wire[31:0]b_o_rsp_cookie,b_o_count,b_o_occupancy,input wire b_o_will_overuse
);
 reg held;wire core_rsp_valid;
 assign rsp_valid=core_rsp_valid&&backend_drained;
 wire c_ready,c_busy,c_fault,l_valid,l_ready,l_rsp_valid,l_rsp_ready,o_valid,o_ready,o_rsp_valid,o_rsp_ready;
 wire[31:0]l_node,o_node,o_net,o_cookie;wire[2:0]o_op;
 assign block_external=held||c_busy||c_fault;
 assign busy=block_external;assign fault=c_fault;
 assign req_ready=c_ready&&admit&&!held&&backend_drained;
 route_commit_controller #(.MAX_PATH(MAX_PATH),.MAX_CYCLES(MAX_CYCLES)) controller(
 .clk(clk),.rst(rst),.abort(abort),.active(active),.lease(held||admit),.active_query(active_query),.active_price(active_price),.active_version(active_version),.active_design(active_design),
 .req_valid(req_valid&&admit&&!held&&backend_drained),.req_ready(c_ready),.req_op(req_op),.req_slot(req_slot),.req_cookie(req_cookie),.req_source(req_source),.req_sink(req_sink),.req_net(req_net),.req_sequence(req_sequence),
 .rsp_valid(core_rsp_valid),.rsp_ready(rsp_ready&&backend_drained),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.rsp_nodes(rsp_nodes),.rsp_acked(rsp_acked),.busy(c_busy),.fault(c_fault),.slot_valid(slot_valid),
 .l_valid(l_valid),.l_ready(l_ready),.l_node(l_node),.l_rsp_valid(l_rsp_valid),.l_rsp_ready(l_rsp_ready),.l_status(b_l_status),.l_present(b_l_present),.l_payload(b_l_payload),
 .o_valid(o_valid),.o_ready(o_ready),.o_op(o_op),.o_node(o_node),.o_net(o_net),.o_cookie(o_cookie),.o_rsp_valid(o_rsp_valid),.o_rsp_ready(o_rsp_ready),.o_status(b_o_status),.o_rsp_cookie(b_o_rsp_cookie));
 always @(posedge clk)begin
  if(rst)held<=0;
  else if(req_valid&&req_ready)held<=1;
  else if(held&&!c_busy&&!c_fault&&backend_drained)held<=0;
 end
 assign b_l_valid=held?l_valid:h_l_valid&&!block_external;
 assign b_l_write=held?1'b0:h_l_write;assign b_l_node=held?l_node:h_l_node;assign b_l_field=held?3'b0:h_l_field;assign b_l_value=held?32'b0:h_l_value;
 assign l_ready=held&&b_l_ready;assign l_rsp_valid=held&&b_l_rsp_valid;assign b_l_rsp_ready=held?l_rsp_ready:h_l_rsp_ready&&!block_external;
 assign h_l_ready=!block_external&&b_l_ready;assign h_l_rsp_valid=!block_external&&b_l_rsp_valid;
 assign h_l_status=b_l_status;assign h_l_present=b_l_present;assign h_l_payload=b_l_payload;
 assign b_o_valid=held?o_valid:h_o_valid&&!block_external;assign b_o_op=held?o_op:h_o_op;assign b_o_node=held?o_node:h_o_node;assign b_o_net=held?o_net:h_o_net;assign b_o_cookie=held?o_cookie:h_o_cookie;
 assign o_ready=held&&b_o_ready;assign o_rsp_valid=held&&b_o_rsp_valid;assign b_o_rsp_ready=held?o_rsp_ready:h_o_rsp_ready&&!block_external;
 assign h_o_ready=!block_external&&b_o_ready;assign h_o_rsp_valid=!block_external&&b_o_rsp_valid;
 assign h_o_status=b_o_status;assign h_o_rsp_cookie=b_o_rsp_cookie;assign h_o_count=b_o_count;assign h_o_occupancy=b_o_occupancy;assign h_o_will_overuse=b_o_will_overuse;
endmodule
