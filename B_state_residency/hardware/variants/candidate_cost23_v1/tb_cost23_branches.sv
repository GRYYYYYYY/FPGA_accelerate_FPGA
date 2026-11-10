`timescale 1ns/1ps
module tb_cost23_branches;
reg  clk=0;
reg  rst=0;
reg  abort=0;
reg  active=0;
reg  decision_lock=0;
reg [1:0] active_query=0;
reg [3:0] active_price=0;
reg [31:0] active_version=0;
reg [63:0] active_design=0;
reg  req_valid=0;
wire  req_ready;
reg [31:0] req_cookie=0;
reg [31:0] req_child=0;
reg [31:0] req_sink=0;
reg [511:0] req_params=0;
reg [447:0] req_config=0;
reg [255:0] req_attrs=0;
reg [31:0] req_count=0;
reg [31:0] req_history=0;
reg [31:0] req_price_value=0;
reg [31:0] req_x=0;
reg [31:0] req_y=0;
reg [31:0] req_upstream=0;
reg [31:0] req_center=0;
reg [127:0] req_net=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_child;
wire [31:0] rsp_version;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [63:0] rsp_design;
wire [735:0] rsp_packet;
wire [159:0] rsp_cost;
wire [415:0] rsp_geometry;
wire [127:0] rsp_geometry_result;
wire  busy;
wire  fault;
wire  c_req_valid;
reg  c_req_ready=0;
wire [31:0] c_req_cookie;
wire [31:0] c_req_node;
wire [1:0] c_req_query;
wire [1:0] c_req_op;
wire [3:0] c_req_price;
reg  c_rsp_valid=0;
wire  c_rsp_ready;
reg [3:0] c_rsp_status=0;
reg [31:0] c_rsp_cookie=0;
reg [31:0] c_rsp_node=0;
reg [31:0] c_rsp_y=0;
reg [31:0] c_rsp_slr=0;
reg [31:0] c_rsp_next=0;
reg [31:0] c_rsp_prev_column=0;
reg [255:0] c_rsp_attrs=0;
reg [1:0] c_rsp_op=0;
reg [1:0] c_rsp_query=0;
reg [3:0] c_rsp_price=0;
cost23_inputs dut(.clk(clk),.rst(rst),.abort(abort),.active(active),.decision_lock(decision_lock),.active_query(active_query),.active_price(active_price),.active_version(active_version),.active_design(active_design),.req_valid(req_valid),.req_ready(req_ready),.req_cookie(req_cookie),.req_child(req_child),.req_sink(req_sink),.req_params(req_params),.req_config(req_config),.req_attrs(req_attrs),.req_count(req_count),.req_history(req_history),.req_price_value(req_price_value),.req_x(req_x),.req_y(req_y),.req_upstream(req_upstream),.req_center(req_center),.req_net(req_net),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.rsp_child(rsp_child),.rsp_version(rsp_version),.rsp_query(rsp_query),.rsp_price(rsp_price),.rsp_design(rsp_design),.rsp_packet(rsp_packet),.rsp_cost(rsp_cost),.rsp_geometry(rsp_geometry),.rsp_geometry_result(rsp_geometry_result),.busy(busy),.fault(fault),.c_req_valid(c_req_valid),.c_req_ready(c_req_ready),.c_req_cookie(c_req_cookie),.c_req_node(c_req_node),.c_req_query(c_req_query),.c_req_op(c_req_op),.c_req_price(c_req_price),.c_rsp_valid(c_rsp_valid),.c_rsp_ready(c_rsp_ready),.c_rsp_status(c_rsp_status),.c_rsp_cookie(c_rsp_cookie),.c_rsp_node(c_rsp_node),.c_rsp_y(c_rsp_y),.c_rsp_slr(c_rsp_slr),.c_rsp_next(c_rsp_next),.c_rsp_prev_column(c_rsp_prev_column),.c_rsp_attrs(c_rsp_attrs),.c_rsp_op(c_rsp_op),.c_rsp_query(c_rsp_query),.c_rsp_price(c_rsp_price));
always #5 clk=~clk;
integer reads=0,mode=0,expected_reads=0,cases=0;reg [735:0] held_packet;reg [159:0] held_cost;
always @(posedge clk)begin
 if(rst)begin reads<=0;c_rsp_valid<=0;c_req_ready<=0;end
 else begin
  c_req_ready<=!c_rsp_valid;
  if(c_rsp_valid&&c_rsp_ready)c_rsp_valid<=0;
  if(c_req_valid&&c_req_ready)begin
   reads<=reads+1;c_rsp_valid<=1;c_rsp_status<=0;c_rsp_cookie<=c_req_cookie;c_rsp_node<=c_req_node;c_rsp_op<=c_req_op;c_rsp_query<=c_req_query;c_rsp_price<=c_req_price;c_rsp_attrs<=req_attrs;
   if(c_req_op==1)begin
    if(reads==0&&c_req_node!=42)$fatal(1,"expected sink SLR first");
    if(reads==1&&c_req_node!=43)$fatal(1,"expected child SLR second");
    c_rsp_y<=c_req_node==42?40:20;c_rsp_slr<=c_req_node==42?0:(mode==1?0:1);
   end else begin
    if(c_req_op!=2||c_req_node!=43||reads!=2)$fatal(1,"column order");
    c_rsp_next<=15;c_rsp_prev_column<=5;
   end
  end
 end
end
task tick;begin @(posedge clk);#1;end endtask
task setup(input integer selected_mode);begin
 @(negedge clk);rst=1;req_valid=0;rsp_ready=0;abort=0;mode=selected_mode;repeat(3)tick();@(negedge clk);rst=0;active=1;decision_lock=1;active_query=1;active_price=3;active_version=32'h10003;active_design=64'h123456789abcdef0;
 req_cookie=77;req_child=43;req_sink=42;req_params=0;req_params[191:160]=32'h3f800000;req_params[223:192]=32'h3f000000;req_params[255:224]=32'h3f4ccccd;req_params[351:320]=60;req_params[383:352]=8;
 req_config=0;req_config[8*32+:32]=30;req_config[9*32+:32]=40;req_config[10*32+:32]=0;req_config[11*32+:32]=100;
 req_attrs=0;req_attrs[191:160]=32'h3f800000;req_attrs[159:144]=2;req_count=3;req_history=32'h3f800000;req_price_value=32'h3f800000;req_x=10;req_y=20;req_upstream=32'h3f800000;req_center=32'h40000000;req_net={32'd10,32'd2,64'd0};
end endtask
task launch;begin
 @(negedge clk);req_valid=1;if(!req_ready)$fatal(1,"ready");tick();@(negedge clk);req_valid=0;
end endtask
task retire(input integer code);begin
 wait(rsp_valid);@(negedge clk);if(rsp_status!=code||rsp_cookie!=77||rsp_child!=43||rsp_version!=32'h10003||rsp_design!=64'h123456789abcdef0)$fatal(1,"response identity/code");
 held_packet=rsp_packet;held_cost=rsp_cost;repeat(5)begin tick();if(!rsp_valid||rsp_packet!==held_packet||rsp_cost!==held_cost||req_ready)$fatal(1,"hold");end
 @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;cases=cases+1;
end endtask
initial begin
 setup(0);launch();wait(rsp_valid);@(negedge clk);$display("OBS geometry=%032h packet12=%0d sf=%08h reads=%0d status=%0d",rsp_geometry_result,rsp_packet[12*32+:32],rsp_cost[31:0],reads,rsp_status);if(rsp_geometry_result!={32'd120,32'd100,32'd20,32'd0}||rsp_packet[12*32+:32]!=120||rsp_cost[31:0]!=32'h40800000||reads!=3)$fatal(1,"cross SLR geometry/actual cost");retire(0);
 $display("BRANCH cross_different_slr geometry=%032h cost=%040h",rsp_geometry_result,rsp_cost);
 setup(1);launch();wait(rsp_valid);@(negedge clk);$display("OBS geometry=%032h packet12=%0d sf=%08h reads=%0d status=%0d",rsp_geometry_result,rsp_packet[12*32+:32],rsp_cost[31:0],reads,rsp_status);if(rsp_geometry_result!={32'd40,32'd20,32'd20,32'd0}||reads!=2)$fatal(1,"same SLR should skip columns");retire(0);
 $display("BRANCH cross_same_slr geometry=%032h cost=%040h",rsp_geometry_result,rsp_cost);
 setup(2);req_params[383:352]=0;launch();wait(rsp_valid);@(negedge clk);$display("OBS geometry=%032h packet12=%0d sf=%08h reads=%0d status=%0d",rsp_geometry_result,rsp_packet[12*32+:32],rsp_cost[31:0],reads,rsp_status);if(rsp_geometry_result!={32'd40,32'd20,32'd20,32'd0}||reads!=0)$fatal(1,"noncross should skip tables");retire(0);
 setup(0);req_params[319:288]=1;launch();retire(6);if(!fault||reads!=0||dut.geometry.bridge.state!=0||dut.arithmetic.bridge.state!=0)$fatal(1,"landmark unsupported accepted");
 setup(2);req_params[383:352]=0;launch();wait(dut.state==10);@(negedge clk);active_version=active_version+65536;retire(5);if(!fault)$fatal(1,"full version drift");
 $display("COST23_BRANCHES_PASS cases=%0d coordinate_requests=3+2+0+0+0",cases);$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
