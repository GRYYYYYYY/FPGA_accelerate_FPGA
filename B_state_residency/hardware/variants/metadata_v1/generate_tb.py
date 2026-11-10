from pathlib import Path
from generate_top import HERE,ports
ps=ports(HERE/'metadata_service.sv');s=['`timescale 1ns/1ps','module tb_metadata;','reg clk=0;always #5 clk=~clk;']
for n,(d,w)in ps.items():
 if n=='clk':continue
 driver=d=='input'and not n.startswith(('g_m_','d_m_'))
 s.append(('reg 'if driver else 'wire ')+w+' '+n+('=0'if driver else '')+';')
s+=['metadata_service dut(.*);','reg[63:0]graph_size0=0,graph_size1=0,graph_size2=0,design_size=0;','reg inject_graph=0,inject_design=0,inject_design_b=0;']
for prefix,tag in [('g','graph'),('d','design')]:
 s.append(f'integer {prefix}_reads,{prefix}_writes,{prefix}_rbeats,{prefix}_wbeats,{prefix}_bs;')
 args={'clk':'clk','rst':'rst','base0':'g_cfg_offsets_base'if prefix=='g'else'd_cfg_base','base1':'g_cfg_edges_base'if prefix=='g'else"64'd0",'base2':'g_cfg_attrs_base'if prefix=='g'else"64'd0",'size0':'graph_size0'if prefix=='g'else'design_size','size1':'graph_size1'if prefix=='g'else"64'd0",'size2':'graph_size2'if prefix=='g'else"64'd0",'inject_r':'inject_graph'if prefix=='g'else'inject_design','inject_b':'inject_design_b'if prefix=='d'else"1'b0"}
 for n in ['araddr','arlen','arsize','arburst','arid','arvalid','arready','rdata','rid','rresp','rlast','rvalid','rready','awaddr','awlen','awsize','awburst','awid','awvalid','awready','wdata','wstrb','wlast','wvalid','wready','bid','bresp','bvalid','bready']:
  if prefix=='d'or n.startswith(('ar','r')):args[n]=prefix+'_m_'+n
  elif n in ['awready','wready','bid','bresp','bvalid']:args[n]=''
  else:args[n]="'0"
 for n,suffix in [('reads','reads'),('writes','writes'),('rbeats','rbeats'),('wbeats','wbeats'),('bresponses','bs')]:args[n]=prefix+'_'+suffix
 s.append(f'axi_file_memory #(.MAX_BEATS(1),.READ_ONLY({1 if prefix=="g"else 0}),.TAG("{tag}"))mem_{prefix}(\n'+',\n'.join('.'+n+'('+v+')'for n,v in args.items())+'\n);')
s+= [(HERE/'tb_body.inc').read_text(),'endmodule'];(HERE/'tb_metadata.sv').write_text('\n'.join(s)+'\n')
