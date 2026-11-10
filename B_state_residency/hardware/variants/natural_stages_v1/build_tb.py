"""Read-only probes; original natural TB and production RTL remain unchanged."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/natural_query_v1/tb_natural_query.sv').read_text()
 assert s.endswith('endmodule\n')
 observer=r'''
integer stage_fd;reg old_qm=0,old_pf=0,old_po=0,old_k=0,old_lc=0,old_of=0;
initial begin stage_fd=$fopen("stage_trace.txt","w");if(!stage_fd)$fatal(1,"stage trace open");end
always @(posedge clk)begin
 if(rst)begin old_qm<=0;old_pf<=0;old_po<=0;old_k<=0;old_lc<=0;old_of<=0;end
 else begin
  old_qm<=dut.q_meta_valid;old_pf<=out_prep_valid;old_po<=out_post_valid;old_k<=out_cost_valid;old_lc<=out_commit_valid;old_of<=out_offer_valid;
  if(expand_valid&&expand_ready)$fdisplay(stage_fd,"X %0d %0d %0d",cycles,expand_cookie,expand_parent);
  if(dut.q_pending&&dut.q_req_ready)$fdisplay(stage_fd,"Q0 %0d %0d %0d",cycles,dut.q_cookie,dut.q_connection);
  if(dut.q_rsp_valid)$fdisplay(stage_fd,"Q1 %0d %0d %0d",cycles,dut.q_cookie,dut.q_connection);
  if(dut.q_meta_valid&&!old_qm)$fdisplay(stage_fd,"QM %0d %0d %0d",cycles,dut.q_cookie,dut.q_connection);
  if(dut.core.m_rsp_valid&&dut.core.m_rsp_ready)$fdisplay(stage_fd,"MR %0d %0d %0d",cycles,dut.core.m_rsp_cookie,dut.core.m_rsp_child);
  if(dut.raw_out_valid&&!dut.raw_seen)$fdisplay(stage_fd,"D %0d %0d %0d %0d",cycles,dut.held_parent,out_node,out_action);
  if(dut.raw_seen&&dut.raw_out_valid&&out_action!=0&&!dut.prep_started&&dut.prefetch_ready)$fdisplay(stage_fd,"PF0 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(out_prep_valid&&!old_pf)$fdisplay(stage_fd,"PF1 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(dut.post_req_valid&&dut.post_req_ready)$fdisplay(stage_fd,"PO0 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(out_post_valid&&!old_po)$fdisplay(stage_fd,"PO1 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(dut.k_req_valid&&dut.k_ready)$fdisplay(stage_fd,"K0 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(out_cost_valid&&!old_k)$fdisplay(stage_fd,"K1 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(dut.commit_req_valid&&dut.commit_ready)$fdisplay(stage_fd,"LC0 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(out_commit_valid&&!old_lc)$fdisplay(stage_fd,"LC1 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(dut.offer_req_valid&&dut.offer_ready)$fdisplay(stage_fd,"OF0 %0d %0d %0d",cycles,dut.held_parent,out_node);
  if(out_offer_valid&&!old_of)$fdisplay(stage_fd,"OF1 %0d %0d %0d",cycles,dut.held_parent,out_node);
  $fflush(stage_fd);
 end
end
'''
 return s[:-len('endmodule\n')]+observer+'endmodule\n'
if __name__=='__main__':Path(__file__).with_name('tb_natural_stages.sv').write_text(make())
