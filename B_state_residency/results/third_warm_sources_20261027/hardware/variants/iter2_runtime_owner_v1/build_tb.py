from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'iter2_g2_warm_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 s=s.replace('.jp_manifest_ready(1\'b1)', '.jp_manifest_ready(snap_manifest)')
 s=s.replace('.pc_release_valid(pc_release_valid)', '.pc_release_valid(snap_root_release_valid)').replace('.pc_release_ready(pc_release_ready)', '.pc_release_ready(raw_pc_release_ready)')
 marker='task iter2_publish_g2;reg[1:0]accepted;begin\n @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;'
 assert s.count(marker)==1;s=s.replace(marker,marker+'\n runtime_owner_snapshot;')
 extra='''
reg snap_cmd=0,snap_rsp_ready=0;wire snap_ready,snap_busy,snap_rsp,snap_receipt,raw_pc_release_ready,snap_root_release_valid,snap_manifest;wire[3:0]snap_status;wire[31:0]snap_cookie,snap_dirty,snap_verified;
wire[63:0]copy_araddr,copy_awaddr;wire copy_arvalid,copy_arready,copy_rvalid,copy_rready,copy_rlast,copy_awvalid,copy_awready,copy_wvalid,copy_wready,copy_bvalid,copy_bready;wire[511:0]copy_rdata,copy_wdata;wire[3:0]copy_rid,copy_bid;wire[1:0]copy_rresp,copy_bresp;
assign pc_release_ready=raw_pc_release_ready&&!snap_busy;
owner_snapshot_checkpoint_adapter #(.MAX_DIRTY(64)) snapshot_writer(
 .host_release_valid(pc_release_valid),.root_release_ready(raw_pc_release_ready),.host_release_ready(pc_release_ready),.root_release_valid(snap_root_release_valid),.manifest_ready(snap_manifest),
 .clk(clk),.rst(k_cold_rst),.lease(pc_owned),.source_drained(f_all_drained&&f_backend_idle&&f_normal_retired),
 .obs_awvalid(owner_m_awvalid),.obs_awready(owner_m_awready),.obs_awaddr(owner_m_awaddr),.obs_awlen(owner_m_awlen),.obs_bvalid(owner_m_bvalid),.obs_bready(owner_m_bready),.obs_bresp(owner_m_bresp),
 .cmd_valid(snap_cmd),.cmd_ready(snap_ready),.source_base(64'h61fffff000),.destination_base(64'ha000000000),.span_bytes(64'd146284032),.cmd_cookie(32'h5a000018),.busy(snap_busy),.rsp_valid(snap_rsp),.rsp_ready(snap_rsp_ready),.status(snap_status),.rsp_cookie(snap_cookie),.receipt_valid(snap_receipt),.dirty_count(snap_dirty),.verified_count(snap_verified),
 .m_araddr(copy_araddr),.m_arvalid(copy_arvalid),.m_arready(copy_arready),.m_rdata(copy_rdata),.m_rid(copy_rid),.m_rresp(copy_rresp),.m_rlast(copy_rlast),.m_rvalid(copy_rvalid),.m_rready(copy_rready),
 .m_awaddr(copy_awaddr),.m_awvalid(copy_awvalid),.m_awready(copy_awready),.m_wdata(copy_wdata),.m_wvalid(copy_wvalid),.m_wready(copy_wready),.m_bid(copy_bid),.m_bresp(copy_bresp),.m_bvalid(copy_bvalid),.m_bready(copy_bready));
axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(0),.MAX_BEATS(1),.SECONDARY_WRITABLE(1),.TAG("copy")) snapshot_copy_memory(
 .clk(clk),.rst(k_cold_rst),.base0(64'h61fffff000),.base1(64'ha000000000),.base2(64'd0),.size0(64'd146284032),.size1(64'd146284032),.size2(64'd0),.inject_r(1'b0),.inject_b(1'b0),
 .araddr(copy_araddr),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(copy_arvalid),.arready(copy_arready),.rdata(copy_rdata),.rid(copy_rid),.rresp(copy_rresp),.rlast(copy_rlast),.rvalid(copy_rvalid),.rready(copy_rready),
 .awaddr(copy_awaddr),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(copy_awvalid),.awready(copy_awready),.wdata(copy_wdata),.wstrb(64'hffffffffffffffff),.wlast(1'b1),.wvalid(copy_wvalid),.wready(copy_wready),.bid(copy_bid),.bresp(copy_bresp),.bvalid(copy_bvalid),.bready(copy_bready));
task runtime_owner_snapshot;begin
 if(!pc_owned||snap_receipt||snap_dirty!=4)$fatal(1,"runtime snapshot prefix");
 $fdisplay(trace,"RUNTIME_OWNER_START %0d %0d",cycles,snap_dirty);
 snap_cmd=1;do @(posedge clk);while(!snap_ready);@(negedge clk);snap_cmd=0;
 wait(snap_rsp);repeat(8)begin @(negedge clk);if(snap_status||snap_cookie!=32'h5a000018||snap_verified!=4||snap_dirty!=4||!snap_receipt||pc_release_ready||!pc_owned)$fatal(1,"runtime snapshot held completion");end
 $fdisplay(trace,"RUNTIME_OWNER_COPIED %0d %0d %0d",cycles,snap_dirty,snap_verified);
 snap_rsp_ready=1;@(negedge clk);snap_rsp_ready=0;wait(!snap_busy);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(snap_busy&&(!pc_owned||pc_release_ready||owner_m_awvalid))$fatal(1,"runtime snapshot source lease");
 if(snap_cmd&&snap_ready)$fdisplay(trace,"RUNTIME_OWNER_ACCEPT %0d %0d",cycles,snap_dirty);
end
'''
 decl,logic=extra.split('assign pc_release_ready',1)
 s=s.replace('module tb_candidate_offer;','module tb_candidate_offer;\n'+decl,1)
 return s.replace('\nendmodule','\n'+logic.replace('=raw_pc_release_ready&&!snap_busy;','',1)+'\nendmodule')
if __name__=='__main__':HERE.joinpath('tb_runtime_owner.sv').write_text(make())
