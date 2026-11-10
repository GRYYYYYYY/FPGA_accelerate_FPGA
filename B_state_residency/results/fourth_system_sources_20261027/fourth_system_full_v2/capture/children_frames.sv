`timescale 1ns/1ps
// Static records only. Consumer MUST re-read all dynamic labels after each resume.
// begin_ready may accept an over-depth request to report fault, but capture_active
// remains zero: the caller must launch its expander only after capture_active.
module children_frames #(parameter integer DEPTH=64,CAPACITY=256,CONTEXT_BITS=512)(
 input wire clk,rst,abort,
 input wire begin_valid,output wire begin_ready,input wire[CONTEXT_BITS-1:0]begin_context,
 input wire child_valid,output wire child_ready,input wire[351:0]child_record,
 input wire finish_valid,output wire finish_ready,input wire[3:0]finish_status,input wire[31:0]finish_count,
 output wire capture_active,output reg fault,output reg[3:0]error_code,
 output wire[31:0]depth,
 output wire frame_valid,output wire[CONTEXT_BITS-1:0]frame_context,
 output wire item_valid,input wire item_ready,output wire[351:0]item_record,
 output wire frame_done,input wire pop_valid,output wire pop_ready
);
 reg[31:0]level,counts[0:DEPTH-1],cursors[0:DEPTH-1];
 reg[CONTEXT_BITS-1:0]contexts[0:DEPTH-1];
 reg[351:0]records[0:DEPTH*CAPACITY-1];
 reg capturing,discarding;reg presented[0:DEPTH-1];
 wire has_frame=level!=0;
 wire[31:0]top=has_frame?level-1:0;
 wire push=begin_valid&&begin_ready;
 assign depth=level;
 assign capture_active=capturing;
 assign begin_ready=!rst&&!abort&&!fault&&!capturing&&!pop_valid;
 // Once exposed capture is accepted, drain its producer even after abort/overflow.
 assign child_ready=!rst&&capturing&&!finish_valid;
 assign finish_ready=!rst&&capturing;
 assign frame_valid=!rst&&!abort&&!fault&&!capturing&&has_frame&&!push;
 assign frame_context=(frame_valid||(has_frame&&presented[top]))?contexts[top]:{CONTEXT_BITS{1'b0}};
 assign item_valid=!rst&&!capturing&&has_frame&&!push&&((frame_valid&&cursors[top]<counts[top])||presented[top]);
 assign item_record=item_valid?records[top*CAPACITY+cursors[top]]:352'b0;
 assign frame_done=!rst&&!capturing&&has_frame&&!push&&((fault||abort)?!presented[top]:cursors[top]==counts[top]);
 assign pop_ready=frame_done&&!begin_valid;
 task stop(input[3:0]code);
  begin fault<=1;if(!fault)error_code<=code;discarding<=1;end
 endtask
 always @(posedge clk)begin
  if(rst)begin level<=0;capturing<=0;discarding<=0;fault<=0;error_code<=0;for(integer i=0;i<DEPTH;i=i+1)presented[i]<=0;end
  else begin
   if(push)begin
    if(level>=DEPTH)stop(1);
    else begin contexts[level]<=begin_context;counts[level]<=0;cursors[level]<=0;presented[level]<=0;level<=level+1;capturing<=1;discarding<=0;end
   end
   if(child_valid&&child_ready)begin
    if(!discarding&&!fault)begin
     if(counts[top]>=CAPACITY)stop(2);
     else begin records[top*CAPACITY+counts[top]]<=child_record;counts[top]<=counts[top]+1;end
    end
   end
   if(finish_valid&&finish_ready)begin
    capturing<=0;
    if(!fault&&!discarding&&(finish_status!=0||finish_count!=counts[top]))stop(3);
   end
   if(item_valid)begin presented[top]<=!item_ready;if(item_ready)cursors[top]<=cursors[top]+1;end
   if(pop_valid&&pop_ready)begin level<=level-1;presented[top]<=0;end
   if(abort)stop(4);
  end
 end
endmodule
