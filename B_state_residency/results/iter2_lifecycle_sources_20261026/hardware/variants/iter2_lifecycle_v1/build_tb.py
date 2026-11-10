"""Real iteration2 prepared data through current autonomous query + route lifecycle."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_retry_system_v2/sources/tb_query_fault.sv')
def make(minimal=False):
 s=BASE.read_text()
 s=s.replace('owner_cfg_capacity=0;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool;', 'owner_cfg_capacity=53734;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool+859776;')
 s=s.replace('.size0(64\'d145424256)', ".size0(64'd146284032)")
 s=s.replace(".as_cfg_capacity(32'd0)",".as_cfg_capacity(32'd53734)")
 s=s.replace(".as_cfg_allocator(jp_authority_stage?64'ha008aaff40:64'h9208aaef40)",".as_cfg_allocator(jp_authority_stage?64'ha008b81dc0:64'h9208b80dc0)")
 s=s.replace(".base2(64'h9208aaef40)",".base2(64'h9208b80dc0)").replace(".size1(64'd145424256)",".size1(64'd146284032)")
 a=s.index('axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot")) authority_memory(');b=s.index(');',a)
 part=s[a:b].replace(".size0(64'd145424192)",".size0(64'd146284032)").replace(".size2(64'd64)",".size2(64'd0)");s=s[:a]+part+s[b:]
 s=s.replace(".ap_checkpoint(32'd18)",".ap_checkpoint(32'd17)").replace('ap_rsp_checkpoint!=18','ap_rsp_checkpoint!=17').replace("ap_rsp_generation!=64'h100000002",'ap_rsp_generation!=generation')
 # The CPU full sequence is independent of storage version3/query1.
 s=s.replace('selected_sink=150697,selected_connection=16506,selected_sequence=1','selected_sink=204279,selected_connection=170782,selected_sequence=180327')
 s=s.replace("32'd65185","32'd66893").replace('qc_cmd_source=65185','qc_cmd_source=66893')
 s=s.replace("32'd2717","32'd26422").replace('host_owner_req_net=2717','host_owner_req_net=26422')
 s=s.replace("32'd295,32'd283,32'd46,32'd38,32'd260", "32'd291,32'd279,32'd31,32'd23,32'd260")
 s=s.replace('out_config[351:320]!=38||out_config[383:352]!=46||out_config[415:384]!=283||out_config[447:416]!=295', 'out_config[351:320]!=23||out_config[383:352]!=31||out_config[415:384]!=279||out_config[447:416]!=291')
 s=s.replace('qc_rsp_nodes!=6||qc_rsp_acked!=6','qc_rsp_nodes!=3||qc_rsp_acked!=3')
 s=s.replace('rc_rsp_nodes!=6||rc_rsp_acked!=6','rc_rsp_nodes!=3||rc_rsp_acked!=3')
 s=s.replace('ss_polls!=(query_index==0?73:43)||ss_expands!=(query_index==0?72:42)||ss_candidates!=(query_index==0?271:176)', 'ss_polls!=171||ss_expands!=170||ss_candidates!=849')
 a=s.index('initial begin\n trace=$fopen("natural_trace.txt"')
 init_end=s.index(' control(1);\n if(!$value$plusargs("faultcase',a)
 prefix=s[a:init_end]
 prefix=prefix.replace('import_i<328','import_i<822')
 b=s.index('\nend\n\ntask ap_get',init_end)
 s=s[:a]+prefix+''' control(1);
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 ap_get(208292,6632,64'h100000001,0,1,2);ap_get(208292,17601,64'h100000001,0,2,2);ap_get(558358,23916,64'h100000001,0,1,2);
 @(negedge clk);pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
 query_index=0;replayed=1;armed=0;
 autonomous_query;
 for(final_index=0;final_index<822;final_index=final_index+1)begin
  rc=$fscanf(finals_fd,"%d",final_node_id);if(rc!=1)$fatal(1,"iter2 final node");
  for(j=0;j<5;j=j+1)begin rc=$fscanf(finals_fd,"%h",word);if(rc!=1)$fatal(1,"iter2 final field");gold_final[j*32+:32]=word;end
  if(final_node_id==selected_sink)gold_final[159:128]=0;
  label_read(final_node_id);if(host_record!==gold_final)$fatal(1,"iter2 final label node=%0d",final_node_id);
  $fdisplay(trace,"Z %0d %0d %040h",cycles,final_node_id,host_record);
 end
 if(commits!=421||candidate_i!=849||expand_i!=170||poll_i!=171||count1!=3||k_count!=3||rc_slots!=1)$fatal(1,"iter2 query aggregate");
 stage_no=0;owner_op(0,339193,1,1);owner_op(0,558358,4,2);owner_op(0,265324,5,1);
 iter2_foreign_probe;
 stage_no=1;route_command(1,0,204279,180327);
 owner_op(0,339193,0,0);owner_op(0,558358,3,2);owner_op(0,265324,4,1);
 iter2_foreign_probe;
 if(rc_slots||k_count!=3||fault||qc_fault||ss_fault||k_fault||cf_fault||lr_fault||!f_all_drained||!f_backend_idle)$fatal(1,"iter2 ripup final state");
 iter2_sequence_reject;
 if(system.controller.last_sequence!=180327||system.controller.last_version!=3||p_active_query!=1||p_active_price!=3)$fatal(1,"iter2 full sequence and storage tags mixed");
 $fdisplay(trace,"ITER2_CONTEXT %0d %0d %0d %0d %0d",cycles,system.controller.last_sequence,system.controller.last_version,p_active_query,p_active_price);
 $fdisplay(trace,"ITER2_LIFECYCLE_PASS %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits);
 $fflush(trace);$fclose(trace);$display("ITER2_LIFECYCLE_PASS polls=%0d expands=%0d candidates=%0d costs=%0d",poll_i,expand_i,candidate_i,commits);$finish;
'''+s[b:]
 s=s.replace('$fatal(1,"autonomous expand identity")', '$fatal(1,"autonomous expand identity status=%0d cookie=%0d wanted=%0d payload=%h",system.inner.c_rsp_payload[3:0],system.inner.c_rsp_payload[35:4],100+expand_i,system.inner.c_rsp_payload)')
 # Warm-stream fixture belongs to a later experiment, never read it at startup.
 a=s.index('initial begin\n if(!$value$plusargs("warmimports=');b=s.index('\nend',a)+4
 s=s[:a]+s[b:]
 s=s.replace('task route_command(input integer op,slot,sink,sequence_id);begin','task route_command(input integer op,slot,sink,sequence_id);begin\n if(op<0||op>1)$fatal(1,"invalid route operation");')
 extra='''task iter2_foreign_probe;begin
 @(negedge clk);host_owner_req_op=0;host_owner_req_node=558358;host_owner_req_net=23916;host_owner_req_cookie=32'hef000001;host_owner_req_valid=1;
 do @(posedge clk);while(!host_owner_req_ready);@(negedge clk);host_owner_req_valid=0;
 wait(host_owner_rsp_valid);@(negedge clk);if(host_owner_rsp_status||host_owner_rsp_count!=1||host_owner_rsp_occupancy!=2)$fatal(1,"foreign net damaged");
 $fdisplay(trace,"ITER2_FOREIGN %0d %0d %0d",cycles,host_owner_rsp_count,host_owner_rsp_occupancy);host_owner_rsp_ready=1;@(negedge clk);host_owner_rsp_ready=0;
end endtask
'''
 extra+='''task iter2_sequence_reject;begin
 @(negedge clk);qc_cmd_cookie=32'hce000002;qc_cmd_source=66893;qc_cmd_key=0;qc_cmd_nodes=9089009;qc_cmd_max_polls=65536;qc_cmd_poll_cookie=32'hcf000002;qc_cmd_design=design_id;qc_cmd_query=1;qc_cmd_price=3;
 qc_cmd_expand={32'd3,32'd291,32'd279,32'd31,32'd23,32'd260,32'd180327,32'd26422,32'd204279,32'd0,32'd0,32'd0,32'd100,32'd170782};qc_cmd_slot=0;qc_cmd_route_cookie=32'hcf000003;
 qc_cmd_valid=1;do @(posedge clk);while(!qc_cmd_ready);@(negedge clk);qc_cmd_valid=0;
 wait(qc_rsp_valid);repeat(8)begin @(negedge clk);if(qc_rsp_status!=1||qc_rsp_committed||qc_prepare_acked||qc_cleanup_acked||qc_fault||ss_busy||rc_slots||k_count!=3)$fatal(1,"iter2 duplicate sequence admitted");end
 $fdisplay(trace,"ITER2_SEQUENCE_REJECT %0d %0d %0d %0d",cycles,qc_rsp_status,qc_prepare_acked,system.controller.last_sequence);
 qc_rsp_ready=1;@(negedge clk);qc_rsp_ready=0;wait(!qc_busy);
end endtask
'''
 s=s.replace('endmodule',extra+'endmodule')
 if minimal:
  s=s.replace('for(field_i=0;field_i<5;field_i=field_i+1)label_write(import_node,field_i,import_record[field_i*32+:32]);', 'if(import_node==66893||import_node==204279)for(field_i=0;field_i<5;field_i=field_i+1)label_write(import_node,field_i,import_record[field_i*32+:32]);')
  debug='always @(posedge clk)if(!rst)begin\n if(system.inner.backend.dut.core.expand_valid&&system.inner.backend.dut.core.expand_ready)$display("ITER2_DEBUG parent=%0d sink=%0d nodes=%0d prune=%0d laguna=%0d flags=%h invalid=%b",system.inner.backend.dut.core.expand_parent,system.inner.backend.dut.core.expand_sink,system.inner.backend.dut.core.held_g_nodes,system.inner.backend.dut.core.expand_prune,system.inner.backend.dut.core.expand_has_laguna,system.inner.backend.dut.core.expand_flags,system.inner.backend.dut.core.controller.invalid);\n if(system.inner.backend.dut.core.e_result_valid)$display("ITER2_DEBUG e_status=%0d",system.inner.backend.dut.core.e_result_status);\nend\n'
  s=s.replace('endmodule',debug+'endmodule')
 return s
if __name__=='__main__':(HERE/'tb_iter2.sv').write_text(make())
