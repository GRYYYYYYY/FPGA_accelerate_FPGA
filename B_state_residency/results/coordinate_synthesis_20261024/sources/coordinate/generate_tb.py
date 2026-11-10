from pathlib import Path
from generate_top import ports,HERE
ps=ports(HERE/'coordinate_service.sv')
s=['`timescale 1ns/1ps','module tb_coordinate_service;','reg clk=0;always #5 clk=~clk;']
for n,(d,w)in ps.items():
 if n=='clk':continue
 drv=d=='input'and not n.startswith(('g_m_','t_m_','p_m_'))
 s.append(('reg 'if drv else 'wire ')+w+' '+n+('=0'if drv else '')+';')
s+=['`ifdef PRESSURE','localparam SLOTS=1,TX_BITS=6,GEN_BITS=3;','`else','localparam SLOTS=32,TX_BITS=16,GEN_BITS=16;','`endif',
 'coordinate_service #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(16384),.INDEX_BITS(14),.HASH_BITS(15))dut(.*);',
 'reg inject_graph=0,inject_table=0,inject_pager=0,inject_pager_b=0;',
 'reg[63:0]graph_size0=0,graph_size1=0,graph_size2=0,table_size0=0,table_size1=0;']
for pre,tag,bits in [('g','graph',64),('t','tables',64),('p','labels',32)]:
 s.append(f'integer {pre}_reads,{pre}_writes,{pre}_rbeats,{pre}_wbeats,{pre}_bs;')
 args={'clk':'clk','rst':'rst','base0':{'g':'g_cfg_offsets_base','t':'t_cfg_rows_base','p':"64'd0"}[pre], 'base1':{'g':'g_cfg_edges_base','t':'t_cfg_columns_base','p':"64'd0"}[pre],'base2':'g_cfg_attrs_base'if pre=='g'else"64'd0",'size0':{'g':'graph_size0','t':'table_size0','p':"64'd3145728"}[pre],'size1':{'g':'graph_size1','t':'table_size1','p':"64'd0"}[pre],'size2':'graph_size2'if pre=='g'else"64'd0",'inject_r':{'g':'inject_graph','t':'inject_table','p':'inject_pager'}[pre],'inject_b':'inject_pager_b'if pre=='p'else"1'b0"}
 for port in ['araddr','arlen','arsize','arburst','arid','arvalid','arready','rdata','rid','rresp','rlast','rvalid','rready','awaddr','awlen','awsize','awburst','awid','awvalid','awready','wdata','wstrb','wlast','wvalid','wready','bid','bresp','bvalid','bready']:
  if pre=='p'or port.startswith(('ar','r')):args[port]=pre+'_m_'+port
  elif port in ['awready','wready','bid','bresp','bvalid']:args[port]=''
  else:args[port]="'0"
 for port,suffix in [('reads','reads'),('writes','writes'),('rbeats','rbeats'),('wbeats','wbeats'),('bresponses','bs')]:args[port]=pre+'_'+suffix
 s.append(f'axi_file_memory #(.ADDR_BITS({bits}),.READ_ONLY({0 if pre=="p"else 1}),.MAX_BEATS({3 if pre=="p"else 1}),.TAG("{tag}"))mem_{pre}(\n'+',\n'.join('.'+p+'('+v+')'for p,v in args.items())+'\n);')
s.append((HERE/'tb_body.inc').read_text());s.append('endmodule');(HERE/'tb_coordinate_service.sv').write_text('\n'.join(s)+'\n')
