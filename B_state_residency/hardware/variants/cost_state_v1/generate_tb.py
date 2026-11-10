from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('parser',HERE.parent/'coordinate_v1/generate_top.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
s=['`timescale 1ns/1ps','module tb_cost_state;','reg clk=0;always #5 clk=~clk;']
for n,(d,w)in g.ports(HERE/'cost_state_store.sv').items():
 if n=='clk':continue
 drv=d=='input'and not n.startswith('m_');s.append(('reg 'if drv else'wire ')+w+' '+n+('=0'if drv else'')+';')
s+=['cost_state_store #(.MAX_CYCLES(2048))dut(.*);','integer reads,writes,rbeats,wbeats,bs;']
args={'clk':'clk','rst':'rst','base0':'cfg_history','base1':"64'd0",'base2':"64'd0",'size0':"64'd4096",'size1':"64'd0",'size2':"64'd0",'inject_r':"1'b0",'inject_b':"1'b0"}
for n in ['araddr','arlen','arsize','arburst','arid','arvalid','arready','rdata','rid','rresp','rlast','rvalid','rready','awaddr','awlen','awsize','awburst','awid','awvalid','awready','wdata','wstrb','wlast','wvalid','wready','bid','bresp','bvalid','bready']:args[n]='m_'+n
for n,v in [('reads','reads'),('writes','writes'),('rbeats','rbeats'),('wbeats','wbeats'),('bresponses','bs')]:args[n]=v
s.append('reg[63:0]image_size=4096,prices_offset=1024,nets_offset=2048;')
args['size0']='image_size'
s.append('axi_file_memory #(.MAX_BEATS(1),.TAG("state"))memory(\n'+',\n'.join('.'+n+'('+v+')'for n,v in args.items())+'\n);')
s.append((HERE/'tb_body.inc').read_text());s.append('endmodule');(HERE/'tb_cost_state.sv').write_text('\n'.join(s)+'\n')
