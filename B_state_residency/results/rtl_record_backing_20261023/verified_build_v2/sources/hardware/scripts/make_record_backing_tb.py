"""Independent AXI slave regression for the synthesizable record adapter.
Reuse frozen service checks; remove testbench codec commit/cancel controls.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 s=(ROOT/'hardware/tb/tb_backing_page_service.sv').read_text()
 s=s.replace('module tb_backing_page_service;', 'module tb_record_backing_service;')
 s=s.replace('reg [1:0] cmd_op=0;', 'reg [2:0] cmd_op=0;')
 s=s.replace('    reg in_valid=0,out_ready=0;reg [511:0] in_data=0;wire in_ready,out_valid;wire [511:0] out_data;', '''    reg record_in_valid=0,record_in_present=0;wire record_in_ready;
    reg [5:0] record_in_offset=0;reg [159:0] record_in_payload=0;
    wire record_out_valid,record_out_present;reg record_out_ready=0;
    wire [5:0] record_out_offset;wire [159:0] record_out_payload;''')
 s=s.replace('backing_page_service #(', 'record_backing_service #(')
 s=s.replace('    reg aw_pending=0', '''    reg [160:0] record_fixtures[0:4095];reg [4095:0] records_path;
    integer active_page=0,input_count=0,output_count=0,write_beats=0,record_checks=0,bad_inputs=0,malformed_reads=0,lookup_checks=0;
    reg memory_success_seen=0,held_record=0;reg [166:0] saved_record;
    always @(posedge clk)begin
        if(rst)begin held_record<=0;memory_success_seen<=0;end
        else begin
            if(record_in_valid && record_in_ready)input_count=input_count+1;
            if(held_record && (!record_out_valid || {record_out_offset,record_out_present,record_out_payload}!==saved_record))$fatal(1,"record changed under backpressure");
            held_record<=record_out_valid&&!record_out_ready;saved_record<={record_out_offset,record_out_present,record_out_payload};
            if(dut.service_valid && dut.state==4 && dut.service_status==0 && dut.op==1 && dut.cookie[58])memory_success_seen<=1;
            if(record_out_valid && !memory_success_seen)$fatal(1,"record before successful memory response");
            if(record_out_valid && record_out_ready)output_count=output_count+1;
            if(m_awvalid && input_count!=64)$fatal(1,"AXI started before all records validated");
            if(m_wvalid && m_wready)begin
                if(write_beats>=21 || m_wdata!==fixtures[active_page*21+write_beats])$fatal(1,"encoded AXI data mismatch");
                write_beats=write_beats+1;
            end
        end
    end
    reg aw_pending=0''')
 s=s.replace(',held_out=0','').replace('    reg [511:0] saved_out;','')
 s=s.replace(';held_out<=0','')
 s=s.replace('            if(held_out && (!out_valid || out_data!==saved_out))$fatal(1,"read stream changed under backpressure");\n','')
 s=s.replace('            held_out<=out_valid&&!out_ready;saved_out<=out_data;\n','')
 # Independent service command helper also supplies valid records for write PIN
 # rejection cases: encoding deliberately precedes any service command/PIN.
 a=s.index('    task automatic request(');b=s.index('    initial begin #100000000',a)
 s=s[:a]+'''    task automatic feed_record(input integer offset_value,input reg [160:0] value);
        integer d;
        begin
            @(negedge clk);record_in_valid=1;record_in_offset=offset_value;record_in_present=value[160];record_in_payload=value[159:0];
            d=0;@(posedge clk);while(!record_in_ready)begin @(posedge clk);d=d+1;if(d>100)$fatal(1,"record input timeout");end
            @(negedge clk);record_in_valid=0;record_in_payload='1;
        end
    endtask
    task automatic feed_page(input integer page_value);
        integer n;
        begin for(n=0;n<64;n=n+1)feed_record(n,record_fixtures[page_value*64+n]);end
    endtask
    task automatic request(input integer op,owner_value,frame_value,input reg [63:0] token,input integer fence,status,expected_frame,published);
        integer old_allocated,old_leased;
        begin
            old_allocated=allocated;old_leased=leased;
            if(op==1)begin input_count=0;output_count=0;write_beats=0;active_page=0;memory_success_seen=0;end
            send(op,owner_value,frame_value,token,fence);
            if(op==1 && !token[58] && !fault)feed_page(0);
            receive(status,expected_frame,published,token);
            if(op==4)begin
                if(allocated!=old_allocated || leased!=old_leased)$fatal(1,"lookup mutated allocation/lease");
                lookup_checks=lookup_checks+1;
            end
        end
    endtask
    task automatic transfer_page(input integer frame_value,page_value,transaction,reading,expect_error);
        reg [63:0] token;
        integer i,d,starting_b,need_b,prior_leases;
        begin
            current_frame=frame_value;expected_next_aw=frame_value*1344;expected_next_ar=frame_value*1344;
            token=make_cookie(24'h100000+frame_value,transaction,reading,test_slot);
            prior_leases=leased;starting_b=b_count;need_b=1+(((frame_value*1344)%4096+1344)>4096);
            input_count=0;output_count=0;write_beats=0;active_page=page_value;memory_success_seen=0;
            send(1,0,frame_value,token,0);
            if(!reading)feed_page(page_value);
            i=0;d=0;
            while(!rsp_valid)begin
                @(negedge clk);record_out_ready=reading && cycle%7>=3;
                @(posedge clk);
                if(record_out_valid && record_out_ready)begin
                    if(expect_error || i>=64 || record_out_offset!==i[5:0] || {record_out_present,record_out_payload}!==record_fixtures[page_value*64+i])$fatal(1,"record response mismatch");
                    i=i+1;record_checks=record_checks+1;
                end
                if(!reading && rsp_valid && !fault && b_count<starting_b+need_b)$fatal(1,"success before final B response");
                d=d+1;if(d>5000)$fatal(1,"record adapter response timeout");
            end
            @(negedge clk);record_out_ready=0;
            if(reading && !expect_error && i!=64)$fatal(1,"success before all decoded records consumed");
            if(reading && expect_error && i!=0)$fatal(1,"failed read exposed records");
            if(!reading && !expect_error && (write_beats!=21 || b_count!=starting_b+need_b))$fatal(1,"write incomplete");
            receive(expect_error?7:0,expect_error?0:frame_value,expect_error?0:1,token);
            if(reading && expect_error && (read_active || m_rvalid))$fatal(1,"undrained read burst after error completion");
            if(leased!==(prior_leases | (1<<test_slot)) || fault!==expect_error[0])$fatal(1,"lease released before consumer commit / wrong fault");
            if(!expect_error)begin if(reading)read_pages=read_pages+1;else write_pages=write_pages+1;end
        end
    endtask
'''+s[b:]
 s=s.replace('$readmemh(fixture_path,fixtures);', '$readmemh(fixture_path,fixtures);\n        if(!$value$plusargs("RECORDS=%s",records_path))$fatal(1,"missing RECORDS");\n        $readmemh(records_path,record_fixtures);')
 s=s.replace('        for(fr=0;fr<64;fr=fr+1)begin', '''        request(4,24'h100000,0,0,0,6,0,0);
        for(j=5;j<8;j=j+1)request(j,0,0,0,0,3,0,0);
        for(fr=0;fr<64;fr=fr+1)begin''',1)
 s=s.replace('            if(allocated!=fr+1)', '''            request(4,24'h100000+fr,0,0,0,0,fr,0);
            request(4,24'h200000+fr,0,0,0,6,0,0);
            if(allocated!=fr+1)''')
 s=s.replace('            request(0,24\'h100000+fr,0,0,0,0,fr,1);', '            request(0,24\'h100000+fr,0,0,0,0,fr,1);\n            request(4,24\'h100000+fr,0,0,0,0,fr,1);')
 s=s.replace("        request(0,24'h200000,0,0,0,4,0,0);", "        request(4,24'h200000,0,0,0,6,0,0);\n        request(0,24'h200000,0,0,0,4,0,0);")
 s=s.replace("        if(allocated!=0 || leased!=0)", "        request(4,24'h100000,0,0,0,6,0,0);\n        if(allocated!=0 || leased!=0)")
 s=s.replace('rst=1;mode=0;in_valid=0;out_ready=0;', 'rst=1;mode=0;record_in_valid=0;record_out_ready=0;')
 s=s.replace('request(2,0,fr,cookie,0,6,0,0);request(3,0,0,0,1,2,0,0);', 'request(2,0,fr,cookie,0,7,0,0);request(3,0,0,0,1,7,0,0);')
 s=s.replace("request(0,24'h100000+fr,0,0,0,0,fr,reads);", "request(0,24'h100000+fr,0,0,0,7,0,0);")
 s=s.replace('        $display("TEST_PASS backing_page_service', '''        // First write burst fails at address4032 while most encoded data remains.
        @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
        for(words=0;words<4;words=words+1)request(0,24'h100000+words,0,0,0,0,words,0);
        mode=1;transfer_page(3,1,0,0,1);if(write_beats!=1)$fatal(1,"expected partial write");errors=errors+1;
        // Invalid host records must not issue AXI, consume a tx or take a lease.
        for(j=0;j<3;j=j+1)begin
            @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
            request(0,24'h100000,0,0,0,0,0,0);
            baseline_b=aw_count;expected_b=b_count;input_count=0;write_beats=0;
            cookie=make_cookie(24'h100000,0,0,0);send(1,0,0,cookie,0);
            if(j==0)begin
                for(k=0;k<63;k=k+1)feed_record(k,record_fixtures[64+k]);
                feed_record(62,record_fixtures[127]);
            end else if(j==1)feed_record(0,record_fixtures[64]^(161'd1<<136));
            else feed_record(0,161'd1);
            receive(3,0,0,cookie);
            if(aw_count!=baseline_b || b_count!=expected_b || write_beats!=0 || leased!=0 || fault)$fatal(1,"bad input issued AXI or poisoned lease");
            bad_inputs=bad_inputs+1;
            transfer_page(0,1,0,0,0);request(2,0,0,cookie,0,0,0,1);
            transfer_page(0,1,1,1,0);request(2,0,0,make_cookie(24'h100000,1,1,0),0,0,0,1);
        end
        // Legal AXI success carrying a malformed canonical page: no records,
        // sticky wrapper fault, and even COMPLETE directory lease is retained.
        for(j=0;j<3;j=j+1)begin
            @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
            request(0,24'h100000,0,0,0,0,0,0);
            transfer_page(0,1,0,0,0);request(2,0,0,make_cookie(24'h100000,0,0,0),0,0,0,1);
            if(j==0)memory[0]=memory[0]^(512'd1<<200);
            else if(j==1)memory[20]=memory[20]^(512'd1<<511);
            else memory[0]=memory[0]^(512'd1<<224); // node1 absent but nonzero
            transfer_page(0,1,1,1,1);malformed_reads=malformed_reads+1;
            request(2,0,0,make_cookie(24'h100000,1,1,0),0,7,0,0);request(3,0,0,0,1,7,0,0);
            if(leased!=1)$fatal(1,"malformed read released address");
        end
        $display("TEST_PASS record_adapter records=%0d lookup_checks=%0d bad_inputs=%0d malformed_reads=%0d",record_checks,lookup_checks,bad_inputs,malformed_reads);
        $display("TEST_PASS record_backing_service''')
 p=ROOT/'hardware/tb/tb_record_backing_service.sv'
 if p.exists():raise FileExistsError(p)
 p.write_text(s)
if __name__=='__main__':main()
