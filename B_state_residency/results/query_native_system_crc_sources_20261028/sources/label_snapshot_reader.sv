`timescale 1ns/1ps
module label_snapshot_reader #(parameter integer FRAMES=16384,INDEX_BITS=14)(
 input wire clk,rst,lease,source_drained,cmd_valid,output wire cmd_ready,
 input wire[1:0]cmd_query,input wire[3:0]cmd_price,input wire[31:0]cmd_nodes,cmd_cookie,
 output wire busy,rsp_valid,input wire rsp_ready,output reg[3:0]status,output reg[31:0]rsp_cookie,record_count,record_crc,page_count,
 output reg receipt_valid,
 output wire scan_valid,input wire scan_ready,output wire[INDEX_BITS-1:0]scan_frame,
 input wire scan_rsp_valid,output wire scan_rsp_ready,input wire[2:0]scan_status,input wire[INDEX_BITS-1:0]scan_result_frame,input wire[26:0]scan_owner,input wire scan_published,
 output wire[31:0]m_araddr,output wire m_arvalid,input wire m_arready,
 input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output wire record_valid,input wire record_ready,output wire[31:0]record_node,output wire[159:0]record_payload
);
 localparam IDLE=0,SCAN_SEND=1,SCAN_WAIT=2,READ_AR=3,READ_R=4,DECODE=5,EMIT=6,DONE=7;
 reg[2:0]state;reg[31:0]frame,nodes;reg[5:0]context_id;reg[20:0]page;reg[1:0]chunk;reg[3:0]offset;reg[1535:0]data;reg[31:0]crc;reg stopped;
 wire unsafe=!lease||!source_drained;
 assign busy=state!=IDLE;assign cmd_ready=state==IDLE;assign rsp_valid=state==DONE;
 assign scan_valid=state==SCAN_SEND&&frame<FRAMES;assign scan_frame=frame[INDEX_BITS-1:0];assign scan_rsp_ready=state==SCAN_WAIT;
 assign m_araddr=frame*192+chunk*64;assign m_arvalid=state==READ_AR;assign m_rready=state==READ_R;
 assign record_valid=state==EMIT;assign record_node={8'd0,page,3'd0}+offset;assign record_payload=data[8+offset*160+:160];
 function[31:0]word_crc(input[31:0]c0,w);reg[31:0]c;integer j;begin c=c0;for(j=0;j<32;j=j+1)c=(c[0]^w[j])?((c>>1)^32'hedb88320):(c>>1);word_crc=c;end endfunction
 function[31:0]row_crc(input[31:0]c0,node,input[159:0]v);reg[31:0]c;integer j;begin c=word_crc(c0,node);for(j=0;j<5;j=j+1)c=word_crc(c,v[j*32+:32]);row_crc=c;end endfunction
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;status<=0;rsp_cookie<=0;record_count<=0;record_crc<=0;page_count<=0;receipt_valid<=0;frame<=0;nodes<=0;context_id<=0;page<=0;chunk<=0;offset<=0;data<=0;crc<=32'hffffffff;stopped<=0;end
  else begin
   if(state!=IDLE&&state!=DONE&&unsafe)stopped<=1;
   case(state)
    IDLE:if(cmd_valid)begin
     status<=0;rsp_cookie<=cmd_cookie;record_count<=0;record_crc<=0;page_count<=0;receipt_valid<=0;frame<=0;nodes<=cmd_nodes;context_id<={cmd_price,cmd_query};crc<=32'hffffffff;stopped<=0;
     if(unsafe||cmd_nodes==0||cmd_nodes>16777216)begin status<=1;state<=DONE;end else state<=SCAN_SEND;
    end
    SCAN_SEND:begin
     if(frame==FRAMES)begin if(stopped||unsafe)status<=2;else begin record_crc<=~crc;receipt_valid<=1;end state<=DONE;end
     else if(scan_ready)state<=SCAN_WAIT;
    end
    SCAN_WAIT:if(scan_rsp_valid)begin
     if(stopped||unsafe)begin status<=2;state<=DONE;end
     else if(scan_status==6)begin record_crc<=~crc;receipt_valid<=1;state<=DONE;end
     else if(scan_status!=0||scan_result_frame!=frame[INDEX_BITS-1:0])begin status<=3;state<=DONE;end
     else if(scan_owner[26:21]!=context_id)begin frame<=frame+1;state<=SCAN_SEND;end
     else if(!scan_published)begin status<=4;state<=DONE;end
     else begin page<=scan_owner[20:0];chunk<=0;state<=READ_AR;end
    end
    READ_AR:if(m_arready)state<=READ_R;
    READ_R:if(m_rvalid)begin
     if(m_rresp!=0||m_rid!=0||!m_rlast)begin status<=5;state<=DONE;end
     else if(stopped||unsafe)begin status<=2;state<=DONE;end
     else begin data[chunk*512+:512]<=m_rdata;if(chunk==2)begin offset<=0;page_count<=page_count+1;state<=DECODE;end else begin chunk<=chunk+1;state<=READ_AR;end end
    end
    DECODE:begin
     if(stopped||unsafe)begin status<=2;state<=DONE;end
     else if(data[1535:1288]!=0)begin status<=6;state<=DONE;end
     else if(offset==8)begin frame<=frame+1;state<=SCAN_SEND;end
     else if(!data[offset])offset<=offset+1;
     else if(record_node>=nodes)begin status<=6;state<=DONE;end
     else state<=EMIT;
    end
    EMIT:if(record_ready)begin
     if(stopped||unsafe)begin status<=2;state<=DONE;end
     else begin crc<=row_crc(crc,record_node,record_payload);record_count<=record_count+1;offset<=offset+1;state<=DECODE;end
    end
    DONE:if(rsp_ready)state<=IDLE;
    default:begin status<=7;receipt_valid<=0;state<=DONE;end
   endcase
  end
 end
endmodule
