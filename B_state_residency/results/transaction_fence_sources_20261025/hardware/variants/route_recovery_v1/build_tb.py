from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/route_fault_v1/tb_route_fault.sv').read_text()
 s=s.replace('reg injected_abort=0,injected_drift=0;', 'reg injected_abort=0,injected_drift=0;reg recover_open=1,recovering=0;reg[1:0]restore_epoch=1;reg[31:0]restore_version=3;wire raw_recovery_ready;reg[31:0]journal[0:31];integer journal_count=0,ji,observed_refs=0,repairs=0;')
 s=s.replace('.req_valid(rc_req_valid),.req_ready(rc_req_ready)', '.req_valid(rc_req_valid&&recover_open),.req_ready(raw_recovery_ready)')
 s=s.replace('candidate_recursive_engine #','assign rc_req_ready=raw_recovery_ready&&recover_open;\ncandidate_recursive_engine #',1)
 for valid,ready in [('expand_valid','expand_ready'),('seed_valid','seed_ready')]:
  s=s.replace('('+valid+'&&!rc_block)', '('+valid+'&&!rc_block&&recover_open)').replace('assign '+ready+'=!rc_block&&raw_'+ready+';', 'assign '+ready+'=!rc_block&&recover_open&&raw_'+ready+';')
 s=s.replace('host_ctrl_query=1;host_ctrl_price=3;host_ctrl_version=3;', 'host_ctrl_query=restore_epoch;host_ctrl_price=restore_version[3:0];host_ctrl_version=restore_version;')
 # Freeze config handshake sequence before editing the main recovery path.
 a=s.index(' @(negedge clk);q_cfg_valid=1;');e=s.index(' control(0);',a);config=s[a:e]
 tasks='''
always @(posedge clk)if(!rst&&armed&&!recovering&&route_join.o_valid&&route_join.o_ready)begin
 if(journal_count>=32)$fatal(1,"journal capacity");journal[journal_count]<=route_join.o_node;journal_count<=journal_count+1;
 $fdisplay(trace,"J %0d %0d",cycles,route_join.o_node);
end
task configure_all;begin
'''+config+'''end endtask
task recovery_owner(input integer op,input[31:0]node);begin
 @(negedge clk);host_owner_req_op=op;host_owner_req_node=node;host_owner_req_net=2717;host_owner_req_cookie=32'hdad00000+node;host_owner_req_valid=1;
 do @(posedge clk);while(!host_owner_req_ready);@(negedge clk);host_owner_req_valid=0;
 wait(host_owner_rsp_valid);@(negedge clk);
 if(host_owner_rsp_status||host_owner_rsp_cookie!=32'hdad00000+node||host_owner_rsp_count>1||host_owner_rsp_occupancy!=(host_owner_rsp_count!=0))$fatal(1,"authority repair rejects unknown owner state");
 observed_refs=host_owner_rsp_count;$fdisplay(trace,"GX %0d %0d %0d %0d %0d",cycles,op,node,host_owner_rsp_count,host_owner_rsp_occupancy);
 host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
end endtask
'''
 pos=s.index('initial begin\n trace=$fopen');s=s[:pos]+tasks+s[pos:]
 a=s.index(' $fflush(trace);$fclose(trace);',s.index('wait(rc_rsp_valid)'))
 s=s[:a]+'''
 // No reset until both protocol observers and actual memory interfaces drained.
 if(!label_drained||!owner_drained||mem_owner.rp||mem_owner.wp||mem_p.rp||mem_p.wp)$fatal(1,"unsafe reset");
 recover_open=0;recovering=1;armed=0;injected_abort=0;injected_drift=0;
 host_ctrl_valid=0;host_io_valid=0;host_owner_req_valid=0;host_design_req_valid=0;expand_valid=0;seed_valid=0;
 q_cfg_valid=0;g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 $fdisplay(trace,"RESET %0d %0d",cycles,journal_count);
 rst=1;repeat(5)@(negedge clk);rst=0;
 restore_epoch=2;restore_version=4;cs_cfg_version=4;
 // New external work remains barred while coordinator alone repairs/reloads.
 rc_req_valid=1;expand_valid=1;seed_valid=1;
 configure_all;
 for(ji=0;ji<journal_count;ji=ji+1)begin
  recovery_owner(0,journal[ji]);
  if(observed_refs!=0)begin recovery_owner(2,journal[ji]);if(observed_refs!=0)$fatal(1,"repair did not restore authority");repairs=repairs+1;end
  recovery_owner(0,journal[ji]);if(observed_refs!=0)$fatal(1,"dirty journal node");
 end
 $fdisplay(trace,"AUTH %0d %0d",cycles,repairs);
 control(0);
 // Probe fresh logical epoch before importing: old physical bytes must not leak.
 @(negedge clk);host_io_valid=1;host_io_node=150697;host_io_field=0;host_io_write=0;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||host_io_present)$fatal(1,"stale physical label exposed after cold reset");
 $fdisplay(trace,"ABS %0d %040h",cycles,host_io_payload);host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
 rc=$fseek(imports_fd,0,0);if(rc)$fatal(1,"authority labels rewind");
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"reload node");
  for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"reload field");import_record[field_i*32+:32]=word;end
  for(field_i=0;field_i<5;field_i=field_i+1)label_write(import_node,field_i,import_record[field_i*32+:32]);
  $fdisplay(trace,"RELOAD %0d %0d %040h",cycles,import_node,import_record);
 end
 control(1);
 rc=$fseek(imports_fd,0,0);
 for(import_i=0;import_i<328;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);import_record[field_i*32+:32]=word;end
  label_read(import_node);if(host_record!==import_record)$fatal(1,"restored authority labels");$fdisplay(trace,"CHECK %0d %0d %040h",cycles,import_node,host_record);
 end
 if(rc_req_ready||expand_ready||seed_ready||rc_slots!=0||rc_fault)$fatal(1,"recovery admission gate");
 rc_req_valid=0;expand_valid=0;seed_valid=0;recover_open=1;
 @(negedge clk);rc_req_op=0;rc_req_slot=0;rc_req_sink=150697;rc_req_sequence=1;rc_req_cookie=32'hfabcd002;rc_req_valid=1;
 do @(posedge clk);while(!rc_req_ready);@(negedge clk);rc_req_valid=0;
 wait(rc_rsp_valid);@(negedge clk);if(rc_rsp_status||rc_rsp_acked!=6||rc_rsp_nodes!=6||rc_slots!=1||rc_fault||!label_drained||!owner_drained)$fatal(1,"recovered commit");
 $fdisplay(trace,"RECOVERED %0d %0d %0d %0d",cycles,rc_rsp_status,rc_rsp_nodes,rc_rsp_acked);
 rc_rsp_ready=1;@(negedge clk);rc_rsp_ready=0;wait(!rc_block);
 control(1);control(2);
 if(fault||rc_fault||repairs!=((fault_case==1||fault_case==3||fault_case==4)?1:0))$fatal(1,"recovery final");
 $fflush(trace);$fclose(trace);$display("ROUTE_RECOVERY_PASS case=%0d journal=%0d repairs=%0d epoch=%0d version=%0d cycles=%0d",fault_case,journal_count,repairs,restore_epoch,restore_version,cycles);$finish;
end
endmodule
'''
 # Watch the coordinator gate throughout the reload, not just at completion.
 s=s.replace(' if(rc_block)begin',' if(recovering&&!recover_open&&(rc_req_ready||expand_ready||seed_ready))$fatal(1,"work admitted during authority restore");\n if(rc_block)begin')
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_route_recovery.sv').write_text(make())
