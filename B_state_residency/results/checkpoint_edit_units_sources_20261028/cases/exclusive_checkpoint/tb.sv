`timescale 1ns/1ps
module tb_query_checkpoint;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,admit=1,backend_fault=0,backend_drained=1,active=1,host_label_edit=0;
reg[63:0]active_design=64'h123456789abcdef0,active_generation=64'h100000001;reg[31:0]active_version=3;reg[1:0]active_query=1;reg[3:0]active_price=3;reg[1:0]route_slots=0;
reg cmd_valid=0,cmd_slot=0,rsp_ready=0;wire cmd_ready,rsp_valid,busy,fault,prepared_event;reg[31:0]cmd_cookie=0,cmd_route_cookie=0,cmd_source=1,cmd_key=0,cmd_nodes=100,cmd_max_polls=10,cmd_poll_cookie=0;
reg[63:0]cmd_design=64'h123456789abcdef0;reg[1:0]cmd_query=1;reg[3:0]cmd_price=3;reg[447:0]cmd_expand=0;
wire[3:0]rsp_status,rsp_detail,phase;wire[31:0]rsp_cookie,rsp_nodes,rsp_acked,prepare_acked,cleanup_acked;wire rsp_committed;
wire service_valid,service_rsp_ready,search_valid,search_abort,search_rsp_ready,route_valid,route_rsp_ready;wire[3:0]service_lane;wire[447:0]service_payload,search_expand;wire[31:0]search_cookie,search_source,search_key,search_nodes,search_max_polls,search_poll_cookie;wire[63:0]search_design;wire[1:0]search_query;wire[3:0]search_price;wire[191:0]route_payload;
reg service_ready=1,service_rsp_valid=0,search_ready=1,search_rsp_valid=0,route_ready=1,route_rsp_valid=0;reg[255:0]service_rsp_payload=0;reg[3:0]search_status=0,route_status=0;reg[31:0]search_rsp_cookie=0,search_result_node=0,route_rsp_cookie=0,route_nodes=2,route_acked=2;
reg cp_valid=0,cp_restore=0,cp_safe=1,cp_rsp_ready=0,cp_s_valid=0,cp_s_last=0,cp_m_ready=0;wire cp_ready,cp_busy,cp_rsp_valid,cp_s_ready,cp_m_valid,cp_m_last;wire[3:0]cp_status;wire[31:0]cp_crc,cp_m_index,cp_m_data;reg[31:0]cp_expected_crc=0,cp_s_index=0,cp_s_data=0;
query_lifecycle #(.CP_SAFE_EXCLUDES_HOST_EDIT(1)) dut(.cp_rebase(1'b0),.cp_rebase_permit(1'b0),.cp_source_version(32'd0),.cp_source_query(2'd0),.cp_source_price(4'd0),.*);
integer events,checks=0,cpchecks=0,cycles=0,services=0,searches=0,routes=0;reg[31:0]image[0:9],saved[0:9];reg[31:0]saved_crc;reg[511:0]old_ledger;reg held_export=0;reg[31:0]held_data,held_index;reg held_last;
function automatic[31:0]crc_image;reg[31:0]v;begin v=32'hffffffff;for(integer x=0;x<10;x=x+1)begin v=v^image[x];for(integer k=0;k<32;k=k+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;end crc_image=~v;end endfunction
always @(posedge clk)begin
 cycles<=cycles+1;if(cycles>100000)$fatal(1,"watchdog cp=%d q=%d",dut.cp_state,phase);
 if(rst)begin service_rsp_valid<=0;search_rsp_valid<=0;route_rsp_valid<=0;end
 else begin
  if(service_valid&&service_ready)begin services<=services+1;service_rsp_payload<=0;service_rsp_payload[4]<=1;service_rsp_payload[100:69]<=32'hffffffff;service_rsp_valid<=1;end
  if(service_rsp_valid&&service_rsp_ready)service_rsp_valid<=0;
  if(search_valid&&search_ready)begin searches<=searches+1;search_rsp_valid<=1;search_rsp_cookie<=search_cookie;search_result_node<=search_expand[191:160];end
  if(search_rsp_valid&&search_rsp_ready)search_rsp_valid<=0;
  if(route_valid&&route_ready)begin routes<=routes+1;route_rsp_valid<=1;route_rsp_cookie<=route_payload[33:2];end
  if(route_rsp_valid&&route_rsp_ready)route_rsp_valid<=0;
  if(cp_restore&&dut.cp_state==1&&{dut.sequence_seen,dut.label_state_dirty,dut.last_sequence,dut.last_design,dut.last_version,dut.last_query,dut.last_price}!==old_ledger)$fatal(1,"partial ledger published");
  if(cp_valid&&cp_ready)$fdisplay(events,"C %0d %0d %016h %016h %0d %0d %0d %08h",cpchecks,cp_restore,active_design,active_generation,active_version,active_query,active_price,cp_expected_crc);
  if(cp_s_valid&&cp_s_ready)$fdisplay(events,"S %0d %0d %08h %0d",cpchecks,cp_s_index,cp_s_data,cp_s_last);
  if(cp_m_valid&&cp_m_ready)$fdisplay(events,"M %0d %0d %08h %0d",cpchecks,cp_m_index,cp_m_data,cp_m_last);
  if(cp_busy&&dut.cp_state!=4&&(dut.cp_drift||abort||backend_fault))$fdisplay(events,"ENV %0d",cpchecks);
  if(host_label_edit)$fdisplay(events,"EDIT %0d",cpchecks);
  if(cp_busy&&(service_valid||search_valid||route_valid||cmd_ready))$fatal(1,"checkpoint emitted backend/new command");
  if(held_export&&(!cp_m_valid||{cp_m_data,cp_m_index,cp_m_last}!={held_data,held_index,held_last}))$fatal(1,"held export retracted/changed");
 end
 held_export<=!rst&&cp_m_valid&&!cp_m_ready;held_data<=cp_m_data;held_index<=cp_m_index;held_last<=cp_m_last;
end
task cold;begin @(negedge clk);rst=1;repeat(3)@(negedge clk);rst=0;repeat(2)@(negedge clk);$fdisplay(events,"RESET %0d %0d",checks,cpchecks);end endtask
task query(input[31:0]seq,input integer status);integer a,b,c;begin
 a=services;b=searches;c=routes;@(negedge clk);cmd_cookie=cmd_cookie+1;cmd_expand=0;cmd_expand[447:416]=active_version;cmd_expand[255:224]=seq;cmd_expand[191:160]=9;cmd_valid=1;
 do @(posedge clk);while(!cmd_ready);@(negedge clk);cmd_valid=0;wait(rsp_valid);@(negedge clk);
 if(rsp_status!=status||rsp_cookie!=cmd_cookie||fault)$fatal(1,"query result %d/%d",rsp_status,status);
 if(status==1&&(services!=a||searches!=b||routes!=c||prepare_acked||cleanup_acked||rsp_committed))$fatal(1,"rejected sequence had side effects");
 if(status==0&&(services-a!=7||searches-b!=1||routes-c!=1||!rsp_committed))$fatal(1,"mock lifecycle missing work");
 $fdisplay(events,"Q %0d %0d %0d %0d %0d %0d %0d",checks,seq,status,dut.last_sequence,services-a,searches-b,routes-c);checks=checks+1;
 repeat(3)@(negedge clk);rsp_ready=1;@(negedge clk);rsp_ready=0;wait(!busy);
end endtask
task start_cp(input integer importing);begin
 old_ledger={dut.sequence_seen,dut.label_state_dirty,dut.last_sequence,dut.last_design,dut.last_version,dut.last_query,dut.last_price};
 @(negedge clk);cp_restore=importing;cp_valid=1;do @(posedge clk);while(!cp_ready);@(negedge clk);cp_valid=0;
end endtask
task cp_result(input integer status);reg[35:0]hold;begin
 wait(cp_rsp_valid);@(negedge clk);if(cp_status!=status)$fatal(1,"cp status %d/%d",cp_status,status);hold={cp_status,cp_crc};
 repeat(5)begin @(negedge clk);if(!cp_rsp_valid||cmd_ready||cp_ready||{cp_status,cp_crc}!==hold)$fatal(1,"held checkpoint reply");end
 $fdisplay(events,"CP %0d %0d %08h %0d %0d %0d",cpchecks,cp_status,cp_crc,dut.sequence_seen,dut.last_sequence,dut.label_state_dirty);cpchecks=cpchecks+1;
 cp_rsp_ready=1;@(negedge clk);cp_rsp_ready=0;wait(!cp_busy);
end endtask
task export_cp(input integer status);begin
 start_cp(0);
 if(status!=1)begin
  for(integer x=0;x<10;x=x+1)begin
   wait(cp_m_valid);@(negedge clk);if(cp_m_index!=x||cp_m_last!=(x==9))$fatal(1,"export index");image[x]=cp_m_data;
   repeat(2)@(negedge clk);cp_m_ready=1;@(negedge clk);cp_m_ready=0;
  end
 end
 cp_result(status);if(status==0&&cp_crc!=crc_image())$fatal(1,"export CRC");
end endtask
task load_cp(input integer status);begin
 cp_expected_crc=crc_image();start_cp(1);
 for(integer x=0;x<10;x=x+1)begin
  @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=image[x];cp_s_last=x==9;do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;
 end
 cp_result(status);
end endtask
task saved_image;begin for(integer x=0;x<10;x=x+1)image[x]=saved[x];end endtask
initial begin
 string p;if(!$value$plusargs("events=%s",p))$fatal(1,"events");events=$fopen(p,"w");cold;
 query(1,0);query(2,0);query(2,1);export_cp(0);for(integer x=0;x<10;x=x+1)saved[x]=image[x];saved_crc=cp_crc;
 for(integer x=0;x<10;x=x+1)$fdisplay(events,"IMAGE %0d %08h",x,image[x]);
 cold;query(2,0); // Counterexample: un-restored original reset semantics replay the old sequence.
 cold;saved_image;load_cp(0);query(2,1);query(1,1);query(3,0);
 saved_image;load_cp(1);if(dut.last_sequence!=3)$fatal(1,"rollback changed floor");query(3,1);
 // Every rejected staged image must preserve all live ledger fields.
 for(integer mode=0;mode<11;mode=mode+1)begin
  saved_image;image[8]=4;
  case(mode)
   0:image[0]=0;1:image[1]=2;2:image[2]=image[2]^1;3:image[5]=image[5]^1;4:image[6]=image[6]+1;5:image[7]=image[7]^1;6:image[7]=image[7]^4;7:image[7]=image[7]|256;8:image[9]=1;9:image[7]=image[7]&32'hffffffbf;10:image[8]=0;
  endcase
  load_cp(1);if(dut.last_sequence!=3||!dut.sequence_seen||dut.label_state_dirty)$fatal(1,"bad import changed ledger");
 end
 saved_image;image[8]=4;cp_expected_crc=crc_image()^1;start_cp(1);
 for(integer x=0;x<10;x=x+1)begin @(negedge clk);cp_s_valid=1;cp_s_index=x;cp_s_data=image[x];cp_s_last=x==9;do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;end
 cp_result(1);if(dut.last_sequence!=3)$fatal(1,"CRC changed ledger");
 // Mid-import permission loss cannot publish partial state.
 saved_image;cp_expected_crc=crc_image();start_cp(1);@(negedge clk);cp_s_valid=1;cp_s_index=0;cp_s_data=image[0];cp_s_last=0;do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;cp_safe=0;cp_result(2);cp_safe=1;
 if(dut.last_sequence!=3)$fatal(1,"partial import changed ledger");
 // Malformed transport boundaries and context changes are not partial restores.
 for(integer mode=0;mode<2;mode=mode+1)begin
  saved_image;cp_expected_crc=crc_image();start_cp(1);@(negedge clk);cp_s_valid=1;cp_s_index=mode==0?1:0;cp_s_data=image[0];cp_s_last=mode==1;do @(posedge clk);while(!cp_s_ready);@(negedge clk);cp_s_valid=0;cp_result(1);
  if(dut.last_sequence!=3)$fatal(1,"transport changed floor");
 end
 saved_image;cp_expected_crc=crc_image();start_cp(1);@(negedge clk);active_generation=active_generation^64'h100000000;cp_result(2);active_generation=active_generation^64'h100000000;
 if(dut.last_sequence!=3)$fatal(1,"generation drift changed floor");
 // Export cannot withdraw an exposed output when permission is revoked.
 start_cp(0);wait(cp_m_valid);@(negedge clk);cp_safe=0;
 for(integer x=0;x<10;x=x+1)begin wait(cp_m_valid);@(negedge clk);if(cp_m_index!=x)$fatal(1,"cancelled export order");repeat(2)@(negedge clk);cp_m_ready=1;@(negedge clk);cp_m_ready=0;end
 cp_result(2);cp_safe=1;
 // Dirty labels remain dirty across cold restore; sequence wrap never becomes0.
 @(negedge clk);host_label_edit=1;@(negedge clk);host_label_edit=0;
 saved_image;image[8]=3;load_cp(1);if(!dut.label_state_dirty)$fatal(1,"old clean checkpoint bypassed host label edits");
 export_cp(0);cold;load_cp(0);query(4,1);
 cold;saved_image;image[8]=32'hffffffff;load_cp(0);query(32'hffffffff,1);query(0,1);query(1,1);
 cold;active_generation=0;export_cp(1);active_generation=64'h100000001;
 export_cp(0);cold;load_cp(0);query(1,0);query(1,1);
 $fflush(events);$fclose(events);$display("QUERY_CHECKPOINT_PASS queries=%0d checkpoints=%0d cycles=%0d",checks,cpchecks,cycles);$finish;
end
endmodule
