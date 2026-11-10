`timescale 1ns/1ps
// Immutable design/profile table. One raw64B record per real global connection index.
module connection_state_reader #(parameter integer MAX_CYCLES=1048576)(
 input wire clk,rst,abort,
 input wire cfg_valid,output wire cfg_ready,input wire [63:0] cfg_base,cfg_design,
 input wire [31:0] cfg_connections,cfg_nodes,cfg_nets,cfg_revision,
 output reg cfg_rsp_valid,input wire cfg_rsp_ready,output reg [2:0] cfg_status,output reg configured,
 output reg [63:0] design_id,output reg [31:0] nodes,nets,connections,revision,
 input wire query_active,decision_lock,input wire [1:0] active_query,input wire [3:0] active_price,
 input wire [31:0] active_version,input wire [63:0] active_design,
 input wire req_valid,output wire req_ready,input wire [31:0] req_cookie,req_connection,req_net,req_sink,req_cross,req_version,
 input wire [1:0] req_query,input wire [3:0] req_price,input wire [63:0] req_design,
 output reg rsp_valid,input wire rsp_ready,output reg [3:0] rsp_status,
 output reg [31:0] rsp_cookie,rsp_connection,rsp_net,rsp_sink,rsp_cross,rsp_version,rsp_revision,
 output reg [1:0] rsp_query,output reg [3:0] rsp_price,output reg [63:0] rsp_design,output reg [511:0] rsp_data,
 output wire busy,fault,
 output reg [63:0] m_araddr,output wire [7:0] m_arlen,output wire [2:0] m_arsize,output wire [1:0] m_arburst,output wire [3:0] m_arid,
 output wire m_arvalid,input wire m_arready,input wire [511:0] m_rdata,input wire [3:0] m_rid,input wire [1:0] m_rresp,input wire m_rlast,m_rvalid,output wire m_rready
);
 // State-table contents are immutable while configured; query labels are not cached here.
 reg cache_valid;
 reg [511:0] cache_data;
 reg [31:0] cache_connection,cache_net,cache_sink,cache_cross,cache_version,cache_revision;
 reg [63:0] cache_design;
 reg [1:0] cache_query;reg [3:0] cache_price;
 wire cache_hit=cache_valid&&req_connection==cache_connection&&req_net==cache_net&&req_sink==cache_sink&&req_cross==cache_cross&&req_version==cache_version&&revision==cache_revision&&req_design==cache_design&&req_query==cache_query&&req_price==cache_price;
 localparam IDLE=0,AR=1,R=2;
 reg [1:0] state;reg stopped,owned,context_owned,response_sent;reg [31:0] elapsed;reg [63:0] base;
 wire [64:0] end_address={1'b0,cfg_base}+({33'b0,cfg_connections}<<6);
 wire bad_config=cfg_base[5:0]!=0||cfg_connections==0||cfg_nodes==0||cfg_nets==0||cfg_revision==0||end_address>65'h10000000000000000;
 wire bad_request=req_connection>=connections||req_net>=nets||req_sink>=nodes||(req_cross&~32'h18)!=0;
 wire bad_identity=!query_active||!decision_lock||req_query!=active_query||req_price!=active_price||req_version!=active_version||req_design!=active_design||req_design!=design_id;
 wire drift=owned&&context_owned&&(!query_active||!decision_lock||active_query!=rsp_query||active_price!=rsp_price||active_version!=rsp_version||active_design!=rsp_design);
 wire unexpected=m_rvalid&&state!=R&&!(state==AR&&m_arready);
 wire bus_error=state==R&&m_rvalid&&(m_rid!=0||m_rresp!=0||!m_rlast);
 wire row_error=state==R&&m_rvalid&&(
  m_rdata[31:0]!=32'h43505331||m_rdata[63:32]!=rsp_connection||m_rdata[95:64]!=rsp_net||m_rdata[127:96]!=rsp_sink||
  m_rdata[159:128]>=nodes||m_rdata[319:288]>1||m_rdata[383:352]!=rsp_cross||m_rdata[511:480]!=0);
 wire timeout=owned&&!response_sent&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire fail_now=abort||drift||unexpected||bus_error||row_error||timeout;
 assign fault=!rst&&(stopped||fail_now);
 assign busy=!rst&&(owned||state!=IDLE||rsp_valid);
 assign cfg_ready=!rst&&!fault&&!configured&&!cfg_rsp_valid&&!busy&&!query_active&&!decision_lock;
 assign req_ready=!rst&&!fault&&configured&&!cfg_rsp_valid&&!busy;
 assign m_arvalid=!rst&&state==AR;assign m_rready=!rst&&state==R;
 assign m_arlen=0;assign m_arsize=6;assign m_arburst=1;assign m_arid=0;
 task reply(input [3:0] code,input [511:0] words);
 begin rsp_status<=code;rsp_data<=words;rsp_valid<=1;response_sent<=1;end endtask
 always @(posedge clk)begin
  if(rst)begin cache_valid<=0;cache_data<=0;cache_connection<=0;cache_net<=0;cache_sink<=0;cache_cross<=0;cache_version<=0;cache_revision<=0;cache_design<=0;cache_query<=0;cache_price<=0;state<=IDLE;stopped<=0;owned<=0;context_owned<=0;response_sent<=0;elapsed<=0;base<=0;
   cfg_rsp_valid<=0;cfg_status<=0;configured<=0;design_id<=0;nodes<=0;nets<=0;connections<=0;revision<=0;
   rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_connection<=0;rsp_net<=0;rsp_sink<=0;rsp_cross<=0;rsp_version<=0;rsp_revision<=0;rsp_query<=0;rsp_price<=0;rsp_design<=0;rsp_data<=0;m_araddr<=0;
  end else begin
   // decision_lock is deliberately absent: it drops between parent expansions.
   // An inactive query, changed full context or fault always revokes reuse.
   if(!query_active||!configured||fail_now||stopped||active_query!=cache_query||active_price!=cache_price||active_version!=cache_version||active_design!=cache_design||revision!=cache_revision)cache_valid<=0;
   if(cfg_rsp_valid&&cfg_rsp_ready)cfg_rsp_valid<=0;
   if(cfg_valid&&cfg_ready)begin cfg_rsp_valid<=1;cfg_status<=bad_config?1:0;
    if(!bad_config)begin configured<=1;base<=cfg_base;design_id<=cfg_design;nodes<=cfg_nodes;nets<=cfg_nets;connections<=cfg_connections;revision<=cfg_revision;end
   end
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;context_owned<=0;end
   if(owned&&state==IDLE&&!rsp_valid&&response_sent)owned<=0;
   if(owned&&!response_sent&&!stopped)elapsed<=elapsed+1'b1;
   case(state)
    IDLE:if(req_valid&&req_ready)begin
     owned<=1;response_sent<=0;context_owned<=0;elapsed<=0;rsp_cookie<=req_cookie;rsp_connection<=req_connection;rsp_net<=req_net;rsp_sink<=req_sink;rsp_cross<=req_cross;rsp_version<=req_version;rsp_revision<=revision;rsp_query<=req_query;rsp_price<=req_price;rsp_design<=req_design;rsp_data<=0;rsp_status<=0;
     if(bad_request)reply(1,0);
     else if(bad_identity)reply(2,0);
     else if(cache_hit)begin context_owned<=1;reply(0,cache_data);end
     else begin context_owned<=1;m_araddr<=base+({32'b0,req_connection}<<6);state<=AR;end
    end
    AR:if(m_arready)state<=R;
    R:if(m_rvalid)begin state<=IDLE;if(!response_sent&&!fail_now&&!stopped)begin
      reply(0,m_rdata);cache_valid<=1;cache_data<=m_rdata;cache_connection<=rsp_connection;cache_net<=rsp_net;cache_sink<=rsp_sink;cache_cross<=rsp_cross;cache_version<=rsp_version;cache_revision<=rsp_revision;cache_design<=rsp_design;cache_query<=rsp_query;cache_price<=rsp_price;
     endend
    default:stopped<=1;
   endcase
   if(fail_now)begin stopped<=1;if(owned&&!response_sent)reply(bus_error?4:row_error?3:5,0);end
  end
 end
endmodule
