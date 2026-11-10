from pathlib import Path
import importlib.util,json,re
HERE=Path(__file__).parent

def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def make():
 b=load(HERE.parent/'search_scheduler_v1/build_join.py','old_builder');s=b.bench().replace('system.','system.inner.')
 top=load(HERE/'build_top.py','top_builder');_,ports=top.make();old=json.loads((HERE.parent/'search_scheduler_v1/interface.json').read_text())
 # Keep old search output probes, replace external direct search command by lifecycle command.
 s=s.replace('search_residency_system #','query_residency_system #',1)
 for n,v in old.items():
  if n.startswith('ss_')and v['direction']=='input':s=s.replace('.'+n+'('+n+'),','')
 decl=''
 for n,v in ports.items():
  if n in old:continue
  decl+=('reg 'if v['direction']=='input'else'wire ')+('['+str(v['width']-1)+':0] 'if v['width']>1 else'')+n+('=0'if v['direction']=='input'else'')+';\n'
 s=s.replace('module tb_candidate_offer;','module tb_candidate_offer;\n'+decl,1)
 needle='))system(';s=s.replace(needle,needle+','.join('.'+n+'('+n+')'for n in ports if n not in old)+',',1)
 # Passive native route observations use the actual request owner, never a host reg.
 a=s.index(' if(system.inner.backend.route_join.l_valid');z=s.index('\nend\n',a)
 s=s[:a]+s[a:z].replace('rc_req_slot','actual_route_slot')+s[z:]
 s=s.replace('reg[31:0]rc_read_node;',"wire actual_route_slot=system.inner.backend.f_broute_payload[1];\nreg[31:0]rc_read_node;",1)
 s=s.replace('if(rc_req_valid&&rc_req_ready)$fdisplay(trace,"FR %0d",cycles);','if(system.inner.backend.rc_req_valid&&system.inner.backend.rc_req_ready)$fdisplay(trace,"FR %0d",cycles);')
 s=s.replace(' $fdisplay(trace,"RC %0d %0d %0d %0d %0d",cycles,op,slot,rc_rsp_nodes,rc_rsp_acked);','')
 s=s.replace(';route_commands=route_commands+1;', ';')
 extra='''always @(posedge clk)if(!rst)begin
 if(qc_busy&&(f_sr!=0||rc_req_ready||k_rec_ready))$fatal(1,"lifecycle lease gap");
 if(system.c_service_valid&&system.c_service_ready)$fdisplay(trace,"LI %0d %0d %0d %0112h",cycles,query_index,system.c_service_lane,system.c_service_payload);
 if(system.c_service_rsp_valid&&system.c_service_rsp_ready)$fdisplay(trace,"LA %0d %0d %0d %064h",cycles,query_index,system.c_service_lane,system.c_service_rsp_payload);
 if(qc_prepared_event)$fdisplay(trace,"LP %0d %0d %0d",cycles,query_index,qc_prepare_acked);
 if(ss_rsp_valid&&system.inner.ss_rsp_ready)$fdisplay(trace,"SEARCH %0d %0d %0d %0d %0d %0d",cycles,query_index,ss_rsp_status,ss_polls,ss_expands,ss_candidates);
 if(system.inner.backend.rc_rsp_valid&&system.inner.backend.rc_rsp_ready)begin
  if(rc_rsp_status||rc_rsp_nodes!=6||rc_rsp_acked!=6)$fatal(1,"native route completion");
  $fdisplay(trace,"RC %0d %0d %0d %0d %0d",cycles,system.inner.backend.f_broute_payload[0],actual_route_slot,rc_rsp_nodes,rc_rsp_acked);route_commands<=route_commands+1;
 end
end
'''
 a=s.index('task autonomous_query;');z=s.index('end endtask',a)+len('end endtask');task=s[a:z]
 for n in ['cookie','source','key','nodes','max_polls','poll_cookie','design','query','price','expand','valid','ready']:task=task.replace('ss_start_'+n,'qc_cmd_'+n)
 task=task.replace('qc_cmd_valid=1;',"qc_cmd_slot=query_index;qc_cmd_route_cookie=32'hf0000000+query_index;\n qc_cmd_valid=1;",1)
 task=task.replace('qc_cmd_valid=0;',"qc_cmd_valid=0;qc_cmd_source=~qc_cmd_source;qc_cmd_expand=~qc_cmd_expand;qc_cmd_slot=~qc_cmd_slot;qc_cmd_route_cookie=~qc_cmd_route_cookie;",1)
 task=task.replace('wait(ss_rsp_valid);','wait(qc_rsp_valid);')
 task=task.replace('if(ss_rsp_status||ss_rsp_cookie', 'if(qc_rsp_status||!qc_rsp_committed||qc_prepare_acked!=4||qc_cleanup_acked!=1||qc_rsp_nodes!=6||qc_rsp_acked!=6||qc_rsp_cookie')
 task=task.replace('||ss_fault||','||qc_fault||ss_fault||')
 task=task.replace('if(!ss_rsp_valid||!ss_busy||','if(!qc_rsp_valid||!qc_busy||')
 task=task.replace(' $fdisplay(trace,"SEARCH %0d %0d %0d %0d %0d %0d",cycles,query_index,ss_rsp_status,ss_polls,ss_expands,ss_candidates);', ' $fdisplay(trace,"LIFECYCLE %0d %0d %0d %0d %0d %0d %0d %0d",cycles,query_index,qc_rsp_status,qc_rsp_committed,qc_prepare_acked,qc_cleanup_acked,qc_rsp_nodes,qc_rsp_acked);')
 task=task.replace('ss_rsp_ready=','qc_rsp_ready=')
 s=s[:a]+extra+task+s[z:]
 # The CPU dump is pre-cleanup; the post-command expected label clears only its sink target.
 s=s.replace('  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"final native', '  if(final_node_id==selected_sink)gold_final[159:128]=0;\n  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"final native',1)
 # Owner probes now observe each automatic commit before the next query.
 s=s.replace(' if(query_index==0)begin\n  route_command(0,0,150697,1);', ' stage_no=query_index;probe_owners;\n if(query_index==0)begin\n  route_command(0,0,150697,1);',1)
 a=s.index('  route_command(0,0,150697,1);');z=s.index('  $fclose(prepared_fd);',a)
 s=s[:a]+s[z:].replace('  $fclose(prepared_fd);','  ',1)
 s=s.replace(' stage_no=0;probe_owners;\n stage_no=1;route_command(0,1,128009,2);probe_owners;\n','')
 assert 'label_write(150697,4,0)'not in s and 'route_command(0,'not in s
 return s
if __name__=='__main__':(HERE/'tb_query_lifecycle_join.sv').write_text(make())
