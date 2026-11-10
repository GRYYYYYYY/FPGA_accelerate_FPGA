from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('g',HERE.parent/'coordinate_v1/generate_top.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=['`timescale 1ns/1ps','module tb_access_service;','reg clk=0;always #5 clk=~clk;']
for k,(d,w)in m.ports(HERE/'access_service.sv').items():
 if k!='clk':s.append(('reg 'if d=='input'else 'wire ')+w+' '+k+('=0'if d=='input'else '')+';')
s+=['access_service dut(.*);',(HERE/'tb_body.inc').read_text(),'endmodule'];(HERE/'tb_access_service.sv').write_text('\n'.join(s)+'\n')
