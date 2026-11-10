from pathlib import Path
import importlib.util
HERE=Path(__file__).parent

def make():
 p=HERE.parent/'residency_system_v1/build.py';sp=importlib.util.spec_from_file_location('parser',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 ports=m.ports(HERE/'search_scheduler.sv')
 shifted=['req_valid','req_ready','req_lane','req_payload','reply_valid','reply_ready','reply_payload']
 bind={n:('c_'+n if n in shifted else n)for n in ports};bind.update(abort='mode==9?lease_cancel:abort',admit='lease_admit')
 s=(HERE/'tb_search_scheduler.sv').read_text().replace('search_scheduler #(.MAX_CYCLES(200))dut(.*);','search_scheduler #(.MAX_CYCLES(200))dut('+','.join('.'+n+'('+v+')'for n,v in bind.items())+');')
 decl=''
 for n in shifted:
  _,w=ports[n];decl+='wire '+('['+str(w-1)+':0] 'if w>1 else '')+'c_'+n+';\n'
 decl+='''wire lease_admit,lease_cancel;wire[15:0]hv=busy?16'hffff:16'd0;wire[15:0]hr,hrv,sv,sr,srv,srr;
 wire[38911:0]sp;wire[4095:0]srp,hrp;wire route_ready,recover_ready,route_valid,recover_valid,out_consume;
 wire recover_intent=mode==9&&abort;
 assign req_valid=sv[c_req_lane];assign req_lane=c_req_lane;assign req_payload=sp[c_req_lane*2432+:448];assign reply_ready=srr[c_req_lane];
 generate for(genvar i=0;i<16;i=i+1)begin:fake_backend
  assign sr[i]=i==c_req_lane&&req_ready;assign srv[i]=i==c_req_lane&&reply_valid;
  assign srp[i*256+:256]=reply_payload;
 end endgenerate
 search_host_fence lease(.search_busy(busy),.search_fault(fault),.start_valid(start_valid),.system_admit(admit),
 .h_valid(hv),.h_ready(hr),.h_payload({38912{1'b1}}),.h_rsp_valid(hrv),.h_rsp_ready(16'hffff),.h_rsp_payload(hrp),
 .h_route_valid(busy),.h_route_ready(route_ready),.h_recover_valid(recover_intent),.h_recover_ready(recover_ready),.h_out_ready(1'b0),
 .s_valid(sv),.s_ready(sr),.s_payload(sp),.s_rsp_valid(srv),.s_rsp_ready(srr),.s_rsp_payload(srp),
 .s_route_valid(route_valid),.s_route_ready(1'b1),.s_recover_valid(recover_valid),.s_recover_ready(1'b1),.s_out_ready(out_consume),
 .c_valid(c_req_valid),.c_ready(c_req_ready),.c_lane(c_req_lane),.c_payload(c_req_payload),
 .c_rsp_valid(c_reply_valid),.c_rsp_ready(c_reply_ready),.c_rsp_payload(c_reply_payload),.c_candidate_ready(candidate_ready),.admit(lease_admit),.cancel(lease_cancel));
 always @(posedge clk)if(!rst&&busy)begin
  if(hr||hrv||route_ready||route_valid||recover_ready||recover_valid)$fatal(1,"query lease leaked host/recovery");
  if(sv!=(c_req_valid?(16'b1<<c_req_lane):16'b0))$fatal(1,"unexpected host acceptance");
  if(out_consume!=candidate_ready)$fatal(1,"candidate ownership");
 end
'''
 instance=s[s.index(' search_scheduler #'):s.index(' integer cycles=0')]
 s=s.replace(instance,'')
 s=s.replace('string path;','string path;\n'+decl+instance)
 s=s.replace('hold_request=0;finish(8);','''hold_request=0;finish(8);
  if(!recover_ready||!recover_valid||hr||route_ready||start_ready)$fatal(1,"recovery handoff after consumed completion");
  $fdisplay(events,"RECOVERY %0d",commands);''',1)
 return s
if __name__=='__main__':(HERE/'tb_search_lease.sv').write_text(make())
