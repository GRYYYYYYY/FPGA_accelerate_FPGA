`timescale 1ns/1ps
module checkpoint_lease_guard(
 input wire clk,rst,acquire_valid,release_valid,healthy,retired,no_offers,route_retired,command_busy,command_valid,test_reset,
 output wire acquire_ready,release_ready,safe,output reg owned
);
 assign acquire_ready=!rst&&!owned&&healthy&&route_retired&&no_offers&&!command_busy&&!test_reset;
 assign release_ready=!rst&&owned&&retired&&route_retired&&!command_busy&&!command_valid&&!test_reset;
 assign safe=!rst&&owned&&healthy;
 always @(posedge clk)begin
  if(rst)owned<=0;
  else if(acquire_valid&&acquire_ready)owned<=1;
  else if(release_valid&&release_ready)owned<=0;
 end
endmodule
