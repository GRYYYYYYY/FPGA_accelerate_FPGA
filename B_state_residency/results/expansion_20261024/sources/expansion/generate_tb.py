from pathlib import Path
from generate_top import ports,HERE
ps=ports(HERE/'node_expansion_engine.sv')
s=['`timescale 1ns/1ps','module tb_node_expansion;',' reg clk=0;always #5 clk=~clk;']
for name,(direction,width)in ps.items():
 if name=='clk':continue
 driven=direction=='input'and not name.startswith(('g_m_','d_m_','p_m_'))
 s.append(' '+('reg 'if driven else 'wire ')+width+' '+name+('=0'if driven else '')+';')
s+=['`ifdef PRESSURE',' localparam SLOTS=1,TX_BITS=6,GEN_BITS=3;','`else',' localparam SLOTS=32,TX_BITS=16,GEN_BITS=16;','`endif',
 ' node_expansion_engine #(.SLOTS(SLOTS),.TX_BITS(TX_BITS),.GEN_BITS(GEN_BITS),.FRAMES(256),.INDEX_BITS(8),.HASH_BITS(8)) dut(.*);',
 ' reg inject_graph=0,inject_design=0,inject_design_b=0,inject_pager=0,inject_pager_b=0;']
for pre,tag,bits,ro in [('g','graph',64,1),('d','design',64,0),('p','labels',32,0)]:
 s.append(f' integer {pre}_reads,{pre}_writes,{pre}_rbeats,{pre}_wbeats,{pre}_bs;')
 args={'clk':'clk','rst':'rst','base0':{'g':'g_cfg_offsets_base','d':'d_cfg_base','p':"64'd0"}[pre],'base1':"g_cfg_edges_base"if pre=='g'else"64'd0",'base2':"g_cfg_attrs_base"if pre=='g'else"64'd0",'size0':{'g':"64'd36356096",'d':"64'd145424192",'p':"64'd49152"}[pre],'size1':"64'd161878144"if pre=='g'else"64'd0",'size2':"64'd290848320"if pre=='g'else"64'd0",'inject_r':{'g':'inject_graph','d':'inject_design','p':'inject_pager'}[pre],'inject_b':{'g':"1'b0",'d':'inject_design_b','p':'inject_pager_b'}[pre]}
 for port in ['araddr','arlen','arsize','arburst','arid','arvalid','arready','rdata','rid','rresp','rlast','rvalid','rready','awaddr','awlen','awsize','awburst','awid','awvalid','awready','wdata','wstrb','wlast','wvalid','wready','bid','bresp','bvalid','bready']:
  if pre!='g'or port.startswith(('ar','r')):args[port]=pre+'_m_'+port
  elif port in ['awready','wready','bid','bresp','bvalid']:args[port]=''
  else:args[port]="'0"
 for port,suffix in [('reads','reads'),('writes','writes'),('rbeats','rbeats'),('wbeats','wbeats'),('bresponses','bs')]:args[port]=pre+'_'+suffix
 s.append(f' axi_file_memory #(.ADDR_BITS({bits}),.READ_ONLY({ro}),.MAX_BEATS({1 if pre in ["g","d"]else 3}),.TAG("{tag}")) mem_{pre}(\n'+',\n'.join('  .'+p+'('+a+')'for p,a in args.items())+'\n );')
s.append((HERE/'tb_body.inc').read_text());s.append('endmodule');(HERE/'tb_node_expansion.sv').write_text('\n'.join(s)+'\n')
