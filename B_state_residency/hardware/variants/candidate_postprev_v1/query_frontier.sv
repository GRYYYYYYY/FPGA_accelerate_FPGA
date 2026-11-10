`timescale 1ns/1ps
// Coupled query lifecycle plus exclusive internal CLEAR; seed port is an explicit fixture boundary.
module query_frontier(
 input wire clk,rst,abort,query_active,query_owned,decision_lock,close_requested,may_close,
 input wire [1:0] query_id,input wire [3:0] price,input wire [31:0] version,
 output wire ready_for_expand,ready_for_close,initialized,busy,fault,
 input wire clear_valid,output wire clear_ready,input wire [31:0] clear_cookie,input wire [1:0] clear_query,input wire [3:0] clear_price,
 output wire clear_rsp_valid,input wire clear_rsp_ready,output wire [31:0] clear_rsp_status,clear_rsp_cookie,clear_rsp_size,output wire [1:0] clear_rsp_query,output wire [3:0] clear_rsp_price,
 input wire seed_valid,output wire seed_ready,input wire [31:0] seed_op,seed_key,seed_id,seed_cookie,seed_version,
 output wire seed_rsp_valid,input wire seed_rsp_ready,output wire [31:0] seed_rsp_status,seed_rsp_cookie,seed_rsp_size,
 output wire [31:0] heap_size
);
 reg [1:0] control;reg closing,stopped;reg [31:0] held_op,held_version;reg [1:0] held_q;reg [3:0] held_p;
 wire fs_active,fs_busy,fs_fault,arb_busy,arb_fault;wire [1:0] fs_q;wire [3:0] fs_p;
 wire fs_req_valid,fs_req_ready,fs_rsp_valid,fs_rsp_ready;
 wire [31:0] fs_req_op,fs_req_key,fs_req_id,fs_req_cookie,fs_rsp_status,fs_rsp_key,fs_rsp_id,fs_rsp_size,fs_rsp_cookie;
 wire [1:0] fs_req_q,fs_rsp_q;wire [3:0] fs_req_p,fs_rsp_p;
 wire [2:0] rv,rr,sv,sr;wire [401:0] rd;wire [497:0] sd;wire [133:0] bd;wire [165:0] bs;
 wire [31:0] ctl_status,ctl_cookie,ctl_size,ctl_key,ctl_id;wire [1:0] ctl_q;wire [3:0] ctl_p;
 wire matching=fs_active&&query_active&&query_owned&&fs_q==query_id&&fs_p==price&&held_version==version;
 wire bad_control=sv[0]&&(ctl_status!=0||ctl_size!=0||ctl_cookie!=(32'hf1000000|held_op)||ctl_q!=held_q||ctl_p!=held_p);
 wire drift=fs_active&&(!query_active||!query_owned||fs_q!=query_id||fs_p!=price||held_version!=version);
 assign fault=!rst&&(stopped||abort||fs_fault||arb_fault||bad_control||drift);
 assign busy=!rst&&(control!=0||arb_busy||fs_busy||fault);
 assign ready_for_expand=!rst&&!fault&&matching&&control==0&&!arb_busy&&!fs_busy&&!seed_valid&&!closing;
 assign ready_for_close=!rst&&!fault&&!fs_active&&control==0&&!arb_busy&&!fs_busy;
 assign rv[0]=control==1&&!fault;assign rd[0+:134]={held_op,32'b0,32'b0,(32'hf1000000|held_op),held_q,held_p};assign sr[0]=control==2;
 assign {ctl_status,ctl_key,ctl_id,ctl_size,ctl_cookie,ctl_q,ctl_p}=sd[0+:166];
 assign rv[1]=clear_valid&&matching&&decision_lock&&!fault;assign clear_ready=rr[1]&&matching&&decision_lock&&!fault;
 assign rd[134+:134]={32'd5,32'b0,32'b0,clear_cookie,clear_query,clear_price};
 wire [31:0] clear_key,clear_id;
 assign clear_rsp_valid=sv[1];assign sr[1]=clear_rsp_ready;
 assign {clear_rsp_status,clear_key,clear_id,clear_rsp_size,clear_rsp_cookie,clear_rsp_query,clear_rsp_price}=sd[166+:166];
 wire seed_permit=matching&&!decision_lock&&!close_requested&&!closing&&seed_version==version&&(seed_op==1||seed_op==3)&&!fault;
 assign rv[2]=seed_valid&&seed_permit;assign seed_ready=rr[2]&&seed_permit;
 assign rd[268+:134]={seed_op,seed_key,seed_id,seed_cookie,query_id,price};
 wire [31:0] seed_key_out,seed_id_out;wire [1:0] seed_q;wire [3:0] seed_p;
 assign seed_rsp_valid=sv[2];assign sr[2]=seed_rsp_ready;
 assign {seed_rsp_status,seed_key_out,seed_id_out,seed_rsp_size,seed_rsp_cookie,seed_q,seed_p}=sd[332+:166];
 assign {fs_req_op,fs_req_key,fs_req_id,fs_req_cookie,fs_req_q,fs_req_p}=bd;
 assign bs={fs_rsp_status,fs_rsp_key,fs_rsp_id,fs_rsp_size,fs_rsp_cookie,fs_rsp_q,fs_rsp_p};
 service_arbiter #(.CLIENTS(3),.REQUEST_BITS(134),.RESPONSE_BITS(166))arb(
 .clk(clk),.rst(rst),.c_req_valid(rv),.c_req_ready(rr),.c_req_data(rd),.c_rsp_valid(sv),.c_rsp_ready(sr),.c_rsp_data(sd),
 .b_req_valid(fs_req_valid),.b_req_ready(fs_req_ready),.b_req_data(bd),.b_rsp_valid(fs_rsp_valid),.b_rsp_ready(fs_rsp_ready),.b_rsp_data(bs),.busy(arb_busy),.fault(arb_fault));
 frontier_service heap(.clk(clk),.rst(rst),.abort(abort||stopped),
 .req_valid(fs_req_valid),.req_ready(fs_req_ready),.req_op(fs_req_op),.req_key_bits(fs_req_key),.req_id(fs_req_id),.req_cookie(fs_req_cookie),.req_query(fs_req_q),.req_price(fs_req_p),
 .rsp_valid(fs_rsp_valid),.rsp_ready(fs_rsp_ready),.rsp_status(fs_rsp_status),.rsp_key_bits(fs_rsp_key),.rsp_id(fs_rsp_id),.rsp_size(fs_rsp_size),.rsp_cookie(fs_rsp_cookie),.rsp_query(fs_rsp_q),.rsp_price(fs_rsp_p),
 .initialized(initialized),.active(fs_active),.owner_query(fs_q),.owner_price(fs_p),.heap_size(heap_size),.busy(fs_busy),.fault(fs_fault));
 always @(posedge clk)begin
  if(rst)begin control<=0;closing<=0;stopped<=0;held_op<=0;held_q<=0;held_p<=0;held_version<=0;end
  else begin
   if(fault)stopped<=1;
   if(!query_active&&!fs_active&&control==0)closing<=0;
   case(control)
    0:if(!fault&&initialized)begin
     if(query_active&&query_owned&&!fs_active&&!closing&&!close_requested)begin held_op<=0;held_q<=query_id;held_p<=price;held_version<=version;control<=1;end
     else if(close_requested&&may_close&&fs_active)begin held_op<=4;held_q<=query_id;held_p<=price;closing<=1;control<=1;end
    end
    1:if(rv[0]&&rr[0])control<=2;
    2:if(sv[0]&&sr[0])control<=0;
    default:stopped<=1;
   endcase
  end
 end
endmodule
