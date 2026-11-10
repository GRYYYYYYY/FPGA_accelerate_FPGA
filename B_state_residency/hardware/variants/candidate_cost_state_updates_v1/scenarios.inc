  if(mode==3||mode==4)begin
   stopped_check();ck(!p_active&&!operation_pending&&cs_reads==0&&cs_writes==0,"configuration mismatch caused activity");
  end else if(mode==1)begin
   allow_fault=1;@(negedge clk);host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=3;host_ctrl_version=19;host_ctrl_valid=1;
   repeat(3)begin @(negedge clk);ck(!host_ctrl_ready,"stale OPEN accepted");end
   host_ctrl_valid=0;stopped_check();ck(!p_active&&!operation_pending&&!result_valid,"stale OPEN activated query");
  end else begin
   control(0,2,3);
   if(mode==0)begin
    // A host edit is rejected while the actual pager query is active.
    cs_start(1,4,0);cs_error(2);wait(!cs_busy);ck(!cs_editing&&cs_published_version==3&&!fault,"active-query edit rejection");
    control(2,2,3);cs_start(1,4,0);cs_finish(4,0);
    write_value=32'h40000000;cs_start(1,1,0);cs_finish(1,0);edited_history=1;
    write_value=32'h3fc00000;cs_start(1,3,0);cs_finish(3,0);edited_price=1;write_value=0;
    @(negedge clk);host_ctrl_op=0;host_ctrl_query=1;host_ctrl_price=4;host_ctrl_version=4;host_ctrl_valid=1;
    repeat(3)begin @(negedge clk);ck(!host_ctrl_ready&&!p_active,"query entered unpublished edits");end
    cs_start(1,5,0);cs_finish(5,0);wait(host_ctrl_ready);@(posedge clk);@(negedge clk);host_ctrl_valid=0;wait(host_ctrl_rsp_valid);@(negedge clk);ck(host_ctrl_status==0&&query_version==4,"published query OPEN");host_ctrl_rsp_ready=1;@(negedge clk);host_ctrl_rsp_ready=0;
    empty_expand();cs_get(0,0);cs_get(2,0);cs_get(6,0);
    // Retire the candidate while the last cost response still owns the lease.
    cs_start(0,0,0);retire_core();wait(cs_rsp_valid);@(negedge clk);
    host_ctrl_op=2;host_ctrl_query=1;host_ctrl_price=4;host_ctrl_version=4;host_ctrl_valid=1;host_io_valid=1;host_design_req_valid=1;host_owner_req_valid=1;
    repeat(3)begin @(negedge clk);ck(!operation_pending&&cost_lease&&!host_ctrl_ready&&!host_io_ready&&!host_design_req_ready&&!host_owner_req_ready,"lease gap after core retirement");end
    host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;cs_finish(0,0);wait(!cost_lease);control(2,1,4);
    // A second real pager query sees the same published values, not query defaults.
    control(0,2,4);empty_expand();cs_get(0,0);cs_get(2,0);retire_core();control(2,2,4);
    ck(cs_published_version==4&&!cs_editing&&!fault&&cs_writes==2,"update lifecycle");
   end else if(mode==2)begin
    allow_fault=1;@(negedge clk);expand_cookie=900;expand_parent=0;expand_sink=0;expand_net=0;expand_version=19;expand_valid=1;
    repeat(3)begin @(negedge clk);ck(!expand_ready,"stale expansion accepted");end
    expand_valid=0;stopped_check();ck(!operation_pending&&!result_valid&&g_reads==0&&d_reads==0&&cs_reads==0,"stale expansion side effects");
   end else if(mode==5)begin
    empty_expand();held_final={result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early};allow_fault=1;inject_cost_r=1;cs_start(0,0,0);wait(cs_rsp_valid);@(negedge clk);
    ck(cs_rsp_status==4&&fault,"actual cost R error propagation");ck({result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early}===held_final,"late error changed exposed core result");
    cs_error(4);retire_core();wait(!cs_busy&&!cost_lease);stopped_check();
   end else if(mode==6)begin
    control(2,2,3);cs_start(1,4,0);cs_finish(4,0);allow_fault=1;inject_cost_b=1;write_value=32'h40000000;cs_start(1,1,0);cs_error(4);wait(!cs_busy);stopped_check();
    ck(cs_editing&&cs_published_version==3&&!p_active&&cs_writes==1,"failed B published edit");
   end else if(mode==7)begin
    empty_expand();hold_cost_ar=1;cs_start(0,0,0);wait(cs_m_arvalid);@(negedge clk);held_cost_ar={cs_m_araddr,cs_m_arlen,cs_m_arsize,cs_m_arburst,cs_m_arid};allow_fault=1;abort=1;
    repeat(4)begin @(negedge clk);ck(cs_m_arvalid&&!cs_m_arready&&cost_lease&&{cs_m_araddr,cs_m_arlen,cs_m_arsize,cs_m_arburst,cs_m_arid}===held_cost_ar,"abort withdrew pending AR/lease");end
    cs_error(5);retire_core();ck(cs_busy&&cost_lease,"logical retirement lost physical lease");hold_cost_ar=0;abort=0;wait(!cs_busy&&!cost_lease);stopped_check();
   end else $fatal(1,"unknown mode");
  end
  ck(owner_writes==0,"owner mutation");
  $display("CANDIDATE_COST_UPDATE_PASS mode=%0d cs_calls=%0d cs_gets=%0d cost_reads=%0d cost_writes=%0d cost_bs=%0d graph_reads=%0d design_reads=%0d design_writes=%0d version=%0d cycles=%0d",mode,cs_calls,cs_gets,cs_reads,cs_writes,cs_bs,g_reads,d_reads,d_writes,cs_published_version,cycles);$finish;
