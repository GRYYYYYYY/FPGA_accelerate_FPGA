`timescale 1ns/1ps
// 192 bytes: bitmap8, eight records (136 data bits +24 zero), 31 zero tail.
// Decode publishes nothing until entire page checked and commit_ok accepted.
module scratch_page_codec_small(
 input wire clk,rst,start_valid,output wire start_ready,input wire start_decode,
 input wire cancel,output wire busy,
 input wire record_in_valid,output wire record_in_ready,
 input wire [2:0] record_in_offset,input wire record_in_present,input wire [159:0] record_in_payload,
 output wire record_out_valid,input wire record_out_ready,
 output wire [2:0] record_out_offset,output wire record_out_present,output wire [159:0] record_out_payload,
 input wire raw_in_valid,output wire raw_in_ready,input wire [511:0] raw_in_data,
 output wire raw_out_valid,input wire raw_out_ready,output wire [511:0] raw_out_data,output wire raw_out_last,
 input wire commit_valid,output wire commit_ready,input wire commit_ok,
 output reg done_valid,input wire done_ready,output reg done_error
);
 localparam IDLE=0,ENCODE=1,RAW_OUT=2,RAW_IN=3,CHECK=4,COMMIT=5,RECORD_OUT=6;
 reg [2:0] state,node;
 reg [1:0] beat;
 reg [1535:0] page;
 reg bad;
 wire [159:0] selected=page[8+node*160 +:160];
 assign busy=state!=IDLE || done_valid;
 assign start_ready=!rst && !cancel && state==IDLE && !done_valid;
 assign record_in_ready=!rst && !cancel && state==ENCODE;
 assign raw_in_ready=!rst && !cancel && state==RAW_IN;
 assign raw_out_valid=!rst && !cancel && state==RAW_OUT;
 assign raw_out_data=page[beat*512 +:512];
 assign raw_out_last=beat==2;
 assign commit_ready=!rst && !cancel && state==COMMIT;
 assign record_out_valid=!rst && !cancel && state==RECORD_OUT;
 assign record_out_offset=node;
 assign record_out_present=page[node];
 assign record_out_payload=selected;
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;node<=0;beat<=0;page<=0;bad<=0;done_valid<=0;done_error<=0;end
  else if(cancel && state!=IDLE)begin state<=IDLE;done_valid<=1;done_error<=1;end
  else begin
   if(done_valid && done_ready)done_valid<=0;
   case(state)
    IDLE:if(start_valid && start_ready)begin
     page<=0;node<=0;beat<=0;bad<=0;done_error<=0;
     state<=start_decode?RAW_IN:ENCODE;
    end
    ENCODE:if(record_in_valid && record_in_ready)begin
     if(record_in_offset!=node || record_in_payload[159:136]!=0 || (!record_in_present && record_in_payload!=0))begin
      state<=IDLE;done_valid<=1;done_error<=1;
     end else begin
      page[node]<=record_in_present;page[8+node*160 +:160]<=record_in_payload;
      if(node==7)begin state<=RAW_OUT;beat<=0;end else node<=node+1'b1;
     end
    end
    RAW_OUT:if(raw_out_valid && raw_out_ready)begin
     if(beat==2)begin state<=IDLE;done_valid<=1;end else beat<=beat+1'b1;
    end
    RAW_IN:if(raw_in_valid && raw_in_ready)begin
     page[beat*512 +:512]<=raw_in_data;
     if(beat==2)begin state<=CHECK;node<=0;end else beat<=beat+1'b1;
    end
    CHECK:begin
     if(selected[159:136]!=0 || (!page[node] && selected!=0))bad<=1;
     if(node==7)state<=COMMIT;else node<=node+1'b1;
    end
    COMMIT:if(commit_valid && commit_ready)begin
     if(bad || !commit_ok)begin state<=IDLE;done_valid<=1;done_error<=1;end
     else begin state<=RECORD_OUT;node<=0;end
    end
    RECORD_OUT:if(record_out_valid && record_out_ready)begin
     if(node==7)begin state<=IDLE;done_valid<=1;end else node<=node+1'b1;
    end
    default:begin state<=IDLE;done_valid<=1;done_error<=1;end
   endcase
  end
 end
endmodule
