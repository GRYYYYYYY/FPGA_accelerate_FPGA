integer f_last_progress=0;
integer f_conflict_cycles=0;
always @(posedge clk)if(!k_cold_rst)begin
 if(f_recovery_owned&&f_sv==16'hffff&&rc_req_valid)f_conflict_cycles<=f_conflict_cycles+1;
 if((|(f_dv&f_dr))||(|(f_drv&f_drr))||k_target_reset||f_broute_valid&&f_broute_ready||f_broute_rsp_valid&&f_broute_rsp_ready)f_last_progress<=cycles;
 if(cycles-f_last_progress>131072)$fatal(1,"fabric no progress phase=%0d drained=%b idle=%b center=%b prefetch=%b post=%b frontier=%b core=%b cc=%b",f_phase,f_all_drained,f_backend_idle,dut.center_retired_idle,dut.prefetch_retired_idle,dut.post_retired_idle,dut.frontier_retired_idle,dut.core_busy,cc_busy);
 if(f_fault||(|f_watch_fault))$fatal(1,"unified fabric/transport fault");
 if((f_recovery_owned||f_phase==4||f_phase==5)&&(f_sr!=0||rc_req_ready))$fatal(1,"recovery host/route admission leak");
 if(k_target_reset&&(!f_recovery_owned||!f_normal_retired))$fatal(1,"target reset outside retired ownership");
 for(integer fx=0;fx<16;fx=fx+1)begin
  if(f_sv[fx]&&f_sr[fx])$fdisplay(trace,"FS %0d %0d",cycles,fx);
  if(f_dv[fx]&&f_dr[fx])$fdisplay(trace,"FD %0d %0d %0d",cycles,f_phase,fx);
  if(f_drv[fx]&&f_drr[fx])$fdisplay(trace,"FB %0d %0d %0d",cycles,f_phase,fx);
 end
 if(rc_req_valid&&rc_req_ready)$fdisplay(trace,"FR %0d",cycles);
 if(k_rec_valid&&k_rec_ready)$fdisplay(trace,"FK %0d",cycles);
end
