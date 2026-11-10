from pathlib import Path
import importlib.util
HERE=Path(__file__).parent;ROOT=HERE.parents[2]
def make():
 p=HERE.parent/'residency_system_v1/build.py';sp=importlib.util.spec_from_file_location('parser',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 ports=m.ports(HERE/'search_host_fence.sv');inputs={n:w for n,(d,w)in ports.items()if d=='input'};outputs={n:w for n,(d,w)in ports.items()if d=='output'}
 s='`timescale 1ns/1ps\nmodule tb_search_mux_equivalence;\n'
 for n,w in inputs.items():s+='reg '+('['+str(w-1)+':0] 'if w>1 else'')+n+'=0;\n'
 for n,w in outputs.items():s+='wire '+('['+str(w-1)+':0] 'if w>1 else'')+'old_'+n+',new_'+n+';\n'
 for prefix,module in [('old','search_host_fence_reference'),('new','search_host_fence')]:s+=module+' '+prefix+'_dut('+','.join('.'+n+'('+n+')'for n in inputs)+','+','.join('.'+n+'('+prefix+'_'+n+')'for n in outputs)+');\n'
 s+='''integer checks=0;reg[31:0]rng=32'h6170beef;
 task step;begin #1;
'''
 s+=' if({'+','.join('old_'+n for n in outputs)+'}!=={'+','.join('new_'+n for n in outputs)+'})$fatal(1,"mux equivalence check=%0d lane=%0d",checks,c_lane);\n'
 s+=''' checks=checks+1;end endtask
 function[31:0]random_word(input[31:0]v);begin random_word=v*32'd1664525+32'd1013904223;end endfunction
 initial begin
  search_busy=1;c_valid=1;c_rsp_ready=1;s_ready=16'hffff;s_rsp_valid=16'hffff;
  // Every response input bit, for every known lane. Distinct payload routing and isolation.
  for(integer lane=0;lane<16;lane=lane+1)begin
   c_lane=lane;
   for(integer bit_index=0;bit_index<4096;bit_index=bit_index+1)begin
    s_rsp_payload=4096'd1<<bit_index;step;
   end
  end
  // Every combination of eight ownership/response gates, on every lane.
  for(integer lane=0;lane<16;lane=lane+1)begin
   c_lane=lane;
   for(integer gates=0;gates<256;gates=gates+1)begin
    {search_busy,search_fault,system_admit,h_route_valid,h_recover_valid,c_valid,c_rsp_ready,c_candidate_ready}=gates;
    rng=random_word(rng);h_valid=rng[15:0];h_rsp_ready=rng[31:16];
    rng=random_word(rng);s_ready=rng[15:0];s_rsp_valid=rng[31:16];
    start_valid=rng[0];h_out_ready=rng[1];s_route_ready=rng[2];s_recover_ready=rng[3];
    for(integer j=0;j<128;j=j+1)begin rng=random_word(rng);s_rsp_payload[j*32+:32]=rng;end
    for(integer j=0;j<1216;j=j+1)begin rng=random_word(rng);h_payload[j*32+:32]=rng;end
    for(integer j=0;j<14;j=j+1)begin rng=random_word(rng);c_payload[j*32+:32]=rng;end
    step;
   end
  end
  if(checks!=69632)$fatal(1,"coverage");
  $display("SEARCH_MUX_EQUIVALENCE_PASS checks=%0d",checks);$finish;
 end
endmodule
'''
 return s
if __name__=='__main__':(HERE/'tb_search_mux_equivalence.sv').write_text(make())
