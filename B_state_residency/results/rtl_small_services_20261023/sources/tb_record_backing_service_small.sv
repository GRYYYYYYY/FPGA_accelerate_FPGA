`timescale 1ns/1ps
module tb_record_backing_service_small;
    integer checkpoint_aw,checkpoint_ar;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;
    wire cmd_ready,rsp_valid,rsp_published;
    reg [2:0] cmd_op=0;reg [26:0] cmd_owner=0;reg [5:0] cmd_frame=0;
    reg [71:0] cmd_cookie=0;reg fence_retired=0;
    wire [2:0] rsp_status;wire [5:0] rsp_frame;wire [31:0] rsp_address;wire [71:0] rsp_cookie;
    reg record_in_valid=0,record_in_present=0;wire record_in_ready;
    reg [2:0] record_in_offset=0;reg [159:0] record_in_payload=0;
    wire record_out_valid,record_out_present;reg record_out_ready=0;
    wire [2:0] record_out_offset;wire [159:0] record_out_payload;
    wire [31:0] leased;wire fault;wire [6:0] allocated;
    wire [31:0] m_awaddr,m_araddr;wire [7:0] m_awlen,m_arlen;wire [2:0] m_awsize,m_arsize;
    wire [1:0] m_awburst,m_arburst;wire [3:0] m_awid,m_arid;wire m_awvalid,m_arvalid;
    wire m_awready,m_arready,m_wready;wire [511:0] m_wdata;wire [63:0] m_wstrb;wire m_wlast,m_wvalid;
    reg [3:0] m_bid=0,m_rid=0;reg [1:0] m_bresp=0,m_rresp=0;reg m_bvalid=0,m_rvalid=0,m_rlast=0;
    wire m_bready,m_rready;reg [511:0] m_rdata=0;
    record_backing_service_small #(.FRAMES(64),.INDEX_BITS(6),.HASH_BITS(8),.PROBE_LIMIT(8),.EPOCH_BITS(2)) dut(.*);
    reg [511:0] fixtures[0:191],memory[0:2047],write_words[0:2];
    reg [160:0] record_fixtures[0:511];reg [4095:0] records_path;
    integer active_page=0,input_count=0,output_count=0,write_beats=0,record_checks=0,bad_inputs=0,malformed_reads=0,lookup_checks=0;
    reg memory_success_seen=0,held_record=0;reg [163:0] saved_record;
    always @(posedge clk)begin
        if(rst)begin held_record<=0;memory_success_seen<=0;end
        else begin
            if(record_in_valid && record_in_ready)input_count=input_count+1;
            if(held_record && (!record_out_valid || {record_out_offset,record_out_present,record_out_payload}!==saved_record))$fatal(1,"record changed under backpressure");
            held_record<=record_out_valid&&!record_out_ready;saved_record<={record_out_offset,record_out_present,record_out_payload};
            if(dut.service_valid && dut.state==4 && dut.service_status==0 && dut.op==1 && dut.cookie[64])memory_success_seen<=1;
            if(record_out_valid && !memory_success_seen)$fatal(1,"record before successful memory response");
            if(record_out_valid && record_out_ready)output_count=output_count+1;
            if(m_awvalid && input_count!=8)$fatal(1,"AXI started before all records validated");
            if(m_wvalid && m_wready)begin
                if(write_beats>=3 || m_wdata!==fixtures[active_page*3+write_beats])$fatal(1,"encoded AXI data mismatch");
                write_beats=write_beats+1;
            end
        end
    end
    reg aw_pending=0,wlast_seen=0,read_active=0;
    reg [31:0] aw_address=0,ar_address=0;
    integer aw_length=0,write_count=0,read_length=0,read_position=0,b_delay=0;
    integer cycle=0,aw_count=0,b_count=0,ar_count=0,r_count=0,checks=0,write_pages=0,read_pages=0;
    integer expected_next_aw=0,expected_next_ar=0,mode=0,current_frame=0,test_slot=0;
    integer j,k,fr,txid=0,baseline_b,expected_b,reads,words,deadline,errors=0;
    reg [63:0] offset_coverage=0;reg [71:0] cookie;
    reg [4095:0] fixture_path;
    reg held_aw=0,held_w=0,held_ar=0;
    reg [48:0] saved_aw,saved_ar;
    reg [576:0] saved_w;

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
            held_aw<=0;held_w<=0;held_ar<=0;
        end else begin
            if(held_aw && (!m_awvalid || {m_awaddr,m_awlen,m_awsize,m_awburst,m_awid}!==saved_aw))$fatal(1,"AW changed under backpressure");
            if(held_ar && (!m_arvalid || {m_araddr,m_arlen,m_arsize,m_arburst,m_arid}!==saved_ar))$fatal(1,"AR changed under backpressure");
            if(held_w && (!m_wvalid || {m_wdata,m_wstrb,m_wlast}!==saved_w))$fatal(1,"W changed under backpressure");
            held_aw<=m_awvalid&&!m_awready;saved_aw<={m_awaddr,m_awlen,m_awsize,m_awburst,m_awid};
            held_ar<=m_arvalid&&!m_arready;saved_ar<={m_araddr,m_arlen,m_arsize,m_arburst,m_arid};
            held_w<=m_wvalid&&!m_wready;saved_w<={m_wdata,m_wstrb,m_wlast};
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
                    for(k=0;k<aw_length;k=k+1)memory[(aw_address>>6)+k]<=write_words[k];
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
                m_rvalid<=1;m_rdata<=memory[(ar_address>>6)+read_position];
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
    function automatic [71:0] make_cookie(input integer owner_value,transaction,kind,slot);
        reg [71:0] result;
        begin result=0;result[31:5]=owner_value;result[47:32]=16'd1;result[63:48]=transaction;
            result[64]=kind;result[4:0]=slot;make_cookie=result;end
    endfunction
    task automatic send(input integer op,owner_value,frame_value,input reg [71:0] token,input integer fence);
        integer d;
        begin
            @(negedge clk);cmd_valid=1;cmd_op=op;cmd_owner=owner_value;cmd_frame=frame_value;cmd_cookie=token;fence_retired=fence;
            d=0;@(posedge clk);while(!cmd_ready)begin @(posedge clk);d=d+1;if(d>2000)$fatal(1,"command stuck");end
            @(negedge clk);cmd_valid=0;cmd_op=3;cmd_owner='1;cmd_frame='1;cmd_cookie='1;fence_retired=0;
        end
    endtask
    task automatic receive(input integer status,frame_value,published,input reg [71:0] token);
        integer d,h;
        begin
            d=0;while(!rsp_valid)begin @(negedge clk);d=d+1;if(d>2000)$fatal(1,"response stuck check=%0d",checks);end
            for(h=0;h<4;h=h+1)begin
                if(!rsp_valid || rsp_status!==status[2:0] || rsp_frame!==frame_value[5:0] || rsp_address!==32'(frame_value*192)
                   || rsp_published!==published[0] || rsp_cookie!==token)$fatal(1,"service mismatch check=%0d status=%0d/%0d frame=%0d/%0d pub=%b/%0d",checks,rsp_status,status,rsp_frame,frame_value,rsp_published,published);
                @(negedge clk);
            end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
    endtask
    task automatic feed_record(input integer offset_value,input reg [160:0] value);
        integer d;
        begin
            @(negedge clk);record_in_valid=1;record_in_offset=offset_value;record_in_present=value[160];record_in_payload=value[159:0];
            d=0;@(posedge clk);while(!record_in_ready)begin @(posedge clk);d=d+1;if(d>100)$fatal(1,"record input timeout");end
            @(negedge clk);record_in_valid=0;record_in_payload='1;
        end
    endtask
    task automatic feed_page(input integer page_value);
        integer n;
        begin for(n=0;n<8;n=n+1)feed_record(n,record_fixtures[page_value*8+n]);end
    endtask
    task automatic request(input integer op,owner_value,frame_value,input reg [71:0] token,input integer fence,status,expected_frame,published);
        integer old_allocated,old_leased;
        begin
            old_allocated=allocated;old_leased=leased;
            if(op==1)begin input_count=0;output_count=0;write_beats=0;active_page=0;memory_success_seen=0;end
            send(op,owner_value,frame_value,token,fence);
            if(op==1 && !token[64] && !fault)feed_page(0);
            receive(status,expected_frame,published,token);
            if(op==4)begin
                if(allocated!=old_allocated || leased!=old_leased)$fatal(1,"lookup mutated allocation/lease");
                lookup_checks=lookup_checks+1;
            end
        end
    endtask
    task automatic transfer_page(input integer frame_value,page_value,transaction,reading,expect_error);
        reg [71:0] token;
        integer i,d,starting_b,need_b,prior_leases;
        begin
            current_frame=frame_value;expected_next_aw=frame_value*192;expected_next_ar=frame_value*192;
            token=make_cookie(27'h7000000+frame_value,transaction,reading,test_slot);
            prior_leases=leased;starting_b=b_count;need_b=1+(((frame_value*192)%4096+192)>4096);
            input_count=0;output_count=0;write_beats=0;active_page=page_value;memory_success_seen=0;
            send(1,0,frame_value,token,0);
            if(!reading)feed_page(page_value);
            i=0;d=0;
            while(!rsp_valid)begin
                @(negedge clk);record_out_ready=reading && cycle%7>=3;
                @(posedge clk);
                if(record_out_valid && record_out_ready)begin
                    if(expect_error || i>=8 || record_out_offset!==i[2:0] || {record_out_present,record_out_payload}!==record_fixtures[page_value*8+i])$fatal(1,"record response mismatch");
                    i=i+1;record_checks=record_checks+1;
                end
                if(!reading && rsp_valid && !fault && b_count<starting_b+need_b)$fatal(1,"success before final B response");
                d=d+1;if(d>5000)$fatal(1,"record adapter response timeout");
            end
            @(negedge clk);record_out_ready=0;
            if(reading && !expect_error && i!=8)$fatal(1,"success before all decoded records consumed");
            if(reading && expect_error && i!=0)$fatal(1,"failed read exposed records");
            if(!reading && !expect_error && (write_beats!=3 || b_count!=starting_b+need_b))$fatal(1,"write incomplete");
            receive(expect_error?7:0,expect_error?0:frame_value,expect_error?0:1,token);
            if(reading && expect_error && (read_active || m_rvalid))$fatal(1,"undrained read burst after error completion");
            if(leased!==(prior_leases | (64'd1<<test_slot)) || fault!==expect_error[0])$fatal(1,"lease released before consumer commit / wrong fault");
            if(!expect_error)begin if(reading)read_pages=read_pages+1;else write_pages=write_pages+1;end
        end
    endtask
    initial begin #100000000;$fatal(1,"watchdog checks=%0d",checks);end
    initial begin
        if(!$value$plusargs("PAGES=%s",fixture_path))$fatal(1,"missing PAGES");
        $readmemh(fixture_path,fixtures);
        if(!$value$plusargs("RECORDS=%s",records_path))$fatal(1,"missing RECORDS");
        $readmemh(records_path,record_fixtures);
        repeat(3)@(negedge clk);rst=0;
        request(4,27'h7000000,0,0,0,6,0,0);
        for(j=6;j<8;j=j+1)request(j,0,0,0,0,3,0,0);
        for(fr=0;fr<64;fr=fr+1)begin
            offset_coverage[(fr*3)%64]=1;
            request(0,27'h7000000+fr,0,0,0,0,fr,0);
            request(0,27'h7000000+fr,0,0,0,0,fr,0);
            request(4,27'h7000000+fr,0,0,0,0,fr,0);
            request(4,27'h6000000+fr,0,0,0,6,0,0);
            if(allocated!=fr+1)$fatal(1,"duplicate owner allocation");
            cookie=make_cookie(27'h7000000+fr,txid,1,0);
            request(1,0,fr,cookie,0,6,0,0); // unpublished frame is unreadable
            cookie=make_cookie(27'h7000000+fr+1,txid,0,0);
            request(1,0,fr,cookie,0,1,0,0); // owner mismatch must not burn tx
            transfer_page(fr,fr,txid,0,0);cookie=make_cookie(27'h7000000+fr,txid,0,0);
            request(0,27'h7000000+fr,0,0,0,0,fr,1);
            request(4,27'h7000000+fr,0,0,0,0,fr,1);
            request(1,0,fr,make_cookie(27'h7000000+fr,txid+1,1,1),0,2,0,0); // same address leased
            request(2,0,fr,cookie^(72'd1<<32),0,1,0,0);
            request(3,0,0,0,1,2,0,0); // completed memory is still leased
            request(2,0,fr,cookie,0,0,fr,1);
            request(1,0,fr,cookie,0,5,0,0); // old transaction cannot repin
            txid=txid+1;
            transfer_page(fr,fr,txid,1,0);cookie=make_cookie(27'h7000000+fr,txid,1,0);
            request(2,0,fr,cookie,0,0,fr,1);txid=txid+1;
        end
        if(offset_coverage!==64'hffffffffffffffff)$fatal(1,"4KB offsets incomplete");
        // All published raw pages survive an internal transaction-ID recycle.
        checkpoint_aw=aw_count;checkpoint_ar=ar_count;
        request(5,0,0,0,0,2,0,0);
        request(5,0,0,0,1,0,0,0);
        if(allocated!=64 || leased!=0 || aw_count!=checkpoint_aw || ar_count!=checkpoint_ar)
            $fatal(1,"checkpoint metadata or unexpected AXI");
        txid=0;
        for(fr=0;fr<64;fr=fr+1)begin
            request(4,27'h7000000+fr,0,0,0,0,fr,1);
            transfer_page(fr,fr,txid,1,0);
            cookie=make_cookie(27'h7000000+fr,txid,1,0);
            request(5,0,0,0,1,2,0,0);
            request(2,0,fr,cookie,0,0,fr,1);txid=txid+1;
        end
        $display("RETAINED_SERVICE_CONTENT_PASS pages=64 records=512");
        // Four independent completed transfers retain address leases until
        // their consumers commit, and can retire in reverse order.
        for(test_slot=0;test_slot<32;test_slot=test_slot+1)begin
            transfer_page(test_slot,test_slot,txid+test_slot,0,0);
            if(leased!=((64'd1<<(test_slot+1))-1))$fatal(1,"independent lease lost");
        end
        request(3,0,0,0,1,2,0,0);
        for(test_slot=31;test_slot>=0;test_slot=test_slot-1)begin
            cookie=make_cookie(27'h7000000+test_slot,txid+test_slot,0,test_slot);
            request(2,0,test_slot,cookie,0,0,test_slot,1);
            if(leased!=((64'd1<<test_slot)-1))$fatal(1,"wrong lease retired");
        end
        test_slot=0;txid=txid+32;
        request(4,27'h6000000,0,0,0,6,0,0);
        request(0,27'h6000000,0,0,0,4,0,0);
        request(0,27'h700003f,0,0,0,0,63,1);
        request(3,0,0,0,0,2,0,0);request(3,0,0,0,1,0,0,0);
        request(4,27'h7000000,0,0,0,6,0,0);
        if(allocated!=0 || leased!=0)$fatal(1,"recycle did not reset ownership");
        request(0,27'h7000000,0,0,0,0,0,0);
        request(1,0,0,make_cookie(27'h7000000,0,1,0),0,6,0,0); // old raw memory remains hidden
        transfer_page(0,0,0,0,0);request(2,0,0,make_cookie(27'h7000000,0,0,0),0,0,0,1);
        // Separate coordinated cold starts for fail-closed AXI error cases.
        for(j=1;j<=7;j=j+1)begin
            @(negedge clk);rst=1;mode=0;record_in_valid=0;record_out_ready=0;
            repeat(3)@(negedge clk);rst=0;
            fr=j>=6?21:0;
            for(words=0;words<=fr;words=words+1)request(0,27'h7000000+words,0,0,0,0,words,0);
            reads=(j>=3 && j!=6);
            if(reads)begin
                transfer_page(fr,1,0,0,0);request(2,0,fr,make_cookie(27'h7000000+fr,0,0,0),0,0,fr,1);
            end
            mode=j;transfer_page(fr,1,reads?1:0,reads,1);
            cookie=make_cookie(27'h7000000+fr,reads?1:0,reads,0);
            request(2,0,fr,cookie,0,7,0,0);request(3,0,0,0,1,7,0,0);
            request(1,0,fr,cookie,0,7,0,0);
            request(0,27'h7000000+fr,0,0,0,7,0,0);
            errors=errors+1;
        end
        // First write burst fails at address4032 while most encoded data remains.
        @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
        for(words=0;words<22;words=words+1)request(0,27'h7000000+words,0,0,0,0,words,0);
        mode=1;transfer_page(21,1,0,0,1);if(write_beats!=1)$fatal(1,"expected partial write");errors=errors+1;
        // Invalid host records must not issue AXI, consume a tx or take a lease.
        for(j=0;j<3;j=j+1)begin
            @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
            request(0,27'h7000000,0,0,0,0,0,0);
            baseline_b=aw_count;expected_b=b_count;input_count=0;write_beats=0;
            cookie=make_cookie(27'h7000000,0,0,0);send(1,0,0,cookie,0);
            if(j==0)begin
                for(k=0;k<7;k=k+1)feed_record(k,record_fixtures[8+k]);
                feed_record(6,record_fixtures[15]);
            end else if(j==1)feed_record(0,record_fixtures[8]^(161'd1<<136));
            else feed_record(0,161'd1);
            receive(3,0,0,cookie);
            if(aw_count!=baseline_b || b_count!=expected_b || write_beats!=0 || leased!=0 || fault)$fatal(1,"bad input issued AXI or poisoned lease");
            bad_inputs=bad_inputs+1;
            transfer_page(0,1,0,0,0);request(2,0,0,cookie,0,0,0,1);
            transfer_page(0,1,1,1,0);request(2,0,0,make_cookie(27'h7000000,1,1,0),0,0,0,1);
        end
        // Legal AXI success carrying a malformed canonical page: no records,
        // sticky wrapper fault, and even COMPLETE directory lease is retained.
        for(j=0;j<3;j=j+1)begin
            @(negedge clk);rst=1;mode=0;repeat(3)@(negedge clk);rst=0;
            request(0,27'h7000000,0,0,0,0,0,0);
            transfer_page(0,1,0,0,0);request(2,0,0,make_cookie(27'h7000000,0,0,0),0,0,0,1);
            if(j==0)memory[0]=memory[0]^(512'd1<<144);
            else if(j==1)memory[2]=memory[2]^(512'd1<<511);
            else memory[0]=memory[0]^(512'd1<<328); // node1 absent but nonzero
            transfer_page(0,1,1,1,1);malformed_reads=malformed_reads+1;
            request(2,0,0,make_cookie(27'h7000000,1,1,0),0,7,0,0);request(3,0,0,0,1,7,0,0);
            if(leased!=1)$fatal(1,"malformed read released address");
        end
        $display("TEST_PASS record_adapter records=%0d lookup_checks=%0d bad_inputs=%0d malformed_reads=%0d",record_checks,lookup_checks,bad_inputs,malformed_reads);
        $display("TEST_PASS record_backing_service checks=%0d write_pages=%0d read_pages=%0d error_cases=%0d aw_bursts=%0d ar_bursts=%0d b_responses=%0d r_beats=%0d",checks,write_pages,read_pages,errors,aw_count,ar_count,b_count,r_count);
        $finish;
    end
endmodule
