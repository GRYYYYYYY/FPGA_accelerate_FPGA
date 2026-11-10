`timescale 1ns/1ps
module tb_crc_unit;
reg clk=0;always #5 clk=~clk;reg rst=1,start=0,ack=0,sv=0,sl=0;wire ready,sr,rsp,busy,fault;wire[3:0]status;wire[31:0]cookie,written,verified,actual_crc;
reg[31:0]expected_crc=0,snode=0;reg[159:0]spayload=0;wire cv,crv,crr,lv,lrq,lw,lrv,lrr,lp;wire[1:0]cop,cq;wire[3:0]cp;wire[31:0]cver,ln,ldata;wire[2:0]lf;reg c_rsp=0,l_rsp=0,l_present=0;reg[159:0]l_payload=0;reg[159:0]mem[0:31];reg[31:0]present=0;
integer phase=0,checks=0,writes=0,reads=0;reg[31:0]nodes[0:1];reg[159:0]values[0:1];
`ifdef CRC_DISABLED
localparam CHECK_CRC=0;
`else
localparam CHECK_CRC=1;
`endif
label_restore_controller #(.MAX_RECORDS(8),.CHECK_SOURCE_CRC(CHECK_CRC),.MAX_CYCLES(4096)) dut(.clk(clk),.rst(rst),.abort(1'b0),.backend_drained(!c_rsp&&!l_rsp),.start_valid(start),.start_ready(ready),.start_design(64'd7),.expected_design(64'd7),.start_checkpoint(32'd18),.expected_checkpoint(32'd18),.start_cookie(32'h77),.start_count(32'd2),.start_nodes(32'd32),.start_probe(32'd31),.start_version(32'd4),.start_query(2'd2),.start_price(4'd4),.start_source_crc(expected_crc),.rsp_source_crc(actual_crc),.s_valid(sv),.s_ready(sr),.s_node(snode),.s_cookie(32'h77),.s_payload(spayload),.s_last(sl),.rsp_valid(rsp),.rsp_ready(ack),.rsp_status(status),.rsp_cookie(cookie),.written(written),.verified(verified),.busy(busy),.fault(fault),.c_valid(cv),.c_ready(!c_rsp),.c_op(cop),.c_query(cq),.c_price(cp),.c_version(cver),.c_rsp_valid(c_rsp),.c_rsp_ready(crr),.c_status(4'd0),.l_valid(lv),.l_ready(!l_rsp),.l_write(lw),.l_node(ln),.l_value(ldata),.l_field(lf),.l_rsp_valid(l_rsp),.l_rsp_ready(lrr),.l_status(4'd0),.l_present(l_present),.l_payload(l_payload));
always @(posedge clk)begin
 if(rst)begin c_rsp<=0;l_rsp<=0;present<=0;writes<=0;reads<=0;for(integer i=0;i<32;i=i+1)mem[i]<=0;end
 else begin
  if(c_rsp&&crr)c_rsp<=0;
  if(l_rsp&&lrr)l_rsp<=0;
  if(cv&&!c_rsp)begin c_rsp<=1;$display("CRC_UNIT_CONTROL %0d %0d",phase,cop);end
  if(lv&&!l_rsp)begin
   l_rsp<=1;l_present<=present[ln];l_payload<=mem[ln];
   if(lw)begin mem[ln][lf*32+:32]<=ldata;present[ln]<=1;writes<=writes+1;$display("CRC_UNIT_W %0d %0d %0d %08h",phase,ln,lf,ldata);end
   else begin reads<=reads+1;$display("CRC_UNIT_R %0d %0d %0d %040h",phase,ln,present[ln],mem[ln]);end
  end
 end
end
task test(input integer which,input[31:0]crc);integer index;begin
 @(negedge clk);rst=1;start=0;ack=0;sv=0;repeat(4)@(negedge clk);rst=0;phase=which;expected_crc=crc;
 @(negedge clk);start=1;do @(posedge clk);while(!ready);@(negedge clk);start=0;expected_crc=crc^32'hffffffff;
 for(integer i=0;i<2;i=i+1)begin
  index=which==4?1-i:i;snode=nodes[index];spayload=values[index];if(which==3&&i==1)spayload[0]=~spayload[0];sl=i==1;sv=1;
  do @(posedge clk);while(!sr);$display("CRC_UNIT_STREAM %0d %0d %040h",phase,snode,spayload);@(negedge clk);sv=0;
 end
 wait(rsp);repeat(8)begin @(negedge clk);
  if(cookie!=32'h77||!busy||ready||status!=((CHECK_CRC&&which>1)?8:0)||written!=((CHECK_CRC&&which>1)?1:2)||verified!=((CHECK_CRC&&which>1)?0:2)||writes!=((CHECK_CRC&&which>1)?5:10)||fault!=((CHECK_CRC&&which>1)?1:0))$fatal(1,"CRC unit status=%0d written=%0d verified=%0d",status,written,verified);
  checks=checks+1;
 end
 $display("CRC_UNIT_RESULT %0d %0d %0d %0d %08h %0d %0d",phase,status,written,verified,actual_crc,writes,reads);
 ack=1;@(negedge clk);ack=0;wait(!busy);
end endtask
reg[31:0]gold_crc;string path;integer fd,rc;
initial begin
 nodes[0]=10;nodes[1]=20;for(integer f=0;f<5;f=f+1)begin values[0][f*32+:32]=32'h1000+f;values[1][f*32+:32]=32'h2000+f;end
 if(!$value$plusargs("crcfile=%s",path))$fatal(1,"crc file");fd=$fopen(path,"r");rc=$fscanf(fd,"%h",gold_crc);if(rc!=1)$fatal(1,"crc input");
 test(1,gold_crc);test(2,gold_crc^1);if(CHECK_CRC)begin test(3,gold_crc);test(4,gold_crc);end
 $display("LABEL_CRC_UNIT_PASS checks=%0d enabled=%0d",checks,CHECK_CRC);$finish;
end
initial begin #1000000;$fatal(1,"CRC unit watchdog");end
endmodule
