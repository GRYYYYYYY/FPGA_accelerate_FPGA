from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('gen',HERE.parent/'coordinate_v1/generate_top.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);ports=mod.ports
paths={'a':HERE.parent/'access_service_v1/access_service.sv','c':HERE.parent/'coordinate_v1/coordinate_service.sv','d':HERE/'access_dispatch.sv'}
def main():
 ps={k:ports(v)for k,v in paths.items()};ext={'clk':('input',''),'rst':('input',''),'abort':('input','')};w={};con={}
 for pre in ['a','c','d']:
  con[pre]={}
  for n,(direction,width)in ps[pre].items():
   sig=pre+'_'+n
   if n in ['clk','rst','abort']:sig=n
   elif pre=='a':
    if n.startswith(('req_','rsp_')):sig=n;ext[sig]=(direction,width)
    elif n in ['active','active_query','active_price']:sig='p_'+n
    else:w[sig]=width
   elif pre=='c':
    if n.startswith(('g_','t_','p_m_','p_active')):sig=n;ext[sig]=(direction,width)
    else:w[sig]=width
   else:
    if n.startswith('req_')or n.startswith('rsp_'):
     tail=n.replace('req_','',1)if n.startswith('req_')else n
     sig='a_svc_'+tail
    elif n in ['active','active_query','active_price']:sig='p_'+n
    elif n.startswith('c_'):sig=n
    elif n.startswith('o_'):sig=n;ext[sig]=(direction,width)
    else:w[sig]=width
   con[pre][n]=sig
 for n,(d,b)in ps['c'].items():
  if n.startswith('host_'):ext[n]=(d,b)
 ext['busy']=('output','');ext['fault']=('output','')
 lines=['`timescale 1ns/1ps','module access_fabric #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,ACCESS_MAX_CYCLES=8388608,SERVICE_MAX_CYCLES=(1<<HASH_BITS)+262144)(', ',\n'.join(' '+d+' wire '+b+' '+n for n,(d,b)in ext.items()),');']
 lines+=[' wire '+b+' '+n+';'for n,b in w.items()if n not in ext];lines+=[' reg host_pending,access_pending;',' wire permit_host=!rst&&!access_pending&&!fault&&!host_pending;',' assign busy=access_pending||host_pending||fault;',' assign fault=a_fault||d_fault||c_fault;',' assign a_svc_fault=d_fault||c_fault;',' assign a_enable=g_configured&&t_configured&&!host_pending&&!host_ctrl_valid&&!host_io_valid;',' always @(posedge clk)begin','  if(rst)begin host_pending<=0;access_pending<=0;end','  else begin','   if(req_valid&&req_ready)access_pending<=1;','   if(rsp_valid&&rsp_ready)access_pending<=0;','   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_pending<=1;','   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_pending<=0;','  end',' end']
 # c fault is wired to dispatch. a_busy controls exclusive use of the label port.
 for n,(direction,width)in ps['c'].items():
  if n.startswith('host_ctrl_'):
   if n=='host_ctrl_valid':expr='host_ctrl_valid&&permit_host';target='c_'+n
   elif n=='host_ctrl_ready':expr='c_'+n+'&&permit_host';target=n
   elif n=='host_ctrl_rsp_valid':expr='c_'+n+'&&host_pending';target=n
   else:target=('c_'+n)if direction=='input'else n;expr=n if direction=='input'else 'c_'+n
   lines.append(' assign '+target+'='+expr+';')
  elif n.startswith('host_io_'):
   sub=n[len('host_io_'):];ln='d_l_'+sub
   if sub=='valid':lines.append(' assign c_'+n+'=access_pending?d_l_valid:(host_io_valid&&permit_host&&!host_ctrl_valid);')
   elif sub=='ready':lines+=[' assign d_l_ready=c_host_io_ready&&access_pending;',' assign host_io_ready=c_host_io_ready&&permit_host&&!host_ctrl_valid;']
   elif sub=='rsp_valid':lines+=[' assign d_l_rsp_valid=c_host_io_rsp_valid&&access_pending&&!host_pending;',' assign host_io_rsp_valid=c_host_io_rsp_valid&&host_pending;']
   elif sub=='rsp_ready':lines.append(' assign c_host_io_rsp_ready=host_pending?host_io_rsp_ready:d_l_rsp_ready;')
   elif direction=='input':lines.append(' assign c_'+n+'=access_pending?'+ln+':'+n+';')
   else:lines+=[' assign '+ln+'=c_'+n+';',' assign '+n+'=c_'+n+';']
 for pre in ['a','c','d']:
  module={'a':'access_service #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(ACCESS_MAX_CYCLES))','c':'coordinate_service #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS),.MAX_CYCLES(SERVICE_MAX_CYCLES))','d':'access_dispatch #(.MAX_CYCLES(SERVICE_MAX_CYCLES))'}[pre]
  lines.append(' '+module+' '+{'a':'access','c':'coordinates','d':'dispatch'}[pre]+'(\n'+',\n'.join('.'+n+'('+sig+')'for n,sig in con[pre].items())+'\n);')
 lines.append('endmodule');(HERE/'access_fabric.sv').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
