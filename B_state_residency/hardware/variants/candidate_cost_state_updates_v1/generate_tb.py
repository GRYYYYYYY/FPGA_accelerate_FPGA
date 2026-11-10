from pathlib import Path
HERE=Path(__file__).resolve().parent
base=(HERE.parent/'candidate_cost_state_v1/tb_candidate_cost_state.sv').read_text()
prefix=base.split(' initial begin\n  rst=1;',1)[0].replace('module tb_candidate_cost_state;','module tb_candidate_cost_state_updates;\nreg allow_fault=0,inject_cost_r=0,inject_cost_b=0,hold_cost_ar=0;wire raw_cost_arready;reg[80:0]held_cost_ar;integer mode=0;reg[31:0]write_value=0;reg edited_history=0,edited_price=0;')
prefix=prefix.replace('if(fault)$fatal','if(fault&&!allow_fault)$fatal')
prefix=prefix.replace('.arvalid(cs_m_arvalid)','.arvalid(cs_m_arvalid&&!hold_cost_ar)').replace('.arready(cs_m_arready)','.arready(raw_cost_arready)')
# Change only the cost memory model's injections.
i=prefix.index('))mem_cs(');j=prefix.index('\n);',i);block=prefix[i:j].replace(".inject_r(1'b0)",'.inject_r(inject_cost_r)').replace(".inject_b(1'b0)",'.inject_b(inject_cost_b)');prefix=prefix[:i]+block+prefix[j:]
prefix=prefix.replace('cs_req_value=0;','cs_req_value=write_value;')
prefix=prefix.replace('if(cs_rsp_data!==expected_cost)', "if(op==0&&index==0&&edited_history)expected_cost=128'h40000000;\n    if(op==2&&index==0&&edited_price)expected_cost=128'h3fc00000;\n    if(cs_rsp_data!==expected_cost)")
setup=base.split(' initial begin\n',1)[1].split('  while(!$feof(fd)',1)[0]
setup=setup.replace('  rst=1;', '  rst=1;rc=$value$plusargs("mode=%d",mode);allow_fault=mode==3||mode==4;')
setup=setup.replace('  repeat(5)@(negedge clk);rst=0;', "  if(mode==3)cs_cfg_nodes=32;\n  if(mode==4)cs_cfg_design_id=64'hbad;\n  repeat(5)@(negedge clk);rst=0;")
s=prefix+(HERE/'tasks.inc').read_text()+' initial begin\n'+setup+(HERE/'scenarios.inc').read_text()+'\n end\nassign cs_m_arready=raw_cost_arready&&!hold_cost_ar;\nendmodule\n'
(HERE/'tb_candidate_cost_state_updates.sv').write_text(s)
