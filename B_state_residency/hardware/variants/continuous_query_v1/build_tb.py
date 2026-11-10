from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/natural_query_v1/tb_natural_query.sv').read_text()
 s=s.replace('integer imports_fd,candidates_fd,polls_fd,finals_fd;','integer imports_fd,candidates_fd,polls_fd,finals_fd,prepared_fd;\ninteger query_index,next_node,path_steps;reg[31:0]route_node;reg[31:0]selected_sink=150697,selected_connection=16506,selected_sequence=1;')
 s=s.replace('import_i<308','import_i<328').replace('final_index<308','final_index<328')
 s=s.replace('poll_node!=150697','poll_node!=selected_sink').replace('expand_sink=150697','expand_sink=selected_sink').replace('expand_connection=16506','expand_connection=selected_connection').replace('expand_sequence=1','expand_sequence=selected_sequence').replace('out_connection!=16506','out_connection!=selected_connection').replace('out_params[127:96]!=150697','out_params[127:96]!=selected_sink').replace('out_config[31:0]!=1','out_config[31:0]!=selected_sequence').replace("32'd1,32'(poll_node)","selected_sequence,32'(poll_node)")
 a=s.index(' frontier_command(1,0,65185);');b=s.index(' if(poll_i!=73',a);search=s[a:b]
 end=s.index(' control(1);control(2);',b);finals=s[s.index(' control(1);',b):end]
 finals=finals.replace('"R %0d %0d %040h",cycles','"R %0d %0d %040h %0d",cycles').replace('final_node_id,host_record);','final_node_id,host_record,query_index);')
 transition=r'''
 if(query_index==0)begin
  // Read actual prev links; neither path nor next node comes from an oracle.
  route_node=150697;path_steps=0;
  while(route_node!=65185)begin
   label_read(route_node);next_node=host_record[95:64];
   $fdisplay(trace,"BT %0d %0d %0d",cycles,route_node,next_node);
   if(next_node==32'hffffffff||path_steps>32)$fatal(1,"backtrace chain");
   route_node=next_node;path_steps=path_steps+1;
   if(route_node!=65185)begin
    @(negedge clk);host_owner_req_op=1;host_owner_req_cookie=32'hd0000000+path_steps;host_owner_req_node=route_node;host_owner_req_net=2717;host_owner_req_valid=1;
    do @(posedge clk);while(!host_owner_req_ready);@(negedge clk);host_owner_req_valid=0;
    wait(host_owner_rsp_valid);@(negedge clk);
    if(host_owner_rsp_status||host_owner_rsp_cookie!=32'hd0000000+path_steps||host_owner_rsp_count!=1||host_owner_rsp_occupancy!=1)$fatal(1,"route owner commit");
    $fdisplay(trace,"OC %0d %0d %0d %0d",cycles,route_node,host_owner_rsp_count,host_owner_rsp_occupancy);
    host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
   end
  end
  if(path_steps!=7)$fatal(1,"path size");
  label_write(150697,4,0);label_write(128009,4,1);
  label_write(65185,0,0);label_write(65185,1,0);label_write(65185,3,2);
  if(!$value$plusargs("prepared=%s",path))$fatal(1,"prepared path");prepared_fd=$fopen(path,"r");
  for(final_index=0;final_index<328;final_index=final_index+1)begin
   rc=$fscanf(prepared_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"prepared node");
   for(j=0;j<5;j=j+1)begin rc=$fscanf(prepared_fd,"%h",word);if(rc!=1)$fatal(1,"prepared word");gold_final[j*32+:32]=word;end
   label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"query2 prepared node=%0d actual=%h expected=%h",final_node_id,host_record,gold_final);
   $fdisplay(trace,"T %0d %0d %040h",cycles,final_node_id,host_record);
  end
  $fclose(prepared_fd);$fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
  if(!$value$plusargs("cost2=%s",path))$fatal(1,"cost2 path");fd_gold=$fopen(path,"r");
  if(!$value$plusargs("candidates2=%s",path))$fatal(1,"candidates2 path");candidates_fd=$fopen(path,"r");
  if(!$value$plusargs("polls2=%s",path))$fatal(1,"polls2 path");polls_fd=$fopen(path,"r");
  if(!$value$plusargs("finals2=%s",path))$fatal(1,"finals2 path");finals_fd=$fopen(path,"r");
  if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"query2 oracle open");
  selected_sink=128009;selected_connection=16497;selected_sequence=2;stopped=0;
 end
'''
 s=s[:a]+' for(query_index=0;query_index<2;query_index=query_index+1)begin\n'+search+finals+transition+' end\n if(poll_i!=116||expand_i!=114||candidate_i!=447||commits!=293||offers!=293||physical_expands!=114||metadata_calls!=447)$fatal(1,"two-query totals");\n'+s[end:]
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_continuous_query.sv').write_text(make())
