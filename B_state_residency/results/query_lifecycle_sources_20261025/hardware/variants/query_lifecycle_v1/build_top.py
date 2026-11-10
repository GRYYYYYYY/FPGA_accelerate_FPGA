from pathlib import Path
import importlib.util,json
HERE=Path(__file__).parent;ROOT=HERE.parents[2]
def load(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def make():
 old=json.loads((HERE.parent/'search_scheduler_v1/interface.json').read_text());parser=load(HERE.parent/'residency_system_v1/build.py','parser');cp=parser.ports(HERE/'query_lifecycle.sv')
 ports={n:v for n,v in old.items()if not(n.startswith('ss_')and v['direction']=='input')}
 expose=[n for n in cp if n.startswith('cmd_')or n.startswith('rsp_')]+['abort','busy','fault','phase','prepared_event','prepare_acked','cleanup_acked']
 for n in expose:
  assert 'qc_'+n not in ports,n
  d,w=cp[n];ports['qc_'+n]=dict(direction=d,width=w)
 def decl(n,d,w):return d+' wire '+('['+str(w-1)+':0] 'if w>1 else'')+n
 s='`timescale 1ns/1ps\nmodule query_residency_system #(parameter integer SLOTS=32,FRAMES=16384,INDEX_BITS=14,HASH_BITS=15,ENABLE_TEST_INJECTION=0)(\n'+',\n'.join(decl(n,v['direction'],v['width'])for n,v in ports.items())+'\n);\n'
 for n,v in old.items():
  if n not in ports:s+=decl(n,'',v['width']).strip()+';\n'
 mux=['f_sv','f_sr','f_sp','f_srv','f_srr','f_srp','rc_req_valid','rc_req_ready','rc_rsp_valid','rc_rsp_ready','f_route_payload','k_rec_valid','k_rec_ready']
 for n in mux:s+=decl('b_'+n,'',old[n]['width']).strip()+';\n'
 local=['service_valid','service_ready','service_lane','service_payload','service_rsp_valid','service_rsp_ready','service_rsp_payload','route_valid','route_ready','route_payload','route_rsp_valid','route_rsp_ready']
 for n in local:s+=decl('c_'+n,'',cp[n][1]).strip()+';\n'
 s+='wire host_open=!qc_busy&&!qc_fault;\n'
 s+='assign f_sr=host_open?b_f_sr:16\'d0;assign f_srv=host_open?b_f_srv:16\'d0;assign f_srp=b_f_srp;\n'
 s+='assign rc_req_ready=host_open&&b_rc_req_ready;assign b_rc_req_valid=qc_busy?c_route_valid:(host_open&&rc_req_valid);assign b_f_route_payload=qc_busy?c_route_payload:f_route_payload;assign rc_rsp_valid=host_open&&b_rc_rsp_valid;assign b_rc_rsp_ready=qc_busy?c_route_rsp_ready:(host_open&&rc_rsp_ready);\n'
 s+='assign c_route_ready=qc_busy&&b_rc_req_ready;assign c_route_rsp_valid=qc_busy&&b_rc_rsp_valid;assign b_k_rec_valid=!qc_busy&&k_rec_valid;assign k_rec_ready=!qc_busy&&b_k_rec_ready;\n'
 s+='assign c_service_ready=qc_busy&&(c_service_lane==8?b_f_sr[8]:b_f_sr[6]);assign c_service_rsp_valid=qc_busy&&(c_service_lane==8?b_f_srv[8]:b_f_srv[6]);assign c_service_rsp_payload=c_service_lane==8?b_f_srp[2048+:256]:b_f_srp[1536+:256];\n'
 s+='''generate for(genvar i=0;i<16;i=i+1)begin:host_lanes
 if(i==6||i==8)begin:owned_service
  assign b_f_sv[i]=qc_busy?(c_service_valid&&c_service_lane==i):(host_open&&f_sv[i]);
  assign b_f_sp[i*2432+:2432]=qc_busy?{1984'd0,c_service_payload}:f_sp[i*2432+:2432];
  assign b_f_srr[i]=qc_busy?(c_service_rsp_ready&&c_service_lane==i):(host_open&&f_srr[i]);
 end else begin:host_only
  assign b_f_sv[i]=host_open&&f_sv[i];assign b_f_sp[i*2432+:2432]=f_sp[i*2432+:2432];assign b_f_srr[i]=host_open&&f_srr[i];
 end
end endgenerate
'''
 s+='search_residency_system #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.ENABLE_TEST_INJECTION(ENABLE_TEST_INJECTION))inner('+','.join('.'+n+'('+('b_'+n if n in mux else n)+')'for n in old)+');\n'
 bind={n:'qc_'+n for n in expose}
 bind.update(clk='clk',rst='rst',abort='qc_abort||k_rec_valid',admit="k_permit&&!fault&&!rc_fault&&!k_fault&&!cf_fault&&!lr_fault&&!f_fault&&!ss_fault&&!ss_busy&&f_phase==0&&f_normal_retired&&f_backend_idle&&f_all_drained&&f_sv==0&&!rc_req_valid&&!k_rec_valid",backend_fault='fault||rc_fault||k_fault||cf_fault||lr_fault||f_fault',backend_drained='f_normal_retired&&f_backend_idle&&f_all_drained&&!ss_busy&&!rc_busy',active='p_active',active_design='design_id',active_version='query_version',active_query='p_active_query',active_price='p_active_price',route_slots='rc_slots',host_label_edit='f_sv[8]&&f_sr[8]&&f_sp[19456]',search_valid='ss_start_valid',search_ready='ss_start_ready',search_abort='ss_abort',search_rsp_valid='ss_rsp_valid',search_rsp_ready='ss_rsp_ready',search_status='ss_rsp_status',search_rsp_cookie='ss_rsp_cookie',search_result_node='ss_result_node',route_status='rc_rsp_status',route_rsp_cookie='rc_rsp_cookie',route_nodes='rc_rsp_nodes',route_acked='rc_rsp_acked')
 for n in ['cookie','source','key','nodes','max_polls','poll_cookie','design','query','price','expand']:bind['search_'+n]='ss_start_'+n
 for n in local:bind[n]='c_'+n
 assert set(bind)==set(cp),(set(cp)-set(bind),set(bind)-set(cp))
 s+='query_lifecycle controller('+','.join('.'+n+'('+v+')'for n,v in bind.items())+');\nendmodule\n';return s,ports
if __name__=='__main__':
 s,p=make();(HERE/'query_residency_system.sv').write_text(s);(HERE/'interface.json').write_text(json.dumps(p,indent=2)+'\n')
