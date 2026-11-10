`timescale 1ns/1ps
module tb_cost_offer;
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
reg [31:0] req_node=0;
reg [31:0] req_key=0;
reg [31:0] req_before=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [31:0] rsp_cookie;
wire [31:0] rsp_node;
wire [31:0] rsp_key;
wire [31:0] rsp_before;
wire [31:0] rsp_size;
wire [31:0] rsp_version;
wire [31:0] rsp_backend_status;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [63:0] rsp_design;
wire  busy;
wire  fault;
wire  f_valid;
reg  f_ready=0;
wire [31:0] f_key;
wire [31:0] f_id;
wire [31:0] f_cookie;
wire [31:0] f_version;
wire [63:0] f_design;
wire [1:0] f_query;
wire [3:0] f_price;
reg  f_rsp_valid=0;
wire  f_rsp_ready;
reg [31:0] f_rsp_status=0;
reg [31:0] f_rsp_cookie=0;
reg [31:0] f_rsp_size=0;
reg [31:0] f_rsp_version=0;
reg [63:0] f_rsp_design=0;
reg [1:0] f_rsp_query=0;
reg [3:0] f_rsp_price=0;
cost_offer #(.MAX_CYCLES(128)) dut(.clk(clk),.rst(rst),.abort(abort),.active(active),.decision_lock(decision_lock),.active_query(active_query),.active_price(active_price),.active_version(active_version),.active_design(active_design),.req_valid(req_valid),.req_ready(req_ready),.req_cookie(req_cookie),.req_node(req_node),.req_key(req_key),.req_before(req_before),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_cookie(rsp_cookie),.rsp_node(rsp_node),.rsp_key(rsp_key),.rsp_before(rsp_before),.rsp_size(rsp_size),.rsp_version(rsp_version),.rsp_backend_status(rsp_backend_status),.rsp_query(rsp_query),.rsp_price(rsp_price),.rsp_design(rsp_design),.busy(busy),.fault(fault),.f_valid(f_valid),.f_ready(f_ready),.f_key(f_key),.f_id(f_id),.f_cookie(f_cookie),.f_version(f_version),.f_design(f_design),.f_query(f_query),.f_price(f_price),.f_rsp_valid(f_rsp_valid),.f_rsp_ready(f_rsp_ready),.f_rsp_status(f_rsp_status),.f_rsp_cookie(f_rsp_cookie),.f_rsp_size(f_rsp_size),.f_rsp_version(f_rsp_version),.f_rsp_design(f_rsp_design),.f_rsp_query(f_rsp_query),.f_rsp_price(f_rsp_price));
always #5 clk=~clk;
integer cases=0,kind;reg [31:0] before_value;reg [127:0] held;
task tick;begin @(posedge clk);#1;end endtask
task setup(input integer before_size);begin
 @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;f_ready=0;f_rsp_valid=0;repeat(3)tick();@(negedge clk);rst=0;active=1;decision_lock=1;active_query=1;active_price=3;active_version=32'h10003;active_design=55;
 req_cookie=77;req_node=42;req_key=32'h7fc12345;req_before=before_size;before_value=before_size;tick();
end endtask
task launch;begin @(negedge clk);req_valid=1;if(!req_ready)$fatal(1,"request ready");tick();@(negedge clk);req_valid=0;req_cookie=999;req_node=999;req_key=0;req_before=999;end endtask
task accept_backend;begin
 repeat(3)begin tick();if(!f_valid||f_key!==32'h7fc12345||f_id!=42||f_cookie!=77||f_version!=32'h10003||f_design!=55||f_query!=1||f_price!=3||req_ready||!busy)$fatal(1,"snapshot/address hold");end
 @(negedge clk);f_ready=1;tick();@(negedge clk);f_ready=0;repeat(2)tick();
end endtask
task reply(input integer injected);begin
 @(negedge clk);f_rsp_status=0;f_rsp_cookie=77;f_rsp_query=1;f_rsp_price=3;f_rsp_version=32'h10003;f_rsp_design=55;f_rsp_size=before_value+1;
 case(injected)
 1:f_rsp_cookie=78;2:f_rsp_query=2;3:f_rsp_price=4;4:f_rsp_version=32'h20003;5:f_rsp_design=56;6:f_rsp_size=before_value;7:f_rsp_status=3;
 8:begin f_rsp_status=2;f_rsp_size=65536;end
 endcase
 f_rsp_valid=1;if(!f_rsp_ready)$fatal(1,"backend reply not owned");tick();@(negedge clk);f_rsp_valid=0;
end endtask
task response(input integer code);begin
 wait(rsp_valid);@(negedge clk);if(rsp_status!=code||rsp_cookie!=77||rsp_node!=42||rsp_key!==32'h7fc12345||rsp_before!=before_value||rsp_version!=32'h10003||rsp_design!=55||rsp_query!=1||rsp_price!=3)$fatal(1,"reply identity/status");
 held={rsp_key,rsp_node,rsp_before,rsp_size};repeat(4)begin tick();if(!rsp_valid||{rsp_key,rsp_node,rsp_before,rsp_size}!==held||rsp_status!=code||req_ready)$fatal(1,"response hold");end
 @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;cases=cases+1;$display("CASE %0d %0d %0d %0d %0d",cases,rsp_status,rsp_before,rsp_size,fault);
end endtask
task drained;begin repeat(4)tick();if(busy||rsp_valid||f_valid)$fatal(1,"not drained");end endtask
initial begin
 setup(3);launch();accept_backend();reply(0);response(0);drained();if(fault||!req_ready)$fatal(1,"normal completion");
 for(kind=1;kind<=7;kind=kind+1)begin setup(3);launch();accept_backend();reply(kind);response(1);drained();if(!fault||req_ready)$fatal(1,"bad response did not stop");end
 setup(65536);launch();accept_backend();reply(8);response(2);drained();if(!fault||req_ready)$fatal(1,"FULL not stopped");
 setup(3);launch();accept_backend();reply(8);response(1);drained();
 setup(3);launch();@(negedge clk);abort=1;tick();@(negedge clk);abort=0;response(3);if(!busy||!f_valid)$fatal(1,"abort lost exposed offer");accept_backend();reply(0);drained();
 setup(3);launch();accept_backend();@(negedge clk);abort=1;tick();@(negedge clk);abort=0;response(3);if(!busy||!f_rsp_ready)$fatal(1,"abort lost pending reply");reply(0);drained();
 setup(3);launch();repeat(140)tick();response(3);if(!f_valid||!busy)$fatal(1,"timeout withdrew offer");accept_backend();reply(0);drained();
 setup(3);launch();accept_backend();@(negedge clk);active_version=active_version+65536;response(3);reply(0);drained();
 setup(3);launch();accept_backend();reply(0);@(negedge clk);active_design=56;response(0);if(!fault)$fatal(1,"late identity fault");drained();
 setup(3);@(negedge clk);f_rsp_valid=1;tick();@(negedge clk);f_rsp_valid=0;tick();if(!fault||req_ready||rsp_valid||busy)$fatal(1,"spurious reply");cases=cases+1;
 $display("COST_OFFER_UNIT_PASS cases=%0d",cases);$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
