`timescale 1ns/1ps
module tb_rearm_loop;
reg  clk=0;
reg  cold_rst=0;
reg  external_abort=0;
reg  external_safe=0;
reg  external_normal_retired=0;
reg  physical_drained=0;
wire  l_start_offer;
wire  l_rearm_retired;
reg  k_cfg_stage=0;
reg  k_publish_valid=0;
reg  k_publish_permit=0;
reg  k_discard_valid=0;
wire  k_publish_ready;
wire  k_discard_ready;
wire  k_staged_valid;
wire [63:0] k_staged_design;
wire [31:0] k_staged_checkpoint;
wire [31:0] k_staged_version;
wire [31:0] k_active_version;
wire [1:0] k_staged_query;
wire [1:0] k_active_query;
wire [3:0] k_staged_price;
wire [3:0] k_active_price;
wire  k_attempt_reset;
reg  k_cfg_valid=0;
wire  k_cfg_ready;
reg  k_cfg_authoritative=0;
reg [63:0] k_cfg_design=0;
reg [31:0] k_cfg_checkpoint=0;
reg [31:0] k_cfg_version=0;
reg [1:0] k_cfg_query=0;
reg [3:0] k_cfg_price=0;
wire  k_cfg_rsp_valid;
reg  k_cfg_rsp_ready=0;
wire  k_cfg_status;
reg  k_j_valid=0;
wire  k_j_ready;
reg [31:0] k_j_node=0;
reg [31:0] k_j_net=0;
reg [2:0] k_j_op=0;
wire [31:0] k_journal_count;
wire  k_journal_full;
wire  k_permit_work;
reg  k_recover_valid=0;
wire  k_recover_ready;
reg [31:0] k_recover_cookie=0;
reg [31:0] k_recover_checkpoint=0;
reg [31:0] k_recover_version=0;
reg [63:0] k_recover_design=0;
reg [1:0] k_recover_query=0;
reg [3:0] k_recover_price=0;
wire  k_target_reset;
wire  k_reconfigure_valid;
wire  k_labels_valid;
reg  k_reconfigure_done=0;
reg  k_labels_done=0;
wire [63:0] k_saved_design;
wire [31:0] k_saved_checkpoint;
wire [31:0] k_new_version;
wire [1:0] k_new_query;
wire [3:0] k_new_price;
wire  k_rsp_valid;
reg  k_rsp_ready=0;
wire [3:0] k_rsp_status;
wire [31:0] k_rsp_cookie;
wire [31:0] k_rsp_corrected;
wire  k_busy;
wire  k_fault;
wire  k_a_valid;
reg  k_a_ready=0;
wire [31:0] k_a_node;
wire [31:0] k_a_net;
wire [31:0] k_a_cookie;
wire [31:0] k_a_checkpoint;
wire [63:0] k_a_design;
reg  k_a_rsp_valid=0;
wire  k_a_rsp_ready;
reg [3:0] k_a_status=0;
reg [31:0] k_a_rsp_cookie=0;
reg [31:0] k_a_rsp_checkpoint=0;
reg [31:0] k_a_refs=0;
reg [31:0] k_a_occupancy=0;
reg [63:0] k_a_rsp_design=0;
wire  k_o_valid;
reg  k_o_ready=0;
wire [2:0] k_o_op;
wire [31:0] k_o_node;
wire [31:0] k_o_net;
wire [31:0] k_o_cookie;
reg  k_o_rsp_valid=0;
wire  k_o_rsp_ready;
reg [3:0] k_o_status=0;
reg [31:0] k_o_rsp_cookie=0;
reg [31:0] k_o_count=0;
reg [31:0] k_o_occupancy=0;
reg  l_start_skip_seed=0;
wire  l_l_import;
wire  l_l_probe;
wire  l_start_ready;
reg [63:0] l_expected_design=0;
reg [31:0] l_expected_checkpoint=0;
reg [31:0] l_start_cookie=0;
reg [31:0] l_start_count=0;
reg [31:0] l_start_nodes=0;
reg [31:0] l_start_probe=0;
reg [31:0] l_start_source_crc=0;
wire [31:0] l_rsp_source_crc;
reg  l_s_valid=0;
wire  l_s_ready;
reg [31:0] l_s_node=0;
reg [31:0] l_s_cookie=0;
reg [159:0] l_s_payload=0;
reg  l_s_last=0;
wire  l_rsp_valid;
reg  l_rsp_ready=0;
wire [3:0] l_rsp_status;
wire [31:0] l_rsp_cookie;
wire [31:0] l_written;
wire [31:0] l_verified;
wire  l_busy;
wire  l_fault;
wire  l_c_valid;
reg  l_c_ready=0;
wire [1:0] l_c_op;
wire [1:0] l_c_query;
wire [3:0] l_c_price;
wire [31:0] l_c_version;
reg  l_c_rsp_valid=0;
wire  l_c_rsp_ready;
reg [3:0] l_c_status=0;
wire  l_l_valid;
reg  l_l_ready=0;
wire  l_l_write;
wire [31:0] l_l_node;
wire [31:0] l_l_value;
wire [2:0] l_l_field;
reg  l_l_rsp_valid=0;
wire  l_l_rsp_ready;
reg [3:0] l_l_status=0;
reg  l_l_present=0;
reg [159:0] l_l_payload=0;
always #5 clk=~clk;
rearm_loop_slice dut(.*);
reg started=0;reg[159:0]ram=0;reg present=0;
integer scenario=0,checks=0,resets=0,writes=0,reads=0,successes=0,failures=0;
reg[159:0]payload=160'h0000000500000004000000030000000200000001;
function[31:0]crcword(input[31:0]c0,w);reg[31:0]c;begin c=c0;for(integer j=0;j<32;j=j+1)c=(c[0]^w[j])?((c>>1)^32'hedb88320):(c>>1);crcword=c;end endfunction
function[31:0]payload_crc;reg[31:0]c;begin c=crcword(32'hffffffff,7);for(integer j=0;j<5;j=j+1)c=crcword(c,payload[j*32+:32]);payload_crc=~c;end endfunction
always @(posedge clk)begin
 if(cold_rst)begin l_c_rsp_valid<=0;l_l_rsp_valid<=0;ram<=0;present<=0;started<=0;k_labels_done<=0;resets<=0;writes<=0;reads<=0;end
 else begin
  if(k_a_valid||k_o_valid)$fatal(1,"J0 unexpectedly accessed owner or authority");
  if(k_attempt_reset)begin
   if(!external_safe||!external_normal_retired||!physical_drained||l_rsp_valid||!l_rearm_retired||k_a_rsp_valid||k_o_rsp_valid)$fatal(1,"unsafe rearm pulse");
   resets<=resets+1;started<=0;k_labels_done<=0;
   $display("RESET %0d %0d",scenario,k_new_version);
  end
  if(k_target_reset)begin started<=0;k_labels_done<=0;end
  if(k_labels_valid&&l_start_offer&&l_start_ready)started<=1;
  if(l_rsp_valid&&l_rsp_ready&&l_rsp_status==0)k_labels_done<=1;
  if(l_c_rsp_valid&&l_c_rsp_ready)l_c_rsp_valid<=0;
  if(l_c_valid&&l_c_ready)begin
   if(l_c_rsp_valid)$fatal(1,"config overlap");l_c_rsp_valid<=1;l_c_status<=0;
   if(l_c_op==0)begin ram<=0;present<=0;end
  end
  if(l_l_rsp_valid&&l_l_rsp_ready)l_l_rsp_valid<=0;
  if(l_l_valid&&l_l_ready)begin
   if(l_l_rsp_valid)$fatal(1,"label overlap");l_l_rsp_valid<=1;l_l_status<=0;l_l_present<=present;l_l_payload<=ram;
   if(l_l_write)begin
    if(l_l_node!=7||l_l_field>4||l_l_value!=payload[l_l_field*32+:32])$fatal(1,"restore data mismatch");
    ram[l_l_field*32+:32]<=l_l_value;present<=1;writes<=writes+1;
    $display("WRITE %0d %0d %h",scenario,l_l_field,l_l_value);
   end else begin reads<=reads+1;if(l_l_probe&&present)$fatal(1,"probe not empty");end
  end
 end
end
assign l_start_offer=!started;
task tick;begin @(posedge clk);#1;end endtask
task init(input integer mode);begin
 @(negedge clk);scenario=mode;cold_rst=1;external_abort=0;external_safe=1;external_normal_retired=1;physical_drained=1;
 k_cfg_valid=0;k_recover_valid=0;k_rsp_ready=0;k_cfg_rsp_ready=0;k_a_rsp_valid=0;k_o_rsp_valid=0;
 l_rsp_ready=0;l_s_valid=1;l_s_node=7;l_s_cookie=17;l_s_payload=payload;l_s_last=1;
 l_expected_design=99;l_expected_checkpoint=17;l_start_cookie=17;l_start_count=1;l_start_nodes=16;l_start_probe=7;l_start_skip_seed=1;
 l_start_source_crc=payload_crc()^1;l_c_ready=1;l_l_ready=1;k_reconfigure_done=1;
 repeat(3)tick;@(negedge clk);cold_rst=0;
 k_cfg_authoritative=1;k_cfg_design=99;k_cfg_checkpoint=17;k_cfg_version=1;k_cfg_query=1;k_cfg_price=1;k_cfg_valid=1;
 do tick;while(!k_cfg_rsp_valid);@(negedge clk);k_cfg_valid=0;
 if(k_cfg_status)$fatal(1,"configuration failed");k_cfg_rsp_ready=1;tick;@(negedge clk);k_cfg_rsp_ready=0;
 k_recover_design=99;k_recover_checkpoint=17;k_recover_version=2;k_recover_query=2;k_recover_price=2;k_recover_cookie=100;
end endtask
task request;begin
 @(negedge clk);k_recover_valid=1;do @(posedge clk);while(!k_recover_ready);@(negedge clk);k_recover_valid=0;
end endtask
task result(input integer status);begin
 wait(k_rsp_valid);@(negedge clk);
 repeat(8)begin tick;
  if(!k_rsp_valid||k_rsp_status!=status||k_rsp_cookie!=k_recover_cookie||k_permit_work||k_rsp_corrected||k_journal_count)$fatal(1,"held coordinator result");checks=checks+1;
 end
 $display("RESULT %0d %0d %0d %0d",scenario,k_rsp_status,k_new_version,resets);
 if(status==0)successes=successes+1;else failures=failures+1;
 @(negedge clk);k_rsp_ready=1;tick;@(negedge clk);k_rsp_ready=0;tick;
end endtask
task fail_labels;begin
 request;wait(l_rsp_valid);@(negedge clk);
 repeat(8)begin tick;if(l_rsp_status!=8||k_rsp_valid||l_rearm_retired||!l_busy||writes)$fatal(1,"failed service not retired");checks=checks+1;end
 @(negedge clk);l_rsp_ready=1;tick;@(negedge clk);l_rsp_ready=0;result(6);
 if(!l_rearm_retired||!k_fault||k_permit_work||resets)$fatal(1,"failure did not stay closed");
end endtask
task success_labels;begin
 wait(l_rsp_valid);@(negedge clk);
 repeat(8)begin tick;if(l_rsp_status||l_written!=1||l_verified!=1||k_rsp_valid||l_rearm_retired||writes!=5||ram!==payload)$fatal(1,"success before full restoration/retirement");checks=checks+1;end
 @(negedge clk);l_rsp_ready=1;tick;@(negedge clk);l_rsp_ready=0;result(0);
 if(!k_permit_work||k_fault||!l_rearm_retired||resets!=1)$fatal(1,"successful retry did not release");
end endtask
initial begin
 for(integer mode=0;mode<3;mode=mode+1)begin
  init(mode);fail_labels;
  // Old attempt remains consumed; no transient reset is permitted.
  k_recover_cookie=101;k_recover_query=3;request;result(1);
  if(resets||!k_fault)$fatal(1,"rejected attempt reset state");
  k_recover_version=3;k_recover_query=3;k_recover_price=3;k_recover_cookie=102;l_start_source_crc=payload_crc();
  external_safe=0;@(negedge clk);k_recover_valid=1;
  repeat(5)begin tick;if(k_recover_ready||k_attempt_reset)$fatal(1,"unsafe retry admitted");checks=checks+1;end
  @(negedge clk);external_safe=1;external_normal_retired=0;
  repeat(4)begin tick;if(k_recover_ready||k_attempt_reset)$fatal(1,"unretired retry admitted");checks=checks+1;end
  @(negedge clk);external_normal_retired=1;
  do @(posedge clk);while(!k_recover_ready);@(negedge clk);k_recover_valid=0;
  if(mode!=0)begin
   if(mode==1)external_safe=0;else begin k_a_rsp_valid=1;external_normal_retired=0;end
   #1;if(k_attempt_reset)$fatal(1,"rearm ignored withdrawn safety or late response");
   repeat(4)tick;
   if(resets||!k_fault)$fatal(1,"unsafe rearm cleared service");
   @(negedge clk);external_safe=1;k_a_rsp_valid=0;external_normal_retired=1;
   result(6);
   k_recover_cookie=103;k_recover_query=0;request;result(1);
   if(resets)$fatal(1,"failed retry floor lost");
   k_recover_version=4;k_recover_query=0;k_recover_price=4;k_recover_cookie=104;request;
  end
  success_labels;
 end
 if(successes!=3||failures!=10)$fatal(1,"scenario accounting %0d %0d",successes,failures);
 $display("REARM_LOOP_PASS scenarios=3 successes=%0d failures=%0d checks=%0d",successes,failures,checks);$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
