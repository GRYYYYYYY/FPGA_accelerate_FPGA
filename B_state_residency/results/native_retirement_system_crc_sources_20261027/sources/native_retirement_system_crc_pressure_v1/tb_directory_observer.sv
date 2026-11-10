`timescale 1ns/1ps
// Passive simulation protocol trace. Excluded from production synthesis.
module tb_directory_observer(input wire clk,rst,cmd_valid,cmd_ready,rsp_valid,rsp_ready,memory_success,fence_retired,any_fault,
input wire[2:0]cmd_op,rsp_status,input wire[26:0]cmd_owner,input wire[31:0]cmd_frame,rsp_frame,allocated,leased,input wire[71:0]cmd_cookie,input wire rsp_published);
integer fd,cycles=0;reg prior_rst=0;string path;
initial begin if(!$value$plusargs("directorylog=%s",path))$fatal(1,"directory trace missing");fd=$fopen(path,"w");if(!fd)$fatal(1,"directory trace open");$fdisplay(fd,"H %m");end
always @(posedge clk)begin
 cycles<=cycles+1;
 if(rst&&!prior_rst)begin $fdisplay(fd,"RESET %0d",cycles);$fflush(fd);end
 if(!rst)begin
  if(cmd_valid&&cmd_ready)$fdisplay(fd,"C %0d %0d %0d %0d %018h %0d %0d",cycles,cmd_op,cmd_owner,cmd_frame,cmd_cookie,memory_success,fence_retired);
  if(rsp_valid&&rsp_ready)$fdisplay(fd,"R %0d %0d %0d %0d %0d %08h %0d",cycles,rsp_status,rsp_frame,rsp_published,allocated,leased,any_fault);
 end
 prior_rst<=rst;
end
endmodule
