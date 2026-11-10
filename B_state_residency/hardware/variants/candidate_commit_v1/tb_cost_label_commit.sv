`timescale 1ns/1ps
module tb_cost_label_commit;
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
reg [31:0] req_parent=0;
reg [31:0] req_child=0;
reg [31:0] req_sequence=0;
reg [31:0] req_partial=0;
reg [31:0] req_total=0;
wire  rsp_valid;
reg  rsp_ready=0;
wire [3:0] rsp_status;
wire [2:0] rsp_acked;
wire [31:0] rsp_cookie;
wire [31:0] rsp_parent;
wire [31:0] rsp_child;
wire [31:0] rsp_sequence;
wire [31:0] rsp_version;
wire [1:0] rsp_query;
wire [3:0] rsp_price;
wire [63:0] rsp_design;
wire [159:0] rsp_payload;
wire  busy;
wire  fault;
wire  l_valid;
reg  l_ready=0;
wire  l_write;
wire [31:0] l_node;
wire [31:0] l_value;
wire [2:0] l_field;
reg  l_rsp_valid=0;
wire  l_rsp_ready;
reg [3:0] l_status=0;
reg [159:0] l_payload=0;
reg  l_present=0;
cost_label_commit #(.MAX_CYCLES(128)) dut(.clk(clk),.rst(rst),.abort(abort),.active(active),.decision_lock(decision_lock),.active_query(active_query),.active_price(active_price),.active_version(active_version),.active_design(active_design),.req_valid(req_valid),.req_ready(req_ready),.req_cookie(req_cookie),.req_parent(req_parent),.req_child(req_child),.req_sequence(req_sequence),.req_partial(req_partial),.req_total(req_total),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.rsp_status(rsp_status),.rsp_acked(rsp_acked),.rsp_cookie(rsp_cookie),.rsp_parent(rsp_parent),.rsp_child(rsp_child),.rsp_sequence(rsp_sequence),.rsp_version(rsp_version),.rsp_query(rsp_query),.rsp_price(rsp_price),.rsp_design(rsp_design),.rsp_payload(rsp_payload),.busy(busy),.fault(fault),.l_valid(l_valid),.l_ready(l_ready),.l_write(l_write),.l_node(l_node),.l_value(l_value),.l_field(l_field),.l_rsp_valid(l_rsp_valid),.l_rsp_ready(l_rsp_ready),.l_status(l_status),.l_payload(l_payload),.l_present(l_present));
always #5 clk=~clk;
integer cases=0,step,fail_step;reg[159:0] memory,held;reg[31:0] held_value;reg[2:0] held_field;
task tick;begin @(posedge clk);#1;end endtask
task setup;begin
 @(negedge clk);rst=1;abort=0;req_valid=0;rsp_ready=0;l_ready=0;l_rsp_valid=0;l_status=0;l_present=1;l_payload=0;
 repeat(3)tick();@(negedge clk);rst=0;active=1;decision_lock=1;active_query=1;active_price=3;active_version=32'h10003;active_design=55;
 req_cookie=77;req_parent=9;req_child=10;req_sequence=32'h80000021;req_partial=32'h80000000;req_total=32'h7fc12345;
 memory={32'd1,32'd17,32'd9,32'd0,32'd0};tick();
end endtask
task launch;begin @(negedge clk);req_valid=1;if(!req_ready)$fatal(1,"ready");tick();@(negedge clk);req_valid=0;end endtask
task accept_write(input integer index);begin
 if(!l_valid||!l_write||l_node!=10||l_field!=(index==0?0:index==1?1:3)||l_value!==(index==0?req_total:index==1?req_partial:req_sequence))$fatal(1,"write order/value %d",index);
 held_value=l_value;held_field=l_field;repeat(3)begin tick();if(!l_valid||l_value!==held_value||l_field!=held_field||req_ready||!busy)$fatal(1,"command hold");end
 @(negedge clk);l_ready=1;tick();memory[held_field*32+:32]=held_value;@(negedge clk);l_ready=0;
 repeat(3)begin tick();if(l_valid)$fatal(1,"advanced before ACK");end
end endtask
task ack(input integer error_kind);begin
 @(negedge clk);l_payload=memory;l_status=error_kind==2?3:0;l_present=error_kind!=3;
 if(error_kind==1)l_payload[held_field*32+:32]=l_payload[held_field*32+:32]^1;
 if(error_kind==4)l_payload[95:64]=8;
 l_rsp_valid=1;if(!l_rsp_ready)$fatal(1,"not waiting ACK");tick();@(negedge clk);l_rsp_valid=0;
end endtask
task response(input integer status,input integer acked);begin
 wait(rsp_valid);@(negedge clk);
 if(rsp_status!=status||rsp_acked!=acked||rsp_cookie!=77||rsp_parent!=9||rsp_child!=10||rsp_sequence!=32'h80000021||rsp_version!=32'h10003||rsp_query!=1||rsp_price!=3||rsp_design!=55)$fatal(1,"response identity/status actual=%0d/%0d expected=%0d/%0d",rsp_status,rsp_acked,status,acked);
 held=rsp_payload;repeat(4)begin tick();if(!rsp_valid||rsp_payload!==held||rsp_status!=status||rsp_acked!=acked||req_ready)$fatal(1,"reply hold");end
 @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;cases=cases+1;$display("CASE %0d %0d %0d %040h %0d",cases,rsp_status,rsp_acked,rsp_payload,fault);
end endtask
task drained;begin repeat(4)tick();if(busy||rsp_valid||l_valid)$fatal(1,"not drained");end endtask
initial begin
 setup();launch();for(step=0;step<3;step=step+1)begin accept_write(step);ack(0);end
 response(0,7);if(rsp_payload!==memory)$fatal(1,"full payload/raw NaN/negative-zero bits");drained();if(!req_ready||fault)$fatal(1,"normal next request");
 for(fail_step=0;fail_step<3;fail_step=fail_step+1)begin
  setup();launch();for(step=0;step<=fail_step;step=step+1)begin accept_write(step);ack(step==fail_step?1:0);end
  response(1,(1<<fail_step)-1);drained();if(!fault||req_ready)$fatal(1,"bad field did not stop");
 end
 setup();launch();accept_write(0);ack(2);response(1,0);drained();
 setup();launch();accept_write(0);ack(3);response(1,0);drained();
 setup();launch();accept_write(0);ack(4);response(1,0);drained();
 setup();launch();@(negedge clk);abort=1;tick();@(negedge clk);abort=0;response(2,0);
 if(!busy||!l_valid||l_field!=0)$fatal(1,"abort dropped exposed write");accept_write(0);ack(0);drained();if(!fault||req_ready)$fatal(1,"abort did not stop");
 setup();launch();accept_write(0);@(negedge clk);abort=1;tick();@(negedge clk);abort=0;response(2,0);
 if(!busy||!l_rsp_ready)$fatal(1,"abort lost pending ACK");ack(0);drained();
 setup();launch();repeat(140)tick();response(2,0);if(!l_valid||!busy)$fatal(1,"timeout dropped write");accept_write(0);ack(0);drained();
 setup();launch();accept_write(0);ack(0);@(negedge clk);active_version=active_version+65536;response(2,1);
 if(!l_valid||l_field!=1||!busy)$fatal(1,"version drift lost pending stage");accept_write(1);ack(0);drained();
 setup();launch();for(step=0;step<3;step=step+1)begin accept_write(step);ack(0);end
 @(negedge clk);active_design=active_design+1;response(0,7);if(!fault)$fatal(1,"late identity fault");drained();
 setup();@(negedge clk);l_rsp_valid=1;tick();@(negedge clk);l_rsp_valid=0;tick();if(!fault||req_ready||rsp_valid||busy)$fatal(1,"idle spurious reply");cases=cases+1;$display("IDLEFAULT %0d",cases);
 $display("COST_LABEL_COMMIT_UNIT_PASS cases=%0d",cases);$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
