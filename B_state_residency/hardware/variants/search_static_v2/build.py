from pathlib import Path
HERE=Path(__file__).parent

def make():
 s=(HERE.parent/'search_scheduler_v1/search_host_fence.sv').read_text()
 old=' assign c_ready=search_busy&&s_ready[c_lane];assign c_rsp_valid=search_busy&&s_rsp_valid[c_lane];assign c_rsp_payload=s_rsp_payload[c_lane*256+:256];'
 new=''' // Constant slices avoid a synthesized variable-offset barrel selection.
 reg selected_ready,selected_valid;reg[255:0]selected_reply;
 always @*begin
  selected_ready=0;selected_valid=0;selected_reply=0;
  case(c_lane)
'''
 for i in range(16):new+=f"   4'd{i}:begin selected_ready=s_ready[{i}];selected_valid=s_rsp_valid[{i}];selected_reply=s_rsp_payload[{i*256}+:256];end\n"
 new+='''  endcase
 end
 assign c_ready=search_busy&&selected_ready;assign c_rsp_valid=search_busy&&selected_valid;assign c_rsp_payload=selected_reply;'''
 assert s.count(old)==1;return s.replace(old,new)
if __name__=='__main__':assert make()==(HERE/'search_host_fence.sv').read_text()
