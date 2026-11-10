`timescale 1ns/1ps
module tb_owner;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,cfg_valid=0,cfg_rsp_ready=1,req_valid=0,rsp_ready=0;
 wire cfg_ready,cfg_rsp_valid,configured,req_ready,rsp_valid,fault,busy;
 wire[2:0]cfg_status;wire[3:0]rsp_status;
 reg[2:0]req_op=0;reg[31:0]req_cookie=0,req_node=0,req_net=0;
 wire[31:0]rsp_cookie,rsp_count,rsp_occupancy;wire rsp_will_overuse;
 reg hold_ar=0,hold_aw=0,hold_w=0,hold_r=0,hold_b=0,inject_r=0,inject_b=0,bad_rid=0,bad_bid=0,bad_last=0,phantom_r=0,phantom_b=0;
 wire raw_arready,raw_awready,raw_wready,raw_rvalid,raw_bvalid,raw_rlast;wire[3:0]raw_rid,raw_bid;
 reg[63:0]cfg_primary=64'h1fffff000,cfg_pool=64'h200000000,cfg_allocator=64'h200002000;reg[31:0]cfg_nodes=128,cfg_capacity=256;
 wire[63:0]m_araddr,m_awaddr;wire[7:0]m_arlen,m_awlen;wire[2:0]m_arsize,m_awsize;wire[1:0]m_arburst,m_awburst;wire[3:0]m_arid,m_awid,m_rid,m_bid;
 wire m_arvalid,m_arready,m_rvalid,m_rready,m_rlast,m_awvalid,m_awready,m_wvalid,m_wready,m_wlast,m_bvalid,m_bready;
 wire[511:0]m_rdata,m_wdata;wire[63:0]m_wstrb;wire[1:0]m_rresp,m_bresp;
 integer reads,writes,rbeats,wbeats,bresponses;
 localparam[63:0]BASE=64'h1fffff000;
 owner_state_store #(.MAX_CYCLES(2048)) dut(.clk(clk),.rst(rst),.abort(abort),.cfg_valid(cfg_valid),.cfg_ready(cfg_ready),.cfg_primary(cfg_primary),.cfg_pool(cfg_pool),.cfg_allocator(cfg_allocator),.cfg_nodes(cfg_nodes),.cfg_capacity(cfg_capacity),.*);
 axi_file_memory #(.MAX_BEATS(1),.TAG("owner")) memory(.clk(clk),.rst(rst),.base0(BASE),.base1(64'd0),.base2(64'd0),.size0(64'd16384),.size1(64'd0),.size2(64'd0),
  .araddr(m_araddr),.arlen(m_arlen),.arsize(m_arsize),.arburst(m_arburst),.arid(m_arid),.arvalid(m_arvalid&&!hold_ar),.arready(raw_arready),.rdata(m_rdata),.rid(raw_rid),.rresp(m_rresp),.rlast(raw_rlast),.rvalid(raw_rvalid),.rready(m_rready&&!hold_r),
  .awaddr(m_awaddr),.awlen(m_awlen),.awsize(m_awsize),.awburst(m_awburst),.awid(m_awid),.awvalid(m_awvalid&&!hold_aw),.awready(raw_awready),.wdata(m_wdata),.wstrb(m_wstrb),.wlast(m_wlast),.wvalid(m_wvalid&&!hold_w),.wready(raw_wready),.bid(raw_bid),.bresp(m_bresp),.bvalid(raw_bvalid),.bready(m_bready&&!hold_b),
  .inject_r(inject_r),.inject_b(inject_b),.*);
 assign m_arready=raw_arready&&!hold_ar;assign m_awready=raw_awready&&!hold_aw;assign m_wready=raw_wready&&!hold_w;
 assign m_rvalid=(raw_rvalid&&!hold_r)||phantom_r;assign m_bvalid=(raw_bvalid&&!hold_b)||phantom_b;
 assign m_rid=bad_rid?4'd1:raw_rid;assign m_bid=bad_bid?4'd1:raw_bid;assign m_rlast=bad_last?1'b0:raw_rlast;
 `include "boundary_body.inc"
endmodule
