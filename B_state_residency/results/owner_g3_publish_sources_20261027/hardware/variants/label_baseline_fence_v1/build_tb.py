from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=ROOT/'hardware/variants/label_baseline_system_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 s=s.replace('.READ_ONLY(1),.TAG("baseline")', '.READ_ONLY(1),.READ_DELAY(BASELINE_DELAY),.TAG("baseline")')
 s=s.replace('wire baseline_req_valid,', '''`ifdef BASE_ABORT_DELAY
localparam BASELINE_DELAY=48;
`else
localparam BASELINE_DELAY=0;
`endif
wire baseline_req_valid,''',1)
 s=s.replace('wire baseline_req_valid,', 'wire baseline_retired,baseline_physical,baseline_owned,baseline_guard_fault;\nwire baseline_req_valid,',1)
 s=s.replace(')system(.baseline_permit', ')system(.baseline_retired(baseline_retired),.baseline_permit',1)
 guard='''baseline_retirement_guard retirement(.clk(clk),.cold_rst(bench_rst),.reader_idle(baseline_idle),.cfg_valid(bcfg_valid),.req_valid(baseline_req_valid),.req_ready(baseline_req_ready),.rsp_valid(baseline_rsp_valid),.rsp_ready(baseline_rsp_ready),.arvalid(bv),.arready(by),.arlen(bl),.rvalid(brv),.rready(brr),.rlast(brlast),.retired(baseline_retired),.physical_drained(baseline_physical),.owned(baseline_owned),.fault(baseline_guard_fault));
'''
 s=s.replace('label_baseline_reader baseline(',guard+'label_baseline_reader baseline(',1)
 # Abort only the query; actual backend work and physical R must retire normally.
 s=s.replace('wait(qc_rsp_valid);@(negedge clk);\n if(qc_rsp_status', 'wait(qc_rsp_valid);@(negedge clk);\n if(baseline_abort_mode)baseline_abort_complete;\n if(qc_rsp_status',1)
 extra='''
reg baseline_abort_mode=0;integer baseline_delay_checks=0,baseline_fault_started=0,baseline_r_consumed=0,baseline_front_consumed=0;
initial begin baseline_abort_mode=$test$plusargs("baselineabort");end
always @(posedge clk)if(!bench_rst)begin
 if(brv&&brr)baseline_r_consumed=baseline_r_consumed+1;
 if(baseline_rsp_valid&&baseline_rsp_ready)baseline_front_consumed=baseline_front_consumed+1;
 if(baseline_guard_fault)$fatal(1,"baseline guard fault");
 if(baseline_fault_started&&baseline_r_consumed==0)begin
  baseline_delay_checks=baseline_delay_checks+1;
  if(baseline_retired||baseline_physical||f_all_drained||f_backend_idle||k_target_reset||pc_acquire_ready||k_rec_ready||qc_rsp_valid)begin $fdisplay(trace,"B_EARLY %0d %0d %0d %0d %0d %0d %0d",cycles,baseline_retired,baseline_physical,f_all_drained,f_backend_idle,k_target_reset,pc_acquire_ready);$fflush(trace);$fatal(1,"premature baseline retirement");end
  $fdisplay(trace,"BWAIT %0d %0d %0d %0d %0d %0d %0d",cycles,baseline_retired,baseline_physical,f_all_drained,f_backend_idle,k_target_reset,pc_acquire_ready);
 end
end
initial begin
 @(negedge bench_rst);if(baseline_abort_mode)begin
  do @(posedge clk);while(!(bv&&by));@(negedge clk);baseline_fault_started=1;qc_abort=1;pc_acquire_valid=1;
  $fdisplay(trace,"B_ABORT %0d",cycles);
 end
end
task baseline_abort_complete;begin
 if(!baseline_fault_started||baseline_delay_checks<32||baseline_r_consumed!=1||baseline_front_consumed!=1||qc_rsp_status!=7||qc_rsp_committed||qc_prepare_acked!=0||!baseline_retired||k_target_reset||pc_owned)$fatal(1,"baseline abort final status%0d ack%0d wait%0d",qc_rsp_status,qc_prepare_acked,baseline_delay_checks);
 repeat(8)begin @(negedge clk);if(!qc_rsp_valid||qc_rsp_status!=7||!baseline_retired||k_target_reset||pc_acquire_ready)$fatal(1,"baseline abort held reply");end
 $fdisplay(trace,"BASELINE_ABORT_PASS %0d %0d %0d %0d %0d",cycles,baseline_delay_checks,baseline_r_consumed,baseline_front_consumed,qc_rsp_status);
 $fflush(trace);$fclose(trace);$display("BASELINE_ABORT_PASS");$finish;
end endtask
'''
 # Declare the abort variables before their first task use, after original clocks exist.
 return s.replace('baseline_retirement_guard retirement(',extra+'\nbaseline_retirement_guard retirement(',1)
if __name__=='__main__':(HERE/'tb_pair.sv').write_text(make())
