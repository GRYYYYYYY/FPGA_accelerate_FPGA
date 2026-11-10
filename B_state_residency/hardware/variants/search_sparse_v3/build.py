from pathlib import Path
HERE=Path(__file__).parent

def make():
 s=(HERE.parent/'search_static_v2/search_host_fence.sv').read_text()
 s=s.replace(' wire host_open=', ' wire scheduler_lane=c_lane==6||c_lane==8||c_lane==11||c_lane==12;\n wire host_open=')
 s=s.replace('c_ready=search_busy&&selected_ready','c_ready=search_busy&&scheduler_lane&&selected_ready').replace('c_rsp_valid=search_busy&&selected_valid','c_rsp_valid=search_busy&&scheduler_lane&&selected_valid')
 old='''  assign s_valid[i]=search_busy?(c_valid&&c_lane==i):(host_open&&h_valid[i]);
  assign s_payload[i*2432+:2432]=search_busy?{1984'd0,c_payload}:h_payload[i*2432+:2432];
  assign s_rsp_ready[i]=search_busy?(c_rsp_ready&&c_lane==i):(host_open&&h_rsp_ready[i]);'''
 new='''  if(i==6||i==8||i==11||i==12)begin:search_service
   assign s_valid[i]=search_busy?(c_valid&&c_lane==i):(host_open&&h_valid[i]);
   assign s_payload[i*2432+:2432]=search_busy?{1984'd0,c_payload}:h_payload[i*2432+:2432];
   assign s_rsp_ready[i]=search_busy?(c_rsp_ready&&c_lane==i):(host_open&&h_rsp_ready[i]);
  end else begin:host_service
   // No search request or reply ownership exists on these lanes.
   // Payload is irrelevant while VALID=0; host functionality is unchanged.
   assign s_valid[i]=host_open&&h_valid[i];
   assign s_payload[i*2432+:2432]=h_payload[i*2432+:2432];
   assign s_rsp_ready[i]=host_open&&h_rsp_ready[i];
  end'''
 assert s.count(old)==1;return s.replace(old,new)
if __name__=='__main__':(HERE/'search_host_fence.sv').write_text(make())
