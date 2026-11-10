`timescale 1ns/1ps
module tb_seed_leaf;
reg clk=0;always #5 clk=~clk;
reg rst=1,abort=0,start=0,enable=0,sv=0,sl=0,ack=0;
reg[31:0]sn=0,expected_crc=0;
reg[159:0]payload=0;
wire ready,sr,rsp,busy,fault,import_write,probe,cv,crr,lv,lw,lrr;
wire[3:0]status,cp;
wire[31:0]cookie,written,verified,actual_crc,cver,ln,ldata;
wire[1:0]cop,cq;wire[2:0]lf;
reg c_rsp=0,l_rsp=0,l_present=0;
reg[159:0]l_payload=0,mem[0:31];reg[31:0]present=0;
integer delay_left=0,writes=0,reads=0,checks=0,phase=0;
reg accepted_enable=0;
reg[159:0]values[0:1];reg[31:0]gold_crc;
label_restore_controller #(.MAX_RECORDS(8),.CHECK_SOURCE_CRC(1),.MAX_CYCLES(4096)) dut(
 .start_skip_seed(enable),.l_import(import_write),.l_probe(probe),
 .clk(clk),.rst(rst),.abort(abort),.backend_drained(!c_rsp&&!l_rsp&&delay_left==0),
 .start_valid(start),.start_ready(ready),.start_design(64'd7),.expected_design(64'd7),
 .start_checkpoint(32'd18),.expected_checkpoint(32'd18),.start_cookie(32'h77),
 .start_count(32'd2),.start_nodes(32'd32),.start_probe(32'd31),
 .start_version(32'd4),.start_query(2'd2),.start_price(4'd4),
 .start_source_crc(expected_crc),.rsp_source_crc(actual_crc),
 .s_valid(sv),.s_ready(sr),.s_node(sn),.s_cookie(32'h77),.s_payload(payload),.s_last(sl),
 .rsp_valid(rsp),.rsp_ready(ack),.rsp_status(status),.rsp_cookie(cookie),
 .written(written),.verified(verified),.busy(busy),.fault(fault),
 .c_valid(cv),.c_ready(!c_rsp),.c_op(cop),.c_query(cq),.c_price(cp),.c_version(cver),
 .c_rsp_valid(c_rsp),.c_rsp_ready(crr),.c_status(4'd0),
 .l_valid(lv),.l_ready(!l_rsp&&delay_left==0),.l_write(lw),.l_node(ln),.l_value(ldata),.l_field(lf),
 .l_rsp_valid(l_rsp),.l_rsp_ready(lrr),.l_status(4'd0),.l_present(l_present),.l_payload(l_payload));
always @(posedge clk)begin
 if(rst)begin
  c_rsp<=0;l_rsp<=0;delay_left<=0;present<=0;writes<=0;reads<=0;accepted_enable<=0;
  for(integer i=0;i<32;i=i+1)mem[i]<=0;
 end else begin
  if(start&&ready)accepted_enable<=enable;
  if(import_write!==(accepted_enable&&(dut.state==6||dut.state==7)))
   $fatal(1,"leaf write provenance changed after start phase=%0d",phase);
  checks<=checks+1;
  if(c_rsp&&crr)c_rsp<=0;
  if(cv&&!c_rsp)c_rsp<=1;
  if(l_rsp&&lrr)l_rsp<=0;
  if(delay_left>0)begin delay_left<=delay_left-1;if(delay_left==1)l_rsp<=1;end
  if(lv&&!l_rsp&&delay_left==0)begin
   delay_left<=4;l_present<=present[ln];l_payload<=mem[ln];
   if(lw)begin
    if(import_write!==accepted_enable)$fatal(1,"write provenance");
    mem[ln][lf*32+:32]<=ldata;present[ln]<=1;writes<=writes+1;
    $display("SEED_LEAF_W %0d %0d %0d %08h %0d",phase,ln,lf,ldata,import_write);
   end else begin
    if(import_write)$fatal(1,"read must not bypass baseline");
    reads<=reads+1;
   end
  end
 end
end
task row(input integer i);begin
 @(negedge clk);sn=10+i*10;payload=values[i];sl=i==1;sv=1;
 do @(posedge clk);while(!sr);
 @(negedge clk);sv=0;
end endtask
task test(input integer which,input bit skip,input bit bad_crc,input bit cancel);begin
 @(negedge clk);rst=1;start=0;abort=0;ack=0;sv=0;
 repeat(4)@(negedge clk);rst=0;phase=which;enable=skip;expected_crc=gold_crc^bad_crc;
 @(negedge clk);start=1;do @(posedge clk);while(!ready);
 @(negedge clk);start=0;enable=!skip;expected_crc=~expected_crc;
 row(0);
 if(cancel)begin
  wait(writes==3);@(negedge clk);abort=1;
  if(delay_left==0)$fatal(1,"cancel missed outstanding response");
 end else row(1);
 wait(rsp);
 repeat(8)begin
  @(negedge clk);
  if(!rsp||!busy||ready||cookie!=32'h77||status!=(cancel?7:bad_crc?8:0)||
     written!=(cancel?0:bad_crc?1:2)||verified!=((cancel||bad_crc)?0:2)||
     writes!=(cancel?3:bad_crc?5:10)||fault!=(cancel||bad_crc)||import_write||delay_left||l_rsp)
    $fatal(1,"leaf result phase=%0d status=%0d written=%0d verified=%0d writes=%0d",phase,status,written,verified,writes);
 end
 $display("SEED_LEAF_RESULT %0d %0d %0d %0d %0d %0d %08h",phase,skip,status,written,verified,writes,actual_crc);
 ack=1;@(negedge clk);ack=0;wait(!busy);
 if((cancel||bad_crc)&&ready)$fatal(1,"failed leaf must remain stopped");
end endtask
string path;integer fd,rc;
initial begin
 for(integer f=0;f<5;f=f+1)begin values[0][f*32+:32]=f==4?8'h12:32'h1000+f;values[1][f*32+:32]=f==4?8'h34:32'h2000+f;end
 if(!$value$plusargs("crcfile=%s",path))$fatal(1,"missing independent CRC");
 fd=$fopen(path,"r");rc=$fscanf(fd,"%h",gold_crc);$fclose(fd);if(rc!=1)$fatal(1,"CRC input");
 test(1,0,0,0);test(2,1,0,0);test(3,1,1,0);test(4,1,0,1);
 $display("SEED_LEAF_PASS checks=%0d scenarios=4",checks);$finish;
end
initial begin #1000000;$fatal(1,"seed leaf watchdog");end
endmodule
