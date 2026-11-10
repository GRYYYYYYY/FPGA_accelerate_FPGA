from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('p',HERE.parent/'coordinate_v1/generate_top.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);ports=mod.ports
def main():
 paths={'g':HERE.parent/'graph_reader_v1/graph_static_reader.sv','d':HERE.parent/'design_store_v3/design_state_store.sv','c':HERE/'metadata_controller.sv'}
 ps={n:ports(p)for n,p in paths.items()};ext={'clk':('input',''),'rst':('input',''),'abort':('input',''),'owner_configured':('input',''),'owner_nodes':('input','[31:0]')};wires={};con={}
 for prefix in ['g','d','c']:
  con[prefix]={}
  for n,(direction,width)in ps[prefix].items():
   if n in ['clk','rst']:sig=n
   elif prefix in ['g','d']:
    sig=prefix+'_'+n
    if n.startswith(('m_','cfg_'))or n=='configured':ext[sig]=(direction,width)
    else:wires[sig]=width
   elif n=='abort':sig='abort||config_fault||owner_lost'
   elif n in ['active','active_query','active_price']or n.startswith(('req_','rsp_')):sig=n;ext[n]=(direction,width)
   elif n.startswith('g_'):sig=n
   elif n=='d_fault':sig='d_fault'
   elif n.startswith('d_'):sig='c_'+n;wires[sig]=width
   elif n=='nodes':sig='held_g_nodes'
   elif n=='claim_active':sig='d_claim_active'
   else:sig='c_'+n;wires[sig]=width
   con[prefix][n]=sig
 for n,v in ps['d'].items():
  if n.startswith(('req_','rsp_')):ext['host_design_'+n]=v
 ext['busy']=('output','');ext['fault']=('output','');ext['design_claim_active']=('output','')
 s=['`timescale 1ns/1ps','module metadata_service #(parameter integer TOKEN_BITS=32,MAX_CYCLES=262144)(', ',\n'.join(' '+d+' wire '+w+' '+n for n,(d,w)in ext.items()),');']
 s+=[' wire '+w+' '+n+';'for n,w in wires.items()]
 s+=[' reg[31:0]held_g_nodes,held_d_nodes;reg meta_pending,host_pending;',
 ' wire config_fault=g_configured&&d_configured&&owner_configured&&(held_g_nodes!=held_d_nodes||held_g_nodes!=owner_nodes);',
 ' wire owner_lost=meta_pending&&!owner_configured;',
 ' wire permit_host=!rst&&!fault&&!meta_pending&&!host_pending;',
 ' assign fault=c_fault||g_fault||d_fault||config_fault||owner_lost;',
 ' assign busy=meta_pending||host_pending;',
 ' assign design_claim_active=d_claim_active;',
 ' assign c_enable=g_configured&&d_configured&&owner_configured&&!g_cfg_rsp_valid&&!d_cfg_rsp_valid&&!host_pending&&!host_design_req_valid;',
 ' always @(posedge clk)begin',
 '  if(rst)begin held_g_nodes<=0;held_d_nodes<=0;meta_pending<=0;host_pending<=0;end',
 '  else begin',
 '   if(g_cfg_valid&&g_cfg_ready)held_g_nodes<=g_cfg_nodes;',
 '   if(d_cfg_valid&&d_cfg_ready)held_d_nodes<=d_cfg_nodes;',
 '   if(req_valid&&req_ready)meta_pending<=1;',
 '   if(rsp_valid&&rsp_ready)meta_pending<=0;',
 '   if(host_design_req_valid&&host_design_req_ready)host_pending<=1;',
 '   if(host_design_rsp_valid&&host_design_rsp_ready)host_pending<=0;',
 '  end',
 ' end']
 for n,(direction,width)in ps['d'].items():
  if n.startswith('req_'):
   if n=='req_valid':s.append(' assign d_req_valid=meta_pending?c_d_req_valid:(host_design_req_valid&&permit_host);')
   elif n=='req_ready':s+=[' assign c_d_req_ready=d_req_ready&&meta_pending;',' assign host_design_req_ready=d_req_ready&&permit_host;']
   else:s.append(' assign d_'+n+'=meta_pending?c_d_'+n+':host_design_'+n+';')
  elif n.startswith('rsp_'):
   if n=='rsp_valid':s+=[' assign c_d_rsp_valid=d_rsp_valid&&!host_pending;',' assign host_design_rsp_valid=d_rsp_valid&&host_pending;']
   elif n=='rsp_ready':s.append(' assign d_rsp_ready=host_pending?host_design_rsp_ready:c_d_rsp_ready;')
   else:s+=[' assign c_d_'+n+'=d_'+n+';',' assign host_design_'+n+'=d_'+n+';']
 for prefix,module,name in [('g','graph_static_reader','graph'),('d','design_state_store','design_store'),('c','metadata_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(MAX_CYCLES))','controller')]:
  s.append(' '+module+' '+name+'(\n'+',\n'.join('.'+n+'('+v+')'for n,v in con[prefix].items())+'\n);')
 s.append('endmodule');(HERE/'metadata_service.sv').write_text('\n'.join(s)+'\n')
if __name__=='__main__':main()
