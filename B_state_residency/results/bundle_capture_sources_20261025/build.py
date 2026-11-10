from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/query_checkpoint_join_v3/sources')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 s=(BASE/'query_residency_system.sv').read_text();at=s.index(')(\n')+3;s=s[:at]+'input wire[63:0]qc_cp_generation,\n'+s[at:]
 s=rep(s,'reg qc_reset_held,qc_pending,qc_import_held;', '''reg qc_reset_held,qc_pending,qc_import_held;reg[63:0]qc_generation_held;
wire[63:0]qc_requested_generation=qc_cp_restore||qc_cp_generation==0?as_bound_generation:qc_cp_generation;
wire[63:0]qc_image_generation=qc_cp_busy?qc_generation_held:((!qc_cp_restore&&qc_requested_generation<as_bound_generation)?64'd0:qc_requested_generation);''')
 s=rep(s,'qc_reset_held<=0;qc_pending<=0;qc_import_held<=0;', 'qc_generation_held<=0;qc_reset_held<=0;qc_pending<=0;qc_import_held<=0;')
 s=rep(s,'if(qc_cp_valid&&qc_cp_ready)begin qc_import_held<=qc_cp_restore;', 'if(qc_cp_valid&&qc_cp_ready)begin qc_generation_held<=qc_image_generation;qc_import_held<=qc_cp_restore;')
 s=rep(s,'.active_generation(as_bound_generation)', '.active_generation(qc_image_generation)')
 directory='expansion_20261024/pager/backend/backing_frame_directory_small.sv'
 d=(BASE/directory).read_text();trace="""
`ifdef BUNDLE_TRACE
 tb_directory_observer capture_trace(.clk(clk),.rst(rst),.cmd_valid(cmd_valid),.cmd_ready(cmd_ready),.rsp_valid(rsp_valid),.rsp_ready(rsp_ready),.cmd_op(cmd_op),.cmd_owner(cmd_owner),.cmd_frame({{(32-INDEX_BITS){1'b0}},cmd_frame}),.cmd_cookie(cmd_cookie),.memory_success(memory_success),.fence_retired(fence_retired),.rsp_status(rsp_status),.rsp_frame({{(32-INDEX_BITS){1'b0}},rsp_frame}),.rsp_published(rsp_published),.allocated({{(31-INDEX_BITS){1'b0}},allocated}),.leased(leased),.any_fault(any_fault));
`endif
"""
 d=rep(d,'endmodule',trace+'\nendmodule')
 return {'query_residency_system.sv':s,directory:d}
if __name__=='__main__':
 for n,s in make().items():
  p=HERE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
