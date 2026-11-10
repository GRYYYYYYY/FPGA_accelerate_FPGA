`timescale 1ns/1ps
module tb_connection_state;
reg  clk=0;
reg  rst=0;
reg  abort=0;
reg  cfg_valid=0;
wire  cfg_ready;
reg [63:0] cfg_base=0;
reg [63:0] cfg_design=0;
reg [31:0] cfg_connections=0;
reg [31:0] cfg_nodes=0;
reg [31:0] cfg_nets=0;
reg [31:0] cfg_revision=0;
wire  cfg_rsp_valid;
reg  cfg_rsp_ready=0;
wire [2:0] cfg_status;
wire  configured;
wire [63:0] design_id;
wire [31:0] nodes;
wire [31:0] nets;
wire [31:0] connections;
wire [31:0] revision;
reg  query_active=0;
reg  decision_lock=0;
reg [1:0] active_query=0;
reg [3:0] active_price=0;
reg [31:0] active_version=0;
reg [63:0] active_design=0;
reg  req_valid=0;
wire  req_ready;
reg [31:0] req_cookie=0;
reg [31:0] req_connection=0;
reg [31:0] req_net=0;
reg [31:0] req_sink=0;
reg [31:0] req_cross=0;
reg [31:0] req_version=0;
reg [1:0] req_query=0;
reg [3:0] req_price=0;
reg [63:0] req_design=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_connection;
wire [31:0] rsp_net;
wire [31:0] rsp_sink;
wire [31:0] rsp_cross;
wire [31:0] rsp_version;
wire [31:0] rsp_revision;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [63:0] rsp_design;
wire [511:0] rsp_data;
wire  busy;
wire  fault;
wire [63:0] m_araddr;
wire [7:0] m_arlen;
wire [2:0] m_arsize;
wire [1:0] m_arburst;
wire [3:0] m_arid;
wire  m_arvalid;
reg  m_arready=0;
reg [511:0] m_rdata=0;
reg [3:0] m_rid=0;
reg [1:0] m_rresp=0;
reg  m_rlast=0;
reg  m_rvalid=0;
wire  m_rready;
connection_state_reader #(.MAX_CYCLES(64)) dut(.clk(clk),.rst(rst),.abort(abort),.cfg_valid(cfg_valid),.cfg_ready(cfg_ready),.cfg_base(cfg_base),.cfg_design(cfg_design),.cfg_connections(cfg_connections),.cfg_nodes(cfg_nodes),.cfg_nets(cfg_nets),.cfg_revision(cfg_revision),.cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(cfg_rsp_ready),.cfg_status(cfg_status),.configured(configured),.design_id(design_id),.nodes(nodes),.nets(nets),.connections(connections),.revision(revision),.query_active(query_active),.decision_lock(decision_lock),.active_query(active_query),.active_price(active_price),.active_version(active_version),.active_design(active_design),.req_valid(req_valid),.req_ready(req_ready),.req_cookie(req_cookie),.req_connection(req_connection),.req_net(req_net),.req_sink(req_sink),.req_cross(req_cross),.req_version(req_version),.req_query(req_query),.req_price(req_price),.req_design(req_design),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.rsp_connection(rsp_connection),.rsp_net(rsp_net),.rsp_sink(rsp_sink),.rsp_cross(rsp_cross),.rsp_version(rsp_version),.rsp_revision(rsp_revision),.rsp_query(rsp_query),.rsp_price(rsp_price),.rsp_design(rsp_design),.rsp_data(rsp_data),.busy(busy),.fault(fault),.m_araddr(m_araddr),.m_arlen(m_arlen),.m_arsize(m_arsize),.m_arburst(m_arburst),.m_arid(m_arid),.m_arvalid(m_arvalid),.m_arready(m_arready),.m_rdata(m_rdata),.m_rid(m_rid),.m_rresp(m_rresp),.m_rlast(m_rlast),.m_rvalid(m_rvalid),.m_rready(m_rready));
always #5 clk=~clk;
integer successes=0,errors=0,fd,i,n,idx;integer serial=0,tag_mode=0,expected_revision=1,ars=0;
always @(posedge clk)if(m_arvalid&&m_arready)ars<=ars+1;reg[511:0] row,held;reg[31:0] words[0:15];reg[2047:0] input_path;
task tick;begin @(posedge clk);#1;end endtask
task setup;begin
 @(negedge clk);rst=1;abort=0;req_valid=0;m_rvalid=0;m_arready=0;rsp_ready=0;query_active=0;decision_lock=0;cfg_valid=0;cfg_rsp_ready=1;
 repeat(3)tick();@(negedge clk);rst=0;cfg_base=64'h8100000000;cfg_design=64'h123456789abcdef0;cfg_connections=180326;cfg_nodes=9089009;cfg_nets=27960;cfg_revision=expected_revision;cfg_valid=1;
 tick();if(!configured||cfg_status!=0)$fatal(1,"config");@(negedge clk);cfg_valid=0;tick();
 query_active=1;decision_lock=1;active_query=2;active_price=3;active_version=32'h10003;active_design=cfg_design;
end endtask
task request(input integer ci);begin
 @(negedge clk);serial=serial+1;req_cookie=serial+100;req_connection=ci;req_net=row[95:64];req_sink=row[127:96];req_cross=row[383:352];req_version=active_version;req_query=active_query;req_price=active_price;req_design=active_design;if(tag_mode==1)req_net=(req_net+1)%27960;if(tag_mode==2)req_sink=(req_sink+1)%9089009;if(tag_mode==3)req_cross=req_cross^8;req_valid=1;
 if(!req_ready)$fatal(1,"not ready");tick();@(negedge clk);req_valid=0;
end endtask
task address_phase;begin
 repeat(3)begin tick();if(!m_arvalid||m_araddr!=cfg_base+64*req_connection||m_arlen!=0||m_arsize!=6||m_arburst!=1||m_arid!=0)$fatal(1,"AR unstable");end
 @(negedge clk);m_arready=1;tick();@(negedge clk);m_arready=0;
end endtask
task data_phase(input integer error_code);begin
 @(negedge clk);m_rdata=row;m_rid=0;m_rresp=error_code;m_rlast=1;m_rvalid=1;tick();@(negedge clk);m_rvalid=0;
end endtask
task retire(input integer code);begin
 if(!rsp_valid||rsp_status!=code||rsp_cookie!=req_cookie||rsp_connection!=req_connection||rsp_version!=req_version||rsp_design!=req_design||rsp_revision!=expected_revision)$fatal(1,"reply identity/code actual=%d expected=%d",rsp_status,code);
 held=rsp_data;repeat(4)begin tick();if(!rsp_valid||rsp_data!==held||req_ready||cfg_ready||!busy)$fatal(1,"response hold");end
 @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;repeat(3)tick();
 if(busy)$fatal(1,"not drained");if(code==0)begin successes=successes+1;$display("ROW %0d %h",rsp_connection,rsp_data);end else errors=errors+1;
end endtask
initial begin
 if(!$value$plusargs("input=%s",input_path))$fatal(1,"missing input");fd=$fopen(input_path,"rb");if(!fd)$fatal(1,"input open");setup();
 for(idx=0;idx<180326;idx=idx+997)begin
 n=$fseek(fd,idx*64,0);row=0;for(i=0;i<64;i=i+1)begin n=$fgetc(fd);if(n<0)$fatal(1,"short input");row[i*8+:8]=n;end
 request(idx);address_phase();data_phase(0);if(rsp_data!==row)$fatal(1,"raw words");retire(0);
 end
 // Last record, then bad request/identity: no bus transaction.
 idx=180325;n=$fseek(fd,idx*64,0);for(i=0;i<64;i=i+1)begin n=$fgetc(fd);row[i*8+:8]=n;end
 request(idx);address_phase();data_phase(0);retire(0);
 // Cache hit must return a fresh cookie and stable complete row with no AR.
 request(180325);if(m_arvalid||rsp_data!==row)$fatal(1,"resident hit");retire(0);
 decision_lock=0;repeat(3)tick();decision_lock=1;
 request(180325);if(m_arvalid||rsp_data!==row)$fatal(1,"inter-parent reuse");retire(0);
 query_active=0;repeat(2)tick();query_active=1;
 request(180325);address_phase();data_phase(0);retire(0);
 active_version=active_version+65536;
 request(180325);address_phase();data_phase(0);retire(0);
 active_price=active_price+1;
 request(180325);address_phase();data_phase(0);retire(0);
 active_query=active_query+1;
 request(180325);address_phase();data_phase(0);retire(0);
 request(180326);if(m_arvalid)$fatal(1,"invalid index reached bus");retire(1);
 @(negedge clk);req_cookie=9876;req_connection=180325;req_version=active_version+65536;req_valid=1;tick();@(negedge clk);req_valid=0;
 if(m_arvalid)$fatal(1,"stale version reached bus");retire(2);
 active_version=active_version+1;request(0); // request() uses new version; force identity failure separately below
 address_phase();data_phase(0);retire(3);if(!fault)$fatal(1,"bad row did not stop");
 setup();request(180325);address_phase();data_phase(2);retire(4);if(!fault)$fatal(1,"bus fault");
 setup();request(180325);repeat(2)tick();@(negedge clk);abort=1;tick();@(negedge clk);abort=0;
 if(!rsp_valid||rsp_status!=5||!m_arvalid)$fatal(1,"abort dropped address");
 @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;repeat(2)tick();if(!busy)$fatal(1,"ownership lost before drain");
 address_phase();data_phase(0);repeat(4)tick();if(busy||rsp_valid||!fault||req_ready)$fatal(1,"abort drain");errors=errors+1;
 setup();request(180325);address_phase();active_version=active_version+65536;tick();if(!fault||rsp_status!=5)$fatal(1,"full version drift");data_phase(0);retire(5);
 setup();request(180325);repeat(70)tick();if(!fault||!rsp_valid||rsp_status!=5||!m_arvalid)$fatal(1,"timeout");address_phase();data_phase(0);retire(5);
 // Matching connection but different net/sink/cross must miss and fail row
 // validation, even though a fully valid row was just cached.
 for(tag_mode=1;tag_mode<=3;tag_mode=tag_mode+1)begin
  n=tag_mode;tag_mode=0;setup();request(180325);address_phase();data_phase(0);retire(0);tag_mode=n;
  request(180325);address_phase();data_phase(0);retire(3);if(!fault)$fatal(1,"wrong-tag cache alias");
 end
 tag_mode=0;expected_revision=2;setup();request(180325);address_phase();data_phase(0);retire(0);
 request(180325);if(m_arvalid||rsp_data!==row)$fatal(1,"new profile hit");retire(0);
 active_design=active_design^64'h100000000;request(180325);if(m_arvalid)$fatal(1,"wrong design bus");retire(2);
 active_design=cfg_design;request(180325);address_phase();data_phase(0);retire(0);
 request(180325);active_version=active_version+65536;tick();if(!fault||rsp_status!=0||rsp_data!==row)$fatal(1,"cached response late drift stability");retire(0);
 if(successes!=195||errors!=11||ars!=199)$fatal(1,"boundary totals success=%0d errors=%0d AR=%0d",successes,errors,ars);
 $display("CONNECTION_RESIDENT_PASS successes=%0d errors=%0d AR=%0d",successes,errors,ars);$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
