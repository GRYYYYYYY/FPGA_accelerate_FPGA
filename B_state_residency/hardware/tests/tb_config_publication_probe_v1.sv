`timescale 1ns/1ps
// Observe the unmodified CP config_restore_controller. This is not a candidate.
module tb_config_publication_probe_v1;
 reg clk=0; always #5 clk=~clk;
 reg rst=1,abort=0,backend_drained=1,normal_retired=1,attempt_reset=0;
 reg load_stage=0,publish_valid=0,publish_permit=0,discard_valid=0;
 wire publish_ready,discard_ready,staged_valid;
 wire[63:0]staged_design; wire[31:0]staged_checkpoint,staged_version,active_version;
 wire[2303:0]staged_payload,active_payload;
 reg load_valid=0,load_authoritative=1,load_rsp_ready=0;
 wire load_ready,load_rsp_valid,load_status;
 reg[2303:0]load_payload=0;
 reg[63:0]load_design=123,start_design=123;
 reg[31:0]load_checkpoint=17,start_checkpoint=17,start_cookie=0,start_version=4;
 reg[3:0]start_price=4;
 reg start_valid=0,rsp_ready=0;
 wire start_ready,rsp_valid,busy,fault;
 wire[5:0]cfg_valid,cfg_rsp_ready,sent,retired;
 reg[5:0]cfg_ready=0,cfg_rsp_valid=0;
 reg[17:0]cfg_status=0;
 wire[2303:0]cfg_payload;
 wire[3:0]rsp_status; wire[31:0]rsp_cookie,saved_checkpoint;
 wire[63:0]saved_design;
 config_restore_controller #(.MAX_CYCLES(256)) dut(.*);
 integer cycles=0,checks=0,loads=0,captures=0,publications=0,clears=0,rejections=0;
 integer mode,events;
 reg[2303:0]gold,expected;
 reg offered_bit;
 string path;

 task tick; begin @(posedge clk); #1; end endtask
 task check(input bit condition,input string message); begin
  if(!condition)$fatal(1,"CONFIG_PUBLICATION_PROBE mode=%0d cycle=%0d: %s",mode,cycles,message);
  checks=checks+1;
 end endtask
 task payload; begin
  load_payload=0;
  load_payload[0+:384]={128'd0,32'd1,32'd8,32'd16,32'd24,64'd123,64'h1000};
  load_payload[384+:384]={128'd0,32'd32,32'd16,64'h4000,64'h3000,64'h2000};
  load_payload[768+:384]={288'd0,32'd16,64'h5000};
  load_payload[1152+:384]={192'd0,32'd0,32'd311,64'h7000,64'h6000};
  load_payload[1536+:384]={128'd0,32'd0,32'd16,64'h9000,64'h9000,64'h8000};
  load_payload[1920+:384]={32'd0,32'd3,32'd8,32'd16,64'd123,64'hc000,64'hb000,64'ha000};
 end endtask
 task initialize; begin
  @(negedge clk);
  rst=1;abort=0;attempt_reset=0;load_stage=0;publish_valid=0;publish_permit=0;discard_valid=0;
  load_valid=0;load_rsp_ready=0;backend_drained=1;normal_retired=1;load_checkpoint=17;
  payload;
  repeat(2)tick();
  @(negedge clk);rst=0;
  tick();check(dut.descriptor===2304'd0&&!staged_valid,"reset clears descriptor and preparation");
 end endtask
 task install(input bit want_reject); begin
  @(negedge clk);load_valid=1;
  check(load_ready===1'b1,"load is ready before acceptance");
  tick();loads=loads+1;
  check(load_rsp_valid===1'b1&&load_status===want_reject,"load response status");
  @(negedge clk);load_valid=0;
  repeat(2)begin
   tick();check(load_rsp_valid===1'b1&&staged_valid===1'b0&&publish_ready===1'b0,
                "held load reply prevents publication");
  end
  @(negedge clk);load_rsp_ready=1;
  tick();
  @(negedge clk);load_rsp_ready=0;
  tick();check(load_rsp_valid===1'b0,"load reply retired");
 end endtask

 always @(posedge clk)begin
  cycles<=cycles+1;
  if(cycles>500)$fatal(1,"CONFIG_PUBLICATION_PROBE watchdog");
  if(!rst)begin
   if(cfg_valid!==6'd0||busy!==1'b0||fault!==1'b0)
    $fatal(1,"metadata probe unexpectedly started recovery or faulted");
   if(publish_valid&&publish_ready)begin
    publications=publications+1;
    $fdisplay(events,"PUBLISH mode=%0d cycle=%0d old=%b staged=%b",mode,cycles,dut.descriptor[0],dut.shadow_payload[0]);
   end
  end
 end

 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path required");
  events=$fopen(path,"w");if(!events)$fatal(1,"cannot open events");
  for(mode=0;mode<7;mode=mode+1)begin
   initialize;
   gold=load_payload;install(0);
   check(dut.descriptor===gold&&active_payload===gold&&saved_checkpoint===32'd17,
         "initial authoritative descriptor installed");
   @(negedge clk);load_stage=1;publish_permit=1;load_checkpoint=18;load_payload=active_payload;
   case(mode)
    0:offered_bit=1'b0;
    1:offered_bit=1'b1;
    2,4,6:offered_bit=1'bx;
    3,5:offered_bit=1'bz;
   endcase
   load_payload[0]=offered_bit;
   install(mode==1);
   check(dut.descriptor===gold&&active_payload===gold&&saved_checkpoint===32'd17,
         "stage/rejection has not changed active descriptor");
   if(mode==1)begin
    rejections=rejections+1;
    check(staged_valid===1'b0&&publish_ready===1'b0,"known mismatch rejected");
    $fdisplay(events,"REJECT mode=%0d bit=%b checkpoint=%0d",mode,offered_bit,saved_checkpoint);
   end else begin
    captures=captures+1;
    expected=gold;expected[0]=offered_bit;
    check(staged_valid===1'b1&&dut.shadow_payload===expected&&staged_payload===expected,
          "original controller captures exact staged bits including X/Z");
    $fdisplay(events,"STAGE mode=%0d bit=%b active=%b",mode,dut.shadow_payload[0],active_payload[0]);
    @(negedge clk);publish_valid=1;backend_drained=0;
    repeat(2)begin tick();check(publish_ready===1'b0&&dut.descriptor===gold,"backend drain blocks publication");end
    @(negedge clk);backend_drained=1;normal_retired=0;
    repeat(2)begin tick();check(publish_ready===1'b0&&dut.descriptor===gold,"normal retirement blocks publication");end
    @(negedge clk);normal_retired=1;
    if(mode==4)abort=1;
    if(mode==5)begin publish_valid=0;discard_valid=1;end
    if(mode==6)attempt_reset=1;
    tick();
    if(mode<=3)begin
     check(dut.descriptor===expected&&active_payload===expected&&saved_checkpoint===32'd18,
           "publication changes exact descriptor bits on its acceptance edge");
     check(cfg_payload[0]===offered_bit,"cfg payload exposes same exact bit");
     $fdisplay(events,"RESULT mode=%0d bit=%b checkpoint=%0d",mode,active_payload[0],saved_checkpoint);
    end else begin
     clears=clears+1;
     check(dut.descriptor===gold&&active_payload===gold&&saved_checkpoint===32'd17,
           "abort/discard/attempt reset preserves active descriptor");
     $fdisplay(events,"CLEAR mode=%0d bit=%b checkpoint=%0d",mode,active_payload[0],saved_checkpoint);
    end
    check(dut.prepared===1'b0&&staged_valid===1'b0,"publication or cancellation clears preparation");
    @(negedge clk);publish_valid=0;discard_valid=0;attempt_reset=0;abort=0;
   end
  end
  check(loads==14&&captures==6&&publications==3&&clears==3&&rejections==1,"nonempty exact coverage");
  $fdisplay(events,"COVERAGE loads=%0d captures=%0d publications=%0d clears=%0d rejections=%0d checks=%0d",loads,captures,publications,clears,rejections,checks);
  $fflush(events);$fclose(events);
  $display("CONFIG_PUBLICATION_PROBE_PASS loads=%0d captures=%0d publications=%0d clears=%0d rejections=%0d checks=%0d",loads,captures,publications,clears,rejections,checks);
  $finish;
 end
endmodule
