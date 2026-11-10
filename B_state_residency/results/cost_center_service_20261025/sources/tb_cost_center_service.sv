`timescale 1ns/1ps
module tb_cost_center_service;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,abort=0,active=1,req_valid=0,rsp_ready=0;
 reg [1:0] active_query=2,req_query=2;
 reg [3:0] active_price=3,req_price=3;
 reg [31:0] active_version=19,req_version=19,req_cookie=0;
 reg [127:0] req_words=0;
 wire req_ready,rsp_valid,busy,fault;
 wire [63:0] rsp_words;wire [31:0] rsp_cookie,rsp_version;
 wire [1:0] rsp_query,rsp_status;wire [3:0] rsp_price;
 cost_center_service dut(.*);
 integer f,o,n,count=0,j,k;reg [31:0] a,b,c,d,e,g;reg [63:0] expected,held;
 initial begin #300000000;$fatal(1,"watchdog");end
 task reset_all;
 begin @(negedge clk);rst=1;req_valid=0;rsp_ready=0;abort=0;
 active=1;active_query=2;active_price=3;active_version=19;req_version=19;
 repeat(4)@(negedge clk);rst=0;repeat(2)@(negedge clk);end endtask
 task send;
 begin while(!req_ready)@(negedge clk);req_valid=1;
 @(negedge clk);req_valid=0;req_words=~req_words;end endtask
 task wait_reply;
 begin k=0;while(!rsp_valid)begin @(negedge clk);k=k+1;
 if(fault||k>1050)$fatal(1,"reply failed count=%0d",count);end end endtask
 task retire;
 begin rsp_ready=1;@(negedge clk);rsp_ready=0;end endtask
 initial begin
 reset_all();f=$fopen("vectors.txt","r");o=$fopen("observed.txt","w");
 if(!f||!o)$fatal(1,"files");
 while(!$feof(f))begin
 n=$fscanf(f,"%h %h %h %h %h %h\n",a,b,c,d,e,g);
 if(n!=6)$fatal(1,"vector format");
 req_words={d,c,b,a};req_cookie=count;expected={g,e};send();wait_reply();
 if(rsp_words!==expected||rsp_status!==0||rsp_cookie!==count||
 rsp_version!==19||rsp_query!==2||rsp_price!==3||!busy)$fatal(1,"mismatch %0d",count);
 held=rsp_words;
 repeat(count%4)begin @(negedge clk);if(rsp_words!==held||!rsp_valid||req_ready||!busy||fault)$fatal(1,"backpressure");end
 $fwrite(o,"%08x %08x\n",rsp_words[31:0],rsp_words[63:32]);retire();count=count+1;
 end
 $fclose(f);$fclose(o);if(count!=110397)$fatal(1,"count");
 // Stale full version has identical low price tag: reject without starting core.
 req_version=3;send();wait_reply();if(rsp_status!==2||rsp_words!==0)$fatal(1,"stale full version");retire();req_version=19;
 active=0;send();wait_reply();if(rsp_status!==1)$fatal(1,"inactive");retire();active=1;
 // Abort and synchronous reset during real arithmetic, then reuse same instance.
 for(j=0;j<120;j=j+1)begin
 reset_all();req_words={32'h3f123456,32'h3f654321,32'h80000000,32'h7fffffff};send();
 repeat(j)@(negedge clk);
 abort=1;#1;if(!fault||req_ready||!busy)$fatal(1,"abort");
 @(negedge clk);abort=0;repeat(2)@(negedge clk);
 if(!fault||req_ready)$fatal(1,"abort sticky");
 reset_all();req_words=0;send();wait_reply();if(rsp_words!==0)$fatal(1,"reset recovery");retire();
 end
 // Identity must remain held while computed reply is backpressured.
 req_words=0;send();wait_reply();held=rsp_words;active_version=35;#1;
 if(!fault||!busy||req_ready)$fatal(1,"owner drift");
 repeat(3)begin @(negedge clk);if(rsp_words!==held||!rsp_valid)$fatal(1,"stable fault reply");end
 retire();if(!fault||!busy||req_ready)$fatal(1,"fault retirement");
 reset_all();req_words=0;send();wait_reply();retire();
 $display("COST_CENTER_SERVICE_PASS vectors=%0d reset_abort_offsets=120",count);$finish;
 end
endmodule
