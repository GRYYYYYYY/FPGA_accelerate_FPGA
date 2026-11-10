from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'iter2_runtime_owner_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 # Flush all live resident pages while ordinary admin control is still admitted.
 marker='task iter2_publish_g2;reg[1:0]accepted;begin\n'
 assert s.count(marker)==1;s=s.replace(marker,marker+' runtime_label_reject_unflushed;\n control(1);\n')
 s=s.replace(' runtime_owner_snapshot;',' runtime_owner_snapshot;\n runtime_label_snapshot;',1)
 s=s.replace('.RESTORE_RECORDS(1024))system(','.RESTORE_RECORDS(1024),.ENABLE_FRAME_SCAN(1))system('+'''.scan_valid(scan_v),.scan_ready(scan_r),.scan_permit(1'b1),.scan_frame(scan_f),.scan_rsp_valid(scan_rv),.scan_rsp_ready(scan_rr),.scan_status(scan_st),.scan_result_frame(scan_rf),.scan_owner(scan_o),.scan_published(scan_pub),''')
 s=s.replace('.pc_release_valid(snap_root_release_valid)', '.pc_release_valid(label_root_release)').replace('.host_release_ready(pc_release_ready)', '.host_release_ready(pc_release_ready)')
 s=s.replace('.root_release_ready(raw_pc_release_ready)', '.root_release_ready(label_gate_ready)')
 s=s.replace('.jp_manifest_ready(snap_manifest)', '.jp_manifest_ready(snap_manifest&&label_manifest)')
 s=s.replace(".snapshot_count(32'd822)",'.snapshot_count(ls_count)')
 s=s.replace('for(integer x=0;x<822;x=x+1)begin\n  rc=$fscanf(warm_fd', 'for(integer x=0;x<ls_count;x=x+1)begin\n  rc=$fscanf(warm_fd').replace('lr_s_last=x==821;', 'lr_s_last=x+1==ls_count;')
 decl='''
reg ls_cmd=0,ls_ack=0;wire ls_ready,ls_busy,ls_rsp,ls_receipt,label_root_release,label_gate_ready,label_manifest;wire[3:0]ls_status;wire[31:0]ls_cookie,ls_count,ls_crc,ls_pages;
wire scan_v,scan_r,scan_rv,scan_rr,scan_pub;wire[INDEX_BITS-1:0]scan_f,scan_rf;wire[2:0]scan_st;wire[26:0]scan_o;
wire[31:0]ls_ar;wire ls_av,ls_aq,ls_rv,ls_rr,ls_rl,ls_v;reg ls_r=0;wire[511:0]ls_data;wire[3:0]ls_id;wire[1:0]ls_resp;wire[31:0]ls_node;wire[159:0]ls_payload;integer ls_fd,ls_emitted=0;
'''
 at=s.index('`endif',s.index('localparam FRAMES=16384,INDEX_BITS=14,HASH_BITS=15;'))+len('`endif')
 s=s[:at]+'\n'+decl+s[at:]
 extra='''
label_snapshot_checkpoint_adapter #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS)) label_snapshot(
 .host_release_valid(snap_root_release_valid),.root_release_ready(raw_pc_release_ready),.host_release_ready(label_gate_ready),.root_release_valid(label_root_release),.manifest_ready(label_manifest),
 .clk(clk),.rst(k_cold_rst),.lease(pc_owned),.source_drained(f_all_drained&&f_backend_idle&&f_normal_retired),.cmd_valid(ls_cmd),.cmd_ready(ls_ready),.cmd_query(2'd1),.cmd_price(4'd3),.cmd_nodes(32'd9089009),.cmd_cookie(32'h1abe0018),.busy(ls_busy),.rsp_valid(ls_rsp),.rsp_ready(ls_ack),.status(ls_status),.rsp_cookie(ls_cookie),.record_count(ls_count),.record_crc(ls_crc),.page_count(ls_pages),.receipt_valid(ls_receipt),
 .scan_valid(scan_v),.scan_ready(scan_r),.scan_frame(scan_f),.scan_rsp_valid(scan_rv),.scan_rsp_ready(scan_rr),.scan_status(scan_st),.scan_result_frame(scan_rf),.scan_owner(scan_o),.scan_published(scan_pub),
 .m_araddr(ls_ar),.m_arvalid(ls_av),.m_arready(ls_aq),.m_rdata(ls_data),.m_rid(ls_id),.m_rresp(ls_resp),.m_rlast(ls_rl),.m_rvalid(ls_rv),.m_rready(ls_rr),.record_valid(ls_v),.record_ready(ls_r),.record_node(ls_node),.record_payload(ls_payload));
axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(1),.MAX_BEATS(1),.TAG("labelsnap")) label_snapshot_memory(
 .clk(clk),.rst(k_cold_rst),.base0(64'd0),.base1(64'd0),.base2(64'd0),.size0(64'd3145728),.size1(64'd0),.size2(64'd0),.inject_r(1'b0),.inject_b(1'b0),
 .araddr(ls_ar),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(ls_av),.arready(ls_aq),.rdata(ls_data),.rid(ls_id),.rresp(ls_resp),.rlast(ls_rl),.rvalid(ls_rv),.rready(ls_rr),
 .awaddr(32'd0),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(1'b0),.wdata(512'd0),.wstrb(64'd0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b0));
task runtime_label_reject_unflushed;begin
 @(negedge clk);pc_acquire_valid=1;do @(posedge clk);while(!pc_acquire_ready);@(negedge clk);pc_acquire_valid=0;
 $fdisplay(trace,"LABEL_UNFLUSHED_BEGIN %0d",cycles);
 ls_cmd=1;do @(posedge clk);while(!ls_ready);@(negedge clk);ls_cmd=0;ls_r=1;
 wait(ls_rsp);ls_r=0;repeat(6)begin @(negedge clk);if(ls_status!=3||ls_count||ls_pages||ls_receipt||pc_release_ready||!pc_owned)$fatal(1,"unflushed label snapshot admitted");end
 $fdisplay(trace,"LABEL_UNFLUSHED_REJECT %0d %0d",cycles,ls_status);
 ls_ack=1;@(negedge clk);ls_ack=0;wait(!ls_busy);
 pc_release_valid=1;do @(posedge clk);while(!pc_release_ready);@(negedge clk);pc_release_valid=0;wait(!pc_owned);
end endtask
task runtime_label_snapshot;begin
 if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"runtime label output path");ls_fd=$fopen(warm_path,"w");if(!ls_fd)$fatal(1,"runtime label output");
 $fdisplay(trace,"LABEL_SNAPSHOT_BEGIN %0d",cycles);
 ls_cmd=1;do @(posedge clk);while(!ls_ready);@(negedge clk);ls_cmd=0;ls_r=1;
 wait(ls_rsp);ls_r=0;
 repeat(8)begin @(negedge clk);if(ls_status||ls_cookie!=32'h1abe0018||ls_count!=822||ls_pages!=403||ls_emitted!=822||!ls_receipt||pc_release_ready||!pc_owned)$fatal(1,"runtime label snapshot status=%0d rows=%0d pages=%0d emitted=%0d",ls_status,ls_count,ls_pages,ls_emitted);end
 $fdisplay(trace,"LABEL_SNAPSHOT_DONE %0d %0d %0d %08h",cycles,ls_count,ls_pages,ls_crc);$fflush(ls_fd);$fclose(ls_fd);
 ls_ack=1;@(negedge clk);ls_ack=0;wait(!ls_busy);
end endtask
always @(posedge clk)if(!k_cold_rst)begin
 if(scan_v&&scan_r)$fdisplay(trace,"FRAME_SCAN_REQUEST %0d %0d",cycles,scan_f);
 if(scan_rv&&scan_rr)$fdisplay(trace,"FRAME_SCAN_REPLY %0d %0d %0d %07h %0d",cycles,scan_st,scan_rf,scan_o,scan_pub);
 if(ls_v&&ls_r)begin
  $fwrite(ls_fd,"%0d",ls_node);for(integer f=0;f<5;f=f+1)$fwrite(ls_fd," %08h",ls_payload[f*32+:32]);$fwrite(ls_fd,"\\n");
  $fdisplay(trace,"LABEL_SNAPSHOT_RECORD %0d %0d %040h",cycles,ls_node,ls_payload);ls_emitted<=ls_emitted+1;
 end
 if(ls_busy&&(!pc_owned||pc_release_ready||host_io_ready))$fatal(1,"runtime label lease");
end
'''
 return s.replace('\nendmodule',extra+'\nendmodule')
if __name__=='__main__':HERE.joinpath('tb_label_snapshot.sv').write_text(make())

def make_default(base):
 return runpy.run_path(str(base))['make']()
