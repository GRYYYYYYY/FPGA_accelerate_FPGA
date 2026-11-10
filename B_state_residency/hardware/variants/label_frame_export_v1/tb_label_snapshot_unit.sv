`timescale 1ns/1ps
module tb_label_snapshot_unit;
reg clk=0;always #5 clk=~clk;reg rst=1,lease=1,grant=1,cmd=0,ack=0,rr=0,inj=0;reg[1:0]query=1;reg[3:0]price=3;wire ready,busy,rsp,receipt,gate_r,gate_v,manifest;wire[3:0]status;wire[31:0]cookie,count,crc,pages;
wire sv,sr,srv,srr,pub;wire[2:0]sf,srf,sst;wire[26:0]so;
reg test_mode=0,test_v=0,test_r=0;reg[2:0]test_f=0;
reg nv=0,nrr=0,memok=1;reg[2:0]nop=0,nframe=0;reg[26:0]nowner=0;reg[71:0]ncookie=0;wire nr,nrv,npub,nfault;wire[2:0]nst,nrf;wire[31:0]naddress,leased;wire[3:0]allocated;
wire[31:0]ar,node;wire av,aq,rv,rq,rl,v;wire[511:0]data;wire[3:0]id;wire[1:0]resp;wire[159:0]payload;
integer emit=0,phase=0,checks=0,held_cycles=0;reg held=0;reg[191:0]held_row;
backing_frame_directory_small #(.FRAMES(8),.INDEX_BITS(3),.HASH_BITS(3),.EPOCH_BITS(3),.ENABLE_FRAME_SCAN(1)) directory(.clk(clk),.rst(rst),.cmd_valid(nv),.cmd_ready(nr),.cmd_op(nop),.cmd_owner(nowner),.cmd_frame(nframe),.cmd_cookie(ncookie),.memory_success(memok),.fence_retired(1'b1),.rsp_valid(nrv),.rsp_ready(nrr),.rsp_status(nst),.rsp_frame(nrf),.rsp_address(naddress),.rsp_published(npub),.allocated(allocated),.leased(leased),.any_fault(nfault),.scan_valid(test_mode?test_v:sv),.scan_ready(sr),.scan_permit(lease&&grant),.scan_frame(test_mode?test_f:sf),.scan_rsp_valid(srv),.scan_rsp_ready(test_mode?test_r:srr),.scan_status(sst),.scan_result_frame(srf),.scan_owner(so),.scan_published(pub));
label_snapshot_checkpoint_adapter #(.FRAMES(8),.INDEX_BITS(3)) reader(.clk(clk),.rst(rst),.lease(lease),.source_drained(1'b1),.cmd_valid(cmd),.cmd_ready(ready),.cmd_query(query),.cmd_price(price),.cmd_nodes(32'd32),.cmd_cookie(32'h123),.busy(busy),.rsp_valid(rsp),.rsp_ready(ack),.status(status),.rsp_cookie(cookie),.record_count(count),.record_crc(crc),.page_count(pages),.receipt_valid(receipt),.scan_valid(sv),.scan_ready(sr),.scan_frame(sf),.scan_rsp_valid(srv),.scan_rsp_ready(srr),.scan_status(sst),.scan_result_frame(srf),.scan_owner(so),.scan_published(pub),.m_araddr(ar),.m_arvalid(av),.m_arready(aq),.m_rdata(data),.m_rid(id),.m_rresp(resp),.m_rlast(rl),.m_rvalid(rv),.m_rready(rq),.record_valid(v),.record_ready(rr),.record_node(node),.record_payload(payload),.host_release_valid(1'b1),.root_release_ready(1'b1),.host_release_ready(gate_r),.root_release_valid(gate_v),.manifest_ready(manifest));
axi_file_memory #(.ADDR_BITS(32),.READ_ONLY(1),.MAX_BEATS(1),.TAG("labelsnap")) mem(.clk(clk),.rst(rst),.base0(64'd0),.base1(64'd0),.base2(64'd0),.size0(64'd1536),.size1(64'd0),.size2(64'd0),.inject_r(inj),.inject_b(1'b0),.araddr(ar),.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.arvalid(av),.arready(aq),.rdata(data),.rid(id),.rresp(resp),.rlast(rl),.rvalid(rv),.rready(rq),.awaddr(32'd0),.awlen(8'd0),.awsize(3'd6),.awburst(2'd1),.awid(4'd0),.awvalid(1'b0),.wdata(512'd0),.wstrb(64'd0),.wlast(1'b0),.wvalid(1'b0),.bready(1'b0));
function[71:0] ck(input integer tx,input[26:0]owner);ck={7'd0,1'b0,16'(tx),16'd1,owner,5'd0};endfunction
task normal(input integer op,f,expected);begin @(negedge clk);nop=op;nframe=f;nv=1;do @(posedge clk);while(!nr);@(negedge clk);nv=0;wait(nrv);repeat(3)begin @(negedge clk);if(nst!=expected)$fatal(1,"directory normal %0d/%0d",nst,expected);checks=checks+1;end nrr=1;@(negedge clk);nrr=0;end endtask
task populate(input integer f,input[26:0]o);begin nowner=o;ncookie=ck(f+1,o);normal(0,0,0);normal(1,f,0);normal(2,f,0);normal(3,f,0);end endtask
task inspect(input integer f,expected,input[26:0]owner,input published);begin test_mode=1;test_f=f;test_v=1;do @(posedge clk);while(!sr);@(negedge clk);test_v=0;wait(srv);nv=1;nop=0;nowner=27'd77;repeat(5)begin @(negedge clk);if(sst!=expected||so!=owner||pub!=published||nr||srf!=f||allocated!=3||leased!=0)$fatal(1,"directory inspect result");checks=checks+1;end nv=0;test_r=1;@(negedge clk);test_r=0;test_mode=0;end endtask
task launch;begin emit=0;query=1;price=3;@(negedge clk);cmd=1;do @(posedge clk);while(!ready);@(negedge clk);cmd=0;rr=1;end endtask
task result(input integer expected,c,p);reg[31:0]saved_crc;begin wait(rsp);@(negedge clk);rr=0;saved_crc=crc;repeat(6)begin @(negedge clk);if(status!=expected||count!=c||pages!=p||cookie!=32'h123||crc!=saved_crc||receipt!=(expected==0)||manifest||gate_r||gate_v)$fatal(1,"snapshot unit status=%0d count=%0d pages=%0d cookie=%h crc=%h saved=%h receipt=%b gate=%b%b%b",status,count,pages,cookie,crc,saved_crc,receipt,manifest,gate_r,gate_v);checks=checks+1;end $display("LABEL_UNIT_RESULT %0d %0d %0d %0d %08h",phase,status,count,pages,crc);ack=1;@(negedge clk);ack=0;wait(!busy);end endtask
always @(posedge clk)if(!rst)begin
 if((busy||cmd)&&(gate_r||gate_v||manifest))$fatal(1,"label gate released lease");
 if(v&&!rr)begin held_cycles<=held_cycles+1;if(held&&held_row!={node,payload})$fatal(1,"label stream hold");held<=1;held_row<={node,payload};end else held<=0;
 if(v&&rr)begin
  if(node!=(emit==0?0:emit==1?2:emit==2?7:17))$fatal(1,"label unit node");
  for(integer f=0;f<5;f=f+1)if(payload[f*32+:32]!=32'h10000000+f*256+node)$fatal(1,"label unit payload");
  $display("LABEL_UNIT_RECORD %0d %0d %040h",phase,node,payload);emit<=emit+1;
 end
end
initial begin
 repeat(4)@(negedge clk);rst=0;wait(nr);populate(0,{4'd3,2'd1,21'd0});populate(1,{4'd3,2'd2,21'd1});populate(2,{4'd3,2'd1,21'd2});
 inspect(0,0,{4'd3,2'd1,21'd0},1);inspect(3,6,0,0);grant=0;inspect(0,2,0,0);grant=1;
 nowner={4'd3,2'd1,21'd2};ncookie=ck(3,nowner);normal(1,2,5);
 phase=1;launch;query=0;price=0;wait(v);@(negedge clk);rr=0;repeat(5)@(negedge clk);rr=1;result(0,4,2);
 nowner={4'd3,2'd1,21'd3};normal(0,0,0);phase=2;launch;result(4,4,2);
 phase=3;inj=1;launch;result(5,0,0);inj=0;
 phase=4;launch;do @(posedge clk);while(!(av&&aq));@(negedge clk);lease=0;result(2,0,0);lease=1;
 // Hold a normal reply so the already-exposed scan descriptor is backpressured.
 @(negedge clk);nop=5;nowner={4'd3,2'd1,21'd0};nv=1;do @(posedge clk);while(!nr);@(negedge clk);nv=0;wait(nrv);
 phase=5;launch;wait(sv&&!sr);@(negedge clk);lease=0;repeat(4)begin @(negedge clk);if(!sv)$fatal(1,"scan VALID cancelled before acceptance");end nrr=1;@(negedge clk);nrr=0;result(2,0,0);
 lease=1;nowner={4'd3,2'd1,21'd3};ncookie=ck(4,nowner);normal(1,3,0);normal(2,3,0);normal(3,3,0);
 phase=6;launch;result(6,4,3);
 if(held_cycles<5)$fatal(1,"stream backpressure not exercised");$display("LABEL_STREAM_HELD %0d",held_cycles);
 $display("LABEL_SNAPSHOT_UNIT_PASS checks=%0d",checks);$finish;
end
initial begin #1000000;$fatal(1,"label snapshot unit watchdog");end
endmodule
