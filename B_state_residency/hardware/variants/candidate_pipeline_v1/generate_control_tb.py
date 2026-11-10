from generate_top import ports,HERE
s=['`timescale 1ns/1ps','module tb_candidate_control;','reg clk=0;always #5 clk=~clk;']
for n,(d,w)in ports(HERE/'candidate_controller.sv').items():
 if n=='clk':continue
 s.append(('reg 'if d=='input'else'wire ')+w+' '+n+('=0'if d=='input'else'')+';')
s+=['candidate_controller #(.MAX_CYCLES(32))dut(.*);',(HERE/'control_tb_body.inc').read_text(),'endmodule']
(HERE/'tb_candidate_control.sv').write_text('\n'.join(s)+'\n')
