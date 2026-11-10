"""Verification-only closed-loop TB derived from the accepted recursive chain TB."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/candidate_recursive_v1/tb_recursive_join.sv').read_text()
 for a,b in [('size0(64\'d192)','size0(64\'d36356040)'),('size1(64\'d64)','size1(64\'d161878144)'),('size2(64\'d1088)','size2(64\'d290848288)'),('size0(64\'d576)','size0(64\'d145424192)'),('size0(64\'d2496)','size0(64\'d1280)'),('size0(64\'d640)','size0(64\'d145424256)'),('size0(64\'d1280)','size0(64\'d36804480)'),('size0(64\'d64)','size0(64\'d11540864)')]:
  # Exact region changes below avoid chaining the tables/cost common size.
  pass
 a=s.index('integer trace,fd_gold')
 prefix=s[:a]
 regions=[('mem_g(',[("64'd192","64'd36356040"),("64'd64","64'd161878144"),("64'd1088","64'd290848288")]),('mem_d(',[("64'd576","64'd145424192")]),('mem_t(',[("64'd2496","64'd1280")]),('mem_owner(',[("64'd640","64'd145424256")]),('mem_cs(',[("64'd1280","64'd36804480")]),('mem_q(',[("64'd64","64'd11540864")])]
 for name,replacements in regions:
  st=prefix.index(name);en=prefix.index(');',st);region=prefix[st:en]
  for old,new in replacements:assert old in region;region=region.replace(old,new,1)
  prefix=prefix[:st]+region+prefix[en:]
 monitor=s[a:s.index('task control(',a)]
 monitor=monitor.replace('1000000','3000000').replace('"joined_trace.txt"','"natural_trace.txt"')
 control=s[s.index('task control('):s.index('task initialize_prev(')]
 # Preserve actual internal services/ACK/frontier monitoring from accepted TB.
 return prefix+monitor+control+r'''
integer imports_fd,candidates_fd,polls_fd,finals_fd;
integer import_i,field_i,candidate_i=0,poll_i=0,expand_i=0,stopped=0;
integer cp_parent,cp_child,cp_pos,cp_action,cp_target,cp_pnode,cp_psize,cp_pkey;
integer poll_node,poll_key,poll_size,host_reads=0;
reg[159:0]host_record;reg[159:0]import_record;reg[31:0]import_node;
string natural_path;
task label_write(input[31:0]n,input integer field,input[31:0]value);begin
 @(negedge clk);host_io_valid=1;host_io_node=n;host_io_field=field;host_io_write=1;host_io_value=value;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status)$fatal(1,"label import n=%0d f=%0d",n,field);host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;
end endtask
task label_read(input[31:0]n);begin
 @(negedge clk);host_io_valid=1;host_io_node=n;host_io_field=0;host_io_write=0;
 do @(posedge clk);while(!host_io_ready);@(negedge clk);host_io_valid=0;
 wait(host_io_rsp_valid);@(negedge clk);if(host_io_status||!host_io_present)$fatal(1,"label read n=%0d",n);host_record=host_io_payload;
 host_io_rsp_ready=1;@(negedge clk);host_io_rsp_ready=0;host_reads=host_reads+1;
end endtask
task frontier_command(input[31:0]op,key,id);begin
 @(negedge clk);seed_valid=1;seed_op=op;seed_key=key;seed_id=id;seed_cookie=32'hc0000000+poll_i;seed_version=query_version;
 do @(posedge clk);while(!seed_ready);@(negedge clk);seed_valid=0;
 wait(seed_rsp_valid);@(negedge clk);if(seed_rsp_status)$fatal(1,"heap op=%0d status=%0d",op,seed_rsp_status);
 poll_node=seed_rsp_id;poll_key=seed_rsp_key;poll_size=seed_rsp_size;
 seed_rsp_ready=1;@(negedge clk);seed_rsp_ready=0;
end endtask
initial begin
 trace=$fopen("natural_trace.txt","w");if(!trace)$fatal(1,"trace open");
 if(!$value$plusargs("costvectors=%s",path))$fatal(1,"cost path");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("finallabels=%s",path))$fatal(1,"final path");finals_fd=$fopen(path,"r");
 if(!$value$plusargs("imports=%s",path))$fatal(1,"import path");imports_fd=$fopen(path,"r");
 if(!$value$plusargs("candidates=%s",path))$fatal(1,"candidate path");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls=%s",path))$fatal(1,"poll path");polls_fd=$fopen(path,"r");
 if(!fd_gold||!finals_fd||!imports_fd||!candidates_fd||!polls_fd)$fatal(1,"oracle open");
 rst=1;design_id=64'h123456789abcdef0;
 g_cfg_offsets_base=64'h1fffff000;g_cfg_edges_base=64'h10fffff000;g_cfg_attrs_base=64'h20fffff000;g_cfg_nodes=9089009;g_cfg_edges=40469536;
 d_cfg_base=64'h31fffff000;d_cfg_nodes=9089009;t_cfg_rows_base=64'h41fffff000;t_cfg_columns_base=64'h51fffff000;t_cfg_rows=311;t_cfg_columns=0;
 owner_cfg_primary=64'h61fffff000;owner_cfg_nodes=9089009;owner_cfg_capacity=0;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool;
 cs_cfg_history=64'h71fffff000;cs_cfg_prices=cs_cfg_history+36356096;cs_cfg_nets=cs_cfg_history+36357120;cs_cfg_nodes=9089009;cs_cfg_net_count=27960;cs_cfg_version=3;cs_cfg_design_id=design_id;
 q_cfg_base=64'h81fffff000;q_cfg_design=design_id;q_cfg_connections=180326;q_cfg_nodes=9089009;q_cfg_nets=27960;q_cfg_revision=1;
 repeat(5)@(negedge clk);rst=0;
 @(negedge clk);q_cfg_valid=1;do @(posedge clk);while(!q_cfg_ready);@(negedge clk);q_cfg_valid=0;
 wait(q_cfg_rsp_valid);@(negedge clk);if(q_cfg_status)$fatal(1,"qconfig");q_cfg_rsp_ready=1;@(negedge clk);q_cfg_rsp_ready=0;
 @(negedge clk);g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;
 wait(g_cfg_ready&&d_cfg_ready&&t_cfg_ready&&owner_cfg_ready&&cs_cfg_ready);@(posedge clk);@(negedge clk);g_cfg_valid=0;d_cfg_valid=0;t_cfg_valid=0;owner_cfg_valid=0;cs_cfg_valid=0;
 wait(g_cfg_rsp_valid&&d_cfg_rsp_valid&&t_cfg_rsp_valid&&owner_cfg_rsp_valid&&cs_cfg_rsp_valid);@(negedge clk);
 if(g_cfg_status||d_cfg_status||t_cfg_status||owner_cfg_status||cs_cfg_status)$fatal(1,"config g=%0d d=%0d t=%0d o=%0d c=%0d",g_cfg_status,d_cfg_status,t_cfg_status,owner_cfg_status,cs_cfg_status);
 g_cfg_rsp_ready=1;d_cfg_rsp_ready=1;t_cfg_rsp_ready=1;owner_cfg_rsp_ready=1;cs_cfg_rsp_ready=1;
 @(negedge clk);g_cfg_rsp_ready=0;d_cfg_rsp_ready=0;t_cfg_rsp_ready=0;owner_cfg_rsp_ready=0;cs_cfg_rsp_ready=0;
 control(0);
 for(import_i=0;import_i<308;import_i=import_i+1)begin
  rc=$fscanf(imports_fd,"%d",import_node);if(rc!=1)$fatal(1,"import node");
  for(field_i=0;field_i<5;field_i=field_i+1)begin rc=$fscanf(imports_fd,"%h",word);if(rc!=1)$fatal(1,"import word");import_record[field_i*32+:32]=word;end
  for(field_i=0;field_i<5;field_i=field_i+1)label_write(import_node,field_i,import_record[field_i*32+:32]);
  $fdisplay(trace,"I %0d %0d %040h",cycles,import_node,import_record);
 end
 frontier_command(1,0,65185); // The actual source seed prepared by the CPU snapshot.
 while(!stopped)begin
  frontier_command(2,0,0);
  rc=$fscanf(polls_fd,"%d %d %d",cp_pnode,cp_pkey,cp_psize);if(rc!=3||poll_node!=cp_pnode||poll_key!==cp_pkey||poll_size!=cp_psize)$fatal(1,"CPU poll mismatch index=%0d node=%0d key=%h size=%0d expected=%0d %h %0d",poll_i,poll_node,poll_key,poll_size,cp_pnode,cp_pkey,cp_psize);
  $fdisplay(trace,"P %0d %0d %08h %0d",cycles,poll_node,poll_key,poll_size);poll_i=poll_i+1;
  label_read(poll_node);if(host_record[31:0]!==poll_key)$fatal(1,"heap/label key");
  if(host_record[128])begin
   if(poll_node!=150697||poll_size!=0)$fatal(1,"unexpected target");stopped=1;
  end else begin
   // Parent is the actual POLL response, never supplied from CPU E/C records.
   @(negedge clk);expand_cookie=100+expand_i;expand_parent=poll_node;expand_prune=0;expand_has_laguna=0;expand_sink=150697;expand_net=2717;expand_sequence=1;expand_flags=260;expand_connection=16506;
   expand_xmin=38;expand_xmax=46;expand_ymin=283;expand_ymax=295;expand_version=3;expand_valid=1;
   do @(posedge clk);while(!expand_ready);@(negedge clk);expand_valid=0;
   host_ctrl_valid=1;host_ctrl_op=2;host_io_valid=1;host_design_req_valid=1;host_owner_req_valid=1;
   while(!result_valid)begin
    wait(out_valid||result_valid);@(negedge clk);
    if(out_valid)begin
     rc=$fscanf(candidates_fd,"%d %d %d %d %d",cp_parent,cp_child,cp_pos,cp_action,cp_target);
     if(rc!=5||dut.held_parent!=poll_node||cp_parent!=poll_node||out_node!=cp_child||out_action!=cp_action||out_sequence!=cp_pos||out_cookie!=100+expand_i)$fatal(1,"candidate mismatch index=%0d parent=%0d child=%0d action=%0d seq=%0d expected=%0d %0d %0d %0d",candidate_i,dut.held_parent,out_node,out_action,out_sequence,cp_parent,cp_child,cp_action,cp_pos);
     if(!out_params_valid||out_connection!=16506||out_params[127:96]!=150697||out_config[31:0]!=1||out_config[351:320]!=38||out_config[383:352]!=46||out_config[415:384]!=283||out_config[447:416]!=295)$fatal(1,"natural State/config");
     if(out_action==1)begin
      rc=$fscanf(fd_gold,"%d %d",logical_parent,logical_child);if(rc!=2||logical_parent!=poll_node||logical_child!=out_node)$fatal(1,"cost identity");
      for(j=0;j<23;j=j+1)begin rc=$fscanf(fd_gold,"%h",word);if(rc!=1)$fatal(1,"packet word");gold_packet[j*32+:32]=word;end
      for(j=0;j<5;j=j+1)begin rc=$fscanf(fd_gold,"%h",word);if(rc!=1)$fatal(1,"cost word");gold_cost[j*32+:32]=word;end
      if(!out_cost_valid||out_cost_status||out_cost_packet!==gold_packet||out_cost_words!==gold_cost)$fatal(1,"natural cost index=%0d packet=%h expected=%h cost=%h expected=%h",candidate_i,out_cost_packet,gold_packet,out_cost_words,gold_cost);
      gold_label={32'(cp_target),32'd1,32'(poll_node),gold_cost[95:64],gold_cost[159:128]};
      if(!out_commit_valid||out_commit_status||out_commit_acked!=7||out_commit_payload!==gold_label)$fatal(1,"label ACK payload index=%0d",candidate_i);
      if(!out_offer_valid||out_offer_status||out_offer_node!=out_node||out_offer_key!==gold_cost[159:128])$fatal(1,"actual OFFER");commits=commits+1;
      $fdisplay(trace,"C %0d %0d %0184h %040h",cycles,out_node,out_cost_packet,out_cost_words);
     end else if(out_cost_valid||out_commit_valid||out_offer_valid)$fatal(1,"skip changed state");
     $fdisplay(trace,"O %0d %0d %0d %0d %0d %0d",cycles,out_cookie,dut.held_parent,out_node,out_action,out_sequence);
     repeat(3)@(negedge clk);out_ready=1;@(negedge clk);out_ready=0;outputs=outputs+1;candidate_i=candidate_i+1;
    end
   end
   @(negedge clk);if(result_status||result_cookie!=100+expand_i)$fatal(1,"expansion result status=%0d",result_status);
   $fdisplay(trace,"Q %0d %0d %0d %0d %0d %0d",cycles,result_cookie,result_count,result_expanded_count,result_raw_count,result_early);
   result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;expand_i=expand_i+1;
  end
 end
 if(poll_i!=73||expand_i!=72||candidate_i!=271||commits!=171||offers!=171||physical_expands!=72||metadata_calls!=271)$fatal(1,"natural totals");
 control(1);
 for(final_index=0;final_index<308;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"final word");gold_final[j*32+:32]=word;end
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"final native node=%0d actual=%h expected=%h",final_node_id,host_record,gold_final);
  $fdisplay(trace,"R %0d %0d %040h",cycles,final_node_id,host_record);
 end
 control(1);control(2);
 if(fault||p_writes!=p_bs||d_writes!=d_bs||!host_blocks)$fatal(1,"outstanding");
 $fflush(trace);$fclose(trace);
 $display("NATURAL_QUERY_PASS outputs=%0d commits=%0d offers=%0d expands=%0d polls=%0d visited=%0d host_blocks=%0d labels_R=%0d labels_W=%0d State_R=%0d cycles=%0d",outputs,commits,offers,physical_expands,poll_i,visited_reads,host_blocks,p_reads,p_writes,q_reads,cycles);$finish;
end
endmodule
'''
if __name__=='__main__':(Path(__file__).parent/'tb_natural_query.sv').write_text(make())
