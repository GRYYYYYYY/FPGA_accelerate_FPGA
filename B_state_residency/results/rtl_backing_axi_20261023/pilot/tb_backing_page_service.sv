`timescale 1ns/1ps
module tb_backing_page_service;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;
    wire cmd_ready,rsp_valid,rsp_published;
    reg [1:0] cmd_op=0;reg [23:0] cmd_owner=0;reg [5:0] cmd_frame=0;
    reg [63:0] cmd_cookie=0;reg fence_retired=0;
    wire [2:0] rsp_status;wire [5:0] rsp_frame;wire [31:0] rsp_address;wire [63:0] rsp_cookie;
    reg in_valid=0,out_ready=0;reg [511:0] in_data=0;wire in_ready,out_valid;wire [511:0] out_data;
    wire [3:0] leased;wire fault;wire [6:0] allocated;
    wire [31:0] m_awaddr,m_araddr;wire [7:0] m_awlen,m_arlen;wire [2:0] m_awsize,m_arsize;
    wire [1:0] m_awburst,m_arburst;wire [3:0] m_awid,m_arid;wire m_awvalid,m_arvalid;
    wire m_awready,m_arready,m_wready;wire [511:0] m_wdata;wire [63:0] m_wstrb;wire m_wlast,m_wvalid;
    reg [3:0] m_bid=0,m_rid=0;reg [1:0] m_bresp=0,m_rresp=0;reg m_bvalid=0,m_rvalid=0,m_rlast=0;
    wire m_bready,m_rready;reg [511:0] m_rdata=0;
    backing_page_service #(.FRAMES(64),.INDEX_BITS(6)) dut(.*);
    reg [511:0] fixtures[0:1343],memory[0:2047],write_words[0:20];
    reg aw_pending=0,wlast_seen=0,read_active=0;
    reg [31:0] aw_address=0,ar_address=0;
    integer aw_length=0,write_count=0,read_length=0,read_position=0,b_delay=0;
    integer cycle=0,aw_count=0,b_count=0,ar_count=0,r_count=0,checks=0,write_pages=0,read_pages=0;
    integer expected_next_aw=0,expected_next_ar=0,mode=0,current_frame=0;
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
                if(aw_pending || m_awid!=0 || m_awsize!=6 || m_awburst!=1 || m_awaddr[5:0]!=0 || m_awlen>20
                   || ({1'b0,m_awaddr[11:0]}+((m_awlen+1)*64)>4096) || m_awaddr!==expected_next_aw[31:0])$fatal(1,"bad AW burst address=%h expected=%h len=%0d",m_awaddr,expected_next_aw,m_awlen);
                aw_pending<=1;aw_address<=m_awaddr;aw_length<=m_awlen+1;aw_count<=aw_count+1;
                expected_next_aw=expected_next_aw+(m_awlen+1)*64;
            end
            if(m_wvalid && m_wready)begin
                if(write_count>20 || m_wstrb!==64'hffffffffffffffff)$fatal(1,"bad W beat");
                write_words[write_count]<=m_wdata;write_count<=write_count+1;
                if(m_wlast)wlast_seen<=1;
            end
            if(aw_pending && wlast_seen && !m_bvalid)begin
                if(write_count!=aw_length)$fatal(1,"WLAST/length mismatch");
                if(b_delay<23)b_delay<=b_delay+1;
                else begin
                    for(k=0;k<aw_length;k=k+1)memory[(aw_address>>6)+k]<=write_words[k];
                    m_bvalid<=1;m_bid<=mode==2?1:0;m_bresp<=mode==1?2:0;
                end
            end
            if(m_bvalid && m_bready)begin
                m_bvalid<=0;aw_pending<=0;wlast_seen<=0;write_count<=0;b_delay<=0;b_count<=b_count+1;
            end
            if(m_arvalid && m_arready)begin
                if(read_active || m_arid!=0 || m_arsize!=6 || m_arburst!=1 || m_araddr[5:0]!=0 || m_arlen>20
                   || ({1'b0,m_araddr[11:0]}+((m_arlen+1)*64)>4096) || m_araddr!==expected_next_ar[31:0])$fatal(1,"bad AR burst");
                read_active<=1;ar_address<=m_araddr;read_length<=m_arlen+1;read_position<=0;ar_count<=ar_count+1;
                expected_next_ar=expected_next_ar+(m_arlen+1)*64;
            end
            if(read_active && !m_rvalid && cycle%5>=2)begin
                m_rvalid<=1;m_rdata<=memory[(ar_address>>6)+read_position];
                m_rid<=mode==5?1:0;m_rresp<=mode==3?3:0;
                m_rlast<=mode==4?1:(read_position==read_length-1);
            end
            if(m_rvalid && m_rready)begin
                m_rvalid<=0;r_count<=r_count+1;
                if(read_position==read_length-1)read_active<=0;
                else read_position<=read_position+1;
            end
        end
    end
    function automatic [63:0] make_cookie(input integer owner_value,transaction,kind,slot);
        reg [63:0] result;
        begin result=0;result[25:2]=owner_value;result[41:26]=16'd1;result[57:42]=transaction;
            result[58]=kind;result[1:0]=slot;make_cookie=result;end
    endfunction
    task automatic send(input integer op,owner_value,frame_value,input reg [63:0] token,input integer fence);
        integer d;
        begin
            @(negedge clk);cmd_valid=1;cmd_op=op;cmd_owner=owner_value;cmd_frame=frame_value;cmd_cookie=token;fence_retired=fence;
            d=0;@(posedge clk);while(!cmd_ready)begin @(posedge clk);d=d+1;if(d>2000)$fatal(1,"command stuck");end
            @(negedge clk);cmd_valid=0;cmd_op=3;cmd_owner='1;cmd_frame='1;cmd_cookie='1;fence_retired=0;
        end
    endtask
    task automatic receive(input integer status,frame_value,published,input reg [63:0] token);
        integer d,h;
        begin
            d=0;while(!rsp_valid)begin @(negedge clk);d=d+1;if(d>2000)$fatal(1,"response stuck check=%0d",checks);end
            for(h=0;h<4;h=h+1)begin
                if(!rsp_valid || rsp_status!==status[2:0] || rsp_frame!==frame_value[5:0] || rsp_address!==32'(frame_value*1344)
                   || rsp_published!==published[0] || rsp_cookie!==token)$fatal(1,"service mismatch check=%0d status=%0d/%0d frame=%0d/%0d pub=%b/%0d",checks,rsp_status,status,rsp_frame,frame_value,rsp_published,published);
                @(negedge clk);
            end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
    endtask
    task automatic request(input integer op,owner_value,frame_value,input reg [63:0] token,input integer fence,status,expected_frame,published);
        begin send(op,owner_value,frame_value,token,fence);receive(status,expected_frame,published,token);end
    endtask
    task automatic transfer_page(input integer frame_value,page_value,transaction,reading,expect_error);
        reg [63:0] token;
        integer i,d,starting_b,need_b;
        begin
            current_frame=frame_value;expected_next_aw=frame_value*1344;expected_next_ar=frame_value*1344;
            token=make_cookie(24'h100000+frame_value,transaction,reading,0);
            starting_b=b_count;need_b=1+(((frame_value*1344)%4096+1344)>4096);
            send(1,0,frame_value,token,0);
            if(!reading)begin
                i=0;
                while(i<21 && !fault)begin
                    @(negedge clk);in_valid=1;in_data=fixtures[page_value*21+i];
                    d=0;@(posedge clk);
                    while(!in_ready && !fault)begin @(posedge clk);d=d+1;if(d>300)$fatal(1,"write stream stuck");end
                    if(in_ready)i=i+1;
                    @(negedge clk);in_valid=0;in_data='1;
                    if(rsp_valid && !fault && b_count<starting_b+need_b)$fatal(1,"success before final B response");
                end
                while(!rsp_valid)begin
                    @(negedge clk);if(rsp_valid && !fault && b_count<starting_b+need_b)$fatal(1,"early B completion");
                end
                if(!expect_error && (b_count!=starting_b+need_b || i!=21))$fatal(1,"write response count mismatch");
                if(!expect_error)write_pages=write_pages+1;
            end else begin
                i=0;d=0;
                while(!rsp_valid)begin
                    @(negedge clk);out_ready=cycle%7>=3;
                    @(posedge clk);
                    if(out_valid && out_ready)begin
                        if(i>=21 || out_data!==fixtures[page_value*21+i])$fatal(1,"read byte mismatch frame=%0d beat=%0d",frame_value,i);
                        i=i+1;
                    end
                    d=d+1;if(d>3000)$fatal(1,"read stream stuck");
                end
                @(negedge clk);out_ready=0;
                if(!expect_error && i!=21)$fatal(1,"early read completion");
                if(expect_error && i!=0)$fatal(1,"erroneous read beat exposed");
                if(!expect_error)read_pages=read_pages+1;
            end
            receive(expect_error?7:0,expect_error?0:frame_value,expect_error?0:1,token);
            if(leased!=1 || fault!==expect_error[0])$fatal(1,"lease released before consumer commit / wrong fault");
        end
    endtask
    initial begin #100000000;$fatal(1,"watchdog checks=%0d",checks);end
    initial begin
        if(!$value$plusargs("PAGES=%s",fixture_path))$fatal(1,"missing PAGES");
        $readmemh(fixture_path,fixtures);
        repeat(3)@(negedge clk);rst=0;
        for(fr=0;fr<64;fr=fr+1)begin
            offset_coverage[(fr*21)%64]=1;
            request(0,24'h100000+fr,0,0,0,0,fr,0);
            request(0,24'h100000+fr,0,0,0,0,fr,0);
            if(allocated!=fr+1)$fatal(1,"duplicate owner allocation");
            cookie=make_cookie(24'h100000+fr,txid,1,0);
            request(1,0,fr,cookie,0,6,0,0); // unpublished frame is unreadable
            cookie=make_cookie(24'h100000+fr+1,txid,0,0);
            request(1,0,fr,cookie,0,1,0,0); // owner mismatch must not burn tx
            transfer_page(fr,fr,txid,0,0);cookie=make_cookie(24'h100000+fr,txid,0,0);
            request(0,24'h100000+fr,0,0,0,0,fr,1);
            request(1,0,fr,make_cookie(24'h100000+fr,txid+1,1,1),0,2,0,0); // same address leased
            request(2,0,fr,cookie^(64'd1<<26),0,1,0,0);
            request(3,0,0,0,1,2,0,0); // completed memory is still leased
            request(2,0,fr,cookie,0,0,fr,1);
            request(1,0,fr,cookie,0,5,0,0); // old transaction cannot repin
            txid=txid+1;
            transfer_page(fr,fr,txid,1,0);cookie=make_cookie(24'h100000+fr,txid,1,0);
            request(2,0,fr,cookie,0,0,fr,1);txid=txid+1;
        end
        if(offset_coverage!==64'hffffffffffffffff)$fatal(1,"4KB offsets incomplete");
        request(0,24'h200000,0,0,0,4,0,0);
        request(0,24'h10003f,0,0,0,0,63,1);
        request(3,0,0,0,0,2,0,0);request(3,0,0,0,1,0,0,0);
        if(allocated!=0 || leased!=0)$fatal(1,"recycle did not reset ownership");
        request(0,24'h100000,0,0,0,0,0,0);
        request(1,0,0,make_cookie(24'h100000,0,1,0),0,6,0,0); // old raw memory remains hidden
        transfer_page(0,0,0,0,0);request(2,0,0,make_cookie(24'h100000,0,0,0),0,0,0,1);
        // Separate coordinated cold starts for fail-closed AXI error cases.
        for(j=1;j<=5;j=j+1)begin
            @(negedge clk);rst=1;mode=0;in_valid=0;out_ready=0;
            repeat(3)@(negedge clk);rst=0;
            request(0,24'h100000,0,0,0,0,0,0);
            if(j>=3)begin
                transfer_page(0,1,0,0,0);request(2,0,0,make_cookie(24'h100000,0,0,0),0,0,0,1);
            end
            mode=j;transfer_page(0,1,j>=3?1:0,j>=3,1);
            cookie=make_cookie(24'h100000,j>=3?1:0,j>=3,0);
            request(2,0,0,cookie,0,6,0,0);request(3,0,0,0,1,2,0,0);
            request(1,0,0,cookie,0,7,0,0);
            request(0,24'h100000,0,0,0,0,0,j>=3);
            errors=errors+1;
        end
        $display("TEST_PASS backing_page_service checks=%0d write_pages=%0d read_pages=%0d error_cases=%0d aw_bursts=%0d ar_bursts=%0d b_responses=%0d r_beats=%0d",checks,write_pages,read_pages,errors,aw_count,ar_count,b_count,r_count);
        $finish;
    end
endmodule
