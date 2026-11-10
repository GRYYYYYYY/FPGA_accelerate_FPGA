 task ck(input bit ok,input string message);begin if(!ok)$fatal(1,"%s mode=%0d",message,mode);end endtask
 task cs_error(input integer status);
  begin
   wait(cs_rsp_valid);@(negedge clk);ck(cs_rsp_status==status,"cost error status");repeat(3)@(negedge clk);cs_rsp_ready=1;@(negedge clk);cs_rsp_ready=0;
  end
 endtask
 task empty_expand;
  begin
   @(negedge clk);nchildren=0;raw_seen=0;expand_cookie=900;expand_parent=0;expand_sink=0;expand_net=0;expand_sequence=11;expand_flags=0;expand_prune=0;expand_has_laguna=0;expand_version=cs_published_version;expand_valid=1;
   wait(expand_ready);@(posedge clk);@(negedge clk);expand_valid=0;
   wait(result_valid);@(negedge clk);ck(result_status==0&&result_count==0&&result_expanded_count==0&&result_raw_count==0,"empty expansion");
  end
 endtask
 task retire_core;
  begin @(negedge clk);result_ready=1;@(negedge clk);result_ready=0;end
 endtask
 task stopped_check;
  begin
   repeat(4)@(negedge clk);ck(fault&&!query_ready&&!expand_ready&&!cs_req_ready,"stopped admission");
  end
 endtask
