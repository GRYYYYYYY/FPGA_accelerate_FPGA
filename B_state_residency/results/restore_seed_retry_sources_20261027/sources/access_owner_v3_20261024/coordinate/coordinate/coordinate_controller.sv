`timescale 1ns/1ps
// One node request; real label prev is never reinterpreted using presence.
module coordinate_controller #(parameter integer TOKEN_BITS=32,MAX_CYCLES=262144)(
 input wire clk,rst,enable,abort,input wire [31:0]nodes,table_rows,table_columns,
 input wire active,input wire [1:0]active_query,input wire [3:0]active_price,
 input wire req_valid,output wire req_ready,input wire [1:0]req_op,req_query,
 input wire [3:0]req_price,input wire [31:0]req_cookie,req_node,
 output wire rsp_valid,input wire rsp_ready,output reg [3:0]rsp_status,
 output reg [1:0]rsp_op,rsp_query,output reg [3:0]rsp_price,
 output reg [31:0]rsp_cookie,rsp_node,rsp_y,rsp_slr,rsp_next,rsp_prev_column,rsp_label_prev,
 output reg rsp_north,rsp_prev_read,rsp_prev_present,output reg [255:0]rsp_attrs,
 output wire busy,fault,
 output wire g_req_valid,input wire g_req_ready,output wire [1:0]g_req_op,
 output wire [31:0]g_req_cookie,g_req_node,g_req_index,
 input wire g_rsp_valid,output wire g_rsp_ready,input wire [3:0]g_rsp_status,
 input wire [31:0]g_rsp_cookie,g_rsp_parent,g_rsp_index,g_rsp_node,g_rsp_start,g_rsp_count,
 input wire [255:0]g_rsp_attrs,input wire g_fault,
 output wire t_req_valid,input wire t_req_ready,output reg t_req_op,
 output wire [31:0]t_req_cookie,output reg [31:0]t_req_index,
 input wire t_rsp_valid,output wire t_rsp_ready,input wire [3:0]t_rsp_status,
 input wire t_rsp_op,input wire [31:0]t_rsp_index,t_rsp_cookie,t_rsp_a,t_rsp_b,input wire t_fault,
 output wire p_io_valid,input wire p_io_ready,output wire p_io_write,
 output wire [31:0]p_io_node,p_io_value,output wire [2:0]p_io_field,
 input wire p_io_rsp_valid,output wire p_io_rsp_ready,input wire [3:0]p_io_status,
 input wire [159:0]p_io_payload,input wire p_io_present,p_fault
);
 localparam [2:0]IDLE=0,GS=1,GW=2,PS=3,PW=4,TS=5,TW=6,REPLY=7;
 localparam integer TBITS=$clog2(MAX_CYCLES+1);
 localparam [31:0]TOKEN_MAX=32'hffffffff>>(32-TOKEN_BITS);
 reg [2:0]state;reg stopped,predecessor,owned;reg [31:0]token,graph_node;reg [TBITS-1:0]elapsed;
 wire unexpected=(g_rsp_valid&&state!=GW)||(t_rsp_valid&&state!=TW)||(p_io_rsp_valid&&state!=PW);
 wire drift=owned&&state!=IDLE&&(!active||active_query!=rsp_query||active_price!=rsp_price);
 wire timeout=state!=IDLE&&state!=REPLY&&elapsed==MAX_CYCLES-1;
 assign fault=!rst&&(stopped||abort||g_fault||t_fault||p_fault||unexpected||drift||timeout);
 assign req_ready=!rst&&!fault&&enable&&state==IDLE;
 assign rsp_valid=!rst&&state==REPLY;
 assign busy=!rst&&(state!=IDLE||fault);
 assign g_req_valid=!rst&&state==GS;assign g_req_op=0;
 assign g_req_cookie=token;assign g_req_node=graph_node;assign g_req_index=0;
 assign g_rsp_ready=!rst&&state==GW;
 assign t_req_valid=!rst&&state==TS;assign t_req_cookie=token;
 assign t_rsp_ready=!rst&&state==TW;
 assign p_io_valid=!rst&&state==PS;assign p_io_write=0;assign p_io_node=rsp_node;assign p_io_value=0;assign p_io_field=2;
 assign p_io_rsp_ready=!rst&&state==PW;
 task fail(input [3:0]code);
 begin stopped<=1;rsp_status<=code;state<=REPLY;end endtask
 task graph_read(input [31:0]n,input pred);
 begin
  if(token==TOKEN_MAX)fail(6);
  else begin token<=token+1;graph_node<=n;predecessor<=pred;state<=GS;end
 end endtask
 task table_read(input op,input [31:0]idx);
 begin
  if(token==TOKEN_MAX)fail(6);
  else begin token<=token+1;t_req_op<=op;t_req_index<=idx;state<=TS;end
 end endtask
 task finish_y(input [31:0]y);
 begin
  rsp_y<=y;
  if(rsp_op==1)begin
   if(y>=table_rows)fail(8);else table_read(0,y);
  end else state<=REPLY;
 end endtask
 wire [31:0]static_y={{16{g_rsp_attrs[143]}},g_rsp_attrs[143:128]};
 wire [31:0]held_end_y={{16{rsp_attrs[143]}},rsp_attrs[143:128]};
 wire [31:0]held_begin_y={{16{rsp_attrs[111]}},rsp_attrs[111:96]};
 wire [31:0]static_x={{16{g_rsp_attrs[127]}},g_rsp_attrs[127:112]};
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;stopped<=0;owned<=0;predecessor<=0;token<=0;graph_node<=0;elapsed<=0;t_req_op<=0;t_req_index<=0;
   rsp_status<=0;rsp_op<=0;rsp_query<=0;rsp_price<=0;rsp_cookie<=0;rsp_node<=0;rsp_y<=0;rsp_slr<=0;rsp_next<=0;rsp_prev_column<=0;rsp_label_prev<=0;
   rsp_north<=0;rsp_prev_read<=0;rsp_prev_present<=0;rsp_attrs<=0;
  end else begin
   if(state==REPLY&&rsp_ready)begin state<=IDLE;owned<=0;end
   if(fault)begin
    stopped<=1;
    if(state!=IDLE&&state!=REPLY)begin
     rsp_status<=5;
     case(state)
      GS:if(g_req_ready)state<=GW;
      GW:if(g_rsp_valid&&g_rsp_ready)state<=REPLY;
      PS:if(p_io_ready)state<=PW;
      PW:if(p_io_rsp_valid&&p_io_rsp_ready)state<=REPLY;
      TS:if(t_req_ready)state<=TW;
      TW:if(t_rsp_valid&&t_rsp_ready)state<=REPLY;
      default:state<=REPLY;
     endcase
    end
   end else begin
    if(state!=IDLE&&state!=REPLY)elapsed<=elapsed+1'b1;
    case(state)
     IDLE:if(req_valid&&req_ready)begin
      rsp_cookie<=req_cookie;rsp_node<=req_node;rsp_op<=req_op;rsp_query<=req_query;rsp_price<=req_price;owned<=0;
      rsp_status<=0;rsp_y<=0;rsp_slr<=0;rsp_next<=0;rsp_prev_column<=0;rsp_label_prev<=0;rsp_north<=0;rsp_prev_read<=0;rsp_prev_present<=0;rsp_attrs<=0;elapsed<=0;
      if(req_node>=nodes||(req_op==2&&table_columns==0))begin rsp_status<=1;state<=REPLY;end
      else if(!active||req_query!=active_query||req_price!=active_price)begin rsp_status<=2;state<=REPLY;end
      else begin owned<=1;graph_read(req_node,0);end
     end
     GS:if(g_req_valid&&g_req_ready)state<=GW;
     GW:if(g_rsp_valid&&g_rsp_ready)begin
      if(g_rsp_status!=0)fail(3);
      else if(g_rsp_cookie!=token||g_rsp_node!=graph_node||g_rsp_parent!=graph_node||g_rsp_index!=0)fail(4);
      else if(predecessor)finish_y(static_y==held_end_y?held_begin_y:held_end_y);
      else begin
       rsp_attrs<=g_rsp_attrs;
       if(rsp_op==3)state<=REPLY;
       else if(rsp_op==2)begin if(static_x>=table_columns)fail(8);else table_read(1,static_x);end
       else if(g_rsp_attrs[71:64]!=5)finish_y(static_y);
       else state<=PS;
      end
     end
     PS:if(p_io_valid&&p_io_ready)state<=PW;
     PW:if(p_io_rsp_valid&&p_io_rsp_ready)begin
      if(p_io_status!=0||(!p_io_present&&p_io_payload!=0))fail(3);
      else begin
       rsp_prev_read<=1;rsp_prev_present<=p_io_present;rsp_label_prev<=p_io_payload[95:64];
       if(p_io_payload[95:64]==32'hffffffff)finish_y(held_end_y);
       else if(p_io_payload[95:64]>=nodes)fail(7);
       else graph_read(p_io_payload[95:64],1);
      end
     end
     TS:if(t_req_valid&&t_req_ready)state<=TW;
     TW:if(t_rsp_valid&&t_rsp_ready)begin
      if(t_rsp_status!=0)fail(3);
      else if(t_rsp_cookie!=token||t_rsp_op!=t_req_op||t_rsp_index!=t_req_index)fail(4);
      else begin
       if(t_req_op)begin rsp_next<=t_rsp_a;rsp_prev_column<=t_rsp_b;end
       else begin rsp_slr<=t_rsp_a;rsp_north<=t_rsp_b[0];end
       state<=REPLY;
      end
     end
     default:begin end
    endcase
   end
  end
 end
endmodule
