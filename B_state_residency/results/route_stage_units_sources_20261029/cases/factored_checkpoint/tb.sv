`timescale 1ns/1ps
module tb_route_commit;

 integer stage_fd,stage_cycle=0,stage_checked=0,stage_captures=0,stage_imports=0;
 reg stage_seen=0;string stage_path;
 reg[31:0]stage_previous[0:29],stage_expected[0:29];


 integer bank_fd,bank_cycle=0;reg bank_seen=0;string bank_path;
 reg[31:0]bank_previous[0:1][0:7];

 wire idle_fault;

 localparam CP_CAPACITY=8;
 reg cp_valid=0,cp_restore=0,cp_safe=1,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0;
 wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;
 reg[63:0]cp_design=64'h123456789abcdef0;reg[31:0]cp_nodes=9089009,cp_nets=27960,cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
 wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;
 reg[31:0]saved[0:29],pristine[0:29];reg[31:0]saved_crc;integer cp_checks=0;
 reg preserve_owner=0;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,lease=1;reg[1:0]active_query=1;reg[3:0]active_price=3;reg[31:0]active_version=3;reg[63:0]active_design=64'h123456789abcdef0;
 reg req_valid=0,req_op=0,req_slot=0,rsp_ready=0;wire req_ready,rsp_valid,busy,fault;reg[31:0]req_cookie=0,req_source=65185,req_sink=150697,req_net=2717,req_sequence=1;
 wire[3:0]rsp_status;wire[31:0]rsp_cookie,rsp_nodes,rsp_acked;wire[1:0]slot_valid;
 wire l_valid,l_rsp_ready,o_valid,o_rsp_ready;reg l_ready=0,l_rsp_valid=0,l_present=1,o_ready=0,o_rsp_valid=0;wire[31:0]l_node,o_node,o_net,o_cookie;wire[2:0]o_op;reg[3:0]l_status=0,o_status=0;reg[159:0]l_payload=0;reg[31:0]o_rsp_cookie=0;
 route_commit_controller #(.FACTORED_STAGE_WRITES(1),.FACTORED_PATH_WRITES(1),.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);
 reg[31:0]nodes[0:1][0:7];reg[159:0]payloads[0:1][0:7];reg[31:0]owner_nodes[0:9];integer refs[0:9];
 integer phase=0,mode=0,ticks=0,lwait=0,owait=0,lr=0,ow=0,checks=0,fd,rc,p,i,j,k,at,owneridx,events;reg[31:0]id;reg[159:0]pl;string path;
 reg held_l=0,held_o=0;reg[31:0]saved_l,saved_on,saved_net,saved_cookie;reg[2:0]saved_op;
 initial begin
  if(!$value$plusargs("labels=%s",path))$fatal(1,"labels path");fd=$fopen(path,"r");if(!fd)$fatal(1,"labels open");
  for(p=0;p<2;p=p+1)for(i=0;i<8;i=i+1)begin rc=$fscanf(fd,"%d %d %h",j,id,pl);if(rc!=3||j!=p)$fatal(1,"labels format");nodes[p][i]=id;payloads[p][i]=pl;end
  for(i=0;i<6;i=i+1)owner_nodes[i]=nodes[0][i+1];at=6;
  for(i=1;i<7;i=i+1)begin k=0;for(j=0;j<6;j=j+1)if(owner_nodes[j]==nodes[1][i])k=1;if(!k)begin owner_nodes[at]=nodes[1][i];at=at+1;end end
  if(at!=10)$fatal(1,"union nodes");
  if(!$value$plusargs("events=%s",path))$fatal(1,"events path");events=$fopen(path,"w");
 end
 always @(posedge clk)begin
  ticks=ticks+1;if(ticks>20000)$fatal(1,"watchdog mode=%0d state=%0d",mode,dut.state);
  if(rst)begin l_rsp_valid<=0;o_rsp_valid<=0;lwait<=0;owait<=0;l_ready<=0;o_ready<=0;held_l<=0;held_o<=0;lr<=0;ow<=0;if(!preserve_owner)for(integer x=0;x<10;x=x+1)refs[x]<=0;end
  else begin
   l_ready<=ticks%4==0&&mode!=6;o_ready<=ticks%5==0&&mode!=7;
   if(held_l&&(!l_valid||l_node!==saved_l))$fatal(1,"label request changed");
   if(held_o&&(!o_valid||{o_node,o_net,o_cookie,o_op}!=={saved_on,saved_net,saved_cookie,saved_op}))$fatal(1,"owner request changed");
   held_l<=l_valid&&!l_ready;saved_l<=l_node;held_o<=o_valid&&!o_ready;saved_on<=o_node;saved_net<=o_net;saved_cookie<=o_cookie;saved_op<=o_op;
   if(l_valid&&l_ready)begin
    if(lwait||l_rsp_valid)$fatal(1,"overlapping label");lr<=lr+1;lwait<=mode==8?300:3;at=-1;
    if(phase==3)begin l_payload<={32'd1,32'd11,32'hffffffff,64'b0};end
    else if(phase==2)begin
     if(l_node<100||l_node>110)$fatal(1,"overflow node");l_payload<={32'(l_node==100),32'd11,32'(l_node==110?32'hffffffff:l_node+1),64'b0};
    end else begin
     for(integer x=0;x<8;x=x+1)if(nodes[phase][x]==l_node)at=x;
     if(at<0)$fatal(1,"unexpected label node %0d",l_node);l_payload<=payloads[phase][at];
     if(mode==1&&at==1)l_payload[95:64]<=l_node;
     if(mode==2&&at==7)l_payload[95:64]<=123;
    end
    l_present<=mode!=3;l_status<=mode==4?1:0;
    $fdisplay(events,"L %0d %0d %0d",mode,phase,l_node);
   end
   if(lwait>0)begin lwait<=lwait-1;if(lwait==1)l_rsp_valid<=1;end
   if(l_rsp_valid&&l_rsp_ready)l_rsp_valid<=0;
   if(o_valid&&o_ready)begin
    if(owait||o_rsp_valid)$fatal(1,"overlapping owner");ow<=ow+1;owait<=3;o_status<=0;o_rsp_cookie<=mode==5&&ow==1?o_cookie+1:o_cookie;
    owneridx=-1;for(integer x=0;x<10;x=x+1)if(owner_nodes[x]==o_node)owneridx=x;
    if(owneridx<0||o_net!=2717||(o_op!=1&&o_op!=2))$fatal(1,"bad owner request");
    if(o_op==2&&refs[owneridx]==0)$fatal(1,"owner underflow");
    refs[owneridx]<=refs[owneridx]+(o_op==1?1:-1);
    $fdisplay(events,"O %0d %0d %0d %0d",mode,o_op,o_node,refs[owneridx]+(o_op==1?1:-1));
   end
   if(owait>0)begin owait<=owait-1;if(owait==1)o_rsp_valid<=1;end
   if(o_rsp_valid&&o_rsp_ready)o_rsp_valid<=0;
  end
 end

 function automatic[31:0]image_crc;reg[31:0]v;begin
  v=32'hffffffff;for(integer x=0;x<30;x=x+1)begin v=v^saved[x];for(integer z=0;z<32;z=z+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;end
  image_crc=~v;
 end endfunction
 task cp_cmd(input integer restore);begin
  @(negedge clk);cp_restore=restore;cp_valid=1;
  do @(posedge clk);while(!cp_ready);@(negedge clk);cp_valid=0;
 end endtask
 task cp_result(input integer want);reg[35:0]hold;begin
  wait(cp_rsp_valid);@(negedge clk);if(cp_status!=want)$fatal(1,"CP status %0d/%0d",cp_status,want);
  hold={cp_status,cp_crc};repeat(5)begin @(negedge clk);if(!cp_rsp_valid||req_ready||!cp_busy||{cp_status,cp_crc}!==hold)$fatal(1,"CP held completion");end
  $fdisplay(events,"CPR %0d %0d %08h %0d",cp_checks,cp_status,cp_crc,slot_valid);cp_checks=cp_checks+1;
  cp_rsp_ready=1;@(negedge clk);cp_rsp_ready=0;repeat(2)@(negedge clk);
 end endtask
 task save_image;reg[64:0]hold;begin
  cp_cmd(0);
  for(integer x=0;x<30;x=x+1)begin
   wait(cp_m_valid);@(negedge clk);hold={cp_m_last,cp_m_index,cp_m_data};
   repeat(3)begin @(negedge clk);if(!cp_m_valid||{cp_m_last,cp_m_index,cp_m_data}!==hold||req_ready)$fatal(1,"CP output backpressure");end
   if(cp_m_index!=x||cp_m_last!=(x==29))$fatal(1,"CP output order");saved[x]=cp_m_data;
   $fdisplay(events,"CPW %0d %0d %08h",cp_checks,x,cp_m_data);
   cp_m_ready=1;@(negedge clk);cp_m_ready=0;
  end
  cp_result(0);saved_crc=cp_crc;if(saved_crc!=image_crc())$fatal(1,"CP CRC");
 end endtask
 task load_image(input integer corruption,input integer status);begin
  cp_expected_crc=image_crc()^(corruption==1);cp_cmd(1);
  for(integer x=0;x<30;x=x+1)begin
   @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=saved[x];cp_s_last=x==29;
   if(corruption==2&&x==3)cp_s_index=4;
   if(corruption==3&&x==3)cp_s_last=1;
   do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;
   if(corruption>=2&&x==3)break;
  end
  cp_result(status);
 end endtask

 task reset_all;begin
  @(negedge clk);rst=1;abort=0;active=1;lease=1;active_query=1;active_price=3;active_version=3;active_design=64'h123456789abcdef0;req_valid=0;rsp_ready=0;phase=0;req_source=65185;req_sink=150697;req_net=2717;req_sequence=1;
  repeat(3)@(negedge clk);rst=0;repeat(2)@(negedge clk);
 end endtask
 task send(input integer op,slot);begin
  @(negedge clk);req_cookie=req_cookie+1;req_op=op;req_slot=slot;req_valid=1;
  do @(posedge clk);while(!req_ready);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,acked);reg[99:0]hold;begin
  wait(rsp_valid);@(negedge clk);
  if(rsp_status!=status||rsp_acked!=acked||rsp_cookie!=req_cookie)$fatal(1,"response mode=%0d status=%0d/%0d ack=%0d/%0d",mode,rsp_status,status,rsp_acked,acked);
  if(l_valid||o_valid||lwait||owait||l_rsp_valid||o_rsp_valid)$fatal(1,"response before drain");
  hold={rsp_status,rsp_cookie,rsp_nodes,rsp_acked};
  repeat(5)begin @(negedge clk);if(!rsp_valid||req_ready||{rsp_status,rsp_cookie,rsp_nodes,rsp_acked}!==hold)$fatal(1,"response instability");end
  $fdisplay(events,"R %0d %0d %0d %0d",mode,rsp_status,rsp_nodes,rsp_acked);checks=checks+1;
  rsp_ready=1;@(negedge clk);rsp_ready=0;repeat(2)@(negedge clk);
 end endtask
 initial begin
  mode=0;reset_all;send(0,0);retire(0,6);if(slot_valid!=1)$fatal(1,"slot0 publish");
  send(0,0);retire(1,0);if(fault)$fatal(1,"occupied-slot rejection poisoned");
  phase=1;req_sink=128009;req_sequence=2;send(0,1);retire(0,6);if(slot_valid!=3)$fatal(1,"slot1 publish");
  for(i=0;i<10;i=i+1)if(refs[i]!=(owner_nodes[i]==554512||owner_nodes[i]==263946?2:1))$fatal(1,"shared refs");
  req_sink=150697;req_source=65185;req_net=999;send(1,0);retire(1,0);req_net=2717;
  active_design=active_design+1;send(1,0);retire(1,0);active_design=active_design-1;
  // No label reads are permitted by the saved-path ripup protocol.
  j=lr;send(1,0);retire(0,6);if(lr!=j||slot_valid!=2)$fatal(1,"ripup reread path");
  req_sink=128009;send(1,1);retire(0,6);if(lr!=j||slot_valid!=0)$fatal(1,"ripup slot1");
  for(i=0;i<10;i=i+1)if(refs[i])$fatal(1,"final refs");
  for(mode=1;mode<=4;mode=mode+1)begin reset_all;send(0,0);retire(mode<3?2:4,0);if(!fault||ow)$fatal(1,"invalid chain mutated owner");end
  mode=9;reset_all;phase=2;req_sink=100;req_source=110;req_sequence=11;send(0,0);retire(3,0);if(!fault||ow)$fatal(1,"path limit");
  mode=5;reset_all;send(0,0);retire(5,1);if(!fault||slot_valid)$fatal(1,"bad owner reply publication");
  mode=6;reset_all;send(0,0);wait(l_valid);repeat(3)@(negedge clk);abort=1;repeat(5)@(negedge clk);if(!l_valid||rsp_valid)$fatal(1,"abort retracted label");mode=10;retire(6,0);
  mode=7;reset_all;send(0,0);wait(o_valid);repeat(3)@(negedge clk);abort=1;repeat(5)@(negedge clk);if(!o_valid||rsp_valid)$fatal(1,"abort retracted owner");mode=10;retire(6,1);
  mode=8;reset_all;send(0,0);retire(6,0);if(!fault)$fatal(1,"timeout");
  mode=10;reset_all;send(0,0);wait(dut.state==2);@(negedge clk);active_version=4;retire(6,0);
  reset_all;send(0,0);wait(dut.state==4);@(negedge clk);active_design=0;retire(6,1);
  for(mode=11;mode<=14;mode=mode+1)begin
   reset_all;send(0,0);wait(dut.state==2);@(negedge clk);
   case(mode)11:active_query=2;12:active_price=4;13:lease=0;14:active=0;endcase
   retire(6,0);if(!fault)$fatal(1,"context drift");
  end
  mode=15;reset_all;phase=3;req_source=200;req_sink=200;req_sequence=11;send(0,0);retire(0,0);if(slot_valid!=1||ow)$fatal(1,"empty path publish");
  send(1,0);retire(0,0);if(slot_valid||ow)$fatal(1,"empty path ripup");
  mode=16;reset_all;send(0,0);wait(rsp_valid);@(negedge clk);active_price=4;retire(0,6);if(!fault||req_ready)$fatal(1,"late held context fault");

  // Save two real same-net routes, erase controller state only, restore, rip up.
  mode=0;reset_all;send(0,0);retire(0,6);phase=1;req_sink=128009;req_sequence=2;send(0,1);retire(0,6);
  save_image;for(i=0;i<30;i=i+1)pristine[i]=saved[i];
  preserve_owner=1;reset_all;if(slot_valid!=0)$fatal(1,"CP reset did not erase paths");
  load_image(1,1);if(slot_valid)$fatal(1,"bad CRC published slots");
  load_image(2,1);if(slot_valid)$fatal(1,"bad order published slots");
  load_image(3,1);if(slot_valid)$fatal(1,"early last published slots");
  for(integer bad=0;bad<8;bad=bad+1)begin
   for(i=0;i<30;i=i+1)saved[i]=pristine[i];
   case(bad)
    0:saved[0]=2;
    1:saved[1]=9;
    2:saved[2]=27960;
    3:saved[3]=9089009;
    4:saved[5]=0;
    5:saved[8]=saved[7];
    6:saved[7]=saved[4];
    7:saved[14]=1;
   endcase
   load_image(0,1);if(slot_valid)$fatal(1,"semantically invalid image published");
  end
  for(i=0;i<30;i=i+1)saved[i]=pristine[i];load_image(0,0);if(slot_valid!=3)$fatal(1,"CP slots not restored");
  // Invalid replacement must leave both live routes intact, not clear them.
  saved[1]=9;load_image(0,1);if(slot_valid!=3)$fatal(1,"failed restore destroyed old slots");
  for(i=0;i<30;i=i+1)saved[i]=pristine[i];
  j=lr;req_sink=150697;req_sequence=1;send(1,0);retire(0,6);
  for(i=0;i<10;i=i+1)if((owner_nodes[i]==554512||owner_nodes[i]==263946)&&refs[i]!=1)$fatal(1,"CP shared refs lost");
  req_sink=128009;send(1,1);retire(0,6);
  for(i=0;i<10;i=i+1)if(refs[i])$fatal(1,"CP final refs");if(lr!=j||slot_valid)$fatal(1,"CP ripup used stale labels");
  preserve_owner=0;reset_all;
  // Admission waits for external physical/logical retirement.
  cp_safe=0;cp_valid=1;repeat(6)begin @(negedge clk);if(cp_ready||req_ready||cp_busy)$fatal(1,"CP unsafe acceptance");end
  cp_valid=0;cp_safe=1;
  // A command offered while an active label request is stalled must not freeze it.
  mode=6;send(0,0);wait(l_valid);@(negedge clk);cp_valid=1;
  repeat(4)begin @(negedge clk);if(cp_ready||!l_valid)$fatal(1,"CP overtook active route");end
  cp_valid=0;mode=0;retire(0,6);
  // Loss of the quiescence lease aborts import without publishing staged words.
  cp_expected_crc=image_crc();cp_cmd(1);
  for(integer x=0;x<3;x=x+1)begin
   @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=saved[x];cp_s_last=0;
   do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;
  end
  cp_safe=0;cp_result(2);cp_safe=1;if(slot_valid!=1||fault)$fatal(1,"CP interrupted import changed slots");
  save_image;
  // Already-exposed export data must survive loss of the lease/backpressure.
  cp_cmd(0);wait(cp_m_valid);@(negedge clk);cp_safe=0;
  repeat(5)begin @(negedge clk);if(!cp_m_valid||cp_m_index||cp_m_data!=saved[0]||cp_rsp_valid)$fatal(1,"CP export retracted after failure");end
  cp_safe=1;
  for(integer x=0;x<30;x=x+1)begin
   if(!cp_m_valid||cp_m_index!=x||cp_m_data!==saved[x]||cp_m_last!=(x==29))$fatal(1,"CP failed export changed frame");
   cp_m_ready=1;@(negedge clk);cp_m_ready=0;
  end
  cp_result(2);if(slot_valid!=1)$fatal(1,"CP export changed live paths");
  cp_design=0;cp_cmd(0);cp_result(1);cp_design=active_design;
  cp_nodes=0;cp_cmd(0);cp_result(1);cp_nodes=9089009;
  // A cold reset interrupts a partial staging bank, while owner memory survives.
  cp_expected_crc=image_crc();cp_cmd(1);
  for(integer x=0;x<5;x=x+1)begin
   @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=saved[x];cp_s_last=0;
   do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;
  end
  preserve_owner=1;reset_all;if(cp_busy||cp_rsp_valid||slot_valid||fault)$fatal(1,"CP partial bank survived reset");
  load_image(0,0);if(slot_valid!=1)$fatal(1,"CP restore after partial reset");
  j=lr;send(1,0);retire(0,6);if(lr!=j||slot_valid)$fatal(1,"CP resumed saved ripup");
  for(i=0;i<10;i=i+1)if(refs[i])$fatal(1,"CP reset recovery refs");
  save_image;for(i=0;i<30;i=i+1)if(saved[i])$fatal(1,"CP invalid slot leaked stale data");
  load_image(0,0);if(slot_valid)$fatal(1,"CP empty restore");

  // Full-capacity synthetic image exercises the last-node duplicate scan and
  // atomic publication. Topology belongs to the trusted checkpoint producer.
  saved[0]=1;saved[1]=CP_CAPACITY;saved[2]=2717;saved[3]=100;saved[4]=200;saved[5]=32'h9abcdef0;saved[6]=32'h12345678;
  for(i=0;i<CP_CAPACITY;i=i+1)saved[7+i]=1000+i;
  load_image(0,0);if(slot_valid!=1)$fatal(1,"CP full length import");save_image;
  saved[7+CP_CAPACITY-1]=saved[7];load_image(0,1);if(slot_valid!=1)$fatal(1,"CP full-length bad replacement published");
  save_image;for(i=0;i<CP_CAPACITY;i=i+1)if(saved[7+i]!=1000+i)$fatal(1,"CP full-length atomic preservation");
  for(i=0;i<30;i=i+1)saved[i]=0;load_image(0,0);if(slot_valid)$fatal(1,"CP full-length cleanup");



  $fflush(events);$fclose(events);$display("ROUTE_CHECKPOINT_PASS checks=%0d cp=%0d",checks,cp_checks);$display("ROUTE_STAGE_BANK_PASS checked=%0d captures=%0d imports=%0d",stage_checked,stage_captures,stage_imports);$finish;
 end
always @(posedge clk)begin
 if(rst&&preserve_owner)$fdisplay(events,"CPRESET %0d",cp_checks);
 if(!rst&&cp_valid&&cp_ready)$fdisplay(events,"CPC %0d %0d %016h %0d %0d %08h",cp_checks,cp_restore,cp_design,cp_nodes,cp_nets,cp_expected_crc);
 if(!rst&&cp_m_valid&&cp_m_ready)$fdisplay(events,"CPO %0d %0d %08h %0d",cp_checks,cp_m_index,cp_m_data,cp_m_last);
end
always @(posedge clk)if(!rst&&cp_s_valid&&cp_s_ready)$fdisplay(events,"CPI %0d %0d %08h %0d %08h",cp_checks,cp_s_index,cp_s_data,cp_s_last,cp_expected_crc);
 initial begin
  if(!$value$plusargs("bank_events=%s",bank_path))$fatal(1,"bank events path");
  bank_fd=$fopen(bank_path,"w");if(!bank_fd)$fatal(1,"bank events open");
 end
 always @(negedge clk)begin
  bank_cycle=bank_cycle+1;
  for(integer bank_slot=0;bank_slot<2;bank_slot=bank_slot+1)
   for(integer bank_word=0;bank_word<8;bank_word=bank_word+1)begin
    if(!bank_seen||dut.path[bank_slot][bank_word]!==bank_previous[bank_slot][bank_word])
     $fdisplay(bank_fd,"BANK %0d %0d %0d %08h",bank_cycle,bank_slot,bank_word,dut.path[bank_slot][bank_word]);
    bank_previous[bank_slot][bank_word]=dut.path[bank_slot][bank_word];
   end
  bank_seen=1;$fflush(bank_fd);
 end

 initial begin
  if(!$value$plusargs("stage_events=%s",stage_path))$fatal(1,"stage events path");
  stage_fd=$fopen(stage_path,"w");if(!stage_fd)$fatal(1,"stage events open");
 end
 // Original control branches, with no dependency on new sw_* event signals.
 always @(posedge clk)begin
  if(dut.rst)begin end
  else begin
   case(dut.cp_state)
    0:if(dut.cp_valid&&dut.cp_ready)begin
     if(dut.cp_design!=dut.active_design||dut.cp_nodes==0||dut.cp_nets==0)begin end
     else if(dut.cp_restore)begin end
     else begin
      stage_captures=stage_captures+1;
      for(integer ss=0;ss<2;ss=ss+1)begin
       stage_expected[ss*15]<=dut.slot_valid[ss]?1:0;
       stage_expected[ss*15+1]<=dut.slot_valid[ss]?dut.sizes[ss]:0;
       stage_expected[ss*15+2]<=dut.slot_valid[ss]?dut.nets[ss]:0;
       stage_expected[ss*15+3]<=dut.slot_valid[ss]?dut.sources[ss]:0;
       stage_expected[ss*15+4]<=dut.slot_valid[ss]?dut.sinks[ss]:0;
       stage_expected[ss*15+5]<=dut.slot_valid[ss]?dut.designs[ss][31:0]:0;
       stage_expected[ss*15+6]<=dut.slot_valid[ss]?dut.designs[ss][63:32]:0;
       for(integer ww=0;ww<8;ww=ww+1)
        stage_expected[ss*15+7+ww]<=dut.slot_valid[ss]&&ww<dut.sizes[ss]?dut.path[ss][ww]:0;
      end
     end
    end
    2:if(dut.cp_failed||dut.abort||dut.fault||dut.cp_drift)begin end
     else if(dut.cp_s_valid&&dut.cp_s_ready)begin
      if(dut.cp_s_index!=dut.cp_pos||dut.cp_s_last!=(dut.cp_pos+1==30))begin end
      else begin stage_expected[dut.cp_pos]<=dut.cp_s_data;stage_imports=stage_imports+1;end
     end
    default:begin end
   endcase
  end
  #1;
  for(integer cc=0;cc<30;cc=cc+1)
   if(dut.cp_stage[cc]!==stage_expected[cc])$fatal(1,"old-tree stage mismatch cycle=%0d word=%0d got=%08h expected=%08h",stage_checked,cc,dut.cp_stage[cc],stage_expected[cc]);
  stage_checked=stage_checked+1;
 end
 always @(negedge clk)begin
  stage_cycle=stage_cycle+1;
  for(integer ww=0;ww<30;ww=ww+1)begin
   if(!stage_seen||dut.cp_stage[ww]!==stage_previous[ww])
    $fdisplay(stage_fd,"STAGE %0d %0d %08h",stage_cycle,ww,dut.cp_stage[ww]);
   stage_previous[ww]=dut.cp_stage[ww];
  end
  stage_seen=1;$fflush(stage_fd);
 end

endmodule
