from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
def coordinator():
 s=(ROOT/'hardware/variants/recovery_coordinator_v1/tb_recovery_coordinator.sv').read_text()
 s=s.replace('reg clk=0;', 'reg retry_safe=1;wire attempt_reset;integer attempt_resets=0;\n reg clk=0;')
 s=s.replace('if(cold_rst)begin a_rsp_valid', 'if(cold_rst)begin attempt_resets<=0;a_rsp_valid')
 s=s.replace('  else begin\n   if(held_a', '  else begin\n   if(attempt_reset)begin attempt_resets<=attempt_resets+1;abort<=0;if(journal_count==0||!retry_safe||!backend_drained||!normal_retired)$fatal(1,"unsafe/empty retry reset");$fdisplay(logfd,"SOFT %0d %0d %0d",mode,journal_count,new_version);end\n   if(held_a')
 s=s.replace('   if(a_rsp_valid&&a_rsp_ready)a_rsp_valid<=0;', '   if(a_rsp_valid&&a_rsp_ready)begin if($isunknown({a_rsp_design,a_rsp_checkpoint,a_rsp_cookie,a_status}))$fatal(1,"unknown authority reply");$fdisplay(logfd,"AD %0d %h %h %h",mode,a_rsp_design,saved_design,dut.a_design);a_rsp_valid<=0;end')
 s=s.replace('a_status<=0;a_rsp_cookie', 'if($isunknown(a_design))$fatal(1,"authority request design X saved=%h internal=%h",saved_design,dut.a_design);a_status<=0;a_rsp_cookie')
 s=s.replace('a_rsp_design<=a_design+(mode==19);', 'if(mode==19)a_rsp_design<=a_design+64\'d1;else a_rsp_design<=a_design;')
 s=s.replace('cold_rst=1;abort=0;cfg_valid=0;', 'cold_rst=1;retry_safe=1;abort=0;cfg_valid=0;')
 extra='''
  // Retry the same dirty journal without a cold reset or authority re-install.
  mode=5;init;install(0);dirty;request;retire(3,0);
  recover_query=3;request;retire(1,0); // version4 already consumed by failed attempt
  recover_version=5;recover_price=5;recover_query=2;request;retire(1,0);
  recover_query=1;request;retire(1,0); // current committed query identity
  recover_query=3;recover_checkpoint=18;request;retire(1,0);recover_checkpoint=17;
  recover_price=4;request;retire(1,0);recover_price=5;
  if(journal_count!=4||resets!=3||attempt_resets||!fault||permit_work)$fatal(1,"invalid retry discarded state");
  mode=0;retry_safe=0;abort=1;
  @(negedge clk);recover_cookie=recover_cookie+100;recover_valid=1;
  repeat(7)begin @(negedge clk);if(recover_ready||attempt_reset||journal_count!=4)$fatal(1,"retry before service retirement");end
  retry_safe=1;backend_drained=0;repeat(4)begin @(negedge clk);if(recover_ready||attempt_reset)$fatal(1,"retry before physical drain");end
  backend_drained=1;normal_retired=0;repeat(4)begin @(negedge clk);if(recover_ready||attempt_reset)$fatal(1,"retry before normal retirement");end
  normal_retired=1;a_rsp_valid=1;repeat(4)begin @(negedge clk);if(recover_ready||attempt_reset)$fatal(1,"retry admitted unexpected authority response");end
  a_rsp_valid=0;do @(posedge clk);while(!recover_ready);@(negedge clk);recover_valid=0;
  retire(0,5);if(journal_count||fault||!permit_work||resets!=6||attempt_resets!=1||new_version!=5||new_query!=3)$fatal(1,"journal preserving retry");
  for(i=0;i<2;i=i+1)for(j=0;j<2;j=j+1)if(current_refs[i][j]!=authority[i][j])$fatal(1,"retry authority mismatch");
  // Failed reply after a physical correction: reread actual refs, no blind inverse.
  mode=7;init;install(0);dirty;request;retire(3,1);
  mode=0;recover_version=5;recover_price=5;recover_query=3;request;retire(0,4);
  if(journal_count||attempt_resets!=1||resets!=6||!permit_work)$fatal(1,"partial repair retry");
  // Labels timeout occurs after all owner corrections; retry must not redo INC/DEC.
  mode=13;init;install(0);dirty;request;retire(6,5);
  mode=0;recover_version=5;recover_price=5;recover_query=3;request;retire(0,0);
  if(journal_count||attempt_resets!=1||resets!=6||!permit_work)$fatal(1,"labels retry");
'''
 s=s.replace('  $fflush(logfd);',extra+'\n  $fflush(logfd);')
 return s

def config():
 s=(ROOT/'hardware/variants/config_restore_v1/tb_config_restore.sv').read_text()
 s=s.replace('reg clk=0;', 'reg attempt_reset=0;reg[2303:0]saved_descriptor;\n reg clk=0;')
 s=s.replace('rst=1;mode=m;', 'rst=1;attempt_reset=0;mode=m;')
 task='''
 task soft_clear;begin
  @(negedge clk);attempt_reset=1;repeat(2)@(negedge clk);attempt_reset=0;
  if(fault||!dut.configured||dut.descriptor!==saved_descriptor||saved_design!=123||saved_checkpoint!=17)$fatal(1,"soft reset lost resident descriptor");
  for(integer x=0;x<6;x=x+1)accepts[x]=0;
 end endtask
'''
 s=s.replace(' initial begin\n  if(!$value$plusargs',task+'\n initial begin\n  if(!$value$plusargs')
 extra='''
  init(11);install(0);saved_descriptor=gold;request;
  wait(rsp_valid);@(negedge clk);attempt_reset=1;
  repeat(4)begin @(negedge clk);if(!rsp_valid||rsp_status!=2||!fault||dut.descriptor!==saved_descriptor)$fatal(1,"soft reset erased unretired reply");end
  attempt_reset=0;result(2,63);
  attempt_reset=1;backend_drained=0;repeat(4)begin @(negedge clk);if(!fault||start_ready)$fatal(1,"soft clear without drain");end
  backend_drained=1;normal_retired=0;repeat(4)begin @(negedge clk);if(!fault||start_ready)$fatal(1,"soft clear before retirement");end
  normal_retired=1;soft_clear;
  mode=0;start_cookie=500;start_version=5;start_price=5;request;result(0,63);
  soft_clear;if(dut.current_version!=5)$fatal(1,"soft clear rolled version back");
  start_cookie=501;request;result(1,0);
  soft_clear;start_cookie=502;start_version=6;start_price=6;request;result(0,63);
  init(12);install(0);saved_descriptor=gold;request;wait(cfg_valid[0]);@(negedge clk);attempt_reset=1;
  repeat(5)begin @(negedge clk);if(!cfg_valid[0]||rsp_valid||dut.descriptor!==saved_descriptor)$fatal(1,"active soft reset withdrew offer");end
  attempt_reset=0;permit_stalled=1;result(0,63);
'''
 s=s.replace('  $fflush(fd);',extra+'\n  $fflush(fd);')
 return s
if __name__=='__main__':
 (HERE/'tb_recovery_coordinator.sv').write_text(coordinator())
 (HERE/'tb_config_restore.sv').write_text(config())
