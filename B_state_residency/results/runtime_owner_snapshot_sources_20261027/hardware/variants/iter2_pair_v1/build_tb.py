from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'iter2_continuous_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 s=s.replace(' $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS %0d",cycles);', ' iter2_next_query;\n $fdisplay(trace,"ITER2_CONTINUOUS_PREP_PASS %0d",cycles);')
 s=s.replace('ss_polls!=171||ss_expands!=170||ss_candidates!=849','ss_polls!=(query_index==0?171:114)||ss_expands!=(query_index==0?170:113)||ss_candidates!=(query_index==0?849:564)')
 extra='''
task iter2_next_query;begin
 $fdisplay(trace,"ITER2_NEXT_BEGIN %0d",cycles);
 $fclose(fd_gold);$fclose(candidates_fd);$fclose(polls_fd);$fclose(finals_fd);
 if(!$value$plusargs("cost2=%s",path))$fatal(1,"cost2");fd_gold=$fopen(path,"r");
 if(!$value$plusargs("candidates2=%s",path))$fatal(1,"candidates2");candidates_fd=$fopen(path,"r");
 if(!$value$plusargs("polls2=%s",path))$fatal(1,"polls2");polls_fd=$fopen(path,"r");
 if(!$value$plusargs("finals2=%s",path))$fatal(1,"finals2");finals_fd=$fopen(path,"r");
 if(!fd_gold||!candidates_fd||!polls_fd||!finals_fd)$fatal(1,"next oracle open");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;offers=0;outputs=0;physical_expands=0;metadata_calls=0;visited_reads=0;
 query_index=1;selected_sink=67922;selected_connection=170996;selected_sequence=180328;stopped=0;
 autonomous_query;
 for(final_index=0;final_index<822;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"next final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"next final word");gold_final[j*32+:32]=word;end
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"next final label node=%0d actual=%h expected=%h",final_node_id,host_record,gold_final);
  $fdisplay(trace,"Z2 %0d %0d %040h",cycles,final_node_id,host_record);
 end
 if(commits!=302||candidate_i!=564||expand_i!=113||poll_i!=114||rc_slots!=3||system.controller.last_sequence!=180328||system.controller.last_version!=3||p_active_query!=1||p_active_price!=3)$fatal(1,"next aggregate/context");
 stage_no=5;owner_op(0,339193,1,1);owner_op(0,990179,2,2);owner_op(0,558358,4,2);owner_op(0,265324,5,1);iter2_foreign_probe;
 $fdisplay(trace,"ITER2_PAIR_PASS %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits);$display("ITER2_PAIR_PASS polls=114 expands=113 candidates=564 costs=302");
end endtask
'''
 return s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':HERE.joinpath('tb_pair.sv').write_text(make())
