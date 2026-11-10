from pathlib import Path
from generate_top import ports,HERE
ps=ports(HERE/'candidate_engine.sv')
s=['`timescale 1ns/1ps','module tb_candidate;','reg clk=0;always #5 clk=~clk;']
for n,(d,w)in ps.items():
 if n=='clk':continue
 drv=d=='input'and not n.startswith(('g_m_','d_m_','t_m_','p_m_','owner_m_'))
 s.append(('reg 'if drv else 'wire ')+w+' '+n+('=0'if drv else '')+';')
s+=['`ifdef PRESSURE','localparam SLOTS=1;','`else','localparam SLOTS=32;','`endif','`ifdef DEFAULT_DIRECTORY','localparam FRAMES=163840,INDEX_BITS=18,HASH_BITS=18;','`else','localparam FRAMES=16384,INDEX_BITS=14,HASH_BITS=15;','`endif','candidate_engine #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS))dut(.*);']
for pre,tag,bits,ro in [('g','graph',64,1),('d','design',64,0),('t','tables',64,1),('p','labels',32,0),('owner','owners',64,0)]:
 s.append(f'integer {pre}_reads,{pre}_writes,{pre}_rbeats,{pre}_wbeats,{pre}_bs;')
 base={'g':['g_cfg_offsets_base','g_cfg_edges_base','g_cfg_attrs_base'],'d':['d_cfg_base',"64'd0","64'd0"],'t':['t_cfg_rows_base','t_cfg_columns_base',"64'd0"],'p':["64'd0"]*3,'owner':['owner_cfg_primary',"64'd0","64'd0"]}[pre]
 size={'g':[36356096,161878144,290848320],'d':[145424192,0,0],'t':[2496,0,0],'p':[3145728,0,0],'owner':[145433472,0,0]}[pre]
 args={'clk':'clk','rst':'rst',**{'base'+str(i):v for i,v in enumerate(base)},**{'size'+str(i):"64'd"+str(v)for i,v in enumerate(size)},'inject_r':"1'b0",'inject_b':"1'b0"}
 for port in ['araddr','arlen','arsize','arburst','arid','arvalid','arready','rdata','rid','rresp','rlast','rvalid','rready','awaddr','awlen','awsize','awburst','awid','awvalid','awready','wdata','wstrb','wlast','wvalid','wready','bid','bresp','bvalid','bready']:
  args[port]=pre+'_m_'+port if not ro or port.startswith(('ar','r'))else(''if port in ['awready','wready','bid','bresp','bvalid']else"'0")
 for port,suffix in [('reads','reads'),('writes','writes'),('rbeats','rbeats'),('wbeats','wbeats'),('bresponses','bs')]:args[port]=pre+'_'+suffix
 if pre=='p':args['size0']="(FRAMES==163840?64'd31457280:64'd3145728)"
 s.append(f'axi_file_memory #(.ADDR_BITS({bits}),.READ_ONLY({ro}),.MAX_BEATS({3 if pre=="p"else 1}),.TAG("{tag}"))mem_{pre}(\n'+',\n'.join('.'+p+'('+v+')'for p,v in args.items())+'\n);')
s.append((HERE/'tb_body.inc').read_text());s.append('endmodule');(HERE/'tb_candidate.sv').write_text('\n'.join(s)+'\n')
