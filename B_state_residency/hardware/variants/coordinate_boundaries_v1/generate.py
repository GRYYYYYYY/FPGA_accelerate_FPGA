from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('top',HERE.parent/'coordinate_v1/generate_top.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
for kind,module in [('controller','coordinate_controller'),('table','geometry_table_reader')]:
 ps=mod.ports(HERE.parent/'coordinate_v1'/f'{module}.sv');s=['`timescale 1ns/1ps',f'module tb_{module};','reg clk=0;always #5 clk=~clk;']
 for n,(d,w)in ps.items():
  if n!='clk':s.append(('reg 'if d=='input'else 'wire ')+w+' '+n+('=0'if d=='input'else '')+';')
 s.append(module+(' #(.TOKEN_BITS(3),.MAX_CYCLES(64))' if kind=='controller' else '')+' dut(.*);');s.append((HERE/(kind+'_body.inc')).read_text());s.append('endmodule')
 (HERE/f'tb_{module}.sv').write_text('\n'.join(s)+'\n')
