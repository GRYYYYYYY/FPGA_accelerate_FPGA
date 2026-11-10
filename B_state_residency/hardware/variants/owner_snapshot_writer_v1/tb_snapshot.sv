`timescale 1ns/1ps
module tb_snapshot;
reg clk=0;always #5 clk=~clk;
reg rst=1,lease=1,drained=1,ov=0,ob=0;reg[63:0]oa=0;reg[7:0]ol=0;reg[1:0]obr=0;
reg cmd=0,ready_rsp=0;wire ready,busy,rsp,receipt;wire[3:0]status;wire[31:0]cookie,dirty,verified;
reg[63:0]src=64'h1000,dst=64'h4000,span=512;reg[31:0]nonce=32'h12345678;
wire[63:0]ar,aw;wire arv,arr,rv,rr,rl,awv,awr,wv,wr,bv,br;wire[511:0]rd,wd;wire[3:0]rid,bid;wire[1:0]rresp,bresp;reg injr=0,injb=0;
wire gate_release,gate_ready,manifest;
integer reads,writes,rbeats,wbeats,bs,checks=0,start_reads,start_writes,start_bs;
owner_snapshot_checkpoint_adapter #(.MAX_DIRTY(4)) dut(.host_release_valid(1'b1),.root_release_ready(1'b1),.host_release_ready(gate_ready),.root_release_valid(gate_release),.manifest_ready(manifest),.clk(clk),.rst(rst),.lease(lease),.source_drained(drained),.obs_awvalid(ov),.obs_awready(1'b1),.obs_awaddr(oa),.obs_awlen(ol),.obs_bvalid(ob),.obs_bready(1'b1),.obs_bresp(obr),.cmd_valid(cmd),.cmd_ready(ready),.source_base(src),.destination_base(dst),.span_bytes(span),.cmd_cookie(nonce),.busy(busy),.rsp_valid(rsp),.rsp_ready(ready_rsp),.status(status),.rsp_cookie(cookie),.receipt_valid(receipt),.dirty_count(dirty),.verified_count(verified),.m_araddr(ar),.m_arvalid(arv),.m_arready(arr),.m_rdata(rd),.m_rid(rid),.m_rresp(rresp),.m_rlast(rl),.m_rvalid(rv),.m_rready(rr),.m_awaddr(aw),.m_awvalid(awv),.m_awready(awr),.m_wdata(wd),.m_wvalid(wv),.m_wready(wr),.m_bid(bid),.m_bresp(bresp),.m_bvalid(bv),.m_bready(br));
axi_file_memory #(.READ_ONLY(0),.MAX_BEATS(1),.SECONDARY_WRITABLE(1),.TAG("copy")) mem(.clk(clk),.rst(rst),.base0(64'h1000),.base1(64'h4000),.base2(64'd0),.size0(64'd512),.size1(64'd512),.size2(64'd0),.araddr(ar),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(arv),.arready(arr),.rdata(rd),.rid(rid),.rresp(rresp),.rlast(rl),.rvalid(rv),.rready(rr),.awaddr(aw),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(awv),.awready(awr),.wdata(wd),.wstrb(64'hffffffffffffffff),.wlast(1'b1),.wvalid(wv),.wready(wr),.bid(bid),.bresp(bresp),.bvalid(bv),.bready(br),.inject_r(injr),.inject_b(injb),.reads(reads),.writes(writes),.rbeats(rbeats),.wbeats(wbeats),.bresponses(bs));
always @(posedge clk)if(!rst)begin if((busy||cmd)&&(gate_release||gate_ready||manifest))$fatal(1,"snapshot adapter released ownership");if(manifest&&!receipt)$fatal(1,"snapshot adapter forged permit");end
task reset_case;begin @(negedge clk);rst=1;cmd=0;ready_rsp=0;ov=0;ob=0;lease=1;drained=1;injr=0;injb=0;src=64'h1000;dst=64'h4000;span=512;nonce=32'h12345678;repeat(4)@(negedge clk);rst=0;repeat(2)@(negedge clk);end endtask
task mark(input integer offset,length,resp);begin @(negedge clk);oa=64'h1000+offset;ol=length;ov=1;@(negedge clk);ov=0;repeat(length+3)@(negedge clk);obr=resp;ob=1;@(negedge clk);ob=0;repeat(2)@(negedge clk);end endtask
task launch;begin @(negedge clk);cmd=1;do @(posedge clk);while(!ready);@(negedge clk);cmd=0;end endtask
task result(input integer expected,n);begin wait(rsp);repeat(6)begin @(negedge clk);if(!rsp||status!=expected||cookie!=32'h12345678||verified!=n||ready||receipt!=(expected==0))$fatal(1,"snapshot result expected=%0d actual=%0d count=%0d",expected,status,verified);checks=checks+1;end $display("SNAPSHOT_RESULT %0d %0d %0d",status,verified,receipt);ready_rsp=1;@(negedge clk);ready_rsp=0;wait(!busy);end endtask
initial begin
 reset_case;launch;result(0,0);
 mark(0,1,0);mark(0,0,0);if(dirty!=2||receipt)$fatal(1,"dirty dedup/receipt");
 launch;src=0;dst=0;span=0;nonce=0;result(0,2);if(writes!=2||rbeats!=4)$fatal(1,"copy counts");
 src=64'h1000;dst=64'h4000;span=512;nonce=32'h12345678;
 mark(128,0,0);lease=0;start_reads=reads;launch;result(1,0);if(reads!=start_reads)$fatal(1,"no lease read");
 lease=1;launch;do @(posedge clk);while(!(arv&&arr));@(negedge clk);lease=0;result(2,0);if(writes!=2)$fatal(1,"cancelled source wrote");
 reset_case;mark(0,0,0);start_bs=bs;launch;do @(posedge clk);while(!(awv&&awr));@(negedge clk);lease=0;result(2,0);if(bs!=start_bs+1)$fatal(1,"cancel did not drain B");
 reset_case;mark(0,0,0);injr=1;launch;result(5,0);
 reset_case;mark(0,0,0);injb=1;launch;result(6,0);
 reset_case;mark(0,0,0);launch;do @(posedge clk);while(!(bv&&br));@(negedge clk);injr=1;result(7,0);
 reset_case;mark(0,4,0);if(dirty!=4)$fatal(1,"overflow prefix");start_reads=reads;launch;result(3,0);if(reads!=start_reads)$fatal(1,"overflow read");
 reset_case;mark(0,0,2);launch;result(3,0);
 reset_case;mark(0,0,0);dst=src;launch;result(4,0);
 $display("SNAPSHOT_UNIT_PASS checks=%0d",checks);$finish;
end
initial begin #1000000;$fatal(1,"snapshot unit watchdog");end
endmodule
