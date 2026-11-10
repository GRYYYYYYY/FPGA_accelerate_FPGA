from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'hardware/variants/route_commit_v1/tb_route_commit.sv'
def make(max_path=8):
 s=BASE.read_text()
 decl='''
 localparam CP_CAPACITY=8;
 reg cp_valid=0,cp_restore=0,cp_safe=1,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0;
 wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;
 reg[63:0]cp_design=64'h123456789abcdef0;reg[31:0]cp_nodes=9089009,cp_nets=27960,cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
 wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;
 reg[31:0]saved[0:29],pristine[0:29];reg[31:0]saved_crc;integer cp_checks=0;
 reg preserve_owner=0;
'''
 s=s.replace(' reg clk=0;',decl+' reg clk=0;')
 s=s.replace('for(integer x=0;x<10;x=x+1)refs[x]<=0;', 'if(!preserve_owner)for(integer x=0;x<10;x=x+1)refs[x]<=0;')
 tasks='''
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
'''
 s=s.replace(' task reset_all;',tasks+'\n task reset_all;')
 s=s.replace('endmodule', '''always @(posedge clk)begin
 if(rst&&preserve_owner)$fdisplay(events,"CPRESET %0d",cp_checks);
 if(!rst&&cp_valid&&cp_ready)$fdisplay(events,"CPC %0d %0d %016h %0d %0d %08h",cp_checks,cp_restore,cp_design,cp_nodes,cp_nets,cp_expected_crc);
 if(!rst&&cp_m_valid&&cp_m_ready)$fdisplay(events,"CPO %0d %0d %08h %0d",cp_checks,cp_m_index,cp_m_data,cp_m_last);
end
always @(posedge clk)if(!rst&&cp_s_valid&&cp_s_ready)$fdisplay(events,"CPI %0d %0d %08h %0d %08h",cp_checks,cp_s_index,cp_s_data,cp_s_last,cp_expected_crc);
endmodule''')
 extra='''
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


'''
 s=s.replace('  $fflush(events);',extra+'\n  $fflush(events);').replace('ROUTE_COMMIT_PASS checks=%0d",checks','ROUTE_CHECKPOINT_PASS checks=%0d cp=%0d",checks,cp_checks')
 if max_path==32:
  s=s.replace('CP_CAPACITY=8','CP_CAPACITY=32')
  s=s.replace('.MAX_PATH(8),.MAX_CYCLES(256)', '.MAX_PATH(32),.MAX_CYCLES(1024)')
  s=s.replace('[0:29]', '[0:77]').replace('x<30','x<78').replace('i<30','i<78').replace('x==29','x==77')
  s=s.replace('saved[1]=9','saved[1]=33').replace('1:saved[1]=9','1:saved[1]=33')
  s=s.replace('l_node>110','l_node>134').replace('l_node==110?', 'l_node==134?').replace('req_source=110','req_source=134')
  s=s.replace('mode==8?300:3','mode==8?1200:3').replace('ticks>20000','ticks>50000')
 return s
if __name__=='__main__':(HERE/'tb_route_commit.sv').write_text(make())
