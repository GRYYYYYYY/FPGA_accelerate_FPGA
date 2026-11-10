`timescale 1ns/1ps
module tb_rebase;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,permit=1,rebase=1,valid=0,restore=1,rsp_ready=0,svalid=0,slast=0,mready=0,cmd_valid=0;
wire ready,busy,rsp_valid,sready,mvalid,mlast,cmd_ready,cmd_rsp_valid;wire[3:0]status,cmd_status;wire[31:0]crc,mindex,mdata;
reg[31:0]index=0,data=0,expected_crc=0,source_version=4;reg[1:0]source_query=2;reg[3:0]source_price=4;
reg[31:0]active_version=5;reg[1:0]active_query=3;reg[3:0]active_price=5;
reg[447:0]expand=0;reg[31:0]image[0:9];integer checks=0,cycles=0,trace;reg active=1;reg prev_permit=1,prev_abort=0,prev_rst=0;
reg safe=1,edit=0;
query_lifecycle #(.ENABLE_REBASE(1),.CP_SAFE_EXCLUDES_HOST_EDIT(1)) dut(.clk(clk),.rst(rst),.abort(abort),.admit(1'b1),.backend_fault(1'b0),.backend_drained(1'b1),.active(active),.host_label_edit(edit),.active_generation(64'h100000002),
.cp_rebase(rebase),.cp_rebase_permit(permit),.cp_source_version(source_version),.cp_source_query(source_query),.cp_source_price(source_price),
.cp_valid(valid),.cp_restore(restore),.cp_safe(safe),.cp_ready(ready),.cp_busy(busy),.cp_expected_crc(expected_crc),.cp_rsp_valid(rsp_valid),.cp_rsp_ready(rsp_ready),.cp_status(status),.cp_crc(crc),.cp_s_valid(svalid),.cp_s_ready(sready),.cp_s_index(index),.cp_s_data(data),.cp_s_last(slast),.cp_m_valid(mvalid),.cp_m_ready(mready),.cp_m_index(mindex),.cp_m_data(mdata),.cp_m_last(mlast),
.active_design(64'h123456789abcdef0),.active_version(active_version),.active_query(active_query),.active_price(active_price),.route_slots(2'b01),
.cmd_valid(cmd_valid),.cmd_ready(cmd_ready),.cmd_slot(1'b1),.cmd_cookie(32'd7),.cmd_route_cookie(32'd8),.cmd_source(32'd65185),.cmd_key(32'd0),.cmd_nodes(32'd9089009),.cmd_max_polls(32'd65536),.cmd_poll_cookie(32'd9),.cmd_design(64'h123456789abcdef0),.cmd_query(active_query),.cmd_price(active_price),.cmd_expand(expand),.rsp_valid(cmd_rsp_valid),.rsp_ready(cmd_rsp_valid),.rsp_status(cmd_status),
.service_ready(1'b0),.service_rsp_valid(1'b0),.service_rsp_payload(256'd0),.search_ready(1'b0),.search_rsp_valid(1'b0),.search_status(4'd0),.search_rsp_cookie(32'd0),.search_result_node(32'd0),.route_ready(1'b0),.route_rsp_valid(1'b0),.route_status(4'd0),.route_rsp_cookie(32'd0),.route_nodes(32'd0),.route_acked(32'd0));
function automatic[31:0]sum;reg[31:0]v;begin v=32'hffffffff;for(integer i=0;i<10;i=i+1)begin v=v^image[i];for(integer b=0;b<32;b=b+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;end sum=~v;end endfunction
task check(input bit ok);begin checks=checks+1;if(!ok)$fatal(1,"check %0d",checks);end endtask
task reset_dut;begin @(negedge clk);rst=1;repeat(3)@(negedge clk);rst=0;end endtask
task start(input bit load);begin @(negedge clk);restore=load;valid=1;do @(posedge clk);while(!ready);@(negedge clk);valid=0;end endtask
task words(input integer count);begin for(integer i=0;i<count;i=i+1)begin @(negedge clk);index=i;data=image[i];slast=i==9;svalid=1;do @(posedge clk);while(!sready);@(negedge clk);svalid=0;end end endtask
task result(input[3:0]wanted,input integer floor);reg[31:0]held;begin wait(rsp_valid);held=crc;repeat(8)begin @(negedge clk);check(status==wanted&&crc==held&&dut.last_sequence==floor&&!cmd_ready);end rsp_ready=1;@(negedge clk);rsp_ready=0;wait(!busy);end endtask
always @(posedge clk)begin
 cycles=cycles+1;
 if(rst&&!prev_rst)$fdisplay(trace,"Z %0d",cycles);prev_rst=rst;
 if(permit!=prev_permit||abort!=prev_abort)$fdisplay(trace,"P %0d %0d %0d",cycles,permit,abort);prev_permit=permit;prev_abort=abort;if(cycles>5000)$fatal(1,"watchdog");
 if(valid&&ready)$fdisplay(trace,"S %0d %0d %0d %0d %0d %0d %0d %0d %0d",cycles,rebase,permit,source_version,active_version,expected_crc,restore,source_query,source_price);
 if(svalid&&sready)$fdisplay(trace,"W %0d %0d %08h %0d",cycles,index,data,slast);
 if(rsp_valid&&rsp_ready)$fdisplay(trace,"R %0d %0d %08h %0d %0d %0d %0d",cycles,status,crc,dut.last_sequence,dut.last_version,dut.last_query,dut.last_price);
 if(mvalid&&mready)$fdisplay(trace,"M %0d %0d %08h %0d",cycles,mindex,mdata,mlast);
 if(cmd_rsp_valid)$fdisplay(trace,"Q %0d %0d",cycles,cmd_status);
end

 integer safe_busy=0,edit_busy=0,overlaps=0;
 always @(posedge clk)if(!rst&&busy)begin
  if(safe)safe_busy=safe_busy+1;
  if(edit)edit_busy=edit_busy+1;
  if(safe&&edit)overlaps=overlaps+1;
 end
initial begin
 trace=$fopen("native.txt","w");$readmemh("query.hex",image);repeat(3)@(negedge clk);rst=0;expected_crc=sum();

 start(1);words(5);check(dut.last_sequence==0);
 @(negedge clk);edit=1;

 for(integer i=5;i<10;i=i+1)begin
  @(negedge clk);index=i;data=image[i];slast=i==9;svalid=1;
  do @(posedge clk);while(!sready);@(negedge clk);svalid=0;
 end
 edit=0;result(0,1);check(crc==sum());

 check(safe_busy>0&&edit_busy>0);
 check(overlaps>0);
 $fdisplay(trace,"CP_EDIT_MONITOR %0d %0d %0d",safe_busy,edit_busy,overlaps);
 $fdisplay(trace,"DONE %0d",checks);$fclose(trace);$display("CHECKPOINT_EDIT_FOCUS_PASS checks=%0d",checks);$finish;
end
endmodule
