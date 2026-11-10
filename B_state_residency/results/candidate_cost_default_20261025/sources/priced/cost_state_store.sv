`timescale 1ns/1ps
// Design-level history/price/net authority. Host edits are fenced by query lifetime.
// History: N u32; price: 256 u32; net: M raw128 {centerX,centerY,fanout,doubleHPWL}.
module cost_state_store #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,
 input wire cfg_valid,output wire cfg_ready,input wire[63:0]cfg_history,cfg_prices,cfg_nets,cfg_design_id,
 input wire[31:0]cfg_nodes,cfg_net_count,cfg_version,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg[2:0]cfg_status,output reg configured,
 input wire query_active,decision_lock,input wire[1:0]active_query,input wire[3:0]active_price,
 output wire ready_for_query,output reg editing,output reg[31:0]published_version,output reg[63:0]design_id,
 input wire req_valid,output wire req_ready,input wire req_host,input wire[2:0]req_op,
 input wire[31:0]req_cookie,req_index,req_value,req_version,input wire[1:0]req_query,input wire[3:0]req_price,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,output reg[31:0]rsp_cookie,rsp_index,rsp_version,
 output reg[2:0]rsp_op,output reg rsp_host,output reg[1:0]rsp_query,output reg[3:0]rsp_price,output reg[127:0]rsp_data,
 output wire busy,fault,
 output reg[63:0]m_araddr,output wire[7:0]m_arlen,output wire[2:0]m_arsize,output wire[1:0]m_arburst,output wire[3:0]m_arid,
 output wire m_arvalid,input wire m_arready,input wire[511:0]m_rdata,input wire[3:0]m_rid,input wire[1:0]m_rresp,input wire m_rlast,m_rvalid,output wire m_rready,
 output reg[63:0]m_awaddr,output wire[7:0]m_awlen,output wire[2:0]m_awsize,output wire[1:0]m_awburst,output wire[3:0]m_awid,
 output wire m_awvalid,input wire m_awready,output reg[511:0]m_wdata,output reg[63:0]m_wstrb,output wire m_wlast,m_wvalid,input wire m_wready,
 input wire[3:0]m_bid,input wire[1:0]m_bresp,input wire m_bvalid,output wire m_bready
);
 localparam IDLE=0,AR=1,R=2,W=3,B=4;
 reg[2:0]state;reg owned,context_owned,response_sent,stopped,aw_done,w_done;reg[31:0]elapsed,nodes,net_count;
 reg[63:0]history_base,price_base,net_base;reg[5:0]offset;reg is_net;
 wire[64:0]hb=({33'b0,cfg_nodes}*65'd4+65'd63)&~65'd63;
 wire[64:0]nb=({33'b0,cfg_net_count}*65'd16+65'd63)&~65'd63;
 wire[64:0]he={1'b0,cfg_history}+hb,pe={1'b0,cfg_prices}+65'd1024,ne={1'b0,cfg_nets}+nb;
 wire bad_config=cfg_nodes==0||cfg_net_count==0||cfg_version==0||cfg_history[5:0]!=0||cfg_prices[5:0]!=0||cfg_nets[5:0]!=0||he>65'h10000000000000000||pe>65'h10000000000000000||ne>65'h10000000000000000||
  ({1'b0,cfg_history}<pe&&{1'b0,cfg_prices}<he)||({1'b0,cfg_history}<ne&&{1'b0,cfg_nets}<he)||({1'b0,cfg_prices}<ne&&{1'b0,cfg_nets}<pe);
 wire unexpected=(m_rvalid&&state!=R&&!(state==AR&&m_arready))||(m_bvalid&&state!=B&&!(state==W&&(aw_done||m_awready)&&(w_done||m_wready)));
 wire bus_error=(state==R&&m_rvalid&&(m_rid!=0||m_rresp!=0||!m_rlast))||(state==B&&m_bvalid&&(m_bid!=0||m_bresp!=0));
 wire drift=owned&&context_owned&&(rsp_host?(query_active||decision_lock):(!query_active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price));
 wire fence_error=query_active&&editing;
 wire timeout=owned&&!response_sent&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire fail_now=abort||unexpected||bus_error||drift||fence_error||timeout;
 assign fault=!rst&&(stopped||fail_now);
 assign busy=!rst&&(owned||state!=IDLE||rsp_valid);
 assign cfg_ready=!rst&&!fault&&!configured&&!cfg_rsp_valid&&!busy&&!query_active&&!decision_lock;
 assign req_ready=!rst&&!fault&&configured&&!cfg_rsp_valid&&!busy;
 assign ready_for_query=!rst&&!fault&&configured&&!editing&&!busy&&!cfg_rsp_valid;
 // AXI requests already presented remain valid even when a late fault stops admission.
 assign m_arvalid=!rst&&state==AR;assign m_rready=!rst&&state==R;
 assign m_awvalid=!rst&&state==W&&!aw_done;assign m_wvalid=!rst&&state==W&&!w_done;assign m_bready=!rst&&state==B;
 assign m_arlen=0;assign m_awlen=0;assign m_arsize=6;assign m_awsize=6;assign m_arburst=1;assign m_awburst=1;assign m_arid=0;assign m_awid=0;assign m_wlast=1;
 wire read_op=req_op==0||req_op==2||req_op==6;
 wire write_op=req_op==1||req_op==3;
 wire invalid_index=((req_op==0||req_op==1)&&req_index>=nodes)||((req_op==2||req_op==3)&&req_index>=256)||(req_op==6&&req_index>=net_count);
 wire bad_identity=req_version!=published_version||(!req_host&&(!query_active||!decision_lock||req_query!=active_query||req_price!=active_price||req_price!=published_version[3:0]));
 wire bad_policy=(!req_host&&!read_op)||(req_host&&(query_active||decision_lock))||(read_op&&editing)||(write_op&&!editing)||(req_op==4&&editing)||(req_op==5&&!editing);
 wire[511:0]read_shifted=m_rdata>>(offset*8);
 reg[63:0]address;
 always @*begin
  if(req_op==0||req_op==1)address=history_base+({32'b0,req_index}<<2);
  else if(req_op==2||req_op==3)address=price_base+({32'b0,req_index}<<2);
  else address=net_base+({32'b0,req_index}<<4);
 end
 task reply(input[3:0]status,input[127:0]data);
  begin rsp_valid<=1;response_sent<=1;rsp_status<=status;rsp_data<=data;end
 endtask
 always @(posedge clk)begin
  if(rst)begin
   state<=IDLE;owned<=0;context_owned<=0;response_sent<=0;stopped<=0;aw_done<=0;w_done<=0;elapsed<=0;nodes<=0;net_count<=0;history_base<=0;price_base<=0;net_base<=0;offset<=0;is_net<=0;
   configured<=0;cfg_rsp_valid<=0;cfg_status<=0;editing<=0;published_version<=0;design_id<=0;
   rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_index<=0;rsp_version<=0;rsp_op<=0;rsp_host<=0;rsp_query<=0;rsp_price<=0;rsp_data<=0;
   m_araddr<=0;m_awaddr<=0;m_wdata<=0;m_wstrb<=0;
  end else begin
   if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
   if(cfg_valid&&cfg_ready)begin
    cfg_rsp_valid<=1;cfg_status<=bad_config?1:0;
    if(!bad_config)begin configured<=1;history_base<=cfg_history;price_base<=cfg_prices;net_base<=cfg_nets;nodes<=cfg_nodes;net_count<=cfg_net_count;published_version<=cfg_version;design_id<=cfg_design_id;end
   end
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;context_owned<=0;end
   if(owned&&state==IDLE&&!rsp_valid&&response_sent)owned<=0;
   if(owned&&!response_sent&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     owned<=1;context_owned<=0;response_sent<=0;elapsed<=0;rsp_cookie<=req_cookie;rsp_index<=req_index;rsp_version<=req_version;rsp_op<=req_op;rsp_host<=req_host;rsp_query<=req_query;rsp_price<=req_price;rsp_status<=0;rsp_data<=0;
     if(req_op==7||invalid_index)reply(1,0);
     else if(bad_identity)reply(3,0);
     else if(bad_policy)reply(2,0);
     else if(req_op==4)begin editing<=1;reply(0,{96'b0,published_version});end
     else if(req_op==5)begin
      if(published_version==32'hffffffff)begin stopped<=1;reply(6,0);end
      else begin published_version<=published_version+1'b1;editing<=0;reply(0,{96'b0,published_version+32'd1});end
     end else begin
      context_owned<=1;offset<=address[5:0];is_net<=req_op==6;
      if(read_op)begin m_araddr<={address[63:6],6'b0};state<=AR;end
      else begin m_awaddr<={address[63:6],6'b0};m_wdata<=({480'b0,req_value}<<(address[5:0]*8));m_wstrb<=64'hf<<address[5:0];aw_done<=0;w_done<=0;state<=W;end
     end
    end
    AR:if(m_arready)state<=R;
    R:if(m_rvalid)begin
     state<=IDLE;
     if(!response_sent&&!fail_now&&!stopped)reply(0,is_net?read_shifted[127:0]:{96'b0,read_shifted[31:0]});
    end
    W:begin
     if(m_awvalid&&m_awready)aw_done<=1;
     if(m_wvalid&&m_wready)w_done<=1;
     if((aw_done||m_awready)&&(w_done||m_wready))state<=B;
    end
    B:if(m_bvalid)begin state<=IDLE;if(!response_sent&&!fail_now&&!stopped)reply(0,0);end
    default:begin stopped<=1;if(owned&&!response_sent)reply(5,0);end
   endcase
   if(fail_now)begin
    stopped<=1;
    if(owned&&!response_sent)reply(bus_error?4:5,0);
   end
  end
 end
endmodule
