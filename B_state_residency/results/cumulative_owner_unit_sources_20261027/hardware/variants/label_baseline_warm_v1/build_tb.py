from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'hardware/variants/label_source_crc_v1/build_tb.py'
PROVIDER=ROOT/'hardware/variants/label_baseline_fence_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 start=s.index(' for(import_i=0;import_i<822;');end=s.index('\n\n\n control(1);',start)
 s=s[:start]+' $fdisplay(trace,"BASELINE_NO_PRELOAD %0d",cycles);\n'+s[end:]
 for stop in [' if(commits!=421',' if(commits!=302']:
  start=s.index(' for(final_index=0;final_index<822;');end=s.index(stop,start);s=s[:start]+s[end:]
 s=s.replace(' if(!$value$plusargs("imports=%s",path))$fatal(1,"import path");imports_fd=$fopen(path,"r");','').replace('||!imports_fd','')
 s=s.replace(' control(0);\n $fdisplay(trace,"BASELINE_NO_PRELOAD', ' baseline_configure;control(0);\n $fdisplay(trace,"BASELINE_NO_PRELOAD',1)
 s=s.replace('query_residency_system #(', 'query_residency_system #(.ENABLE_BASELINE(1),',1)
 names=['baseline_retired','baseline_req_valid','baseline_req_ready','baseline_req_node','baseline_req_epoch','baseline_rsp_valid','baseline_rsp_ready','baseline_rsp_status','baseline_rsp_node','baseline_rsp_epoch','baseline_rsp_payload']
 ties=".baseline_permit(1'b1),.baseline_epoch(64'h300010003),"+''.join('.'+n+'('+n+'),'for n in names)
 s=s.replace(')system(',')system('+ties,1)
 provider=runpy.run_path(str(PROVIDER))['make']();a=provider.index('reg bcfg_valid=');b=provider.index('query_residency_system #(',a);extra=provider[a:b]
 a=extra.index('reg baseline_abort_mode=');b=extra.index('baseline_retirement_guard retirement(',a);extra=extra[:a]+extra[b:]
 s=s.replace('query_residency_system #(',extra+'\nquery_residency_system #(',1)
 s=s.replace(' runtime_label_reject_unflushed;', ' $fdisplay(trace,"DEMAND_LABEL_SOURCE %0d",cycles);',1)
 s=s.replace('lr_written!=822||lr_verified!=822','lr_written!=ls_count||lr_verified!=ls_count')
 s=s.replace('lr_written!=821','lr_written+1!=ls_count')
 s=s.replace('ls_count!=822||ls_pages!=403||ls_emitted!=822','ls_count==0||ls_pages==0||ls_emitted!=ls_count')
 s=s.replace(' iter2_next_query;\n $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS', ' iter2_next_query;control(1);\n $fdisplay(trace,"BASELINE_WARM_DONE %0d",cycles);\n $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS',1)
 # Guard must retain ownership across native recovery target reset.
 extra2='''
always @(posedge clk)if(!bench_rst)begin
 if(baseline_guard_fault)$fatal(1,"baseline guard fault");
 if(k_target_reset&&!baseline_retired)$fatal(1,"reset before baseline retirement");
 if(k_target_reset)$fdisplay(trace,"BASELINE_TARGET_RESET %0d %0d %0d %0d",cycles,baseline_retired,baseline_physical,baseline_owned);
 if(!baseline_retired&&(f_all_drained||f_backend_idle))$fatal(1,"baseline missing from full warm fence");
end
'''
 return s.replace('\nendmodule',extra2+'\nendmodule')
if __name__=='__main__':(HERE/'tb_warm.sv').write_text(make())
