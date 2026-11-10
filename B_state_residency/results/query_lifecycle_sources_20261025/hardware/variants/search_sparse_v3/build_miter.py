from pathlib import Path
import importlib.util,re
HERE=Path(__file__).parent

def make():
 p=HERE.parent/'search_static_v2/build_miter.py';sp=importlib.util.spec_from_file_location('miter',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.make()
 s=s.replace('for(integer lane=0;lane<16;lane=lane+1)begin\n   c_lane=lane;', 'for(integer lane=0;lane<4;lane=lane+1)begin\n   case(lane)0:c_lane=6;1:c_lane=8;2:c_lane=11;3:c_lane=12;endcase')
 s=''.join(line.replace('old_s_payload,','').replace('new_s_payload,','')if line.startswith(' if({')else line for line in s.splitlines(keepends=True))
 s=s.replace(' checks=checks+1;end endtask', ''' for(integer k=0;k<16;k=k+1)if(new_s_valid[k]&&old_s_payload[k*2432+:2432]!==new_s_payload[k*2432+:2432])$fatal(1,"valid payload mismatch lane=%0d",k);
 checks=checks+1;end endtask''')
 s=s.replace('  if(checks!=69632)', '''  search_busy=1;search_fault=0;c_valid=1;c_rsp_ready=1;s_ready=16'hffff;s_rsp_valid=16'hffff;h_valid=16'hffff;
  for(integer lane=0;lane<16;lane=lane+1)if(lane!=6&&lane!=8&&lane!=11&&lane!=12)begin
   c_lane=lane;#1;
   if(new_c_ready||new_c_rsp_valid||new_s_valid||new_s_rsp_ready||new_h_ready)$fatal(1,"unsupported scheduler lane admitted");
   checks=checks+1;
  end
  if(checks!=17420)''').replace('SEARCH_MUX_EQUIVALENCE_PASS','SEARCH_SPARSE_EQUIVALENCE_PASS')
 return s
if __name__=='__main__':(HERE/'tb_search_mux_equivalence.sv').write_text(make())
