from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/route_commit_join_v1/tb_route_join.sv').read_text()
 s=s.replace('if(fault)$fatal(1,"join fault','if(fault&&!armed)$fatal(1,"join fault')
 s=s.replace('.admit(!busy&&','.admit(!fault&&!busy&&')
 s=s.replace('module tb_candidate_offer;','module tb_candidate_offer;\ninteger fault_case=0,armed=0,injection_seen=0,owner_b_start=0,owner_r_start=0,label_r_start=0;reg injected_abort=0,injected_drift=0;')
 s=s.replace(".abort(1'b0),.active(p_active)",".abort(injected_abort),.active(p_active)")
 s=s.replace('.abort(injected_abort),.active(p_active)', '.abort(injected_abort),.active(p_active),.backend_drained(label_drained&&owner_drained)')
 monitors='' 
 for prefix,tag in [('p_m','label'),('owner_m','owner')]:
  connections=','.join('.'+field+'('+prefix+'_'+field+')'for field in ['arvalid','arready','arlen','rvalid','rready','rlast','awvalid','awready','awlen','wvalid','wready','wlast','bvalid','bready'])
  monitors+='axi_drain_watch '+tag+'_watch(.clk(clk),.rst(rst),'+connections+',.drained('+tag+'_drained),.fault('+tag+'_watch_fault));\n'
 s=s.replace('reg injected_abort=0,injected_drift=0;', 'reg injected_abort=0,injected_drift=0;wire label_drained,owner_drained,label_watch_fault,owner_watch_fault;')
 s=s.replace('route_commit_host_adapter #',monitors+'route_commit_host_adapter #',1)
 s=s.replace('.active_version(query_version),.active_design(design_id)',".active_version(query_version^(injected_drift?32'd1:32'd0)),.active_design(design_id)")
 for name,r,b in [('mem_owner(',"armed&&fault_case==5","armed&&fault_case==1"),('mem_p(',"armed&&fault_case==2","1'b0")]:
  a=s.index(name);e=s.index(');',a);part=s[a:e];part=part.replace(".inject_r(1'b0)",'.inject_r('+r+')').replace(".inject_b(1'b0)",'.inject_b('+b+')');s=s[:a]+part+s[e:]
 # The successful route task is replaced by an explicit failed operation/check.
 a=s.index('task route_command(');b=s.index('initial begin\n trace=$fopen',a)
 s=s[:a]+'''always @(posedge clk)if(!rst&&armed)begin
 if((fault_case==3||fault_case==4)&&!injection_seen&&((owner_m_awvalid&&owner_m_awready)||(owner_m_wvalid&&owner_m_wready)))begin
  injection_seen<=1;if(fault_case==3)injected_abort<=1;else injected_drift<=1;
  $fdisplay(trace,"FI %0d %0d",cycles,fault_case);
 end
 if((fault_case==1&&owner_m_bvalid&&owner_m_bready)||(fault_case==5&&owner_m_rvalid&&owner_m_rready)||(fault_case==2&&p_m_rvalid&&p_m_rready))begin
  injection_seen<=1;$fdisplay(trace,"FI %0d %0d",cycles,fault_case);
 end
end
'''+s[b:]
 a=s.index(' for(query_index=0;');s=s[:a]+'''
 control(1); // Durable import complete before arming any fault.
 if(!$value$plusargs("faultcase=%d",fault_case)||fault_case<1||fault_case>5)$fatal(1,"faultcase");
 owner_b_start=mem_owner.bresponses;owner_r_start=mem_owner.rbeats;label_r_start=mem_p.rbeats;armed=1;
 @(negedge clk);rc_req_op=0;rc_req_slot=0;rc_req_sink=150697;rc_req_sequence=1;rc_req_cookie=32'hfabcd001;rc_req_valid=1;
 do @(posedge clk);while(!rc_req_ready);@(negedge clk);rc_req_valid=0;
 host_ctrl_valid=1;host_io_valid=1;host_owner_req_valid=1;host_design_req_valid=1;expand_valid=1;seed_valid=1;
 q_cfg_valid=1;g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;
 wait(rc_rsp_valid);@(negedge clk);
 if(!injection_seen||!rc_fault||!rc_block||rc_slots!=0||label_watch_fault||owner_watch_fault)$fatal(1,"fault not contained");
 if(rc_rsp_cookie!=32'hfabcd001||rc_rsp_status!=(fault_case==2?4:(fault_case==3||fault_case==4)?6:5)||rc_rsp_acked!=((fault_case==3||fault_case==4)?1:0))$fatal(1,"fault result status=%0d ack=%0d",rc_rsp_status,rc_rsp_acked);
 if(mem_owner.rp||mem_owner.wp||mem_owner.rvalid||mem_owner.bvalid||mem_p.rp||mem_p.wp||mem_p.rvalid||mem_p.bvalid||route_join.l_valid||route_join.o_valid||b_l_rsp_valid||b_o_rsp_valid)$fatal(1,"completion before physical drain");
 $fdisplay(trace,"FC %0d %0d %0d %0d %0d %0d %0d",cycles,fault_case,rc_rsp_status,rc_rsp_acked,mem_owner.bresponses-owner_b_start,mem_owner.rbeats-owner_r_start,mem_p.rbeats-label_r_start);
 repeat(7)begin @(negedge clk);if(!rc_rsp_valid||!rc_block||rc_req_ready||rc_rsp_status!=(fault_case==2?4:(fault_case==3||fault_case==4)?6:5))$fatal(1,"held fault response");end
 rc_rsp_ready=1;@(negedge clk);rc_rsp_ready=0;
 repeat(32)begin @(negedge clk);if(!rc_block||!rc_fault||rc_req_ready||host_io_ready||host_owner_req_ready||host_ctrl_ready||expand_ready||seed_ready)$fatal(1,"fault fence released");end
 $fflush(trace);$fclose(trace);
 $display("ROUTE_FAULT_PASS case=%0d status=%0d acked=%0d owner_B=%0d owner_R=%0d label_R=%0d cycles=%0d",fault_case,rc_rsp_status,rc_rsp_acked,mem_owner.bresponses-owner_b_start,mem_owner.rbeats-owner_r_start,mem_p.rbeats-label_r_start,cycles);$finish;
end
endmodule
'''
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_route_fault.sv').write_text(make())
