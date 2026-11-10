`timescale 1ns/1ps
// Coupled query lifecycle plus exclusive internal CLEAR; seed port is an explicit fixture boundary.
module query_frontier_offer(
 input wire [63:0] design_id,
 input wire offer_valid,output wire offer_ready,input wire [31:0] offer_key,offer_id,offer_cookie,offer_version,input wire [63:0] offer_design,input wire [1:0] offer_query,input wire [3:0] offer_price,
 output wire offer_rsp_valid,input wire offer_rsp_ready,output wire [31:0] offer_rsp_status,offer_rsp_cookie,offer_rsp_size,offer_rsp_version,output wire [63:0] offer_rsp_design,output wire [1:0] offer_rsp_query,output wire [3:0] offer_rsp_price,
 output wire [31:0] seed_rsp_key,seed_rsp_id,
 input wire clk,rst,abort,query_active,query_owned,decision_lock,close_requested,may_close,
 input wire [1:0] query_id,input wire [3:0] price,input wire [31:0] version,
 output wire ready_for_expand,ready_for_close,initialized,busy,fault,retired_idle,
 input wire clear_valid,output wire clear_ready,input wire [31:0] clear_cookie,input wire [1:0] clear_query,input wire [3:0] clear_price,
 output wire clear_rsp_valid,input wire clear_rsp_ready,output wire [31:0] clear_rsp_status,clear_rsp_cookie,clear_rsp_size,output wire [1:0] clear_rsp_query,output wire [3:0] clear_rsp_price,
 input wire seed_valid,output wire seed_ready,input wire [31:0] seed_op,seed_key,seed_id,seed_cookie,seed_version,
 output wire seed_rsp_valid,input wire seed_rsp_ready,output wire [31:0] seed_rsp_status,seed_rsp_cookie,seed_rsp_size,
 output wire [31:0] heap_size
);
 reg [63:0] held_design,owned_offer_design;reg [31:0] owned_offer_version;reg offer_pending;
 reg [1:0] control;reg closing,stopped;reg [31:0] held_op,held_version;reg [1:0] held_q;reg [3:0] held_p;
 wire fs_active,fs_busy,fs_fault,arb_busy,arb_fault,fs_retired_idle;wire [1:0] fs_q;wire [3:0] fs_p;
 wire fs_req_valid,fs_req_ready,fs_rsp_valid,fs_rsp_ready;
 wire [31:0] fs_req_op,fs_req_key,fs_req_id,fs_req_cookie,fs_rsp_status,fs_rsp_key,fs_rsp_id,fs_rsp_size,fs_rsp_cookie;
 wire [1:0] fs_req_q,fs_rsp_q;wire [3:0] fs_req_p,fs_rsp_p;
 wire [3:0] rv,rr,sv,sr;wire [535:0] rd;wire [663:0] sd;wire [133:0] bd;wire [165:0] bs;
 wire [31:0] ctl_status,ctl_cookie,ctl_size,ctl_key,ctl_id;wire [1:0] ctl_q;wire [3:0] ctl_p;
 wire matching=fs_active&&query_active&&query_owned&&fs_q==query_id&&fs_p==price&&held_version==version&&held_design==design_id;
 wire bad_control=sv[0]&&(ctl_status!=0||ctl_size!=0||ctl_cookie!=(32'hf1000000|held_op)||ctl_q!=held_q||ctl_p!=held_p);
 wire drift=fs_active&&(!query_active||!query_owned||fs_q!=query_id||fs_p!=price||held_version!=version||held_design!=design_id);
 assign fault=!rst&&(stopped||abort||fs_fault||arb_fault||bad_control||drift);
 assign busy=!rst&&(control!=0||arb_busy||fs_busy||offer_pending||fault);
 assign retired_idle=!rst&&control==0&&!arb_busy&&!offer_pending&&fs_retired_idle;
 assign ready_for_expand=!rst&&!fault&&matching&&control==0&&!arb_busy&&!fs_busy&&!seed_valid&&!closing;
 assign ready_for_close=!rst&&!fault&&!fs_active&&control==0&&!arb_busy&&!fs_busy;
 assign rv[0]=control==1&&!fault;assign rd[0+:134]={held_op,32'b0,32'b0,(32'hf1000000|held_op),held_q,held_p};assign sr[0]=control==2;
 assign {ctl_status,ctl_key,ctl_id,ctl_size,ctl_cookie,ctl_q,ctl_p}=sd[0+:166];
 assign rv[1]=clear_valid&&matching&&decision_lock&&!fault;assign clear_ready=rr[1]&&matching&&decision_lock&&!fault;
 assign rd[134+:134]={32'd5,32'b0,32'b0,clear_cookie,clear_query,clear_price};
 wire [31:0] clear_key,clear_id;
 assign clear_rsp_valid=sv[1];assign sr[1]=clear_rsp_ready;
 assign {clear_rsp_status,clear_key,clear_id,clear_rsp_size,clear_rsp_cookie,clear_rsp_query,clear_rsp_price}=sd[166+:166];
 wire seed_permit=matching&&!decision_lock&&!close_requested&&!closing&&seed_version==version&&(seed_op==1||seed_op==2||seed_op==3)&&!fault;
 assign rv[2]=seed_valid&&seed_permit;assign seed_ready=rr[2]&&seed_permit;
 assign rd[268+:134]={seed_op,seed_key,seed_id,seed_cookie,query_id,price};
 wire [31:0] seed_key_out,seed_id_out;wire [1:0] seed_q;wire [3:0] seed_p;
 assign seed_rsp_valid=sv[2];assign sr[2]=seed_rsp_ready;
 assign {seed_rsp_status,seed_key_out,seed_id_out,seed_rsp_size,seed_rsp_cookie,seed_q,seed_p}=sd[332+:166];
 assign seed_rsp_key=seed_key_out;assign seed_rsp_id=seed_id_out;
 wire offer_permit=matching&&decision_lock&&!closing&&control==0&&offer_version==version&&offer_design==design_id&&offer_query==query_id&&offer_price==price&&!fault;
 assign rv[3]=offer_valid&&offer_permit;assign offer_ready=rr[3]&&offer_permit;
 assign rd[402+:134]={32'd1,offer_key,offer_id,offer_cookie,offer_query,offer_price};
 wire [31:0] offer_unused_key,offer_unused_id;
 assign offer_rsp_valid=sv[3];assign sr[3]=offer_rsp_ready;
 assign {offer_rsp_status,offer_unused_key,offer_unused_id,offer_rsp_size,offer_rsp_cookie,offer_rsp_query,offer_rsp_price}=sd[498+:166];
 assign offer_rsp_version=owned_offer_version;assign offer_rsp_design=owned_offer_design;
 always @(posedge clk)begin
  if(rst)begin offer_pending<=0;owned_offer_version<=0;owned_offer_design<=0;end
  else begin
   if(sv[3]&&sr[3])offer_pending<=0;
   if(rv[3]&&rr[3])begin offer_pending<=1;owned_offer_version<=offer_version;owned_offer_design<=offer_design;end
  end
 end
 assign {fs_req_op,fs_req_key,fs_req_id,fs_req_cookie,fs_req_q,fs_req_p}=bd;
 assign bs={fs_rsp_status,fs_rsp_key,fs_rsp_id,fs_rsp_size,fs_rsp_cookie,fs_rsp_q,fs_rsp_p};
 service_arbiter #(.CLIENTS(4),.REQUEST_BITS(134),.RESPONSE_BITS(166))arb(
 .clk(clk),.rst(rst),.c_req_valid(rv),.c_req_ready(rr),.c_req_data(rd),.c_rsp_valid(sv),.c_rsp_ready(sr),.c_rsp_data(sd),
 .b_req_valid(fs_req_valid),.b_req_ready(fs_req_ready),.b_req_data(bd),.b_rsp_valid(fs_rsp_valid),.b_rsp_ready(fs_rsp_ready),.b_rsp_data(bs),.busy(arb_busy),.fault(arb_fault));
 frontier_service heap(.clk(clk),.rst(rst),.abort(abort||stopped),
 .req_valid(fs_req_valid),.req_ready(fs_req_ready),.req_op(fs_req_op),.req_key_bits(fs_req_key),.req_id(fs_req_id),.req_cookie(fs_req_cookie),.req_query(fs_req_q),.req_price(fs_req_p),
 .rsp_valid(fs_rsp_valid),.rsp_ready(fs_rsp_ready),.rsp_status(fs_rsp_status),.rsp_key_bits(fs_rsp_key),.rsp_id(fs_rsp_id),.rsp_size(fs_rsp_size),.rsp_cookie(fs_rsp_cookie),.rsp_query(fs_rsp_q),.rsp_price(fs_rsp_p),
 .initialized(initialized),.active(fs_active),.owner_query(fs_q),.owner_price(fs_p),.heap_size(heap_size),.busy(fs_busy),.fault(fs_fault),.retired_idle(fs_retired_idle));
 always @(posedge clk)begin
  if(rst)begin control<=0;closing<=0;stopped<=0;held_op<=0;held_q<=0;held_p<=0;held_version<=0;held_design<=0;end
  else begin
   if(fault)stopped<=1;
   if(!query_active&&!fs_active&&control==0)closing<=0;
   case(control)
    0:if(!fault&&initialized)begin
     if(query_active&&query_owned&&!fs_active&&!closing&&!close_requested)begin held_op<=0;held_q<=query_id;held_p<=price;held_version<=version;held_design<=design_id;control<=1;end
     else if(close_requested&&may_close&&fs_active)begin held_op<=4;held_q<=query_id;held_p<=price;closing<=1;control<=1;end
    end
    1:if(rv[0]&&rr[0])control<=2;
    2:if(sv[0]&&sr[0])control<=0;
    default:stopped<=1;
   endcase
  end
 end
endmodule
