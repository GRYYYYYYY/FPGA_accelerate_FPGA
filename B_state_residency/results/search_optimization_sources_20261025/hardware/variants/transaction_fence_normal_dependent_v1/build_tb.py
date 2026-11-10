from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent

def make():
 p=ROOT/'hardware/variants/transaction_fence_normal_v1/build_tb.py';sp=importlib.util.spec_from_file_location('normal_builder',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.make()
 s=s.replace('task route_command(', (HERE/'continuation.inc').read_text()+'\ntask route_command(',1)
 needle='   result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;'
 assert s.count(needle)==1
 s=s.replace(needle,'   if(expand_i==0||expand_i==72)retire_with_dependents;else begin result_ready=1;@(negedge clk);result_ready=0;end\n   host_ctrl_valid=0;')
 # Distinguish native and frontend parent reply retirements, with held parent payload checks.
 s=s.replace('if(rc_req_valid&&rc_req_ready)$fdisplay(trace,"FR %0d",cycles);','if(result_valid&&result_ready)$fdisplay(trace,"DF %0d %0d",cycles,result_cookie);\n if(rc_req_valid&&rc_req_ready)$fdisplay(trace,"FR %0d",cycles);')
 return s
if __name__=='__main__':(HERE/'tb_transaction_fence_normal_dependent.sv').write_text(make())
