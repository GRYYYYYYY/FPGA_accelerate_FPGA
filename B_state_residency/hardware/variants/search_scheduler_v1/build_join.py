from pathlib import Path
import importlib.util,json,re
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent

def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def top():
 old=json.loads((ROOT/'hardware/variants/residency_system_v1/interface.json').read_text())
 parser=load(ROOT/'hardware/variants/residency_system_v1/build.py','port_parser');cp=parser.ports(HERE/'search_scheduler.sv')
 expose=['start_valid','start_ready','start_cookie','start_source','start_key','start_nodes','start_max_polls','start_poll_cookie','start_design','start_query','start_price','start_expand','rsp_valid','rsp_ready','rsp_status','rsp_cookie','polls','expands','candidates','result_node','result_key','busy','fault','phase','poll_event','poll_node','poll_key','poll_size']
 ports=dict(old);ports['ss_abort']={'direction':'input','width':1}
 for n in expose:d,w=cp[n];ports['ss_'+n]={'direction':d,'width':w}
 def declaration(n,d,w):return d+' wire '+('['+str(w-1)+':0] 'if w>1 else '')+n
 s='`timescale 1ns/1ps\nmodule search_residency_system #(parameter integer SLOTS=32,FRAMES=16384,INDEX_BITS=14,HASH_BITS=15,ENABLE_TEST_INJECTION=0)(\n'+',\n'.join(declaration(n,v['direction'],v['width'])for n,v in ports.items())+'\n);\n'
 mux=['f_sv','f_sr','f_sp','f_srv','f_srr','f_srp','out_ready','rc_req_valid','rc_req_ready','k_rec_valid','k_rec_ready']
 for n in mux:s+=declaration('b_'+n,'',old[n]['width']).strip()+';\n'
 s+='wire c_valid,c_ready,c_rsp_valid,c_rsp_ready,c_candidate_ready,ss_admit,ss_cancel;wire[3:0]c_lane;wire[447:0]c_payload;wire[255:0]c_rsp_payload;\n'
 s+='residency_system #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.ENABLE_TEST_INJECTION(ENABLE_TEST_INJECTION))backend('+','.join('.'+n+'('+('b_'+n if n in mux else n)+')'for n in old)+');\n'
 hp={'search_busy':'ss_busy','search_fault':'ss_fault','start_valid':'ss_start_valid','system_admit':'k_permit&&!fault&&!rc_fault&&!k_fault&&!cf_fault&&!lr_fault&&!f_fault&&f_phase==0&&f_normal_retired&&f_backend_idle&&f_all_drained','h_valid':'f_sv','h_ready':'f_sr','h_payload':'f_sp','h_rsp_valid':'f_srv','h_rsp_ready':'f_srr','h_rsp_payload':'f_srp','h_route_valid':'rc_req_valid','h_route_ready':'rc_req_ready','h_recover_valid':'k_rec_valid','h_recover_ready':'k_rec_ready','h_out_ready':'out_ready','s_valid':'b_f_sv','s_ready':'b_f_sr','s_payload':'b_f_sp','s_rsp_valid':'b_f_srv','s_rsp_ready':'b_f_srr','s_rsp_payload':'b_f_srp','s_route_valid':'b_rc_req_valid','s_route_ready':'b_rc_req_ready','s_recover_valid':'b_k_rec_valid','s_recover_ready':'b_k_rec_ready','s_out_ready':'b_out_ready','c_valid':'c_valid','c_ready':'c_ready','c_lane':'c_lane','c_payload':'c_payload','c_rsp_valid':'c_rsp_valid','c_rsp_ready':'c_rsp_ready','c_rsp_payload':'c_rsp_payload','c_candidate_ready':'c_candidate_ready','admit':'ss_admit','cancel':'ss_cancel'}
 s+='search_host_fence host_fence('+','.join('.'+n+'('+v+')'for n,v in hp.items())+');\n'
 bind={n:'ss_'+n for n in expose};bind.update(clk='clk',rst='rst',abort='ss_abort||ss_cancel',admit='ss_admit',backend_fault='fault||rc_fault||k_fault||cf_fault||lr_fault||f_fault',backend_drained='f_normal_retired&&f_backend_idle&&f_all_drained',active='p_active',active_design='design_id',active_version='query_version',active_query='p_active_query',active_price='p_active_price',req_valid='c_valid',req_ready='c_ready',req_lane='c_lane',req_payload='c_payload',reply_valid='c_rsp_valid',reply_ready='c_rsp_ready',reply_payload='c_rsp_payload',candidate_valid='out_valid',candidate_ready='c_candidate_ready',candidate_error="out_action==1&&(!out_cost_valid||out_cost_status!=0||!out_commit_valid||out_commit_status!=0||out_commit_acked!=7||!out_offer_valid||out_offer_status!=0)")
 assert set(bind)==set(cp),(set(cp)-set(bind),set(bind)-set(cp))
 s+='search_scheduler search_ctl('+','.join('.'+n+'('+v+')'for n,v in bind.items())+');\nendmodule\n'
 return s,ports

def bench():
 builder=load(ROOT/'hardware/variants/residency_system_v1/build.py','system_builder');s=builder.bench('normal');s=s.replace('system.','system.backend.')
 s=s.replace('residency_system #','search_residency_system #',1)
 _,ports=top();old=json.loads((ROOT/'hardware/variants/residency_system_v1/interface.json').read_text());decl=''
 for n,v in ports.items():
  if n in old:continue
  decl+=('reg 'if v['direction']=='input'else'wire ')+('['+str(v['width']-1)+':0] 'if v['width']>1 else'')+n+('=0'if v['direction']=='input'else'')+';\n'
 s=s.replace('module tb_candidate_offer;','module tb_candidate_offer;\n'+decl,1)
 # Add new ports to the instance without changing the old interface bindings.
 needle='))system(';assert s.count(needle)==1;s=s.replace(needle,needle+','.join('.'+n+'('+n+')'for n in ports if n not in old)+',')
 # Actual fabric acceptance now includes the scheduler, while host probes remain separate.
 s=s.replace('if(f_sv[fx]&&f_sr[fx])$fdisplay(trace,"FS %0d %0d %0608h",cycles,fx,f_sp[fx*2432+:2432]);','if(system.backend.f_sv[fx]&&system.backend.f_sr[fx])$fdisplay(trace,"FS %0d %0d %0608h",cycles,fx,system.backend.f_sp[fx*2432+:2432]);')
 oldtb=(ROOT/'hardware/variants/route_commit_join_drain_v2/tb_route_join_drain.sv').read_text()
 a=oldtb.index('     rc=$fscanf(candidates_fd,');b=oldtb.index('     repeat(3)@(negedge clk);out_ready=1;',a)
 score=oldtb[a:b].replace('dut.','system.backend.dut.')
 observer='''always @(posedge clk)if(!rst&&ss_busy)begin
 if(f_sr!=0||rc_req_ready||k_rec_ready)$fatal(1,"search host lease gap");
 if(ss_poll_event)begin
  poll_node=ss_poll_node;poll_key=ss_poll_key;poll_size=ss_poll_size;
  rc=$fscanf(polls_fd,"%d %d %d",cp_pnode,cp_pkey,cp_psize);
  if(rc!=3||poll_node!=cp_pnode||poll_key!==cp_pkey||poll_size!=cp_psize)$fatal(1,"autonomous poll CPU mismatch");
  $fdisplay(trace,"P %0d %0d %08h %0d",cycles,poll_node,poll_key,poll_size);poll_i=poll_i+1;
 end
 if(out_valid&&system.b_out_ready)begin
'''+score+'''
  outputs=outputs+1;candidate_i=candidate_i+1;
 end
 if(system.c_rsp_valid&&system.c_rsp_ready&&system.c_lane==11)begin
  if(system.c_rsp_payload[3:0]||system.c_rsp_payload[35:4]!=100+expand_i)$fatal(1,"autonomous expand identity");
  $fdisplay(trace,"Q %0d %0d %0d %0d %0d %0d",cycles,system.c_rsp_payload[35:4],system.c_rsp_payload[67:36],system.c_rsp_payload[99:68],system.c_rsp_payload[131:100],system.c_rsp_payload[165]);expand_i=expand_i+1;
 end
end
'''
 valid=['q_cfg_valid','g_cfg_valid','d_cfg_valid','t_cfg_valid','owner_cfg_valid','cs_cfg_valid','host_ctrl_valid','host_design_req_valid','host_io_valid','host_owner_req_valid','cc_req_valid','expand_valid','seed_valid','cs_req_valid','k_cfg_valid','cf_load_valid','rc_req_valid']
 task='''task autonomous_query;begin
 @(negedge clk);ss_start_cookie=32'h50000000+query_index;ss_start_source=65185;ss_start_key=0;ss_start_nodes=9089009;ss_start_max_polls=65536;
 ss_start_poll_cookie=32'hc0000000+poll_i;ss_start_design=design_id;ss_start_query=1;ss_start_price=3;
 ss_start_expand={32'd3,32'd295,32'd283,32'd46,32'd38,32'd260,selected_sequence,32'd2717,selected_sink,32'd0,32'd0,32'd0,32'(100+expand_i),selected_connection};
 ss_start_valid=1;do @(posedge clk);while(!ss_start_ready);@(negedge clk);ss_start_valid=0;
'''+''.join(n+'=1;\n'for n in valid)+'''
 wait(ss_rsp_valid);@(negedge clk);
 if(ss_rsp_status||ss_rsp_cookie!=32'h50000000+query_index||ss_result_node!=selected_sink||ss_fault||ss_polls!=(query_index==0?73:43)||ss_expands!=(query_index==0?72:42)||ss_candidates!=(query_index==0?271:176))$fatal(1,"autonomous query result status=%0d polls=%0d expands=%0d candidates=%0d",ss_rsp_status,ss_polls,ss_expands,ss_candidates);
 repeat(5)begin @(negedge clk);if(!ss_rsp_valid||!ss_busy||f_sr!=0||rc_req_ready||k_rec_ready||!f_all_drained||!f_backend_idle)$fatal(1,"autonomous held/drain response");end
 $fdisplay(trace,"SEARCH %0d %0d %0d %0d %0d %0d",cycles,query_index,ss_rsp_status,ss_polls,ss_expands,ss_candidates);
'''+''.join(n+'=0;\n'for n in valid)+'''
 ss_rsp_ready=1;@(negedge clk);ss_rsp_ready=0;
end endtask
'''
 # Replace all search stimulus, leaving final-state reads, real prepare/commit/ripup tests intact.
 a=s.index(' frontier_command(1,0,65185);');b=s.index(' for(final_index=0;final_index<328;',a)
 s=s[:a]+' autonomous_query;\n'+s[b:]
 s=s.replace('initial begin\n trace=$fopen',observer+task+'\ninitial begin\n trace=$fopen',1)
 return s

if __name__=='__main__':
 s,p=top();(HERE/'search_residency_system.sv').write_text(s);(HERE/'interface.json').write_text(json.dumps(p,indent=2)+'\n');(HERE/'tb_search_join.sv').write_text(bench())
