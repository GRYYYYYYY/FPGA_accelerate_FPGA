from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('parser',HERE.parent/'coordinate_v1/generate_top.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);ports=g.ports
PARAM='SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,OWNER_BITS=32,MAX_CYCLES=33554432'
def main():
 old=(HERE.parent/'candidate_pipeline_v1/candidate_engine.sv').read_text();assert old.count(' wire  operation_pending;')==1
 core=old.replace('module candidate_engine #(','module candidate_query_core #(',1).replace(' input wire  clk,',' output wire operation_pending,\n input wire  clk,',1).replace(' wire  operation_pending;','')
 (HERE/'candidate_query_core.sv').write_text(core);cp=ports(HERE/'candidate_query_core.sv');sp=ports(HERE.parent/'cost_state_v1/cost_state_store.sv')
 ext=dict(cp);ext.update({'design_id':('input','[63:0]'),'host_ctrl_version':('input','[31:0]'),'expand_version':('input','[31:0]'),'query_version':('output','[31:0]'),'query_ready':('output',''),'cost_lease':('output','')})
 wires={};con={};lines=[]
 def wire(n,w):
  if n not in ext:wires[n]=w
 con['core']={}
 for n,(d,w)in cp.items():
  sig=n
  if n=='abort':sig='abort||fence_stopped'
  elif n in ['fault','busy']:sig='core_'+n;wire(sig,w)
  elif n in ['expand_valid','expand_ready','host_ctrl_valid','host_ctrl_ready','host_io_valid','host_io_ready','host_design_req_valid','host_design_req_ready','host_owner_req_valid','host_owner_req_ready']:sig='core_'+n;wire(sig,w)
  con['core'][n]=sig
 con['store']={}
 for n,(d,w)in sp.items():
  if n in ['clk','rst']:sig=n
  elif n=='abort':sig='abort||fence_stopped'
  elif n=='query_active':sig='p_active'
  elif n=='decision_lock':sig='operation_pending||cost_lease'
  elif n in ['active_query','active_price']:sig='p_'+n
  elif n in ['req_valid','req_ready']:sig='raw_cs_'+n;wire(sig,w);ext['cs_'+n]=(d,w)
  else:sig='cs_'+n;ext[sig]=(d,w)
  con['store'][n]=sig
 for n,w in [('all_configured',''),('configuration_fault',''),('permit_open',''),('permit_control',''),('permit_expand',''),('permit_cs_request',''),('query_drift',''),('bad_control_identity',''),('bad_expand_identity',''),('internal_fire','')]:wire(n,w)
 lines+=['assign all_configured=g_configured&&d_configured&&owner_configured&&t_configured&&cs_configured&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!owner_cfg_rsp_valid&&!t_cfg_rsp_valid&&!cs_cfg_rsp_valid;',
 'assign configuration_fault=g_configured&&d_configured&&owner_configured&&cs_configured&&(g_nodes!=d_nodes||g_nodes!=owner_nodes||g_nodes!=cost_nodes||cs_design_id!=design_id);',
 'assign query_drift=query_owned&&p_active&&(query_version!=cs_published_version||p_active_price!=query_version[3:0]||cs_editing);',
 'assign query_ready=all_configured&&cs_ready_for_query&&!core_busy&&!cost_lease&&!fault;',
 'assign permit_open=query_ready&&host_ctrl_version==cs_published_version&&host_ctrl_price==cs_published_version[3:0];',
 'assign permit_control=!cost_lease&&!cs_busy&&!fault&&(host_ctrl_op==0?permit_open:(query_owned&&host_ctrl_version==query_version&&host_ctrl_query==p_active_query&&host_ctrl_price==p_active_price));',
 'assign core_host_ctrl_valid=host_ctrl_valid&&permit_control;',
 'assign host_ctrl_ready=core_host_ctrl_ready&&permit_control;',
 'assign permit_expand=!cost_lease&&cs_ready_for_query&&query_owned&&!fault&&expand_version==query_version&&cs_published_version==query_version;',
 'assign core_expand_valid=expand_valid&&permit_expand;',
 'assign expand_ready=core_expand_ready&&permit_expand;',
 'assign permit_cs_request=!fault&&(cs_req_host?(!core_busy&&!cost_lease&&(cs_editing||(!host_ctrl_valid&&!expand_valid))):(operation_pending&&query_owned));',
 'assign raw_cs_req_valid=cs_req_valid&&permit_cs_request;',
 'assign cs_req_ready=raw_cs_req_ready&&permit_cs_request;',
 'assign internal_fire=raw_cs_req_valid&&raw_cs_req_ready&&!cs_req_host;',
 'assign bad_control_identity=host_ctrl_valid&&query_ready&&(host_ctrl_op==0?(host_ctrl_version!=cs_published_version||host_ctrl_price!=cs_published_version[3:0]):(!query_owned||host_ctrl_version!=query_version||host_ctrl_query!=p_active_query||host_ctrl_price!=p_active_price));',
 'assign bad_expand_identity=expand_valid&&!core_busy&&!cost_lease&&p_active&&cs_ready_for_query&&query_owned&&(expand_version!=query_version);',
 'assign fault=core_fault||cs_fault||fence_stopped||configuration_fault||query_drift;',
 'assign busy=core_busy||cs_busy||cost_lease;']
 for group in ['host_io','host_design_req','host_owner_req']:
  lines+=['assign core_'+group+'_valid='+group+'_valid&&!cost_lease&&!fault;','assign '+group+'_ready=core_'+group+'_ready&&!cost_lease&&!fault;']
 lines+=['always @(posedge clk)begin',
 ' if(rst)begin cost_lease<=0;query_owned<=0;query_version<=0;fence_stopped<=0;g_nodes<=0;d_nodes<=0;owner_nodes<=0;cost_nodes<=0;end',
 ' else begin',
 '  if(g_cfg_valid&&g_cfg_ready)g_nodes<=g_cfg_nodes;',
 '  if(d_cfg_valid&&d_cfg_ready)d_nodes<=d_cfg_nodes;',
 '  if(owner_cfg_valid&&owner_cfg_ready)owner_nodes<=owner_cfg_nodes;',
 '  if(cs_cfg_valid&&cs_cfg_ready)cost_nodes<=cs_cfg_nodes;',
 '  if(cost_lease&&!cs_busy)cost_lease<=0;',
 '  if(internal_fire)cost_lease<=1;',
 '  if(host_ctrl_valid&&host_ctrl_ready&&host_ctrl_op==0)begin query_owned<=1;query_version<=host_ctrl_version;end',
 '  else if(!p_active&&!core_busy)query_owned<=0;',
 '  if(host_ctrl_rsp_valid&&host_ctrl_rsp_ready&&host_ctrl_status!=0)query_owned<=0;',
 '  if(core_fault||cs_fault||configuration_fault||query_drift||bad_control_identity||bad_expand_identity)fence_stopped<=1;',
 ' end',
 'end']
 regs={'cost_lease','query_version'}
 text=['`timescale 1ns/1ps',f'module candidate_cost_state_engine #(parameter integer {PARAM})(',',\n'.join(d+(' reg 'if n in regs else' wire ')+w+' '+n for n,(d,w)in ext.items()),');','reg query_owned,fence_stopped;reg[31:0]g_nodes,d_nodes,owner_nodes,cost_nodes;']
 text+=['wire '+w+' '+n+';'for n,w in wires.items()]+lines
 for pre,module in [('core','candidate_query_core #('+','.join('.'+x+'('+x+')'for x in [v.split('=')[0]for v in PARAM.split(',')])+')'),('store','cost_state_store')]:text.append(module+' '+pre+'(\n'+',\n'.join('.'+n+'('+v+')'for n,v in con[pre].items())+'\n);')
 text+=['endmodule'];(HERE/'candidate_cost_state_engine.sv').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()
