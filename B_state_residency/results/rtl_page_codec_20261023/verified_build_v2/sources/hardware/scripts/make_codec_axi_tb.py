"""Derive composition test from the frozen independent AXI slave/service test.
The testbench coordinator represents the future synthesizable adapter: it is
not evidence that COMPLETE/RETIRE/fence have been integrated into the page core.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=ROOT/'hardware/tb/tb_backing_page_service.sv'
 s=p.read_text().replace('module tb_backing_page_service;', 'module tb_codec_axi;')
 s=s.replace('reg in_valid=0,out_ready=0;reg [511:0] in_data=0;', 'wire in_valid,out_ready;wire [511:0] in_data;')
 extra='''
    reg c_start=0,c_read=0,c_cancel=0,c_input_valid=0,c_present=0;
    wire c_start_ready,c_busy,c_input_ready;
    reg [5:0] c_offset=0;reg [159:0] c_payload=0;
    wire c_output_valid,c_output_present;reg c_output_ready=0;
    wire [5:0] c_output_offset;wire [159:0] c_output_payload;
    wire c_raw_last,c_commit_ready,c_done,c_error;
    reg c_commit=0,c_ok=0,c_done_ready=0,c_allowed=0;
    reg [160:0] record_fixtures[0:4095];reg [4095:0] records_path;
    integer record_checks=0,raw_checks=0,c_raw_count=0,c_page=0;
    scratch_page_codec codec(.clk(clk),.rst(rst),.start_valid(c_start),.start_ready(c_start_ready),.start_decode(c_read),
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
        if(c_raw_count>=21 || in_data!==fixtures[c_page*21+c_raw_count] || c_raw_last!==(c_raw_count==20))$fatal(1,"codec AXI write byte mismatch");
        c_raw_count=c_raw_count+1;raw_checks=raw_checks+1;
      end
      if(out_valid && out_ready)begin
        if(c_raw_count>=21 || out_data!==fixtures[c_page*21+c_raw_count])$fatal(1,"codec AXI read byte mismatch");
        c_raw_count=c_raw_count+1;raw_checks=raw_checks+1;
      end
    end
'''
 s=s.replace('    reg aw_pending=0',extra+'    reg aw_pending=0')
 a=s.index('    task automatic transfer_page(');b=s.index('    initial begin #100000000',a)
 s=s[:a]+'''    task automatic transfer_page(input integer frame_value,page_value,transaction,reading,expect_error);
        reg [63:0] token;
        integer i,d,starting_b,need_b,prior_leases;
        begin
            current_frame=frame_value;expected_next_aw=frame_value*1344;expected_next_ar=frame_value*1344;
            token=make_cookie(24'h100000+frame_value,transaction,reading,test_slot);
            prior_leases=leased;starting_b=b_count;need_b=1+(((frame_value*1344)%4096+1344)>4096);
            @(negedge clk);if(!c_start_ready)$fatal(1,"codec start blocked");
            c_start=1;c_read=reading;c_allowed=0;c_raw_count=0;c_page=page_value;
            @(posedge clk);@(negedge clk);c_start=0;
            send(1,0,frame_value,token,0);
            if(!reading)begin
                for(i=0;i<64;i=i+1)begin
                    @(negedge clk);c_input_valid=1;c_offset=i;c_present=record_fixtures[page_value*64+i][160];c_payload=record_fixtures[page_value*64+i][159:0];
                    @(posedge clk);while(!c_input_ready)@(posedge clk);
                    @(negedge clk);c_input_valid=0;c_payload='1;
                end
            end
            d=0;
            while(!rsp_valid)begin
                @(negedge clk);d=d+1;if(d>4000)$fatal(1,"codec AXI response timeout");
                if(!reading && rsp_valid && !fault && b_count<starting_b+need_b)$fatal(1,"success before B responses");
            end
            if(!expect_error)begin
                if(c_raw_count!=21)$fatal(1,"incomplete raw page on success");
                if(!reading && (!c_done || c_error || b_count!=starting_b+need_b))$fatal(1,"incomplete encode/B on success");
            end
            receive(expect_error?7:0,expect_error?0:frame_value,expect_error?0:1,token);
            if(reading && expect_error && (read_active || m_rvalid))$fatal(1,"undrained read error burst");
            if(leased!==(prior_leases | (1<<test_slot)) || fault!==expect_error[0])$fatal(1,"lease released before codec consumer");
            if(expect_error)begin
                if(!c_done)begin @(negedge clk);c_cancel=1;@(posedge clk);@(negedge clk);c_cancel=0;end
                if(!c_done || (reading && !c_error) || c_output_valid)$fatal(1,"failed AXI codec cancellation");
            end else if(reading)begin
                // Only the successful service response authorizes decoded output.
                d=0;while(!c_commit_ready)begin @(negedge clk);d=d+1;if(d>40)$fatal(1,"codec commit wait");end
                repeat(13)begin if(c_output_valid)$fatal(1,"record before commit");@(negedge clk);end
                c_commit=1;c_ok=1;c_allowed=1;
                @(posedge clk);@(negedge clk);c_commit=0;c_ok=0;
                i=0;d=0;
                while(i<64)begin
                    @(negedge clk);c_output_ready=cycle%7>=3;@(posedge clk);
                    if(c_output_valid && c_output_ready)begin
                        if(c_output_offset!==i[5:0] || {c_output_present,c_output_payload}!==record_fixtures[page_value*64+i])$fatal(1,"AXI decoded record mismatch");
                        i=i+1;record_checks=record_checks+1;
                    end
                    d=d+1;if(d>2000)$fatal(1,"codec output timeout");
                end
                @(negedge clk);c_output_ready=0;
                if(!c_done || c_error)$fatal(1,"decode incomplete after records");
                read_pages=read_pages+1;
            end else write_pages=write_pages+1;
            if(leased!==(prior_leases | (1<<test_slot)))$fatal(1,"codec retired address lease");
            repeat(3)@(negedge clk);
            c_done_ready=1;@(posedge clk);@(negedge clk);c_done_ready=0;
        end
    endtask
'''+s[b:]
 s=s.replace('$readmemh(fixture_path,fixtures);', '$readmemh(fixture_path,fixtures);\n        if(!$value$plusargs("RECORDS=%s",records_path))$fatal(1,"missing RECORDS");\n        $readmemh(records_path,record_fixtures);')
 s=s.replace('rst=1;mode=0;in_valid=0;out_ready=0;', 'rst=1;mode=0;c_input_valid=0;c_output_ready=0;')
 s=s.replace('        $display("TEST_PASS backing_page_service', '''        // First-burst failure at offset 4032 must abort a partially encoded page.
        @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
        for(words=0;words<4;words=words+1)request(0,24'h100000+words,0,0,0,0,words,0);
        mode=1;transfer_page(3,1,0,0,1);
        if(c_raw_count!=1)$fatal(1,"expected partial write before B failure");errors=errors+1;
        $display("TEST_PASS codec_axi records=%0d raw_beats=%0d",record_checks,raw_checks);
        $display("TEST_PASS codec_axi_service''')
 target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'hardware/tb/tb_codec_axi.sv'
 if target.exists():raise FileExistsError(target)
 target.write_text(s)
if __name__=='__main__':main()
