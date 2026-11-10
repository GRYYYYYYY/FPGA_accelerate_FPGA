`timescale 1ns/1ps
module tb_node_expansion_fault;
 reg clk=0;always #5 clk=~clk;
 reg  rst=0;
 reg  g_cfg_valid=0;
 wire  g_cfg_ready;
 reg [63:0] g_cfg_offsets_base=0;
 reg [63:0] g_cfg_edges_base=0;
 reg [63:0] g_cfg_attrs_base=0;
 reg [31:0] g_cfg_nodes=0;
 reg [31:0] g_cfg_edges=0;
 wire  g_cfg_rsp_valid;
 reg  g_cfg_rsp_ready=0;
 wire [2:0] g_cfg_status;
 wire  g_configured;
 wire [63:0] g_m_araddr;
 wire [7:0] g_m_arlen;
 wire [2:0] g_m_arsize;
 wire [1:0] g_m_arburst;
 wire [3:0] g_m_arid;
 wire  g_m_arvalid;
 wire  g_m_arready;
 wire [511:0] g_m_rdata;
 wire [3:0] g_m_rid;
 wire [1:0] g_m_rresp;
 wire  g_m_rlast;
 wire  g_m_rvalid;
 wire  g_m_rready;
 reg  d_cfg_valid=0;
 wire  d_cfg_ready;
 reg [63:0] d_cfg_base=0;
 reg [31:0] d_cfg_nodes=0;
 wire  d_cfg_rsp_valid;
 reg  d_cfg_rsp_ready=0;
 wire [2:0] d_cfg_status;
 wire  d_configured;
 wire [63:0] d_m_araddr;
 wire [7:0] d_m_arlen;
 wire [2:0] d_m_arsize;
 wire [1:0] d_m_arburst;
 wire [3:0] d_m_arid;
 wire  d_m_arvalid;
 wire  d_m_arready;
 wire [511:0] d_m_rdata;
 wire [3:0] d_m_rid;
 wire [1:0] d_m_rresp;
 wire  d_m_rlast;
 wire  d_m_rvalid;
 wire  d_m_rready;
 wire [63:0] d_m_awaddr;
 wire [7:0] d_m_awlen;
 wire [2:0] d_m_awsize;
 wire [1:0] d_m_awburst;
 wire [3:0] d_m_awid;
 wire  d_m_awvalid;
 wire  d_m_awready;
 wire [511:0] d_m_wdata;
 wire [63:0] d_m_wstrb;
 wire  d_m_wlast;
 wire  d_m_wvalid;
 wire  d_m_wready;
 wire [3:0] d_m_bid;
 wire [1:0] d_m_bresp;
 wire  d_m_bvalid;
 wire  d_m_bready;
 wire [31:0] p_m_awaddr;
 wire [7:0] p_m_awlen;
 wire [2:0] p_m_awsize;
 wire [1:0] p_m_awburst;
 wire [3:0] p_m_awid;
 wire  p_m_awvalid;
 wire  p_m_awready;
 wire [511:0] p_m_wdata;
 wire [63:0] p_m_wstrb;
 wire  p_m_wlast;
 wire  p_m_wvalid;
 wire  p_m_wready;
 wire [3:0] p_m_bid;
 wire [1:0] p_m_bresp;
 wire  p_m_bvalid;
 wire  p_m_bready;
 wire [31:0] p_m_araddr;
 wire [7:0] p_m_arlen;
 wire [2:0] p_m_arsize;
 wire [1:0] p_m_arburst;
 wire [3:0] p_m_arid;
 wire  p_m_arvalid;
 wire  p_m_arready;
 wire [511:0] p_m_rdata;
 wire [3:0] p_m_rid;
 wire [1:0] p_m_rresp;
 wire  p_m_rlast;
 wire  p_m_rvalid;
 wire  p_m_rready;
 reg  expand_valid=0;
 wire  expand_ready;
 reg [31:0] expand_cookie=0;
 reg [31:0] expand_parent=0;
 reg [31:0] expand_prune=0;
 reg [31:0] expand_has_laguna=0;
 wire  out_valid;
 reg  out_ready=0;
 wire [31:0] out_node;
 wire [31:0] out_position;
 wire [31:0] out_sequence;
 wire [255:0] out_attrs;
 wire  result_valid;
 reg  result_ready=0;
 wire [3:0] result_status;
 wire [31:0] result_detail;
 wire [31:0] result_cookie;
 wire [31:0] result_count;
 wire [31:0] result_raw_count;
 wire [31:0] result_mask;
 wire  result_hit;
 wire  busy;
 wire  fault;
 reg  host_ctrl_valid=0;
 wire  host_ctrl_ready;
 reg [1:0] host_ctrl_op=0;
 reg [1:0] host_ctrl_query=0;
 reg [3:0] host_ctrl_price=0;
 wire  host_ctrl_rsp_valid;
 reg  host_ctrl_rsp_ready=0;
 wire [3:0] host_ctrl_status;
 reg  host_io_valid=0;
 wire  host_io_ready;
 reg  host_io_write=0;
 reg [31:0] host_io_node=0;
 reg [31:0] host_io_value=0;
 reg [2:0] host_io_field=0;
 wire  host_io_rsp_valid;
 reg  host_io_rsp_ready=0;
 wire [3:0] host_io_status;
 wire [159:0] host_io_payload;
 wire  host_io_present;
 wire  p_active;
 wire [1:0] p_active_query;
 wire [3:0] p_active_price;
`ifdef PRESSURE
 localparam SLOTS=1,TX_BITS=6,GEN_BITS=3;
`else
 localparam SLOTS=32,TX_BITS=16,GEN_BITS=16;
`endif
`ifdef TOKEN_LIMIT
 localparam TEST_TOKEN_BITS=4,TEST_OWNER_BITS=32;
`elsif OWNER_LIMIT
 localparam TEST_TOKEN_BITS=32,TEST_OWNER_BITS=3;
`else
 localparam TEST_TOKEN_BITS=32,TEST_OWNER_BITS=32;
`endif
 node_expansion_engine #(.TOKEN_BITS(TEST_TOKEN_BITS),.OWNER_BITS(TEST_OWNER_BITS),.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(256),.INDEX_BITS(8),.HASH_BITS(8)) dut(.*);
 reg inject_graph=0,inject_design=0,inject_design_b=0,inject_pager=0,inject_pager_b=0;
 integer g_reads,g_writes,g_rbeats,g_wbeats,g_bs;
 axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("graph")) mem_g(
  .clk(clk),
  .rst(rst),
  .base0(g_cfg_offsets_base),
  .base1(g_cfg_edges_base),
  .base2(g_cfg_attrs_base),
  .size0(64'd36356096),
  .size1(64'd161878144),
  .size2(64'd290848320),
  .inject_r(inject_graph),
  .inject_b(1'b0),
  .araddr(g_m_araddr),
  .arlen(g_m_arlen),
  .arsize(g_m_arsize),
  .arburst(g_m_arburst),
  .arid(g_m_arid),
  .arvalid(g_m_arvalid),
  .arready(g_m_arready),
  .rdata(g_m_rdata),
  .rid(g_m_rid),
  .rresp(g_m_rresp),
  .rlast(g_m_rlast),
  .rvalid(g_m_rvalid),
  .rready(g_m_rready),
  .awaddr('0),
  .awlen('0),
  .awsize('0),
  .awburst('0),
  .awid('0),
  .awvalid('0),
  .awready(),
  .wdata('0),
  .wstrb('0),
  .wlast('0),
  .wvalid('0),
  .wready(),
  .bid(),
  .bresp(),
  .bvalid(),
  .bready('0),
  .reads(g_reads),
  .writes(g_writes),
  .rbeats(g_rbeats),
  .wbeats(g_wbeats),
  .bresponses(g_bs)
 );
 integer d_reads,d_writes,d_rbeats,d_wbeats,d_bs;
 axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.TAG("design")) mem_d(
  .clk(clk),
  .rst(rst),
  .base0(d_cfg_base),
  .base1(64'd0),
  .base2(64'd0),
  .size0(64'd145424192),
  .size1(64'd0),
  .size2(64'd0),
  .inject_r(inject_design),
  .inject_b(inject_design_b),
  .araddr(d_m_araddr),
  .arlen(d_m_arlen),
  .arsize(d_m_arsize),
  .arburst(d_m_arburst),
  .arid(d_m_arid),
  .arvalid(d_m_arvalid),
  .arready(d_m_arready),
  .rdata(d_m_rdata),
  .rid(d_m_rid),
  .rresp(d_m_rresp),
  .rlast(d_m_rlast),
  .rvalid(d_m_rvalid),
  .rready(d_m_rready),
  .awaddr(d_m_awaddr),
  .awlen(d_m_awlen),
  .awsize(d_m_awsize),
  .awburst(d_m_awburst),
  .awid(d_m_awid),
  .awvalid(d_m_awvalid),
  .awready(d_m_awready),
  .wdata(d_m_wdata),
  .wstrb(d_m_wstrb),
  .wlast(d_m_wlast),
  .wvalid(d_m_wvalid),
  .wready(d_m_wready),
  .bid(d_m_bid),
  .bresp(d_m_bresp),
  .bvalid(d_m_bvalid),
  .bready(d_m_bready),
  .reads(d_reads),
  .writes(d_writes),
  .rbeats(d_rbeats),
  .wbeats(d_wbeats),
  .bresponses(d_bs)
 );
 integer p_reads,p_writes,p_rbeats,p_wbeats,p_bs;
 axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(0),.MAX_BEATS(3),.TAG("labels")) mem_p(
  .clk(clk),
  .rst(rst),
  .base0(64'd0),
  .base1(64'd0),
  .base2(64'd0),
  .size0(64'd49152),
  .size1(64'd0),
  .size2(64'd0),
  .inject_r(inject_pager),
  .inject_b(inject_pager_b),
  .araddr(p_m_araddr),
  .arlen(p_m_arlen),
  .arsize(p_m_arsize),
  .arburst(p_m_arburst),
  .arid(p_m_arid),
  .arvalid(p_m_arvalid),
  .arready(p_m_arready),
  .rdata(p_m_rdata),
  .rid(p_m_rid),
  .rresp(p_m_rresp),
  .rlast(p_m_rlast),
  .rvalid(p_m_rvalid),
  .rready(p_m_rready),
  .awaddr(p_m_awaddr),
  .awlen(p_m_awlen),
  .awsize(p_m_awsize),
  .awburst(p_m_awburst),
  .awid(p_m_awid),
  .awvalid(p_m_awvalid),
  .awready(p_m_awready),
  .wdata(p_m_wdata),
  .wstrb(p_m_wstrb),
  .wlast(p_m_wlast),
  .wvalid(p_m_wvalid),
  .wready(p_m_wready),
  .bid(p_m_bid),
  .bresp(p_m_bresp),
  .bvalid(p_m_bvalid),
  .bready(p_m_bready),
  .reads(p_reads),
  .writes(p_writes),
  .rbeats(p_rbeats),
  .wbeats(p_wbeats),
  .bresponses(p_bs)
 );
 integer scenario=0,cycles=0,k,old_reads;reg expected_fault=0;
 reg[164:0]held_result;reg[351:0]held_child;
 always @(posedge clk)begin
  cycles<=cycles+1;if(cycles>1000000)$fatal(1,"boundary watchdog scenario=%0d state=%0d",scenario,dut.controller.state);
  if(!rst)begin
   if(fault&&!expected_fault)$fatal(1,"unplanned fault scenario=%0d state=%0d status=%0d detail=%0d",scenario,dut.controller.state,result_status,result_detail);
   if(busy&&(host_ctrl_ready||host_io_ready||expand_ready))$fatal(1,"admission during busy/fault");
  end
 end
 task configure;
  begin
   rst=1;repeat(5)@(negedge clk);rst=0;
   g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
   d_cfg_base=64'h31fffff000;d_cfg_nodes=scenario==11?9089008:9089009;
   @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;wait(g_cfg_ready&&d_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;
   wait(g_cfg_rsp_valid&&d_cfg_rsp_valid);@(negedge clk);if(g_cfg_status||d_cfg_status)$fatal(1,"config");g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;@(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;
  end
 endtask
 task open_query;
  begin
   @(negedge clk);host_ctrl_valid=1;host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;
   wait(host_ctrl_rsp_valid);@(negedge clk);if(host_ctrl_status)$fatal(1,"open");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
  end
 endtask
 task start(input[31:0]parent,prune,laguna);
  begin
   @(negedge clk);expand_parent=parent;expand_prune=prune;expand_has_laguna=laguna;expand_cookie=expand_cookie+1;expand_valid=1;
   wait(expand_ready);@(posedge clk);@(negedge clk);expand_valid=0;
   host_ctrl_valid=1;host_ctrl_op=2;host_io_valid=1;host_io_write=1;host_io_node=parent;host_io_field=2;host_io_value=32'hbadabcde;
  end
 endtask
 task response(input integer status,detail,failed);
  begin
   wait(result_valid);@(negedge clk);
   if(result_status!=status||result_detail!=detail||result_cookie!=expand_cookie||fault!==failed)$fatal(1,"response scenario=%0d st=%0d/%0d detail=%0d/%0d fault=%b/%0d",scenario,result_status,status,result_detail,detail,fault,failed);
   held_result={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};
   repeat(4)begin @(negedge clk);if(!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==held_result||!busy)$fatal(1,"result hold");end
   result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;
   if(failed&&!busy)$fatal(1,"fault lost lock");
  end
 endtask
 initial begin
  if(!$value$plusargs("scenario=%d",scenario))$fatal(1,"scenario");expected_fault=scenario!=0;
  configure();
  if(scenario==11)begin
   repeat(5)@(negedge clk);host_ctrl_valid=1;host_io_valid=1;
   repeat(5)begin @(negedge clk);if(!fault||!busy||result_valid||host_ctrl_ready||host_io_ready||expand_ready||g_reads||d_reads)$fatal(1,"mismatched config");end
  end else begin
   open_query();
   case(scenario)
    0:begin
     start(0,2,0);response(1,0,0);start(0,0,2);response(1,0,0);start(9089009,0,0);response(1,0,0);
     if(g_reads||d_reads)$fatal(1,"invalid request AXI");start(0,0,0);response(0,0,0);
    end
    1:begin inject_graph=1;start(0,0,0);response(4,0,1);if(dut.d_claim_active||d_writes)$fatal(1,"META error claimed state");end
    2:begin inject_design=1;start(0,0,0);response(4,0,1);if(dut.d_claim_active||d_writes)$fatal(1,"CLAIM read error wrote");end
    3:begin start(9,0,0);wait(dut.g_req_valid&&dut.g_req_op==1);inject_graph=1;response(4,0,1);if(!dut.d_claim_active)$fatal(1,"NEXT error lost claim");end
    4:begin start(9,0,0);wait(dut.d_req_valid&&dut.d_req_op==2);inject_design_b=1;response(4,0,1);if(!dut.d_claim_active||d_writes!=1)$fatal(1,"CREATE error lost claim");end
    5:begin start(0,0,0);wait(dut.d_req_valid&&dut.d_req_op==5);inject_design_b=1;response(4,0,1);if(!dut.d_claim_active||d_writes!=1)$fatal(1,"PUBLISH error lost claim");end
    6:begin start(9,0,0);wait(dut.p_edge_valid);force dut.p_fault=1;response(4,0,1);if(!dut.d_claim_active)$fatal(1,"pager fault claim");release dut.p_fault;end
    7:begin start(0,0,0);wait(dut.g_rsp_valid);force dut.g_rsp_cookie=0;response(5,1,1);release dut.g_rsp_cookie;end
    8:begin start(0,0,0);wait(dut.d_rsp_valid);force dut.d_rsp_cookie=0;response(5,5,1);release dut.d_rsp_cookie;end
    9:begin start(9,0,0);wait(dut.p_result_valid);force dut.p_result_cookie=0;response(5,24,1);release dut.p_result_cookie;end
    10:begin
     start(0,0,0);wait(result_valid);@(negedge clk);held_result={result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit};force dut.g_fault=1;
     repeat(4)begin @(negedge clk);if(!fault||!result_valid||{result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}!==held_result)$fatal(1,"late final mutation");end
     response(0,0,1);release dut.g_fault;
    end
    12:begin
     start(9,0,0);wait(out_valid);@(negedge clk);held_child={out_node,out_position,out_sequence,out_attrs};force dut.g_fault=1;
     repeat(4)begin @(negedge clk);if(!fault||!out_valid||{out_node,out_position,out_sequence,out_attrs}!==held_child)$fatal(1,"late stream mutation");end
     out_ready=1;@(negedge clk);out_ready=0;response(4,0,1);release dut.g_fault;
    end
    13:begin
     start(9,0,0);response(3,1,1);
     if(dut.controller.token!=15||!dut.d_claim_active||dut.d_claim_mask!=3)$fatal(1,"token exhaustion boundary token=%d mask=%h",dut.controller.token,dut.d_claim_mask);
    end
    14:begin
     for(k=0;k<7;k=k+1)begin start(0,0,0);response(0,0,0);end
     old_reads=g_reads;start(0,0,0);response(3,0,1);
     if(dut.controller.last_owner!=7||g_reads!=old_reads||dut.d_claim_active)$fatal(1,"owner exhaustion boundary");
    end
    default:$fatal(1,"unknown scenario");
   endcase
  end
  repeat(8)@(negedge clk);
  if(scenario!=0&&(!fault||!busy||expand_ready||host_ctrl_ready||host_io_ready))$fatal(1,"fault persistence");
  $display("EXPANSION_BOUNDARY_PASS scenario=%0d fault=%0d claim=%0d token=%0d owner=%0d graph_reads=%0d design_reads=%0d design_writes=%0d cycles=%0d",scenario,fault,dut.d_claim_active,dut.controller.token,dut.controller.last_owner,g_reads,d_reads,d_writes,cycles);$finish;
 end

endmodule
