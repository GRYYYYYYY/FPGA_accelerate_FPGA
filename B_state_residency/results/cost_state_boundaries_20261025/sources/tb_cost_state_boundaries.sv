`timescale 1ns/1ps
module tb_cost_state_boundaries;
reg hold_ar=0,hold_aw=0,hold_w=0,inject_r=0,inject_b=0;wire raw_arready,raw_awready,raw_wready;
reg clk=0;always #5 clk=~clk;
reg  rst=0;
reg  abort=0;
reg  cfg_valid=0;
wire  cfg_ready;
reg [63:0] cfg_history=0;
reg [63:0] cfg_prices=0;
reg [63:0] cfg_nets=0;
reg [63:0] cfg_design_id=0;
reg [31:0] cfg_nodes=0;
reg [31:0] cfg_net_count=0;
reg [31:0] cfg_version=0;
wire  cfg_rsp_valid;
reg  cfg_rsp_ready=0;
wire [2:0] cfg_status;
wire  configured;
reg  query_active=0;
reg  decision_lock=0;
reg [1:0] active_query=0;
reg [3:0] active_price=0;
wire  ready_for_query;
wire  editing;
wire [31:0] published_version;
wire [63:0] design_id;
reg  req_valid=0;
wire  req_ready;
reg  req_host=0;
reg [2:0] req_op=0;
reg [31:0] req_cookie=0;
reg [31:0] req_index=0;
reg [31:0] req_value=0;
reg [31:0] req_version=0;
reg [1:0] req_query=0;
reg [3:0] req_price=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_index;
wire [31:0] rsp_version;
wire [2:0] rsp_op;
wire  rsp_host;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [127:0] rsp_data;
wire  busy;
wire  fault;
wire [63:0] m_araddr;
wire [7:0] m_arlen;
wire [2:0] m_arsize;
wire [1:0] m_arburst;
wire [3:0] m_arid;
wire  m_arvalid;
wire  m_arready;
wire [511:0] m_rdata;
wire [3:0] m_rid;
wire [1:0] m_rresp;
wire  m_rlast;
wire  m_rvalid;
wire  m_rready;
wire [63:0] m_awaddr;
wire [7:0] m_awlen;
wire [2:0] m_awsize;
wire [1:0] m_awburst;
wire [3:0] m_awid;
wire  m_awvalid;
wire  m_awready;
wire [511:0] m_wdata;
wire [63:0] m_wstrb;
wire  m_wlast;
wire  m_wvalid;
wire  m_wready;
wire [3:0] m_bid;
wire [1:0] m_bresp;
wire  m_bvalid;
wire  m_bready;
cost_state_store #(.MAX_CYCLES(64))dut(.*);
integer reads,writes,rbeats,wbeats,bs;
reg[63:0]image_size=4096,prices_offset=1024,nets_offset=2048;
axi_file_memory #(.MAX_BEATS(1),.TAG("state"))memory(
.clk(clk),
.rst(rst),
.base0(cfg_history),
.base1(64'd0),
.base2(64'd0),
.size0(image_size),
.size1(64'd0),
.size2(64'd0),
.inject_r(inject_r),
.inject_b(inject_b),
.araddr(m_araddr),
.arlen(m_arlen),
.arsize(m_arsize),
.arburst(m_arburst),
.arid(m_arid),
. arvalid(m_arvalid&&!hold_ar),
.arready(raw_arready),
.rdata(m_rdata),
.rid(m_rid),
.rresp(m_rresp),
.rlast(m_rlast),
.rvalid(m_rvalid),
.rready(m_rready),
.awaddr(m_awaddr),
.awlen(m_awlen),
.awsize(m_awsize),
.awburst(m_awburst),
.awid(m_awid),
. awvalid(m_awvalid&&!hold_aw),
.awready(raw_awready),
.wdata(m_wdata),
.wstrb(m_wstrb),
.wlast(m_wlast),
. wvalid(m_wvalid&&!hold_w),
.wready(raw_wready),
.bid(m_bid),
.bresp(m_bresp),
.bvalid(m_bvalid),
.bready(m_bready),
.reads(reads),
.writes(writes),
.rbeats(rbeats),
.wbeats(wbeats),
.bresponses(bs)
);
 integer fd,rc,k,cycles=0,checks=0,reloads=0,errors=0;string initial_path;
 reg[7:0]initial_bytes[0:4095],four[0:3];reg[80:0]held_ar,held_aw;reg[575:0]held_w;reg[237:0]held_response;
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>100000)$fatal(1,"boundary watchdog state=%d owned=%b rsp=%b",dut.state,dut.owned,rsp_valid);end
 task tick;begin @(posedge clk);#1;end endtask
 task ck(input bit ok,input string message);begin if(!ok)$fatal(1,"%s state=%d",message,dut.state);checks=checks+1;end endtask
 task reset_reload(input[31:0]version);
  begin
   @(negedge clk);rst=1;abort=0;query_active=0;decision_lock=0;active_query=0;active_price=0;req_valid=0;rsp_ready=0;cfg_valid=0;cfg_rsp_ready=0;hold_ar=0;hold_aw=0;hold_w=0;inject_r=0;inject_b=0;
   cfg_history=64'h1fffff000;cfg_prices=cfg_history+1024;cfg_nets=cfg_history+2048;cfg_nodes=32;cfg_net_count=16;cfg_version=version;cfg_design_id=reloads+1;
   repeat(2)tick();rc=$fseek(memory.fd[0],0,0);if(rc)$fatal(1,"reload seek");for(k=0;k<4096;k=k+1)$fwrite(memory.fd[0],"%c",initial_bytes[k]);$fflush(memory.fd[0]);reloads=reloads+1;$fdisplay(memory.logfd,"N %0d",reloads);
   @(negedge clk);rst=0;cfg_valid=1;wait(cfg_ready);tick();@(negedge clk);cfg_valid=0;wait(cfg_rsp_valid);ck(cfg_status==0&&configured,"config");cfg_rsp_ready=1;tick();@(negedge clk);cfg_rsp_ready=0;
  end
 endtask
 task send(input bit host,input[2:0]op,input[31:0]index,value);
  begin
   wait(!busy);@(negedge clk);req_host=host;req_op=op;req_cookie=32'h1234;req_index=index;req_value=value;req_version=published_version;req_query=active_query;req_price=active_price;req_valid=1;
   wait(req_ready);tick();@(negedge clk);req_valid=0;req_op=7;req_index=0;req_value=32'hbad;req_version=0;
  end
 endtask
 task response(input[3:0]status);
  begin
   wait(rsp_valid);@(negedge clk);ck(rsp_status==status&&rsp_cookie==32'h1234,"response status/cookie");held_response={rsp_status,rsp_cookie,rsp_index,rsp_version,rsp_op,rsp_host,rsp_query,rsp_price,rsp_data};
   repeat(3)begin tick();ck(rsp_valid&&{rsp_status,rsp_cookie,rsp_index,rsp_version,rsp_op,rsp_host,rsp_query,rsp_price,rsp_data}===held_response,"response stable");end
  end
 endtask
 task retire;
  begin @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;wait(!busy);end
 endtask
 task begin_edit;
  begin send(1,4,0,0);response(0);retire();ck(editing&&!ready_for_query,"edit fence");end
 endtask
 task query_on;
  begin @(negedge clk);query_active=1;decision_lock=1;active_query=2;active_price=published_version[3:0];end
 endtask
 task stopped_check;
  begin ck(fault&&!req_ready&&!ready_for_query&&!rsp_valid,"stopped after drain");errors=errors+1;end
 endtask
 initial begin
  rst=1;if(!$value$plusargs("initial=%s",initial_path))$fatal(1,"initial path");fd=$fopen(initial_path,"rb");if(!fd)$fatal(1,"initial open");rc=$fread(initial_bytes,fd);if(rc!=4096)$fatal(1,"initial bytes");$fclose(fd);
  // Actual R error and stable already-exposed error under late abort.
  reset_reload(1);query_on();inject_r=1;send(0,0,1,0);response(4);abort=1;tick();ck(rsp_status==4,"late abort does not replace error");retire();abort=0;stopped_check();
  // An error B has already changed backing bytes: no rollback.
  reset_reload(1);begin_edit();inject_b=1;send(1,1,17,32'h41000000);response(4);retire();rc=$fseek(memory.fd[0],68,0);rc=$fread(four,memory.fd[0]);ck(rc==4&&{four[3],four[2],four[1],four[0]}==32'h41000000,"failed B physically changed history");stopped_check();
  // AR is retained through abort; error can retire before physical drain.
  reset_reload(1);query_on();hold_ar=1;send(0,0,17,0);wait(m_arvalid);@(negedge clk);held_ar={m_araddr,m_arlen,m_arsize,m_arburst,m_arid};abort=1;
  repeat(4)begin tick();ck(m_arvalid&&{m_araddr,m_arlen,m_arsize,m_arburst,m_arid}===held_ar&&!m_arready,"AR stable on abort");end
  response(5);@(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;ck(busy&&m_arvalid,"busy until late AR drain");hold_ar=0;abort=0;wait(!busy);stopped_check();
  // AW and W each retain their payload when the other channel has progressed.
  reset_reload(1);begin_edit();hold_aw=1;send(1,1,2,32'h40400000);wait(m_awvalid);@(negedge clk);held_aw={m_awaddr,m_awlen,m_awsize,m_awburst,m_awid};abort=1;
  repeat(4)begin tick();ck(m_awvalid&&{m_awaddr,m_awlen,m_awsize,m_awburst,m_awid}===held_aw&&!m_awready,"AW stable on abort");end
  response(5);@(negedge clk);abort=0;hold_aw=0;retire();stopped_check();
  reset_reload(1);begin_edit();hold_w=1;send(1,1,31,32'h40800000);wait(m_wvalid);@(negedge clk);held_w={m_wstrb,m_wdata};abort=1;
  repeat(4)begin tick();ck(m_wvalid&&{m_wstrb,m_wdata}===held_w&&!m_wready,"W stable on abort");end
  response(5);@(negedge clk);abort=0;hold_w=0;retire();stopped_check();
  // Timeout also preserves pending AR and requires drain before reuse/reset.
  reset_reload(1);query_on();hold_ar=1;send(0,2,255,0);response(5);ck(m_arvalid&&busy,"timeout pending AR");@(negedge clk);hold_ar=0;retire();stopped_check();
  // Query context cannot change while a reader owns a request.
  reset_reload(1);query_on();hold_ar=1;send(0,6,15,0);wait(m_arvalid);@(negedge clk);active_query=1;response(5);hold_ar=0;retire();stopped_check();
  // A caller attempting to enter a query during editing violates the fence.
  reset_reload(1);begin_edit();query_on();tick();ck(fault&&!rsp_valid&&!ready_for_query,"query/edit fence violation");errors=errors+1;
  // Never wrap the full published generation.
  reset_reload(32'hffffffff);begin_edit();send(1,5,0,0);response(6);retire();ck(published_version==32'hffffffff&&editing,"version did not wrap");stopped_check();
  // Explicit final reload recovers, and persistent storage matches imported state.
  reset_reload(1);query_on();send(0,0,17,0);response(0);ck(rsp_data==128'h40040000,"reload recovered imported history");retire();ck(!fault&&ready_for_query,"normal recovery");
  $display("COST_STATE_BOUNDARY_PASS checks=%0d errors=%0d reloads=%0d reads=%0d writes=%0d bs=%0d cycles=%0d",checks,errors,reloads,reads,writes,bs,cycles);$finish;
 end

assign m_arready=raw_arready&&!hold_ar;
assign m_awready=raw_awready&&!hold_aw;
assign m_wready=raw_wready&&!hold_w;
endmodule
