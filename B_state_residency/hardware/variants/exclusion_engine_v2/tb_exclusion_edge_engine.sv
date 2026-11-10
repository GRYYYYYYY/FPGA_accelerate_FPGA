`timescale 1ns/1ps
module tb_exclusion_edge_engine;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,edge_valid=0,result_ready=0;wire edge_ready,result_valid,fault;
    reg [31:0] edge_cookie=0,edge_parent=0,edge_child=0,edge_flags=0,edge_created=0,edge_has_laguna=0;
    reg [1:0] edge_query=1;reg [3:0] edge_price=3;
    wire [3:0] result_status;wire [31:0] result_detail,result_cookie,result_generation;wire result_excluded;
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


    exclusion_edge_engine dut(.*);
    integer checks=0,edges=0,read_requests=0,native_reads=0,hls_calls=0,responses=0;
    integer expected_generation=0,edge_index=0,read_index=0,response_index=0,error_mode=0,errors_tested=0;
    integer fixture,rc,k,j,mode,fields[0:18],calls_before,reads_before,responses_before;
    reg active_edge=0;
    reg [4095:0] fixture_path;
    reg held_result=0,held_resolve=0,held_native=0;
    reg [132:0] saved_result;reg [122:0] saved_resolve;reg [90:0] saved_native;
    wire [132:0] result_packet={result_status,result_detail,result_cookie,result_generation,result_excluded};
    wire [122:0] resolve_packet={resolve_token,resolve_generation,resolve_phase,resolve_page,resolve_query,resolve_price};
    wire [90:0] native_packet={native_cmd_op,native_cmd_slot,native_cmd_query,native_cmd_page,native_cmd_price,native_cmd_generation,native_cmd_offset,native_cmd_field,native_cmd_value,1'b0};
    function integer slot_for(input integer node);
        if((node>>3)==2)slot_for=0;else if((node>>3)==3)slot_for=1;else if((node>>3)==21'h1fffff)slot_for=31;else slot_for=-1;
    endfunction
    function [31:0] expected_value(input integer phase);
        if(phase==1||phase==4)expected_value=fields[6];else if(phase==2)expected_value=fields[7];else expected_value=fields[8];
    endfunction
    always @(posedge clk)begin
        cycles<=cycles+1;
        if(rst)begin held_result<=0;held_resolve<=0;held_native<=0;end
        else begin
            if(held_result&&(!result_valid||result_packet!==saved_result))$fatal(1,"engine result changed under backpressure");
            if(held_resolve&&!fault&&(!resolve_valid||resolve_packet!==saved_resolve))$fatal(1,"engine resolver packet unstable");
            if(held_native&&!fault&&(!native_cmd_valid||native_packet!==saved_native))$fatal(1,"engine native packet unstable");
            held_result<=result_valid&&!result_ready;saved_result<=result_packet;
            held_resolve<=resolve_valid&&!resolve_ready;saved_resolve<=resolve_packet;
            held_native<=native_cmd_valid&&!native_cmd_ready;saved_native<=native_packet;
            if(active_edge&&edge_ready)$fatal(1,"engine accepted work before retiring edge");
            if(m_awvalid||m_wvalid||m_arvalid||ep_fault)$fatal(1,"resident engine unexpected AXI/fault");
            if(bridge_mode&&cmd_valid&&cmd_ready)begin
                native_reads<=native_reads+1;
                if(cmd_op!=2||cmd_value!=0)$fatal(1,"engine emitted non-read native command");
            end
            if(dut.ap_start&&dut.ap_ready)begin
                hls_calls<=hls_calls+1;
                if(dut.hls_command[31:0]==1)begin
                    responses<=responses+1;
                    if(error_mode!=0)$fatal(1,"engine submitted RESPONSE after injected read failure");
                    if(response_index>=fields[10]||dut.hls_command[223:192]!==expected_generation||
                       dut.hls_command[255:224]!==fields[11+response_index*2]||
                       dut.hls_command[287:256]!==expected_value(fields[11+response_index*2]))
                        $fatal(1,"engine HLS RESPONSE identity/value mismatch edge=%0d read=%0d",edge_index,response_index);
                    response_index<=response_index+1;
                end else if(dut.hls_command[31:0]!=0)$fatal(1,"unexpected HLS operation");
            end
        end
    end
    initial begin #100000000;$fatal(1,"engine watchdog edge=%0d",edge_index);end
    task cold_reset;
        begin
            @(negedge clk);rst=1;edge_valid=0;result_ready=0;map_valid=0;resolve_ready=0;
            host_valid=0;host_ready=0;bridge_mode=0;hold_native=0;hold_reply=0;inject_fault=0;
            stray_native=0;override_status=0;active_edge=0;expected_generation=0;error_mode=0;
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

    task setup;
        begin
            cold_reset;
            host_command(0,0,0,0,0,0,0,1,3,0);
            host_command(1,0,2,16'h8100,0,0,0,1,3,0);
            host_command(1,1,3,16'h8101,0,0,0,1,3,0);
            host_command(1,31,21'h1fffff,16'h811f,0,0,0,1,3,0);
        end
    endtask
    task begin_edge;
        begin
            @(negedge clk);bridge_mode=1;edge_cookie=32'hfed00000+edge_index;
            edge_parent=fields[1];edge_child=fields[2];edge_flags=fields[3];edge_created=fields[4];edge_has_laguna=fields[5];
            edge_query=1;edge_price=3;edge_valid=1;
            do @(posedge clk);while(!edge_ready);
            @(negedge clk);active_edge=1;read_index=0;response_index=0;
            // Keep an invalid next edge offered while busy; it must not launch.
            edge_parent=32'hffffffff;edge_child=0;edge_flags=256;edge_created=2;edge_has_laguna=2;edge_cookie=0;
        end
    endtask
    task resolve_one;
        begin
            if(read_index>=fields[10]||resolve_generation!==expected_generation||resolve_phase!==fields[11+2*read_index]||
               resolve_page!==(fields[12+2*read_index]>>3)||resolve_query!=1||resolve_price!=3)
                $fatal(1,"engine resolver order/identity mismatch edge=%0d index=%0d",edge_index,read_index);
            repeat(2+edge_index%3)@(negedge clk);resolve_ready=1;@(negedge clk);resolve_ready=0;
            read_requests=read_requests+1;
            map_token=resolve_token;map_generation=resolve_generation;map_phase=resolve_phase;
            map_page=resolve_page;map_query=resolve_query;map_price=resolve_price;
            map_slot=slot_for(fields[12+2*read_index]);map_binding_generation=16'h8100+map_slot;
            map_status=error_mode==1?9:0;
            if(error_mode==2)map_binding_generation=map_binding_generation-1;
            if(error_mode==3)map_token=map_token-1;
            hold_native=1;hold_reply=1;@(negedge clk);map_valid=1;
            do @(posedge clk);while(!map_ready);
            @(negedge clk);map_valid=0;
            if(error_mode==0||error_mode==2||error_mode==4)begin
                wait(native_cmd_valid);repeat(3)@(negedge clk);hold_native=0;
                wait(ep_valid);repeat(2)@(negedge clk);hold_reply=0;
                if(error_mode==0)begin
                    if(ep_status!=0||ep_present!==fields[0][0])$fatal(1,"native record presence/status mismatch");
                end
                if(error_mode==4)begin
                    wait(dut.label_reply_valid);@(negedge clk);inject_fault=1;
                    #1;if(!fault||dut.call_valid||dut.ap_start)$fatal(1,"same-cycle label fault reached HLS");
                end
            end
            read_index=read_index+1;
        end
    endtask
    task retire(input integer status,poison);
        begin
            wait(result_valid);repeat(4)@(negedge clk);
            if(result_status!==status[3:0]||fault!==poison[0]||result_cookie!==32'hfed00000+edge_index||edge_ready)
                $fatal(1,"edge result status/identity mismatch edge=%0d status=%0d expected=%0d fault=%b",edge_index,result_status,status,fault);
            if(status==0)begin
                if(result_generation!==expected_generation||result_excluded!==fields[9][0]||
                   read_index!=fields[10]||response_index!=fields[10])$fatal(1,"edge result/trace mismatch edge=%0d",edge_index);
            end else if(result_excluded)$fatal(1,"error emitted exclusion decision");
            edge_valid=0;result_ready=1;@(negedge clk);result_ready=0;active_edge=0;
            checks=checks+1;
            if(poison)begin repeat(3)@(negedge clk);if(edge_ready||dut.ap_start||resolve_valid)$fatal(1,"failed edge resumed");end
        end
    endtask
    task prepare_error_edge;
        begin
            setup;
            for(j=0;j<19;j=j+1)fields[j]=0;
            fields[1]=16;fields[2]=17;fields[3]=32;fields[4]=1;fields[5]=1;
            fields[6]=32'hffffffff;fields[10]=2;fields[11]=1;fields[12]=17;fields[13]=4;fields[14]=17;
            host_command(3,0,2,16'h8100,1,2,32'hffffffff,1,3,0);
            expected_generation=1;
        end
    endtask
    initial begin
        setup;
`ifdef HLS_GEN3
        for(j=0;j<19;j=j+1)fields[j]=0;
        fields[1]=16;fields[2]=17;
        for(k=1;k<=7;k=k+1)begin
            edge_index=k;expected_generation=k;begin_edge;retire(0,0);
        end
        edge_index=8;begin_edge;retire(2,1);
        if(result_detail!=5||hls_calls!=8||read_requests!=0||responses!=0)$fatal(1,"real HLS gen3 exhaustion not propagated");
        $display("EDGE_GEN3_PASS accepted=7 exhausted=1 hls_calls=%0d",hls_calls);$finish;
`endif
        if(!$value$plusargs("fixture=%s",fixture_path))$fatal(1,"missing fixture");
        fixture=$fopen(fixture_path,"r");if(!fixture)$fatal(1,"cannot open fixture");
        for(edge_index=0;edge_index<27680;edge_index=edge_index+1)begin
            for(j=0;j<19;j=j+1)begin rc=$fscanf(fixture,"%h",fields[j]);if(rc!=1)$fatal(1,"short fixture");end
            if(fields[0])begin
                host_command(3,slot_for(fields[2]),fields[2]>>3,16'h8100+slot_for(fields[2]),fields[2]&7,2,fields[6],1,3,0);
                host_command(3,slot_for(fields[2]),fields[2]>>3,16'h8100+slot_for(fields[2]),fields[2]&7,3,fields[7],1,3,0);
                host_command(3,slot_for(fields[1]),fields[1]>>3,16'h8100+slot_for(fields[1]),fields[1]&7,3,fields[8],1,3,0);
            end
            expected_generation=expected_generation+1;begin_edge;
            while(!result_valid)begin
                if(resolve_valid)resolve_one;else @(negedge clk);
            end
            retire(0,0);edges=edges+1;
        end
        rc=$fscanf(fixture,"%h",mode);if(rc==1)$fatal(1,"unconsumed fixture");$fclose(fixture);
        for(k=0;k<5;k=k+1)begin
            for(j=0;j<19;j=j+1)fields[j]=0;
            fields[1]=16;fields[2]=17;
            case(k)
                0:fields[1]=32'h01000000;
                1:fields[2]=32'h01000000;
                2:fields[3]=256;
                3:fields[4]=2;
                4:fields[5]=2;
            endcase
            calls_before=hls_calls;reads_before=read_requests;begin_edge;retire(1,0);
            if(hls_calls!=calls_before||read_requests!=reads_before||result_generation!=0)$fatal(1,"invalid edge reached HLS");
            errors_tested=errors_tested+1;
        end
        for(k=1;k<=4;k=k+1)begin
            prepare_error_edge;error_mode=k;calls_before=hls_calls;responses_before=responses;
            begin_edge;wait(resolve_valid);resolve_one;retire(k<=2?3:5,1);
            if(hls_calls!=calls_before+1||responses!=responses_before)$fatal(1,"label failure continued HLS");
            if(k==1&&result_detail!=32'h29)$fatal(1,"lost resolver error detail");
            if(k==2&&result_detail!=32'h41)$fatal(1,"lost native error detail");
            errors_tested=errors_tested+1;
        end
        // Preserve held final result, but make a new fault visible before acceptance.
        setup;for(j=0;j<19;j=j+1)fields[j]=0;fields[1]=16;fields[2]=17;
        expected_generation=1;begin_edge;wait(result_valid);@(negedge clk);inject_fault=1;
        #1;if(!fault||result_status!=0||!result_valid)$fatal(1,"held final fault not visible");
        retire(0,1);errors_tested=errors_tested+1;
        if(edges!=27680||errors_tested!=10)$fatal(1,"engine coverage incomplete");
        $display("EDGE_ENGINE_PASS edges=%0d error_cases=%0d checks=%0d label_requests=%0d native_reads=%0d hls_calls=%0d responses=%0d",edges,errors_tested,checks,read_requests,native_reads,hls_calls,responses);
        $finish;
    end
endmodule
