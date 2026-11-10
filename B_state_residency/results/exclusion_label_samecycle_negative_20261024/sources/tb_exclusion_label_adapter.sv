`timescale 1ns/1ps
module tb_exclusion_label_adapter;
`ifdef TOKEN_SMALL
    localparam TOKEN_BITS=3;
`else
    localparam TOKEN_BITS=32;
`endif
    reg clk=0; always #5 clk=~clk;
    reg rst=1;
    reg req_valid=0; wire req_ready;
    reg [31:0] req_node=0, req_generation=0, req_phase=0;
    reg [1:0] req_query=0; reg [3:0] req_price=0;
    wire resolve_valid; reg resolve_ready=0;
    wire [31:0] resolve_token, resolve_generation, resolve_phase;
    wire [20:0] resolve_page; wire [1:0] resolve_query; wire [3:0] resolve_price;
    reg map_valid=0; wire map_ready;
    reg [31:0] map_token=0, map_generation=0, map_phase=0;
    reg [20:0] map_page=0; reg [1:0] map_query=0;
    reg [3:0] map_price=0, map_status=0;
    reg [4:0] map_slot=0; reg [15:0] map_binding_generation=0;
    wire native_cmd_valid, native_cmd_ready;
    wire [3:0] native_cmd_op, native_cmd_price;
    wire [4:0] native_cmd_slot; wire [1:0] native_cmd_query;
    wire [20:0] native_cmd_page; wire [15:0] native_cmd_generation;
    wire [2:0] native_cmd_offset, native_cmd_field;
    wire [31:0] native_cmd_value;
    wire native_rsp_valid, native_rsp_ready;
    wire [3:0] native_rsp_status; wire [159:0] native_rsp_payload;
    wire native_rsp_present, native_fault;
    wire rsp_valid; reg rsp_ready=0;
    wire [3:0] rsp_status, rsp_service_status;
    wire [31:0] rsp_generation, rsp_phase, rsp_value;
    wire rsp_present, fault;
    exclusion_label_adapter #(.TOKEN_BITS(TOKEN_BITS)) dut(.*);

    // Host initialization and resolver fault injection are test-only agents.
    // The read service is the complete frozen sparse_records endpoint RTL.
    reg bridge_mode=0, hold_native=0, hold_reply=0, inject_fault=0;
    reg stray_native=0; reg [3:0] override_status=0;
    reg host_valid=0,host_ready=0;
    reg [3:0] host_op=0,host_price=0;
    reg [4:0] host_slot=0; reg [1:0] host_query=0;
    reg [20:0] host_page=0; reg [15:0] host_generation=0;
    reg [2:0] host_offset=0,host_field=0; reg [31:0] host_value=0;
    wire cmd_valid=bridge_mode?(native_cmd_valid&&!hold_native):host_valid;
    wire cmd_ready;
    wire [3:0] cmd_op=bridge_mode?native_cmd_op:host_op;
    wire [3:0] cmd_price=bridge_mode?native_cmd_price:host_price;
    wire [4:0] cmd_slot=bridge_mode?native_cmd_slot:host_slot;
    wire [1:0] cmd_query=bridge_mode?native_cmd_query:host_query;
    wire [20:0] cmd_page=bridge_mode?native_cmd_page:host_page;
    wire [15:0] cmd_generation=bridge_mode?native_cmd_generation:host_generation;
    wire [2:0] cmd_offset=bridge_mode?native_cmd_offset:host_offset;
    wire [2:0] cmd_field=bridge_mode?native_cmd_field:host_field;
    wire [31:0] cmd_value=bridge_mode?native_cmd_value:host_value;
    wire ep_valid; wire ep_ready=bridge_mode?(native_rsp_ready&&!hold_reply):host_ready;
    wire [3:0] ep_status; wire [159:0] ep_payload;
    wire ep_present, ep_dirty, ep_fault, draining;
    wire [15:0] ep_tx; wire [31:0] page_leases,memory_leases;
    wire [5:0] allocated; wire [1:0] fence_tag;
    assign native_cmd_ready=bridge_mode&&!hold_native&&cmd_ready;
    assign native_rsp_valid=stray_native||(bridge_mode&&!hold_reply&&ep_valid);
    assign native_rsp_status=override_status!=0?override_status:ep_status;
    assign native_rsp_payload=ep_payload;
    assign native_rsp_present=ep_present;
    assign native_fault=ep_fault||inject_fault;
    integer cycles=0;
    wire dispatch_enable=cycles%5!=0, execute_enable=cycles%7>=2;
    wire fence_service_enable=1,ack_receive_enable=cycles%11>=3;
    wire [31:0] m_awaddr,m_araddr;
    wire [7:0] m_awlen,m_arlen; wire [2:0] m_awsize,m_arsize;
    wire [1:0] m_awburst,m_arburst; wire [3:0] m_awid,m_arid;
    wire m_awvalid,m_wvalid,m_arvalid,m_wlast,m_bready,m_rready;
    wire [511:0] m_wdata; wire [63:0] m_wstrb;
    wire m_awready=0,m_wready=0,m_arready=0,m_bvalid=0,m_rvalid=0,m_rlast=0;
    wire [3:0] m_bid=0,m_rid=0; wire [1:0] m_bresp=0,m_rresp=0;
    wire [511:0] m_rdata=0;
    memory_scratch_endpoint_small_staticcodec #(.FRAMES(32),.INDEX_BITS(5),
        .HASH_BITS(5),.PROBE_LIMIT(32),.EPOCH_BITS(16)) endpoint(
        .rsp_valid(ep_valid),.rsp_ready(ep_ready),.rsp_status(ep_status),
        .rsp_payload(ep_payload),.rsp_present(ep_present),.rsp_dirty(ep_dirty),
        .rsp_tx(ep_tx),.fault(ep_fault),.*);

    integer checks=0, native_reads=0, resolve_requests=0, matrix_reads=0;
    integer cookie_errors=0, service_errors=0, abort_cases=0, blocked_cycles=0;
    integer s,o,p,k,reads_before,prev_token=0;
    reg [31:0] expected_node,expected_generation,expected_phase;
    reg [1:0] expected_query; reg [3:0] expected_price;
    reg [31:0] golden_prev[0:31][0:7],golden_visited[0:31][0:7];
    reg [20:0] pages[0:31];
    reg held_resolve=0,held_native=0,held_final=0,held_ep=0;
    reg [122:0] saved_resolve;
    reg [90:0] saved_native;
    reg [104:0] saved_final;
    reg [165:0] saved_ep;
    wire [122:0] resolve_packet={resolve_token,resolve_generation,resolve_phase,resolve_page,resolve_query,resolve_price};
    wire [90:0] native_packet={native_cmd_op,native_cmd_slot,native_cmd_query,native_cmd_page,native_cmd_price,native_cmd_generation,native_cmd_offset,native_cmd_field,native_cmd_value,1'b0};
    wire [104:0] final_packet={rsp_status,rsp_service_status,rsp_generation,rsp_phase,rsp_value,rsp_present};
    wire [165:0] ep_packet={ep_status,ep_payload,ep_present,ep_dirty};
    always @(posedge clk) begin
        cycles<=cycles+1;
        if(rst) begin held_resolve<=0;held_native<=0;held_final<=0;held_ep<=0; end
        else begin
            if(held_resolve&&!native_fault&&!fault&&!stray_native && (!resolve_valid||resolve_packet!==saved_resolve))
                $fatal(1,"resolver packet changed under backpressure");
            if(held_native&&!native_fault&&!fault&&!stray_native && (!native_cmd_valid||native_packet!==saved_native))
                $fatal(1,"native packet changed under backpressure");
            if(held_final && (!rsp_valid||final_packet!==saved_final))$fatal(1,"final packet changed under backpressure");
            if(held_ep && (!ep_valid||ep_packet!==saved_ep))$fatal(1,"endpoint packet changed under backpressure");
            held_resolve<=resolve_valid&&!resolve_ready;saved_resolve<=resolve_packet;
            held_native<=native_cmd_valid&&!native_cmd_ready;saved_native<=native_packet;
            held_final<=rsp_valid&&!rsp_ready;saved_final<=final_packet;
            held_ep<=ep_valid&&!ep_ready;saved_ep<=ep_packet;
            if((resolve_valid&&!resolve_ready)||(native_cmd_valid&&!native_cmd_ready)||(rsp_valid&&!rsp_ready)) blocked_cycles<=blocked_cycles+1;
            if(resolve_valid&&resolve_ready) resolve_requests<=resolve_requests+1;
            if(bridge_mode&&cmd_valid&&cmd_ready) begin
                native_reads<=native_reads+1;
                if(cmd_op!==2 || cmd_value!==0 || cmd_page!==expected_node[23:3] || cmd_offset!==expected_node[2:0] ||
                   cmd_query!==expected_query || cmd_price!==expected_price || cmd_field!==((expected_phase==1||expected_phase==4)?3'd2:3'd3))
                    $fatal(1,"wrong native READ conversion");
            end
            if(m_awvalid||m_wvalid||m_arvalid)$fatal(1,"resident-only test unexpectedly issued AXI traffic");
            if(ep_fault)$fatal(1,"unexpected real endpoint fault");
        end
    end
    initial begin #5000000; $fatal(1,"watchdog expired checks=%0d",checks); end

    task cold_reset;
        begin
            @(negedge clk);rst=1;req_valid=0;resolve_ready=0;map_valid=0;rsp_ready=0;
            host_valid=0;host_ready=0;bridge_mode=0;hold_native=0;hold_reply=0;
            inject_fault=0;stray_native=0;override_status=0;prev_token=0;
            repeat(6)@(negedge clk);rst=0;repeat(3)@(negedge clk);
        end
    endtask
    task host_command(input integer op,sl,pg,gen,off,field_id,input [31:0] value,
                      input integer q,pr,expected_status);
        begin
            @(negedge clk);bridge_mode=0;host_op=op;host_slot=sl;host_page=pg;
            host_generation=gen;host_offset=off;host_field=field_id;host_value=value;
            host_query=q;host_price=pr;host_valid=1;
            do @(posedge clk);while(!cmd_ready);
            @(negedge clk);host_valid=0;
            wait(ep_valid);@(negedge clk);
            if(ep_status!==expected_status[3:0])$fatal(1,"host op%0d status%0d wanted%0d",op,ep_status,expected_status);
            host_ready=1;@(negedge clk);host_ready=0;checks=checks+1;
        end
    endtask
    task submit(input [31:0] n,g,ph,input [1:0] q,input [3:0] pr);
        begin
            @(negedge clk);bridge_mode=1;
            expected_node=n;expected_generation=g;expected_phase=ph;expected_query=q;expected_price=pr;
            req_node=n;req_generation=g;req_phase=ph;req_query=q;req_price=pr;req_valid=1;
            do @(posedge clk);while(!req_ready);
            @(negedge clk);req_valid=0;
            // Changes on unaccepted input wires must not affect the transaction.
            req_node=32'hdeadbeef;req_generation=0;req_phase=99;req_query=3;req_price=15;
        end
    endtask
    task accept_resolve;
        begin
            wait(resolve_valid);repeat(3)@(negedge clk);
            if(resolve_generation!==expected_generation || resolve_phase!==expected_phase ||
               resolve_page!==expected_node[23:3] || resolve_query!==expected_query || resolve_price!==expected_price ||
               resolve_token!==prev_token+1)$fatal(1,"wrong resolver identity/token");
            prev_token=resolve_token;resolve_ready=1;@(negedge clk);resolve_ready=0;
        end
    endtask
    task send_map(input integer sl,gen,status,corrupt);
        begin
            repeat(2)@(negedge clk);
            map_token=resolve_token;map_generation=resolve_generation;map_phase=resolve_phase;
            map_page=resolve_page;map_query=resolve_query;map_price=resolve_price;
            map_slot=sl;map_binding_generation=gen;map_status=status;
            case(corrupt)
                1:map_token=map_token-1;
                2:map_generation=map_generation-1;
                3:map_phase=map_phase^1;
                4:map_page=map_page^1;
                5:map_query=map_query^1;
                6:map_price=map_price^1;
                default:begin end
            endcase
            map_valid=1;do @(posedge clk);while(!map_ready);
            @(negedge clk);map_valid=0;
        end
    endtask
    task expect_reply(input integer status,service,input [31:0] value,input integer present,poison);
        begin
            wait(rsp_valid);repeat(4)@(negedge clk);
            if(rsp_status!==status[3:0] || rsp_service_status!==service[3:0] || rsp_value!==value ||
               rsp_present!==present[0] || rsp_generation!==expected_generation || rsp_phase!==expected_phase || fault!==poison[0])
                $fatal(1,"reply mismatch check%0d got status=%0d service=%0d value=%h present=%b fault=%b expected=%0d/%0d/%h/%0d/%0d",
                    checks,rsp_status,rsp_service_status,rsp_value,rsp_present,fault,status,service,value,present,poison);
            if(req_ready)$fatal(1,"accepted new request while reply pending");
            rsp_ready=1;@(negedge clk);rsp_ready=0;checks=checks+1;
            if(poison) begin
                repeat(4)@(negedge clk);
                if(req_ready||resolve_valid||native_cmd_valid)$fatal(1,"poisoned adapter still accepts work");
            end
        end
    endtask
    task read_label(input [31:0] n,g,ph,input integer sl,bgen,q,pr,status,service,input [31:0] value,input integer present);
        begin
            hold_native=1;hold_reply=1;
            submit(n,g,ph,q,pr);accept_resolve;send_map(sl,bgen,0,0);
            wait(native_cmd_valid);repeat(5)@(negedge clk);hold_native=0;
            wait(ep_valid);repeat(3)@(negedge clk);hold_reply=0;
            expect_reply(status,service,value,present,0);
        end
    endtask
    task minimal_setup;
        begin
            cold_reset;
            host_command(0,0,0,0,0,0,0,1,3,0);
            host_command(1,0,7,4,0,0,0,1,3,0);
        end
    endtask
    initial begin
        cold_reset;
        if(TOKEN_BITS==3) begin
            for(k=1;k<=7;k=k+1)begin
                submit(56,77,1,1,3);accept_resolve;send_map(0,4,9,0);expect_reply(2,9,0,0,0);
            end
            submit(56,77,1,1,3);expect_reply(6,0,0,0,0);
            submit(32'h01000000,77,1,1,3);expect_reply(1,0,0,0,0);
            if(resolve_requests!=7||native_reads!=0||resolve_token!=7)$fatal(1,"token exhaustion wrapped or issued read");
            $display("TOKEN_EXHAUSTION_PASS accepted=7 refused=1 invalid=1 checks=%0d",checks);$finish;
        end
        host_command(0,0,0,0,0,0,0,1,3,0);
        for(s=0;s<32;s=s+1)begin
            pages[s]=(s==31)?21'h1fffff:(21'h10000+s*19);
            host_command(1,s,pages[s],16'h8100+s,0,0,0,1,3,0);
            for(o=0;o<8;o=o+1)begin
                golden_prev[s][o]=(o==0)?32'hffffffff:(32'h12000000+s*8+o);
                golden_visited[s][o]=32'h80000000+s*8+o;
                if(o==7)begin golden_prev[s][o]=0;golden_visited[s][o]=0;end
                else begin
                    host_command(3,s,pages[s],16'h8100+s,o,0,32'h3f800000,1,3,0);
                    host_command(3,s,pages[s],16'h8100+s,o,1,32'h40000000,1,3,0);
                    host_command(3,s,pages[s],16'h8100+s,o,2,golden_prev[s][o],1,3,0);
                    host_command(3,s,pages[s],16'h8100+s,o,3,golden_visited[s][o],1,3,0);
                    host_command(3,s,pages[s],16'h8100+s,o,4,1,1,3,0);
                end
            end
        end
        for(s=0;s<32;s=s+1)for(o=0;o<8;o=o+1)for(p=1;p<=4;p=p+1)begin
            read_label({8'b0,pages[s],o[2:0]},32'hf0000000+s*8+o,p,s,16'h8100+s,1,3,0,0,
                (p==1||p==4)?golden_prev[s][o]:golden_visited[s][o],o!=7);
            matrix_reads=matrix_reads+1;
        end
        // Invalid requests cannot truncate an out-of-range node into a valid page.
        reads_before=native_reads;
        submit(32'h01000000,1,1,1,3);expect_reply(1,0,0,0,0);
        submit(32'hffffffff,1,1,1,3);expect_reply(1,0,0,0,0);
        submit(0,0,1,1,3);expect_reply(1,0,0,0,0);
        submit(0,1,0,1,3);expect_reply(1,0,0,0,0);
        submit(0,1,5,1,3);expect_reply(1,0,0,0,0);
        if(native_reads!=reads_before)$fatal(1,"invalid request touched backend");
        // Real endpoint rejects stale binding, wrong slot, page, price and query.
        read_label({8'b0,pages[0],3'b0},1,1,0,16'h80ff,1,3,4,1,0,0);
        read_label({8'b0,pages[0],3'b0},1,1,1,16'h8101,1,3,4,1,0,0);
        read_label({8'b0,pages[0]+21'd1,3'b0},1,1,0,16'h8100,1,3,4,1,0,0);
        read_label({8'b0,pages[0],3'b0},1,1,0,16'h8100,1,4,4,1,0,0);
        read_label({8'b0,pages[0],3'b0},1,1,0,16'h8100,2,3,4,1,0,0);
        // Every service status must be an explicit failure, never numeric success.
        for(k=1;k<16;k=k+1)begin
            reads_before=native_reads;
            submit(0,1,1,1,3);accept_resolve;send_map(0,1,k,0);expect_reply(2,k,0,0,0);
            if(native_reads!=reads_before)$fatal(1,"resolver error issued native command");
            override_status=k;
            read_label({8'b0,pages[0],3'b0},1,1,0,16'h8100,1,3,4,k,0,0);
            override_status=0;service_errors=service_errors+2;
        end
        // A resolver can race with a rebind; native generation validation wins.
        minimal_setup;
        submit(56,32'h12345678,1,1,3);accept_resolve;
        host_command(4,0,7,4,0,0,0,1,3,0);
        host_command(1,0,7,5,0,0,0,1,3,0);
        bridge_mode=1;send_map(0,4,0,0);expect_reply(4,1,0,0,0);
        read_label(56,32'h12345678,1,0,5,1,3,0,0,0,0);
        host_command(0,0,0,0,0,0,0,2,4,0);
        read_label(56,32'h12345678,1,0,5,1,3,4,1,0,0);
        // Every echoed identity component is checked, including same-edge token.
        for(k=1;k<=6;k=k+1)begin
            cold_reset;
            if(k==1)begin
                submit(56,77,1,1,3);accept_resolve;send_map(0,4,9,0);expect_reply(2,9,0,0,0);
            end
            submit(56,77,1,1,3);accept_resolve;
            send_map(0,4,8,k);expect_reply(3,0,0,0,1);cookie_errors=cookie_errors+1;
        end
        // Duplicate service replies poison idle instead of becoming later data.
        cold_reset;submit(56,77,1,1,3);accept_resolve;send_map(0,4,9,0);expect_reply(2,9,0,0,0);
        @(negedge clk);map_valid=1;repeat(2)@(negedge clk);
        if(!fault||req_ready||rsp_valid)$fatal(1,"duplicate resolver reply not fail-stop");
        map_valid=0;abort_cases=abort_cases+1;
        cold_reset;stray_native=1;repeat(2)@(negedge clk);
        if(!fault||req_ready||rsp_valid)$fatal(1,"unsolicited native reply not fail-stop");
        stray_native=0;abort_cases=abort_cases+1;
        // Abort during resolver send/wait, native send/wait, held final, and idle.
        for(k=0;k<6;k=k+1)begin
            minimal_setup;
            if(k!=5)submit(56,77,1,1,3);
            if(k>=1&&k<=4)accept_resolve;
            if(k>=2&&k<=4)begin
                hold_native=1;send_map(0,4,0,0);wait(native_cmd_valid);
            end
            if(k>=3&&k<=4)begin
                hold_reply=1;@(negedge clk);hold_native=0;wait(ep_valid);
            end
            if(k==4)begin @(negedge clk);hold_reply=0;wait(rsp_valid);end
            @(negedge clk);inject_fault=1;
            // This is the final ready/valid acceptance cycle, not two cycles later.
            if(k==4) begin
                #1;if(!fault || !rsp_valid || rsp_status!=0)$fatal(1,"same-cycle abort invisible at successful reply acceptance");
            end
            repeat(2)@(negedge clk);
            if(k<4)expect_reply(5,0,0,0,1);
            else if(k==4)expect_reply(0,0,0,0,1);
            else if(!fault||req_ready||rsp_valid)$fatal(1,"idle fault not fail-stop");
            abort_cases=abort_cases+1;
        end
        if(matrix_reads!=1024||cookie_errors!=6||service_errors!=30||abort_cases!=8||blocked_cycles<1000)
            $fatal(1,"coverage counts incomplete");
        $display("EXCLUSION_LABEL_PASS matrix_reads=%0d cookie_errors=%0d service_errors=%0d abort_cases=%0d checks=%0d native_reads=%0d blocked_cycles=%0d",matrix_reads,cookie_errors,service_errors,abort_cases,checks,native_reads,blocked_cycles);
        $finish;
    end
endmodule
