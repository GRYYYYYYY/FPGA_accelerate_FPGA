`timescale 1ns/1ps
module tb_search_mux_equivalence;
reg search_busy=0;
reg search_fault=0;
reg start_valid=0;
reg system_admit=0;
reg [15:0] h_valid=0;
reg [38911:0] h_payload=0;
reg [15:0] h_rsp_ready=0;
reg h_route_valid=0;
reg h_recover_valid=0;
reg h_out_ready=0;
reg [15:0] s_ready=0;
reg [15:0] s_rsp_valid=0;
reg [4095:0] s_rsp_payload=0;
reg s_route_ready=0;
reg s_recover_ready=0;
reg c_valid=0;
reg [3:0] c_lane=0;
reg [447:0] c_payload=0;
reg c_rsp_ready=0;
reg c_candidate_ready=0;
wire [15:0] old_h_ready,new_h_ready;
wire [15:0] old_h_rsp_valid,new_h_rsp_valid;
wire [4095:0] old_h_rsp_payload,new_h_rsp_payload;
wire old_h_route_ready,new_h_route_ready;
wire old_h_recover_ready,new_h_recover_ready;
wire [15:0] old_s_valid,new_s_valid;
wire [38911:0] old_s_payload,new_s_payload;
wire [15:0] old_s_rsp_ready,new_s_rsp_ready;
wire old_s_route_valid,new_s_route_valid;
wire old_s_recover_valid,new_s_recover_valid;
wire old_s_out_ready,new_s_out_ready;
wire old_c_ready,new_c_ready;
wire old_c_rsp_valid,new_c_rsp_valid;
wire [255:0] old_c_rsp_payload,new_c_rsp_payload;
wire old_admit,new_admit;
wire old_cancel,new_cancel;
search_host_fence_reference old_dut(.search_busy(search_busy),.search_fault(search_fault),.start_valid(start_valid),.system_admit(system_admit),.h_valid(h_valid),.h_payload(h_payload),.h_rsp_ready(h_rsp_ready),.h_route_valid(h_route_valid),.h_recover_valid(h_recover_valid),.h_out_ready(h_out_ready),.s_ready(s_ready),.s_rsp_valid(s_rsp_valid),.s_rsp_payload(s_rsp_payload),.s_route_ready(s_route_ready),.s_recover_ready(s_recover_ready),.c_valid(c_valid),.c_lane(c_lane),.c_payload(c_payload),.c_rsp_ready(c_rsp_ready),.c_candidate_ready(c_candidate_ready),.h_ready(old_h_ready),.h_rsp_valid(old_h_rsp_valid),.h_rsp_payload(old_h_rsp_payload),.h_route_ready(old_h_route_ready),.h_recover_ready(old_h_recover_ready),.s_valid(old_s_valid),.s_payload(old_s_payload),.s_rsp_ready(old_s_rsp_ready),.s_route_valid(old_s_route_valid),.s_recover_valid(old_s_recover_valid),.s_out_ready(old_s_out_ready),.c_ready(old_c_ready),.c_rsp_valid(old_c_rsp_valid),.c_rsp_payload(old_c_rsp_payload),.admit(old_admit),.cancel(old_cancel));
search_host_fence new_dut(.search_busy(search_busy),.search_fault(search_fault),.start_valid(start_valid),.system_admit(system_admit),.h_valid(h_valid),.h_payload(h_payload),.h_rsp_ready(h_rsp_ready),.h_route_valid(h_route_valid),.h_recover_valid(h_recover_valid),.h_out_ready(h_out_ready),.s_ready(s_ready),.s_rsp_valid(s_rsp_valid),.s_rsp_payload(s_rsp_payload),.s_route_ready(s_route_ready),.s_recover_ready(s_recover_ready),.c_valid(c_valid),.c_lane(c_lane),.c_payload(c_payload),.c_rsp_ready(c_rsp_ready),.c_candidate_ready(c_candidate_ready),.h_ready(new_h_ready),.h_rsp_valid(new_h_rsp_valid),.h_rsp_payload(new_h_rsp_payload),.h_route_ready(new_h_route_ready),.h_recover_ready(new_h_recover_ready),.s_valid(new_s_valid),.s_payload(new_s_payload),.s_rsp_ready(new_s_rsp_ready),.s_route_valid(new_s_route_valid),.s_recover_valid(new_s_recover_valid),.s_out_ready(new_s_out_ready),.c_ready(new_c_ready),.c_rsp_valid(new_c_rsp_valid),.c_rsp_payload(new_c_rsp_payload),.admit(new_admit),.cancel(new_cancel));
integer checks=0;reg[31:0]rng=32'h6170beef;
 task step;begin #1;
 if({old_h_ready,old_h_rsp_valid,old_h_rsp_payload,old_h_route_ready,old_h_recover_ready,old_s_valid,old_s_payload,old_s_rsp_ready,old_s_route_valid,old_s_recover_valid,old_s_out_ready,old_c_ready,old_c_rsp_valid,old_c_rsp_payload,old_admit,old_cancel}!=={new_h_ready,new_h_rsp_valid,new_h_rsp_payload,new_h_route_ready,new_h_recover_ready,new_s_valid,new_s_payload,new_s_rsp_ready,new_s_route_valid,new_s_recover_valid,new_s_out_ready,new_c_ready,new_c_rsp_valid,new_c_rsp_payload,new_admit,new_cancel})$fatal(1,"mux equivalence check=%0d lane=%0d",checks,c_lane);
 checks=checks+1;end endtask
 function[31:0]random_word(input[31:0]v);begin random_word=v*32'd1664525+32'd1013904223;end endfunction
 initial begin
  search_busy=1;c_valid=1;c_rsp_ready=1;s_ready=16'hffff;s_rsp_valid=16'hffff;
  // Every response input bit, for every known lane. Distinct payload routing and isolation.
  for(integer lane=0;lane<16;lane=lane+1)begin
   c_lane=lane;
   for(integer bit_index=0;bit_index<4096;bit_index=bit_index+1)begin
    s_rsp_payload=4096'd1<<bit_index;step;
   end
  end
  // Every combination of eight ownership/response gates, on every lane.
  for(integer lane=0;lane<16;lane=lane+1)begin
   c_lane=lane;
   for(integer gates=0;gates<256;gates=gates+1)begin
    {search_busy,search_fault,system_admit,h_route_valid,h_recover_valid,c_valid,c_rsp_ready,c_candidate_ready}=gates;
    rng=random_word(rng);h_valid=rng[15:0];h_rsp_ready=rng[31:16];
    rng=random_word(rng);s_ready=rng[15:0];s_rsp_valid=rng[31:16];
    start_valid=rng[0];h_out_ready=rng[1];s_route_ready=rng[2];s_recover_ready=rng[3];
    for(integer j=0;j<128;j=j+1)begin rng=random_word(rng);s_rsp_payload[j*32+:32]=rng;end
    for(integer j=0;j<1216;j=j+1)begin rng=random_word(rng);h_payload[j*32+:32]=rng;end
    for(integer j=0;j<14;j=j+1)begin rng=random_word(rng);c_payload[j*32+:32]=rng;end
    step;
   end
  end
  if(checks!=69632)$fatal(1,"coverage");
  $display("SEARCH_MUX_EQUIVALENCE_PASS checks=%0d",checks);$finish;
 end
endmodule
