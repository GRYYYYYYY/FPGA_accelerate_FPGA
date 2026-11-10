from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/authority_recovery_v2/sources/tb_authority_recovery.sv')
def make():
 s=BASE.read_text().replace('cycles>2000000','cycles>100000');s=s.replace('recovery_coordinator coordinator(',"recovery_coordinator coordinator(.cfg_stage(1'b0),.publish_valid(1'b0),.publish_permit(1'b0),.discard_valid(1'b0),")
 s=s.replace('dirty=0,cycles=0,','dirty=0,steps=0,seen_key=0,expected_failure=0,cycles=0,')
 a=s.index(' while(!$feof(fd))begin');b=s.index(' if(journal_count!=dirty',a)
 s=s[:a]+''' if($value$plusargs("expectfailure=%d",expected_failure))begin end
 while(!$feof(fd))begin
  rc=$fscanf(fd,"%d %d %d %d %d %d %d %d\\n",idx,node,net,operation,before_ref,before_occ,after_ref,after_occ);if(rc!=8||idx!=steps||(operation!=1&&operation!=2))$fatal(1,"mutation record");
  seen_key=0;for(integer x=0;x<dirty;x=x+1)if(mn[x]==node&&mt[x]==net)seen_key=1;
  if(!seen_key)begin mn[dirty]=node;mt[dirty]=net;mr[dirty]=before_ref;mo[dirty]=2;dirty=dirty+1;end
  @(negedge clk);j_node=node;j_net=net;j_op=operation;j_valid=1;do @(posedge clk);while(!j_ready);@(negedge clk);j_valid=0;
  host_op(operation,node,net,after_ref,after_occ);steps=steps+1;
 end
'''+s[b:]
 a=s.index(' k_version=5;');b=s.index(' if(k_fault||fault||!permit_work',a)
 s=s[:a]+''' k_version=5;k_query=3;k_cookie=k_cookie+256;request_recovery;
 if(expected_failure)begin
  k_result(3,0,dirty);if(!k_fault||permit_work||journal_count!=3)$fatal(1,"capacity failure lost isolation/journal");
  $fflush(events);$fclose(events);$display("MULTI_OWNER_CAPACITY_REPRO steps=%0d dirty=%0d",steps,dirty);$finish;
 end
 k_result(0,4,0);
'''+s[b:]
 s=s.replace('"AUTHORITY_RECOVERY_PASS dirty=%0d', '"MULTI_OWNER_RECOVERY_PASS dirty=%0d')
 s=s.replace('endmodule', 'initial begin #10000;$display("MULTI_DEBUG rst=%b cfg=%b/%b configured=%b authority=%0d live=%b/%0d drained=%b retired=%b kcfg=%b/%b kstate=%0d kfault=%b krsp=%b/%b kconf=%b dirty=%0d j=%b/%b steps=%0d",rst,cfg_valid,cfg_ready,configured,dut.state,l_configured,live_store.state,both_drained,retired,k_cfg_valid,k_cfg_ready,coordinator.state,k_fault,k_cfg_rsp_valid,k_cfg_rsp_ready,coordinator.configured,dirty,j_valid,j_ready,steps);$fflush(events);end\nendmodule')
 return s
if __name__=='__main__':(HERE/'tb_multi_owner.sv').write_text(make())
