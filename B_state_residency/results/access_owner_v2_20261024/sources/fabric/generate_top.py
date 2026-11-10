from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('basegen',HERE.parent/'coordinate_v1/generate_top.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);ports=mod.ports
def main():
 base=HERE.parent/'access_fabric_v3/access_fabric.sv';old=ports(base);raw=ports(HERE.parent/'owner_axi_v1/owner_state_store.sv');bridge=ports(HERE.parent/'owner_bridge_v1/owner_bridge.sv')
 ext={n:v for n,v in old.items()if not n.startswith('o_')}
 for n,v in raw.items():
  if n.startswith(('cfg_','m_'))or n=='configured':ext['owner_'+n]=v
 for n,v in bridge.items():
  if n.startswith('h_'):ext['host_owner_'+n[2:]]=v
 text=base.read_text();body=text[text.index(');')+2:];body=body.rsplit('endmodule',1)[0]
 body=body.replace('assign fault=a_fault||d_fault||c_fault;','assign fault=a_fault||d_fault||c_fault||o_fault;')
 body=body.replace('assign a_enable=g_configured&&t_configured&&!host_pending&&!host_ctrl_valid&&!host_io_valid;', 'assign a_enable=g_configured&&t_configured&&owner_configured&&!host_pending&&!host_ctrl_valid&&!host_io_valid&&!bridge_host_pending&&!host_owner_req_valid&&!owner_cfg_valid&&!owner_cfg_rsp_valid;')
 lines=[text[:text.index('(')+1]+',\n'.join(' '+d+' wire '+w+' '+n for n,(d,w)in ext.items())+');']
 # The first '(' belongs to the parameter list; preserve its full declaration.
 header=text[:text.index(')(\n')+3]
 lines=[header+',\n'.join(' '+d+' wire '+w+' '+n for n,(d,w)in ext.items())+'\n);']
 lines+=[' wire '+w+' '+n+';'for n,(d,w)in old.items()if n.startswith('o_')]
 wires={};con_b={};con_r={}
 for n,(d,w)in bridge.items():
  if n in ['clk','rst','abort']:sig=n
  elif n=='decision_lock':sig='access_pending'
  elif n in ['active','active_query','active_price']:sig='p_'+n
  elif n.startswith('s_'):sig='o_'+n[2:]
  elif n.startswith('h_'):
   sig='host_owner_'+n[2:]
   if n=='h_req_valid':sig='host_owner_req_valid&&!owner_cfg_valid&&!owner_cfg_rsp_valid'
   if n=='h_req_ready':sig='bridge_h_ready';wires[sig]=w
  elif n=='fault':sig='o_fault'
  else:sig='bridge_'+n;wires[sig]=w
  con_b[n]=sig
 for n,(d,w)in raw.items():
  if n in ['clk','rst','abort']:sig=n
  elif n.startswith(('cfg_','m_'))or n=='configured':sig='owner_'+n
  elif n=='busy':sig='raw_busy';wires[sig]=w
  elif n=='fault':sig='bridge_b_fault'
  else:sig='bridge_b_'+n
  if n=='cfg_valid':sig='owner_cfg_valid&&!access_pending&&!bridge_busy&&!host_owner_req_valid'
  if n=='cfg_ready':sig='raw_cfg_ready';wires[sig]=w
  con_r[n]=sig
 lines+=[' wire '+w+' '+n+';'for n,w in wires.items()]
 lines.append(body)
 lines+=[' assign owner_cfg_ready=raw_cfg_ready&&!access_pending&&!bridge_busy&&!host_owner_req_valid;',' assign host_owner_req_ready=bridge_h_ready&&!owner_cfg_valid&&!owner_cfg_rsp_valid;']
 for module,name,con in [('owner_bridge','owners',con_b),('owner_state_store','owner_store',con_r)]:lines.append(' '+module+' '+name+'(\n'+',\n'.join('.'+n+'('+v+')'for n,v in con.items())+'\n);')
 lines.append('endmodule');(HERE/'access_fabric.sv').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
