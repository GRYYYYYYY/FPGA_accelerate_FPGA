`timescale 1ns/1ps
// Hold the whole query's ingress lease, including gaps between service requests.
module search_host_fence(
 input wire search_busy,search_fault,start_valid,system_admit,
 input wire[15:0]h_valid,output wire[15:0]h_ready,input wire[38911:0]h_payload,
 output wire[15:0]h_rsp_valid,input wire[15:0]h_rsp_ready,output wire[4095:0]h_rsp_payload,
 input wire h_route_valid,output wire h_route_ready,input wire h_recover_valid,output wire h_recover_ready,input wire h_out_ready,
 output wire[15:0]s_valid,input wire[15:0]s_ready,output wire[38911:0]s_payload,
 input wire[15:0]s_rsp_valid,output wire[15:0]s_rsp_ready,input wire[4095:0]s_rsp_payload,
 output wire s_route_valid,input wire s_route_ready,output wire s_recover_valid,input wire s_recover_ready,output wire s_out_ready,
 input wire c_valid,output wire c_ready,input wire[3:0]c_lane,input wire[447:0]c_payload,
 output wire c_rsp_valid,input wire c_rsp_ready,output wire[255:0]c_rsp_payload,input wire c_candidate_ready,
 output wire admit,output wire cancel
);
 wire host_open=!search_busy&&!search_fault;
 assign admit=system_admit&&h_valid==0&&!h_route_valid&&!h_recover_valid;
 assign cancel=h_recover_valid;
 assign h_ready=host_open?s_ready:16'd0;assign h_rsp_valid=host_open?s_rsp_valid:16'd0;assign h_rsp_payload=s_rsp_payload;
 assign h_route_ready=host_open&&s_route_ready;assign s_route_valid=host_open&&h_route_valid;
 assign h_recover_ready=!search_busy&&s_recover_ready;assign s_recover_valid=!search_busy&&h_recover_valid;
 assign s_out_ready=search_busy?c_candidate_ready:h_out_ready;
 // Constant slices avoid a synthesized variable-offset barrel selection.
 reg selected_ready,selected_valid;reg[255:0]selected_reply;
 always @*begin
  selected_ready=0;selected_valid=0;selected_reply=0;
  case(c_lane)
   4'd0:begin selected_ready=s_ready[0];selected_valid=s_rsp_valid[0];selected_reply=s_rsp_payload[0+:256];end
   4'd1:begin selected_ready=s_ready[1];selected_valid=s_rsp_valid[1];selected_reply=s_rsp_payload[256+:256];end
   4'd2:begin selected_ready=s_ready[2];selected_valid=s_rsp_valid[2];selected_reply=s_rsp_payload[512+:256];end
   4'd3:begin selected_ready=s_ready[3];selected_valid=s_rsp_valid[3];selected_reply=s_rsp_payload[768+:256];end
   4'd4:begin selected_ready=s_ready[4];selected_valid=s_rsp_valid[4];selected_reply=s_rsp_payload[1024+:256];end
   4'd5:begin selected_ready=s_ready[5];selected_valid=s_rsp_valid[5];selected_reply=s_rsp_payload[1280+:256];end
   4'd6:begin selected_ready=s_ready[6];selected_valid=s_rsp_valid[6];selected_reply=s_rsp_payload[1536+:256];end
   4'd7:begin selected_ready=s_ready[7];selected_valid=s_rsp_valid[7];selected_reply=s_rsp_payload[1792+:256];end
   4'd8:begin selected_ready=s_ready[8];selected_valid=s_rsp_valid[8];selected_reply=s_rsp_payload[2048+:256];end
   4'd9:begin selected_ready=s_ready[9];selected_valid=s_rsp_valid[9];selected_reply=s_rsp_payload[2304+:256];end
   4'd10:begin selected_ready=s_ready[10];selected_valid=s_rsp_valid[10];selected_reply=s_rsp_payload[2560+:256];end
   4'd11:begin selected_ready=s_ready[11];selected_valid=s_rsp_valid[11];selected_reply=s_rsp_payload[2816+:256];end
   4'd12:begin selected_ready=s_ready[12];selected_valid=s_rsp_valid[12];selected_reply=s_rsp_payload[3072+:256];end
   4'd13:begin selected_ready=s_ready[13];selected_valid=s_rsp_valid[13];selected_reply=s_rsp_payload[3328+:256];end
   4'd14:begin selected_ready=s_ready[14];selected_valid=s_rsp_valid[14];selected_reply=s_rsp_payload[3584+:256];end
   4'd15:begin selected_ready=s_ready[15];selected_valid=s_rsp_valid[15];selected_reply=s_rsp_payload[3840+:256];end
  endcase
 end
 assign c_ready=search_busy&&selected_ready;assign c_rsp_valid=search_busy&&selected_valid;assign c_rsp_payload=selected_reply;
 generate for(genvar i=0;i<16;i=i+1)begin:lanes
  assign s_valid[i]=search_busy?(c_valid&&c_lane==i):(host_open&&h_valid[i]);
  assign s_payload[i*2432+:2432]=search_busy?{1984'd0,c_payload}:h_payload[i*2432+:2432];
  assign s_rsp_ready[i]=search_busy?(c_rsp_ready&&c_lane==i):(host_open&&h_rsp_ready[i]);
 end endgenerate
endmodule
