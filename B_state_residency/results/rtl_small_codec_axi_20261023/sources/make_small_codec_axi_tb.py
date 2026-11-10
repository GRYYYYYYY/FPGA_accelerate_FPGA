"""Reuse independent AXI slave/scoreboards; replace directory driver with direct engine."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate():
 s=(ROOT/'hardware/tb/tb_codec_axi.sv').read_text()
 a=s.index('    reg rst=');b=s.index('    reg c_start=')
 ports=s[s.index('    wire [31:0] m_awaddr'):s.index('    backing_page_service')]
 s=s[:a]+'''    reg rst=1,req_valid=0,req_write=0,done_ready=0;
    reg [31:0] req_address=0;reg [71:0] req_cookie=0;
    wire req_ready,done_valid,done_error,busy,fault;wire [71:0] done_cookie;
    wire in_valid,in_ready,out_valid,out_ready;wire [511:0] in_data,out_data;
'''+ports+'''    scratch_page_axi_small dut(.*);
    reg [511:0] fixtures[0:191],memory[0:2047],write_words[0:2];
'''+s[b:]
 s=s.replace('module tb_codec_axi;','module tb_small_codec_axi;').replace('scratch_page_codec codec','scratch_page_codec_small codec')
 s=s.replace('[5:0] c_offset','[2:0] c_offset').replace('[5:0] c_output_offset','[2:0] c_output_offset').replace('record_fixtures[0:4095]','record_fixtures[0:511]')
 s=s.replace('c_raw_count>=21','c_raw_count>=3').replace('c_page*21','c_page*3').replace('c_raw_count==20','c_raw_count==2')
 s=s.replace('m_awlen>20','m_awlen>2').replace('m_arlen>20','m_arlen>2').replace('write_count>20','write_count>2')
 s=s.replace('memory[(aw_address>>6)+k]','memory[((aw_address>>6)+k)%2048]').replace('memory[(ar_address>>6)+read_position]','memory[((ar_address>>6)+read_position)%2048]')
 s=s[:s.index('    function automatic [63:0] make_cookie')]+TAIL
 return s
TAIL=r'''
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
'''
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_small_codec_axi.sv';s=generate()
 if p.exists():assert p.read_text()==s
 else:p.write_text(s)
