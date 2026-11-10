`timescale 1ns/1ps
// One query, one outstanding command. Cold reset must also drain upstream traffic.
// Heap payload survives reset; boot CLEAR is mandatory before admission.
module frontier_service #(
 parameter integer MAX_CALL_CYCLES=256,
 parameter integer MAX_SERVICE_CYCLES=512
)(
 input wire clk,rst,abort,
 input wire req_valid,output wire req_ready,
 input wire [31:0] req_op,req_key_bits,req_id,req_cookie,
 input wire [1:0] req_query,input wire [3:0] req_price,
 output wire rsp_valid,input wire rsp_ready,
 output reg [31:0] rsp_status,rsp_key_bits,rsp_id,rsp_size,rsp_cookie,
 output reg [1:0] rsp_query,output reg [3:0] rsp_price,
 output reg initialized,active,output reg [1:0] owner_query,
 output reg [3:0] owner_price,output reg [31:0] heap_size,
 output wire busy,fault
);
 localparam [2:0] BOOT=0,IDLE=1,SEND=2,WAIT_RESULT=3,REPLY=4;
 localparam integer TIMER_BITS=$clog2(MAX_SERVICE_CYCLES+1);
 reg [2:0] state;
 reg boot_call,stopped;
 reg [31:0] held_op,held_bits,held_id;
 reg [TIMER_BITS-1:0] elapsed;
 wire call_ready,call_reply_valid,call_fault;
 wire [127:0] reply_data;
 wire [95:0] hls_command;
 wire [127:0] hls_reply;
 wire [3:0] hls_valid;
 wire ap_start,ap_ready,ap_done,ap_idle;
 wire timeout=(state==SEND||state==WAIT_RESULT) && elapsed==MAX_SERVICE_CYCLES-1;
 assign fault=!rst&&(stopped||abort||call_fault||timeout);
 assign req_ready=!rst&&!fault&&state==IDLE&&initialized;
 assign rsp_valid=!rst&&state==REPLY;
 assign busy=!rst&&(state!=IDLE||fault);
 wire [31:0] raw_op=(boot_call||held_op==0||held_op==4)?0:held_op;
 frontier_hls_call #(.MAX_CALL_CYCLES(MAX_CALL_CYCLES)) collector(
  .clk(clk),.rst(rst),.abort(abort),.call_valid(state==SEND&&!fault),.call_ready(call_ready),
  .call_command({held_id,held_bits,raw_op}),.reply_valid(call_reply_valid),
  .reply_ready(state==WAIT_RESULT&&!fault),.reply_data(reply_data),.fault(call_fault),
  .ap_start(ap_start),.ap_ready(ap_ready),.ap_done(ap_done),.ap_idle(ap_idle),
  .hls_command(hls_command),.hls_reply(hls_reply),.hls_valid(hls_valid));
 frontier_step heap(.ap_clk(clk),.ap_rst(rst),.ap_start(ap_start),.ap_ready(ap_ready),.ap_done(ap_done),.ap_idle(ap_idle),
  .op(hls_command[31:0]),.key_bits(hls_command[63:32]),.id(hls_command[95:64]),
  .status(hls_reply[31:0]),.result_bits(hls_reply[63:32]),.result_id(hls_reply[95:64]),.size(hls_reply[127:96]),
  .status_ap_vld(hls_valid[0]),.result_bits_ap_vld(hls_valid[1]),.result_id_ap_vld(hls_valid[2]),.size_ap_vld(hls_valid[3]));
 reg [31:0] expected_status,expected_size;
 always @* begin
  expected_status=0;expected_size=heap_size;
  case(raw_op)
   0:expected_size=0;
   1:if(heap_size==65536)expected_status=2;else expected_size=heap_size+1;
   2:if(heap_size==0)expected_status=1;else expected_size=heap_size-1;
   3:begin end
   default:expected_status=3;
  endcase
 end
 wire bad_reply=reply_data[31:0]!=expected_status||reply_data[127:96]!=expected_size||
  ((raw_op!=2||expected_status!=0)&&reply_data[95:32]!=0);
 always @(posedge clk)begin
  if(rst)begin
   state<=BOOT;boot_call<=1;stopped<=0;initialized<=0;active<=0;
   owner_query<=0;owner_price<=0;heap_size<=0;elapsed<=0;
   held_op<=0;held_bits<=0;held_id<=0;
   rsp_status<=0;rsp_key_bits<=0;rsp_id<=0;rsp_size<=0;rsp_cookie<=0;rsp_query<=0;rsp_price<=0;
  end else begin
   // A result already offered remains stable through late fault and retires once.
   if(state==REPLY&&rsp_ready)state<=IDLE;
   if(fault)stopped<=1;
   else begin
    if(state==SEND||state==WAIT_RESULT)elapsed<=elapsed+1'b1;
    case(state)
     BOOT:begin boot_call<=1;state<=SEND;elapsed<=0;end
     IDLE:if(req_valid&&req_ready)begin
      rsp_cookie<=req_cookie;rsp_query<=req_query;rsp_price<=req_price;
      rsp_status<=0;rsp_key_bits<=0;rsp_id<=0;rsp_size<=heap_size;
      held_op<=req_op;held_bits<=req_key_bits;held_id<=req_id;
      boot_call<=0;elapsed<=0;
      if(req_op>4)begin rsp_status<=3;state<=REPLY;end
      else if(req_op==0&&active)begin rsp_status<=6;state<=REPLY;end
      else if(req_op!=0&&!active)begin rsp_status<=4;state<=REPLY;end
      else if(req_op!=0&&(req_query!=owner_query||req_price!=owner_price))begin rsp_status<=5;state<=REPLY;end
      else state<=SEND;
     end
     SEND:if(call_ready)state<=WAIT_RESULT;
     WAIT_RESULT:if(call_reply_valid)begin
      if(bad_reply)stopped<=1;
      else begin
       heap_size<=reply_data[127:96];
       if(boot_call)begin initialized<=1;state<=IDLE;end
       else begin
        rsp_status<=reply_data[31:0];rsp_key_bits<=reply_data[63:32];rsp_id<=reply_data[95:64];rsp_size<=reply_data[127:96];
        if(held_op==0)begin active<=1;owner_query<=rsp_query;owner_price<=rsp_price;end
        if(held_op==4)begin active<=0;owner_query<=0;owner_price<=0;end
        state<=REPLY;
       end
      end
     end
     default:begin end
    endcase
   end
  end
 end
endmodule
