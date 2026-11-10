from pathlib import Path
import re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def ports(p):
 s=re.sub(r'//[^\n]*','',p.read_text());s=s[:s.index(');')];a=re.split(r'\b(input|output)\s+(?:wire|reg)\s*',s);out={}
 for i in range(1,len(a),2):
  b=a[i+1].strip().rstrip(',');m=re.match(r'(\[[^]]+\])\s*',b);w=m[1]if m else '';b=b[m.end():]if m else b
  for n in b.split(','):out[n.strip()]=(a[i],w)
 return out
paths={'g':ROOT/'hardware/variants/graph_reader_v1/graph_static_reader.sv','t':HERE/'geometry_table_reader.sv','p':ROOT/'hardware/variants/auto_pager_v1/paged_exclusion_engine.sv','c':HERE/'coordinate_controller.sv'}
def main():
 ps={k:ports(p)for k,p in paths.items()};external={'clk':('input',''),'rst':('input','')};wires={};con={}
 for pre in ['g','t','p']:
  con[pre]={}
  for n,spec in ps[pre].items():
   sig=n if n in ['clk','rst']else pre+'_'+n;con[pre][n]=sig
   if n in ['clk','rst']:continue
   if n.startswith('m_')or(pre in ['g','t']and(n.startswith('cfg_')or n=='configured')):external[sig]=spec
   else:wires[sig]=spec[1]
 con['c']={}
 for n,spec in ps['c'].items():
  if n.startswith('p_io_'):sig='c_'+n;wires[sig]=spec[1]
  elif n in ['active','active_query','active_price']:sig='p_'+n
  elif n in ['nodes','table_rows','table_columns','enable']:sig=n;wires[sig]=spec[1]
  else:
   sig=n
   if n not in wires and n not in external:external[n]=spec
  con['c'][n]=sig
 for n,spec in ps['p'].items():
  if n.startswith(('ctrl_','io_')):external['host_'+n]=spec
 for n in ['p_active','p_active_query','p_active_price']:external[n]=('output',wires.pop(n))
 text=['`timescale 1ns/1ps','module coordinate_service #(parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,FRAMES=163840,INDEX_BITS=18,HASH_BITS=18,PROBE_LIMIT=64,EPOCH_BITS=16,TOKEN_BITS=32,MAX_CYCLES=262144)(', ',\n'.join(' '+d+' wire '+w+' '+n for n,(d,w)in external.items()),');']
 text+=[' wire '+w+' '+n+';'for n,w in wires.items()]
 text+=[' reg host_pending;reg [31:0]held_nodes,held_rows,held_columns;',' wire permit_host=!rst&&!busy&&!fault&&!host_pending;',
 ' assign enable=!host_pending&&!host_ctrl_valid&&!host_io_valid&&g_configured&&t_configured;',
 ' assign nodes=held_nodes;assign table_rows=held_rows;assign table_columns=held_columns;',
 ' always @(posedge clk)begin',
 '  if(rst)begin host_pending<=0;held_nodes<=0;held_rows<=0;held_columns<=0;end',
 '  else begin',
 '   if(g_cfg_valid&&g_cfg_ready)held_nodes<=g_cfg_nodes;',
 '   if(t_cfg_valid&&t_cfg_ready)begin held_rows<=t_cfg_rows;held_columns<=t_cfg_columns;end',
 '   if((host_ctrl_valid&&host_ctrl_ready)||(host_io_valid&&host_io_ready))host_pending<=1;',
 '   if((host_ctrl_rsp_valid&&host_ctrl_rsp_ready)||(host_io_rsp_valid&&host_io_rsp_ready))host_pending<=0;',
 '  end',' end']
 for n,(d,w)in ps['p'].items():
  if n.startswith('ctrl_'):
   if n=='ctrl_valid':text.append(' assign p_ctrl_valid=host_ctrl_valid&&permit_host;')
   elif n=='ctrl_ready':text.append(' assign host_ctrl_ready=p_ctrl_ready&&permit_host;')
   elif d=='input':text.append(f' assign p_{n}=host_{n};')
   else:text.append(f' assign host_{n}=p_{n};')
  elif n.startswith('io_'):
   if n=='io_valid':text.append(' assign p_io_valid=busy?c_p_io_valid:(host_io_valid&&permit_host&&!host_ctrl_valid);')
   elif n=='io_ready':text+=[' assign c_p_io_ready=p_io_ready&&busy;',' assign host_io_ready=p_io_ready&&permit_host&&!host_ctrl_valid;']
   elif n=='io_rsp_valid':text+=[' assign c_p_io_rsp_valid=p_io_rsp_valid&&!host_pending;',' assign host_io_rsp_valid=p_io_rsp_valid&&host_pending;']
   elif n=='io_rsp_ready':text.append(' assign p_io_rsp_ready=host_pending?host_io_rsp_ready:c_p_io_rsp_ready;')
   elif d=='input':text.append(f' assign p_{n}=busy?c_p_{n}:host_{n};')
   else:text+= [f' assign c_p_{n}=p_{n};',f' assign host_{n}=p_{n};']
 for n,(d,w)in ps['p'].items():
  if n in ['clk','rst']or n.startswith(('ctrl_','io_','m_'))or d!='input':continue
  text.append(f' assign p_{n}='+('1'if n in ['dispatch_enable','execute_enable','fence_service_enable','ack_receive_enable','result_ready']else '0')+';')
 mods={'g':'graph_static_reader','t':'geometry_table_reader','p':'paged_exclusion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS))','c':'coordinate_controller #(.TOKEN_BITS(TOKEN_BITS),.MAX_CYCLES(MAX_CYCLES))'}
 for pre in ['g','t','p','c']:text.append(' '+mods[pre]+' '+{'g':'graph','t':'tables','p':'pager','c':'controller'}[pre]+'(\n'+',\n'.join(' .'+n+'('+sig+')'for n,sig in con[pre].items())+'\n );')
 text.append('endmodule');(HERE/'coordinate_service.sv').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()
