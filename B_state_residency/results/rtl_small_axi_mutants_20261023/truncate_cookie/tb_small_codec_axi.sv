`timescale 1ns/1ps
module tb_small_codec_axi;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,req_valid=0,req_write=0,done_ready=0;
    reg [31:0] req_address=0;reg [71:0] req_cookie=0;
    wire req_ready,done_valid,done_error,busy,fault;wire [71:0] done_cookie;
    wire in_valid,in_ready,out_valid,out_ready;wire [511:0] in_data,out_data;
    wire [31:0] m_awaddr,m_araddr;wire [7:0] m_awlen,m_arlen;wire [2:0] m_awsize,m_arsize;
    wire [1:0] m_awburst,m_arburst;wire [3:0] m_awid,m_arid;wire m_awvalid,m_arvalid;
    wire m_awready,m_arready,m_wready;wire [511:0] m_wdata;wire [63:0] m_wstrb;wire m_wlast,m_wvalid;
    reg [3:0] m_bid=0,m_rid=0;reg [1:0] m_bresp=0,m_rresp=0;reg m_bvalid=0,m_rvalid=0,m_rlast=0;
    wire m_bready,m_rready;reg [511:0] m_rdata=0;
    scratch_page_axi_small dut(.*);
    reg [511:0] fixtures[0:191],memory[0:2047],write_words[0:2];
    reg c_start=0,c_read=0,c_cancel=0,c_input_valid=0,c_present=0;
    wire c_start_ready,c_busy,c_input_ready;
    reg [2:0] c_offset=0;reg [159:0] c_payload=0;
    wire c_output_valid,c_output_present;reg c_output_ready=0;
    wire [2:0] c_output_offset;wire [159:0] c_output_payload;
    wire c_raw_last,c_commit_ready,c_done,c_error;
    reg c_commit=0,c_ok=0,c_done_ready=0,c_allowed=0;
    reg [160:0] record_fixtures[0:511];reg [4095:0] records_path;
    integer record_checks=0,raw_checks=0,c_raw_count=0,c_page=0;
    scratch_page_codec_small codec(.clk(clk),.rst(rst),.start_valid(c_start),.start_ready(c_start_ready),.start_decode(c_read),
      .cancel(c_cancel),.busy(c_busy),.record_in_valid(c_input_valid),.record_in_ready(c_input_ready),
      .record_in_offset(c_offset),.record_in_present(c_present),.record_in_payload(c_payload),
      .record_out_valid(c_output_valid),.record_out_ready(c_output_ready),.record_out_offset(c_output_offset),
      .record_out_present(c_output_present),.record_out_payload(c_output_payload),
      .raw_in_valid(out_valid),.raw_in_ready(out_ready),.raw_in_data(out_data),
      .raw_out_valid(in_valid),.raw_out_ready(in_ready),.raw_out_data(in_data),.raw_out_last(c_raw_last),
      .commit_valid(c_commit),.commit_ready(c_commit_ready),.commit_ok(c_ok),
      .done_valid(c_done),.done_ready(c_done_ready),.done_error(c_error));
    always @(posedge clk)if(!rst)begin
      if(c_output_valid && !c_allowed)$fatal(1,"AXI failure or pending completion exposed record");
      if(in_valid && in_ready)begin
        if(c_raw_count>=3 || in_data!==fixtures[c_page*3+c_raw_count] || c_raw_last!==(c_raw_count==2))$fatal(1,"codec AXI write byte mismatch");
        c_raw_count=c_raw_count+1;raw_checks=raw_checks+1;
      end
      if(out_valid && out_ready)begin
        if(c_raw_count>=3 || out_data!==fixtures[c_page*3+c_raw_count])$fatal(1,"codec AXI read byte mismatch");
        c_raw_count=c_raw_count+1;raw_checks=raw_checks+1;
      end
    end
    reg aw_pending=0,wlast_seen=0,read_active=0;
    reg [31:0] aw_address=0,ar_address=0;
    integer aw_length=0,write_count=0,read_length=0,read_position=0,b_delay=0;
    integer cycle=0,aw_count=0,b_count=0,ar_count=0,r_count=0,checks=0,write_pages=0,read_pages=0;
    integer expected_next_aw=0,expected_next_ar=0,mode=0,current_frame=0,test_slot=0;
    integer j,k,fr,txid=0,baseline_b,expected_b,reads,words,deadline,errors=0;
    reg [63:0] offset_coverage=0,cookie;
    reg [4095:0] fixture_path;
    reg held_aw=0,held_w=0,held_ar=0,held_out=0;
    reg [48:0] saved_aw,saved_ar;
    reg [576:0] saved_w;
    reg [511:0] saved_out;
    assign m_awready=!rst && !aw_pending && !m_bvalid && (cycle%7!=0)
        && (current_frame%2==0 || m_wvalid || write_count!=0);
    assign m_wready=!rst && !wlast_seen && !m_bvalid && (cycle%5>=2);
    assign m_arready=!rst && !read_active && !m_rvalid && cycle%7>=2;
    // Independent burst slave, including W-before-AW acceptance, delayed B,
    // response errors, address/length validation and held valid outputs.
    always @(posedge clk) begin
        cycle<=cycle+1;
        if(rst)begin
            aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;m_bvalid<=0;
            read_active<=0;read_position<=0;m_rvalid<=0;
            held_aw<=0;held_w<=0;held_ar<=0;held_out<=0;
        end else begin
            if(held_aw && (!m_awvalid || {m_awaddr,m_awlen,m_awsize,m_awburst,m_awid}!==saved_aw))$fatal(1,"AW changed under backpressure");
            if(held_ar && (!m_arvalid || {m_araddr,m_arlen,m_arsize,m_arburst,m_arid}!==saved_ar))$fatal(1,"AR changed under backpressure");
            if(held_w && (!m_wvalid || {m_wdata,m_wstrb,m_wlast}!==saved_w))$fatal(1,"W changed under backpressure");
            if(held_out && (!out_valid || out_data!==saved_out))$fatal(1,"read stream changed under backpressure");
            held_aw<=m_awvalid&&!m_awready;saved_aw<={m_awaddr,m_awlen,m_awsize,m_awburst,m_awid};
            held_ar<=m_arvalid&&!m_arready;saved_ar<={m_araddr,m_arlen,m_arsize,m_arburst,m_arid};
            held_w<=m_wvalid&&!m_wready;saved_w<={m_wdata,m_wstrb,m_wlast};
            held_out<=out_valid&&!out_ready;saved_out<=out_data;
            if(m_awvalid && m_awready)begin
                if(aw_pending || m_awid!=0 || m_awsize!=6 || m_awburst!=1 || m_awaddr[5:0]!=0 || m_awlen>2
                   || ({1'b0,m_awaddr[11:0]}+((m_awlen+1)*64)>4096) || m_awaddr!==expected_next_aw[31:0])$fatal(1,"bad AW burst address=%h expected=%h len=%0d",m_awaddr,expected_next_aw,m_awlen);
                aw_pending<=1;aw_address<=m_awaddr;aw_length<=m_awlen+1;aw_count<=aw_count+1;
                expected_next_aw=expected_next_aw+(m_awlen+1)*64;
            end
            if(m_wvalid && m_wready)begin
                if(write_count>2 || m_wstrb!==64'hffffffffffffffff)$fatal(1,"bad W beat");
                write_words[write_count]<=m_wdata;write_count<=write_count+1;
                if(m_wlast)wlast_seen<=1;
            end
            if(aw_pending && wlast_seen && !m_bvalid)begin
                if(write_count!=aw_length)$fatal(1,"WLAST/length mismatch");
                if(b_delay<23)b_delay<=b_delay+1;
                else begin
                    for(k=0;k<aw_length;k=k+1)memory[((aw_address>>6)+k)%2048]<=write_words[k];
                    m_bvalid<=1;m_bid<=mode==2?1:0;m_bresp<=(mode==1 || (mode==6 && aw_address>=4096))?2:0;
                end
            end
            if(m_bvalid && m_bready)begin
                m_bvalid<=0;aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;b_count<=b_count+1;
            end
            if(m_arvalid && m_arready)begin
                if(read_active || m_arid!=0 || m_arsize!=6 || m_arburst!=1 || m_araddr[5:0]!=0 || m_arlen>2
                   || ({1'b0,m_araddr[11:0]}+((m_arlen+1)*64)>4096) || m_araddr!==expected_next_ar[31:0])$fatal(1,"bad AR burst");
                read_active<=1;ar_address<=m_araddr;read_length<=m_arlen+1;read_position<=0;ar_count<=ar_count+1;
                expected_next_ar=expected_next_ar+(m_arlen+1)*64;
            end
            if(read_active && !m_rvalid && cycle%5>=2)begin
                m_rvalid<=1;m_rdata<=memory[((ar_address>>6)+read_position)%2048];
                m_rid<=mode==5?1:0;m_rresp<=(mode==3 || (mode==7 && ar_address>=4096))?3:0;
                m_rlast<=mode==4?1:(read_position==read_length-1);
            end
            if(m_rvalid && m_rready)begin
                m_rvalid<=0;r_count<=r_count+1;
                if(read_position==read_length-1)read_active<=0;
                else read_position<=read_position+1;
            end
        end
    end

 task reset_all;begin
  @(negedge clk);rst=1;mode=0;req_valid=0;done_ready=0;c_start=0;c_commit=0;c_done_ready=0;c_cancel=0;c_input_valid=0;c_output_ready=0;c_allowed=0;
  repeat(3)@(negedge clk);rst=0;
 end endtask
 task transfer(input reg[31:0] address,input integer page_id,reading,expect_error);
  reg [71:0] token;integer n,d,start_b,need_b;
  begin
   current_frame=page_id;expected_next_aw=address;expected_next_ar=address;
   token={8'h01,16'hfedc,16'h9876,32'hfefedcba} ^ checks;
   start_b=b_count;need_b=1+({1'b0,address[11:0]}+192>4096);
   @(negedge clk);if(!c_start_ready || !req_ready)$fatal(1,"start blocked");
   c_start=1;c_read=reading;c_allowed=0;c_raw_count=0;c_page=page_id;
   req_valid=1;req_write=!reading;req_address=address;req_cookie=token;
   @(posedge clk);@(negedge clk);c_start=0;req_valid=0;req_cookie='1;
   if(!reading)for(n=0;n<8;n=n+1)begin
    @(negedge clk);c_input_valid=1;c_offset=n;c_present=record_fixtures[page_id*8+n][160];c_payload=record_fixtures[page_id*8+n][159:0];
    @(posedge clk);while(!c_input_ready)@(posedge clk);@(negedge clk);c_input_valid=0;
   end
   d=0;while(!done_valid)begin @(negedge clk);d=d+1;if(d>4000)$fatal(1,"AXI done timeout");end
   repeat(4)begin
    if(!done_valid || done_cookie!==token || done_error!==expect_error[0] || req_ready)$fatal(1,"AXI done/cookie hold mismatch");
    @(negedge clk);
   end
   if(!expect_error)begin
    if(c_raw_count!=3 || fault)$fatal(1,"incomplete page");
    if(!reading && (b_count!=start_b+need_b || !c_done || c_error))$fatal(1,"write before all B/encode");
   end else begin
    if(!fault)$fatal(1,"missing sticky AXI fault");
    if(reading && (read_active || m_rvalid))$fatal(1,"undrained error");
   end
   if(expect_error)begin
    if(!c_done)begin c_cancel=1;@(posedge clk);@(negedge clk);c_cancel=0;end
    if(!c_done || c_output_valid || (reading && !c_error))$fatal(1,"cancel failed");
   end else if(reading)begin
    d=0;while(!c_commit_ready)begin @(negedge clk);d=d+1;if(d>40)$fatal(1,"commit timeout");end
    repeat(13)begin if(c_output_valid)$fatal(1,"premature commit");@(negedge clk);end
    c_commit=1;c_ok=1;c_allowed=1;@(posedge clk);@(negedge clk);c_commit=0;c_ok=0;
    n=0;d=0;while(n<8)begin
     @(negedge clk);c_output_ready=cycle%7>=3;@(posedge clk);
     if(c_output_valid && c_output_ready)begin
      if(c_output_offset!==n[2:0] || {c_output_present,c_output_payload}!==record_fixtures[page_id*8+n])$fatal(1,"record mismatch");
      n=n+1;record_checks=record_checks+1;
     end
     d=d+1;if(d>200)$fatal(1,"record timeout");
    end
    @(negedge clk);c_output_ready=0;if(!c_done || c_error)$fatal(1,"decode finish");read_pages=read_pages+1;
   end else write_pages=write_pages+1;
   c_done_ready=1;done_ready=1;@(posedge clk);@(negedge clk);c_done_ready=0;done_ready=0;checks=checks+1;
  end
 endtask
 task bad_address(input reg[31:0] address);integer before_aw,before_ar;begin
  before_aw=aw_count;before_ar=ar_count;
  @(negedge clk);req_valid=1;req_write=1;req_address=address;req_cookie=72'h01ffffffffffffffff;
  @(posedge clk);@(negedge clk);req_valid=0;
  if(!done_valid || !done_error || fault || done_cookie!==72'h01ffffffffffffffff || aw_count!=before_aw || ar_count!=before_ar || m_awvalid || m_arvalid)$fatal(1,"invalid address accepted");
  done_ready=1;@(posedge clk);@(negedge clk);done_ready=0;checks=checks+1;
 end endtask
 initial begin #100000000;$fatal(1,"watchdog checks=%0d",checks);end
 initial begin
  if(!$value$plusargs("PAGES=%s",fixture_path))$fatal(1,"missing PAGES");$readmemh(fixture_path,fixtures);
  if(!$value$plusargs("RECORDS=%s",records_path))$fatal(1,"missing RECORDS");$readmemh(records_path,record_fixtures);
  reset_all;
  for(fr=0;fr<64;fr=fr+1)begin
   offset_coverage[(fr*3)%64]=1;
   transfer(fr*192,fr,0,0);transfer(fr*192,fr,1,0);
  end
  if(offset_coverage!==64'hffffffffffffffff)$fatal(1,"offset coverage");
  transfer(32'hffffff40,63,0,0);transfer(32'hffffff40,63,1,0);
  bad_address(1);bad_address(32'hffffff80);bad_address(32'hffffffc0);
  for(j=1;j<=7;j=j+1)begin
   reset_all;reads=j>=3 && j!=6;
   if(reads)transfer(4032,1,0,0);
   mode=j;transfer(4032,1,reads,1);errors=errors+1;
   if(req_ready)$fatal(1,"fault reopened");
  end
  // First beat read error with two remaining beats must be drained as well.
  reset_all;transfer(0,2,0,0);mode=3;transfer(0,2,1,1);errors=errors+1;
  $display("SMALL_CODEC_AXI_PASS checks=%0d write_pages=%0d read_pages=%0d errors=%0d records=%0d raw_beats=%0d",checks,write_pages,read_pages,errors,record_checks,raw_checks);
  $finish;
 end
endmodule
