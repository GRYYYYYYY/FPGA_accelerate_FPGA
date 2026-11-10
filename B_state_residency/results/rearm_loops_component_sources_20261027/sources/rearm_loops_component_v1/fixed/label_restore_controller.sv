`timescale 1ns/1ps
// Exclusive trusted snapshot stream. rst is service cold reset, not target_reset.
module label_restore_controller #(parameter integer MAX_RECORDS=512,CHECK_SOURCE_CRC=0,MAX_CYCLES=1048576)(
 output wire rearm_retired,
 input wire start_skip_seed,output wire l_import,
 output wire l_probe,
 input wire clk,rst,abort,backend_drained,
 input wire start_valid,output wire start_ready,input wire[63:0]start_design,expected_design,
 input wire[31:0]start_checkpoint,expected_checkpoint,start_cookie,start_count,start_nodes,start_probe,start_version,
 input wire[1:0]start_query,input wire[3:0]start_price,
 input wire[31:0]start_source_crc,output reg[31:0]rsp_source_crc,
 input wire s_valid,output wire s_ready,input wire[31:0]s_node,s_cookie,input wire[159:0]s_payload,input wire s_last,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[31:0]rsp_cookie,written,verified,output wire busy,fault,
 output wire c_valid,input wire c_ready,output wire[1:0]c_op,c_query,output wire[3:0]c_price,output wire[31:0]c_version,
 input wire c_rsp_valid,output wire c_rsp_ready,input wire[3:0]c_status,
 output wire l_valid,input wire l_ready,output wire l_write,output wire[31:0]l_node,l_value,output wire[2:0]l_field,
 input wire l_rsp_valid,output wire l_rsp_ready,input wire[3:0]l_status,input wire l_present,input wire[159:0]l_payload
);
 reg skip_seed;reg[31:0]running_crc,expected_crc;
 function[31:0]word_crc(input[31:0]c0,w);reg[31:0]c;integer j;begin c=c0;for(j=0;j<32;j=j+1)c=(c[0]^w[j])?((c>>1)^32'hedb88320):(c>>1);word_crc=c;end endfunction
 function[31:0]row_crc(input[31:0]c0,node,input[159:0]v);reg[31:0]c;integer j;begin c=word_crc(c0,node);for(j=0;j<5;j=j+1)c=word_crc(c,v[j*32+:32]);row_crc=c;end endfunction
 localparam IDLE=0,CS=1,CW=2,PS=3,PW=4,STREAM=5,WS=6,WW=7,LOAD=8,RS=9,RW=10,DRAIN=11,DONE=12,FAILWAIT=13;
 reg[3:0]state,error_code;reg stopped,checkpoint_phase;reg[31:0]elapsed,count,nodes,probe,version,index,verify_index,node;
 reg[1:0]query;reg[3:0]price;reg[2:0]field;reg[159:0]payload;reg[191:0]rows[0:MAX_RECORDS-1];reg[191:0]row;
 wire fail_now=busy&&!rsp_valid&&(abort||elapsed>=MAX_CYCLES);
 // Retirement must not be made true by the reset it authorizes. The
 // synchronous service state and outstanding reply are the authority.
 assign rearm_retired=state==IDLE&&!rsp_valid;
 assign busy=!rst&&state!=IDLE;assign fault=!rst&&(stopped||fail_now);
 assign l_import=!rst&&skip_seed&&(state==WS||state==WW);
 assign l_probe=!rst&&(state==PS||state==PW);
 assign start_ready=!rst&&state==IDLE&&!stopped&&backend_drained;
 assign s_ready=!rst&&state==STREAM&&!stopped&&!fail_now;
 assign c_valid=!rst&&state==CS;assign c_op=checkpoint_phase?2'd1:2'd0;assign c_query=query;assign c_price=price;assign c_version=version;assign c_rsp_ready=!rst&&state==CW;
 assign l_valid=!rst&&(state==PS||state==WS||state==RS);assign l_write=state==WS;
 assign l_node=state==PS?probe:state==RS?row[191:160]:node;
 assign l_field=state==WS?field:3'd0;assign l_value=payload>>(field*32);
 assign l_rsp_ready=!rst&&(state==PW||state==WW||state==RW);
 task fail(input[3:0]code);begin stopped<=1;error_code<=code;state<=FAILWAIT;end endtask
 always @(posedge clk)begin
  if(rst)begin skip_seed<=0;running_crc<=32'hffffffff;expected_crc<=0;rsp_source_crc<=0;state<=IDLE;stopped<=0;error_code<=0;checkpoint_phase<=0;elapsed<=0;count<=0;nodes<=0;probe<=0;version<=0;index<=0;verify_index<=0;node<=0;query<=0;price<=0;field<=0;payload<=0;row<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;written<=0;verified<=0;end
  else begin
   if(busy&&!rsp_valid&&!stopped)elapsed<=elapsed+1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=7;end
   case(state)
    IDLE:if(start_valid&&start_ready)begin
     skip_seed<=(start_skip_seed===1'b1);
     running_crc<=32'hffffffff;expected_crc<=start_source_crc;rsp_source_crc<=0;elapsed<=0;rsp_cookie<=start_cookie;written<=0;verified<=0;rsp_status<=0;index<=0;verify_index<=0;checkpoint_phase<=0;
     count<=start_count;nodes<=start_nodes;probe<=start_probe;version<=start_version;query<=start_query;price<=start_price;
     if(start_design!=expected_design||start_checkpoint!=expected_checkpoint||start_count==0||start_count>MAX_RECORDS||start_nodes==0||start_probe>=start_nodes||start_price!=start_version[3:0])fail(1);
     else state<=CS;
    end
    CS:if(c_ready)state<=CW;
    CW:if(c_rsp_valid)begin
     if(stopped||fail_now)state<=FAILWAIT;else if(c_status!=0)fail(2);else if(checkpoint_phase)begin verify_index<=0;state<=LOAD;end else state<=PS;
    end
    PS:if(l_ready)state<=PW;
    PW:if(l_rsp_valid)begin
     if(stopped||fail_now)state<=FAILWAIT;else if(l_status!=0)fail(4);else if(l_present)fail(3);else state<=STREAM;
    end
    STREAM:if(stopped||fail_now)state<=FAILWAIT;else if(s_valid&&s_ready)begin
     if(s_cookie!=rsp_cookie||s_node>=nodes||s_last!=(index+1==count))fail(5);
     else begin
      if(CHECK_SOURCE_CRC!=0)begin running_crc<=row_crc(running_crc,s_node,s_payload);rsp_source_crc<=~row_crc(running_crc,s_node,s_payload);end
      if(CHECK_SOURCE_CRC!=0&&s_last&&~row_crc(running_crc,s_node,s_payload)!=expected_crc)fail(8);
      else begin rows[index]<={s_node,s_payload};node<=s_node;payload<=s_payload;field<=0;state<=WS;end
     end
    end
    WS:if(l_ready)state<=WW;
    WW:if(l_rsp_valid)begin
     if(stopped||fail_now)state<=FAILWAIT;else if(l_status!=0)fail(4);
     else if(field<4)begin field<=field+1;state<=WS;end
     else begin written<=written+1;if(index+1==count)begin checkpoint_phase<=1;state<=CS;end else begin index<=index+1;state<=STREAM;end end
    end
    LOAD:if(stopped||fail_now)state<=FAILWAIT;else begin row<=rows[verify_index];state<=RS;end
    RS:if(l_ready)state<=RW;
    RW:if(l_rsp_valid)begin
     if(stopped||fail_now)state<=FAILWAIT;else if(l_status!=0)fail(4);else if(!l_present||l_payload!=row[159:0])fail(6);
     else begin verified<=verified+1;if(verify_index+1==count)state<=DRAIN;else begin verify_index<=verify_index+1;state<=LOAD;end end
    end
    DRAIN:if(stopped||fail_now)state<=FAILWAIT;else if(backend_drained)begin rsp_status<=0;rsp_valid<=1;state<=DONE;end
    FAILWAIT:if(backend_drained)begin rsp_status<=fail_now&&!stopped?7:error_code;rsp_valid<=1;state<=DONE;end
    DONE:if(rsp_valid&&rsp_ready)begin rsp_valid<=0;state<=IDLE;end
    default:fail(7);
   endcase
  end
 end
endmodule
