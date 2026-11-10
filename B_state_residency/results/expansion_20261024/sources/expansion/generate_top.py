"""Wire existing frozen interface shapes without modifying their implementations."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
paths={'g':ROOT/'hardware/variants/graph_reader_v1/graph_static_reader.sv','d':ROOT/'hardware/variants/design_store_v3/design_state_store.sv','b':ROOT/'hardware/variants/children_engine_v2/children_build_engine.sv','p':ROOT/'hardware/variants/auto_pager_v1/paged_exclusion_engine.sv','c':HERE/'expansion_controller.sv'}
def ports(path):
 s=re.sub(r'//[^\n]*','',path.read_text());s=s[:s.index(');')];parts=re.split(r'\b(input|output)\s+(?:wire|reg)\s*',s);out={}
 for i in range(1,len(parts),2):
  direction=parts[i];body=parts[i+1].strip().rstrip(',');match=re.match(r'(\[[^]]+\])\s*',body)
  width=match[1]if match else '';body=body[match.end():]if match else body
  for name in body.split(','):
   name=name.strip();assert re.fullmatch('[A-Za-z_][A-Za-z_0-9]*',name),(path,name)
   out[name]=(direction,width)
 return out
ps={k:ports(p)for k,p in paths.items()};external={'clk':('input',''),'rst':('input','')};wires={};connections={}
for pre in ['g','d','b','p']:
 connections[pre]={}
 for name,spec in ps[pre].items():
  signal=name if name in ['clk','rst']else pre+'_'+name;connections[pre][name]=signal
  expose=(pre in ['g','d']and(name.startswith('cfg_')or name=='configured'))or(name.startswith('m_')and pre in ['g','d','p'])
  if signal not in ['clk','rst']:
   if expose:external[signal]=spec
   else:wires[signal]=spec[1]
# Controller matches names of internal request/reply nets, and has user-facing expansion streams.
connections['c']={}
for name,spec in ps['c'].items():
 connections['c'][name]=name
 if name not in wires and name not in external:
  if name in ['enable','configuration_fault']:wires[name]=spec[1]
  else:external[name]=spec
for name,spec in ps['p'].items():
 if name.startswith(('ctrl_','io_')):external['host_'+name]=spec
# Public status for host query lifecycle, assigned by pager.
for name in ['p_active','p_active_query','p_active_price']:
 external[name]=('output',wires.pop(name))
text=['`timescale 1ns/1ps','module node_expansion_engine #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,OWNER_BITS=32)(']
text.append(',\n'.join(' '+d+' wire '+w+' '+name for name,(d,w)in external.items()));text+=[');']
text += [' wire '+w+' '+name+';'for name,w in wires.items()]
text += [' reg host_pending;reg[31:0] graph_nodes,design_nodes;',' wire permit_host=!rst&&!busy&&!fault&&!host_pending;',
 ' assign enable=!host_pending&&!host_ctrl_valid&&!host_io_valid&&p_active&&g_configured&&d_configured;',
 ' assign configuration_fault=g_configured&&d_configured&&graph_nodes!=design_nodes;',
 ' always @(posedge clk)begin',
 '  if(rst)begin host_pending<=0;graph_nodes<=0;design_nodes<=0;end',
 '  else begin',
 '   if(g_cfg_valid&&g_cfg_ready)graph_nodes<=g_cfg_nodes;',
 '   if(d_cfg_valid&&d_cfg_ready)design_nodes<=d_cfg_nodes;',
 '   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_pending<=1;',
 '   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_pending<=0;',
 '  end',' end']
for name,(direction,width)in ps['p'].items():
 if not name.startswith(('ctrl_','io_')):continue
 if name in ['ctrl_valid','io_valid']:
  extra='&&!host_ctrl_valid'if name=='io_valid'else ''
  text.append(f' assign p_{name}=host_{name}&&permit_host{extra};')
 elif name in ['ctrl_ready','io_ready']:
  extra='&&!host_ctrl_valid'if name=='io_ready'else ''
  text.append(f' assign host_{name}=p_{name}&&permit_host{extra};')
 elif direction=='input':text.append(f' assign p_{name}=host_{name};')
 else:text.append(f' assign host_{name}=p_{name};')
for name in ['dispatch_enable','execute_enable','fence_service_enable','ack_receive_enable']:text.append(f' assign p_{name}=1;')
modules={'g':'graph_static_reader','d':'design_state_store','b':'children_build_engine','p':'paged_exclusion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS))','c':'expansion_controller #(.TOKEN_BITS(TOKEN_BITS),.OWNER_BITS(OWNER_BITS))'}
for pre in ['g','d','b','p','c']:text.append(' '+modules[pre]+' '+{'g':'graph','d':'design_store','b':'builder','p':'pager','c':'controller'}[pre]+'(\n'+',\n'.join('  .'+p+'('+sig+')'for p,sig in connections[pre].items())+'\n );')
text.append('endmodule');(HERE/'node_expansion_engine.sv').write_text('\n'.join(text)+'\n')
if __name__=='__main__':print('EXPANSION_TOP_GENERATED ports='+str(len(external)))
