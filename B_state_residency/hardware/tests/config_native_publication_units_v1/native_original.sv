`timescale 1ns/1ps
// Original controller and the exact native payload/authority feedback muxes.
// No candidate, force, or hierarchical write is used by this testbench.
module tb_config_native_feedback_v1;
 integer pubcmp_file;
 string pubcmp_path;
 localparam integer PUBCMP_NATIVE=1;

 reg clk=0; always #5 clk=~clk;
 reg rst=1,abort=0,backend_drained=1,normal_retired=1,attempt_reset=0;
 reg load_stage=0,publish_valid=0,discard_valid=0;
 wire publish_ready,discard_ready,staged_valid;
 wire[63:0]staged_design; wire[31:0]staged_checkpoint,staged_version,active_version;
 wire[2303:0]staged_payload,active_payload;
 reg load_valid=0,host_authoritative=1,load_rsp_ready=0;
 wire load_ready,load_rsp_valid,load_status;
 reg[2303:0]host_payload=0;
 wire[2303:0]feedback_payload=load_stage?active_payload:host_payload;
 wire feedback_authoritative=load_stage?1'b1:host_authoritative;
 reg[63:0]load_design=123,start_design=123;
 reg[31:0]load_checkpoint=17,start_checkpoint=17,start_cookie=91,start_version=4;
 reg[3:0]start_price=4;
 reg start_valid=0,rsp_ready=0;
 wire start_ready,rsp_valid,busy,fault;
 wire[5:0]cfg_valid,cfg_rsp_ready,sent,retired;
 reg[5:0]cfg_ready=6'b111111,cfg_rsp_valid=0;
 reg[17:0]cfg_status=0;
 wire[2303:0]cfg_payload;
 wire[3:0]rsp_status; wire[31:0]rsp_cookie,saved_checkpoint;
 wire[63:0]saved_design;
 config_restore_controller #(.MAX_CYCLES(256)) dut(
  .load_payload(feedback_payload),.load_authoritative(feedback_authoritative),
  .publish_permit(load_stage),.*);
 integer cycles=0,checks=0,loads=0,recoveries=0,captures=0,publications=0,clears=0;
 integer blocked_overwrites=0,configuration_requests=0,alias_checks=0,prepared_checks=0;
 integer data_case,action,events;
 reg[5:0]seen=0;
 reg[2303:0]gold,expected_active,expected_raw;
 reg data_bit;
 string path;

 task tick;begin @(posedge clk);#1;end endtask
 task check(input bit condition,input string message);begin
  if(!condition)$fatal(1,"NATIVE_FEEDBACK data=%0d action=%0d cycle=%0d: %s",data_case,action,cycles,message);
  checks=checks+1;
 end endtask
 task make_payload;begin
  host_payload=0;
  host_payload[0+:384]={128'd0,32'd1,32'd8,32'd16,32'd24,64'd123,64'h1000};
  host_payload[384+:384]={128'd0,32'd32,32'd16,64'h4000,64'h3000,64'h2000};
  host_payload[768+:384]={288'd0,32'd16,64'h5000};
  host_payload[1152+:384]={192'd0,32'd0,32'd311,64'h7000,64'h6000};
  host_payload[1536+:384]={128'd0,32'd0,32'd16,64'h9000,64'h9000,64'h8000};
  host_payload[1920+:384]={32'd0,32'd3,32'd8,32'd16,64'd123,64'hc000,64'hb000,64'ha000};
  host_payload[0]=data_bit;
 end endtask
 task initialize;begin
  @(negedge clk);rst=1;abort=0;attempt_reset=0;load_stage=0;publish_valid=0;discard_valid=0;
  load_valid=0;load_rsp_ready=0;host_authoritative=1;backend_drained=1;normal_retired=1;
  load_checkpoint=17;start_valid=0;rsp_ready=0;start_checkpoint=17;start_version=4;start_price=4;
  make_payload;gold=host_payload;
  repeat(2)tick();@(negedge clk);rst=0;tick();
  check(dut.descriptor===2304'd0&&dut.prepared===1'b0,"cold reset establishes known control");
 end endtask
 task install(input bit status);begin
  @(negedge clk);load_valid=1;
  check(load_ready===1'b1,"load acceptance ready");
  tick();loads=loads+1;
  check(load_rsp_valid===1'b1&&load_status===status,"exact load status");
  @(negedge clk);load_valid=0;
  repeat(2)begin tick();check(load_rsp_valid===1'b1&&publish_ready===1'b0,"held response blocks publish");end
  @(negedge clk);load_rsp_ready=1;tick();@(negedge clk);load_rsp_ready=0;tick();
  check(load_rsp_valid===1'b0,"load response consumed");
 end endtask
 task advance_version;begin
  @(negedge clk);start_valid=1;
  check(start_ready===1'b1,"recovery ready before stage");
  tick();@(negedge clk);start_valid=0;
  while(rsp_valid!==1'b1)tick();
  check(rsp_status===4'd0&&rsp_cookie===32'd91&&sent===6'd63&&retired===6'd63&&seen===6'd63,
        "six real request/response lanes retire before successful version change");
  check(dut.descriptor===gold&&active_version===32'd4,"version advanced without rewriting raw descriptor");
  expected_active=gold;expected_active[2240+:32]=4;
  check(active_payload===expected_active,"active payload patches only version slice");
  @(negedge clk);rsp_ready=1;tick();@(negedge clk);rsp_ready=0;tick();
  check(busy===1'b0&&fault===1'b0,"recovery completion retired");
  recoveries=recoveries+1;
 end endtask

 always @(posedge clk)begin
  cycles<=cycles+1;
  if(cycles>3000)$fatal(1,"NATIVE_FEEDBACK watchdog");
  if(rst)begin cfg_rsp_valid<=0;seen<=0;end
  else begin
   cfg_rsp_valid<=(cfg_rsp_valid&~cfg_rsp_ready)|(cfg_valid&cfg_ready);
   seen<=seen|(cfg_valid&cfg_ready);
   for(integer lane=0;lane<6;lane=lane+1)if(cfg_valid[lane]&&cfg_ready[lane])begin
    if(seen[lane])$fatal(1,"duplicate lane request");
    if(lane!=0&&!retired[0])$fatal(1,"dependent lane sent before connection retired");
    if(cfg_payload!=={gold[2303:2272],32'd4,gold[2239:0]})$fatal(1,"configuration descriptor changed");
    configuration_requests=configuration_requests+1;
   end
   if(dut.load_stage===1'b1&&dut.load_valid===1'b1&&dut.load_ready===1'b1)begin
    if(dut.load_payload!==dut.active_payload||dut.load_authoritative!==1'b1)
     $fatal(1,"native feedback alias violated at accepted load");
    alias_checks=alias_checks+1;
   end
   if(dut.prepared===1'b1)begin
    if(dut.state!==3'd0||dut.configured!==1'b1||
       {dut.shadow_payload[2303:2272],dut.shadow_payload[2239:0]}!=={dut.descriptor[2303:2272],dut.descriptor[2239:0]}||
       dut.shadow_payload[2240+:32]!==dut.current_version)
     $fatal(1,"prepared native full-bank invariant violated");
    prepared_checks=prepared_checks+1;
   end
   if(publish_valid&&publish_ready)publications=publications+1;
  end
 end

 initial begin
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path required");
  events=$fopen(path,"w");if(!events)$fatal(1,"cannot open events");
  for(data_case=0;data_case<4;data_case=data_case+1)begin
   case(data_case)0:data_bit=1'b0;1:data_bit=1'b1;2:data_bit=1'bx;3:data_bit=1'bz;endcase
   for(action=0;action<5;action=action+1)begin
    initialize;install(0);
    check(dut.descriptor===gold&&active_payload===gold,"initial 0/1/X/Z descriptor exact");
    advance_version;
    @(negedge clk);load_stage=1;load_checkpoint=18;host_payload='1;host_authoritative=0;
    install(0);captures=captures+1;
    check(dut.descriptor===gold&&staged_payload===expected_active&&staged_valid===1'b1,
          "stage selected feedback despite invalid hostile host descriptor");
    @(negedge clk);load_checkpoint=19;
    install(1);blocked_overwrites=blocked_overwrites+1;
    check(dut.descriptor===gold&&staged_payload===expected_active&&staged_checkpoint===32'd18,
          "prepared state rejects second load without changing bank");
    @(negedge clk);load_checkpoint=18;start_valid=1;start_version=5;start_price=5;
    repeat(2)begin tick();check(start_ready===1'b0&&dut.descriptor===gold&&dut.prepared===1'b1,
                              "prepared state blocks another recovery");end
    @(negedge clk);start_valid=0;publish_valid=1;load_stage=1'bx;
    tick();check(publish_ready!==1'b1&&dut.descriptor===gold&&dut.prepared===1'b1,
                 "unknown permit does not accept publication");
    @(negedge clk);load_stage=1'bz;
    tick();check(publish_ready!==1'b1&&dut.descriptor===gold&&dut.prepared===1'b1,
                 "high-impedance permit does not accept publication");
    @(negedge clk);load_stage=1;backend_drained=0;
    repeat(2)begin tick();check(publish_ready===1'b0&&dut.descriptor===gold,"backend drain holds publication");end
    @(negedge clk);backend_drained=1;normal_retired=0;
    repeat(2)begin tick();check(publish_ready===1'b0&&dut.descriptor===gold,"normal retirement holds publication");end
    @(negedge clk);normal_retired=1;
    if(action==1)abort=1;
    if(action==2)begin publish_valid=0;discard_valid=1;end
    if(action==3)attempt_reset=1;
    if(action==4)begin
     discard_valid=1;
     repeat(2)begin tick();check(publish_ready===1'b0&&discard_ready===1'b0&&dut.descriptor===gold&&dut.prepared===1'b1,
                               "simultaneous publish/discard accepts neither");end
     @(negedge clk);publish_valid=0;
    end
    tick();
    expected_raw=action==0?expected_active:gold;
    check(dut.descriptor===expected_raw&&active_payload===expected_active&&active_version===32'd4,
          "raw and active full banks match expected exact publication/cancel edge");
    check(saved_checkpoint===(action==0?32'd18:32'd17)&&dut.prepared===1'b0,
          "checkpoint and preparation follow publication or cancellation");
    if(action!=0)clears=clears+1;
    $fdisplay(events,"NATIVE data=%b action=%0d raw_version=%0d active_version=%0d checkpoint=%0d",data_bit,action,dut.descriptor[2240+:32],active_version,saved_checkpoint);
    @(negedge clk);publish_valid=0;discard_valid=0;attempt_reset=0;abort=0;
   end
  end
  check(loads==60&&recoveries==20&&captures==20&&publications==4&&clears==16&&blocked_overwrites==20&&configuration_requests==120&&alias_checks==40&&prepared_checks>0,
        "all data/actions and native feedback checks nonempty");
  $fdisplay(events,"COVERAGE loads=%0d recoveries=%0d captures=%0d publications=%0d clears=%0d blocked_overwrites=%0d configuration_requests=%0d alias_checks=%0d prepared_checks=%0d checks=%0d",loads,recoveries,captures,publications,clears,blocked_overwrites,configuration_requests,alias_checks,prepared_checks,checks);
  $fflush(events);$fclose(events);
  $display("CONFIG_NATIVE_FEEDBACK_PASS cases=20 loads=%0d recoveries=%0d captures=%0d publications=%0d clears=%0d blocked_overwrites=%0d configuration_requests=%0d alias_checks=%0d prepared_checks=%0d checks=%0d",loads,recoveries,captures,publications,clears,blocked_overwrites,configuration_requests,alias_checks,prepared_checks,checks);
  $finish;
 end
 // Record each rising edge after NBA and before the original tick task's #1 checks.
 initial begin
  if(!$value$plusargs("publication_bank_trace=%s",pubcmp_path))$fatal(1,"publication bank trace path");
  pubcmp_file=$fopen(pubcmp_path,"w");if(!pubcmp_file)$fatal(1,"publication bank trace open");
 end
 always @(posedge clk)begin
  if(PUBCMP_NATIVE&&!rst&&dut.load_valid===1'b1&&dut.load_ready===1'b1&&dut.load_stage===1'b1)begin
   if(dut.load_payload!==dut.active_payload)$fatal(1,"publication native accepted-stage payload alias");
  end
  if(PUBCMP_NATIVE&&!rst&&dut.prepared===1'b1)begin
   if({dut.shadow_payload[2303:2272],dut.shadow_payload[2239:0]}!==
      {dut.descriptor[2303:2272],dut.descriptor[2239:0]})
    $fatal(1,"publication native prepared bank mismatch before NBA");
  end
  #0.1;
  if(PUBCMP_NATIVE&&!rst&&dut.prepared===1'b1)begin
   if({dut.shadow_payload[2303:2272],dut.shadow_payload[2239:0]}!==
      {dut.descriptor[2303:2272],dut.descriptor[2239:0]})
    $fatal(1,"publication native prepared bank mismatch after NBA");
  end
  $fdisplay(pubcmp_file,"BANK %0d %0t %h %h",cycles,$time,
   {dut.state,dut.configured,dut.stopped,dut.error_code,dut.elapsed,dut.current_version,dut.tx_version,
    dut.descriptor,dut.prepared,dut.shadow_payload,dut.shadow_design,dut.shadow_checkpoint},
   {publish_ready,discard_ready,staged_valid,staged_design,staged_checkpoint,staged_version,
    active_version,staged_payload,active_payload,load_ready,load_rsp_valid,load_status,start_ready,
    cfg_valid,cfg_payload,cfg_rsp_ready,rsp_valid,rsp_status,rsp_cookie,busy,fault,sent,retired,saved_design,saved_checkpoint});
  $fflush(pubcmp_file);
 end

endmodule
