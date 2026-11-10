 integer cases=0,cycles=0,i;reg[132:0]held;
 wire[132:0]bundle={rsp_status,rsp_op,rsp_index,rsp_cookie,rsp_a,rsp_b};
 always @(posedge clk)begin cycles<=cycles+1;if(cycles>10000)$fatal(1,"watchdog");end
 task reset_case;
 begin
  @(negedge clk);rst=1;req_valid=0;rsp_ready=0;cfg_valid=0;cfg_rsp_ready=0;m_arready=0;m_rvalid=0;m_rid=0;m_rresp=0;m_rlast=1;m_rdata=0;
  cfg_rows_base=64'h1fffff000;cfg_columns_base=64'h21fffff000;cfg_rows=128;cfg_columns=64;
  repeat(2)@(negedge clk);rst=0;@(negedge clk);if(fault)$fatal(1,"reset");
 end endtask
 task configure(input integer expected);
 begin
  cfg_valid=1;wait(cfg_ready);@(posedge clk);@(negedge clk);cfg_valid=0;
  wait(cfg_rsp_valid);@(negedge clk);if(cfg_status!=expected||configured!=(expected==0))$fatal(1,"configuration %0d/%0d",cfg_status,expected);
  cfg_rsp_ready=1;@(negedge clk);cfg_rsp_ready=0;
 end endtask
 task start(input integer op,idx);
 begin
  @(negedge clk);req_op=op;req_index=idx;req_cookie=123;req_valid=1;wait(req_ready);@(posedge clk);@(negedge clk);req_valid=0;
 end endtask
 task retire(input integer status,input bad);
 begin
  wait(rsp_valid);@(negedge clk);if(rsp_status!=status||fault!==bad)$fatal(1,"table case=%0d status=%0d/%0d fault=%b",cases,rsp_status,status,fault);
  held=bundle;repeat(3)begin @(negedge clk);if(!rsp_valid||held!==bundle)$fatal(1,"unstable");end
  rsp_ready=1;@(negedge clk);rsp_ready=0;cases=cases+1;
 end endtask
 initial begin
  reset_case;start(0,0);retire(1,0);
  for(i=0;i<5;i=i+1)begin
   reset_case;
   case(i)0:cfg_rows_base=3;1:cfg_rows=0;2:cfg_columns=65537;3:cfg_rows_base=64'hffffffffffffffc0;4:cfg_columns_base=cfg_rows_base;endcase
   configure(i==0?1:i==4?3:2);cases=cases+1;
  end
  reset_case;configure(0);start(0,128);retire(2,0);start(1,64);retire(2,0);
  reset_case;cfg_columns=0;configure(0);start(1,0);retire(2,0);
  for(i=0;i<6;i=i+1)begin
   reset_case;configure(0);start(i==5?1:0,9);wait(m_arvalid);@(negedge clk);
   if(m_araddr!==(i==5?cfg_columns_base:cfg_rows_base)+64||m_arlen||m_arsize!=6||m_arburst!=1||m_arid)$fatal(1,"read address");
   m_arready=1;@(negedge clk);m_arready=0;m_rdata=0;m_rdata[127:64]=64'h0000000100000002;
   case(i)1:m_rid=1;2:m_rresp=2;3:m_rlast=0;4:m_rdata[127:96]=2;5:m_rdata[127:64]=64'h800000007fffffff;endcase
   m_rvalid=1;wait(m_rready);@(posedge clk);@(negedge clk);m_rvalid=0;
   if(i==0&&(rsp_a!=2||rsp_b!=1))$fatal(1,"row lane");
   if(i==5&&(rsp_a!=32'h7fffffff||rsp_b!=32'h80000000))$fatal(1,"sentinel lost");
   retire(i==0||i==5?0:i==4?4:3,i!=0&&i!=5);
  end
  reset_case;configure(0);m_rvalid=1;@(negedge clk);if(!fault||req_ready||rsp_valid)$fatal(1,"unowned read");m_rvalid=0;@(negedge clk);if(!fault)$fatal(1,"not sticky");cases=cases+1;
  reset_case;configure(0);start(0,9);wait(m_arvalid);@(negedge clk);m_arready=1;m_rvalid=1;m_rdata=0;m_rdata[127:64]=64'h0000000100000002;
  @(negedge clk);m_arready=0;wait(m_rready);@(posedge clk);@(negedge clk);m_rvalid=0;wait(rsp_valid);held=bundle;
  // A second unowned response cannot change an already exposed result.
  m_rvalid=1;@(negedge clk);if(!fault||held!==bundle)$fatal(1,"late response");m_rvalid=0;retire(0,1);
  $display("TABLE_BOUNDARIES_PASS cases=%0d cycles=%0d",cases,cycles);$finish;
 end
