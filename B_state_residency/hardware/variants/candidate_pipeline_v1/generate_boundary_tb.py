from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'tb_candidate.sv').read_text().replace('module tb_candidate;','module tb_candidate_boundary;')
s=s.replace('module tb_candidate_boundary;', 'module tb_candidate_boundary;\n reg hold_graph_ar=0,inject_graph_r=0;wire graph_mem_arready;integer mode=0;reg[80:0]held_ar;')
s=s.replace('.arvalid(g_m_arvalid)', '.arvalid(g_m_arvalid&&!hold_graph_ar)',1).replace('.arready(g_m_arready)', '.arready(graph_mem_arready)',1).replace(".inject_r(1'b0)",'.inject_r(inject_graph_r)',1)
old='   if(fault)$fatal(1,"candidate fault cookie=%d k=%d e=%d m=%d a=%d gf=%b df=%b pf=%b of=%b",cookie,dut.controller.state,dut.expansion.state,dut.metadata.state,dut.access.controller.state,dut.g_fault,dut.d_fault,dut.p_fault,dut.o_fault);'
assert old in s;s=s.replace(old,'   // Fault is expected in this separate boundary harness.')
s=s.replace('  rst=1;','  rst=1;rc=$value$plusargs("mode=%d",mode);',1)
anchor='    for(k=0;k<acount;k=k+1)begin'
body='''    if(nchildren>0)begin
     // Gate the actual shared graph AXI AR before metadata's first graph fetch.
     wait(dut.controller.m_pending);@(negedge clk);hold_graph_ar=1;wait(g_m_arvalid);@(negedge clk);
     held_ar={g_m_araddr,g_m_arlen,g_m_arsize,g_m_arburst,g_m_arid};
     if(mode==0)begin
      abort=1;
      repeat(4)begin @(negedge clk);if(!g_m_arvalid||{g_m_araddr,g_m_arlen,g_m_arsize,g_m_arburst,g_m_arid}!==held_ar||g_m_arready)$fatal(1,"AR withdrawn/changed on abort");end
     end else inject_graph_r=1;
     hold_graph_ar=0;
     wait(result_valid);@(negedge clk);
     if(result_status!=4||!dut.stopped||!dut.operation_pending)$fatal(1,"boundary error result");
     held_final={result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early};
     wait(!dut.metadata.g_pending&&!dut.metadata.d_pending&&!dut.arb_g_busy&&!mem_g.rp&&!g_m_rvalid&&!g_m_arvalid);
     repeat(4)begin @(negedge clk);if(!result_valid||{result_status,result_cookie,result_count,result_expanded_count,result_raw_count,result_mask,result_hit,result_early}!==held_final||!dut.operation_pending)$fatal(1,"boundary result/lock stability");end
     if(mode==1&&!dut.g_fault)$fatal(1,"actual R error not latched");
     result_ready=1;@(negedge clk);result_ready=0;host_ctrl_valid=0;host_io_valid=0;host_design_req_valid=0;host_owner_req_valid=0;abort=0;inject_graph_r=0;
     repeat(3)@(negedge clk);
     if(dut.operation_pending||expand_ready||host_ctrl_ready||host_io_ready||host_design_req_ready||host_owner_req_ready||owner_writes)$fatal(1,"stopped admission or owner corruption");
     $display("CANDIDATE_BOUNDARY_PASS mode=%0d cookie=%0d graph_reads=%0d owner_writes=%0d cycles=%0d",mode,cookie,g_reads,owner_writes,cycles);$finish;
    end
'''
assert anchor in s;s=s.replace(anchor,body+anchor)
s=s.replace('endmodule','assign g_m_arready=graph_mem_arready&&!hold_graph_ar;\nendmodule')
(HERE/'tb_candidate_boundary.sv').write_text(s)
