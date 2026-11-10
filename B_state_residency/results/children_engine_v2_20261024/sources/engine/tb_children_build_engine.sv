`timescale 1ns/1ps
module tb_children_build_engine;
`ifdef PILOT
    localparam NORMAL_LIMIT=1024;
`else
    localparam NORMAL_LIMIT=93728;
`endif
    reg clk=0;always #5 clk=~clk;
    reg rst=1,build_valid=0,result_ready=0,svc_ready=0,svc_reply_valid=0,service_fault=0;
    reg [31:0] build_cookie=0,build_parent=0,build_count=0,build_prune=0;
    reg [1:0] build_query=0;reg [3:0] build_price=0;
    wire build_ready,result_valid,fault,busy,svc_valid,svc_reply_ready;
    wire [3:0] result_status;wire [31:0] result_detail,result_cookie,result_generation,result_emitted;
    wire [31:0] svc_generation,svc_parent,svc_position,svc_phase,svc_node,svc_emitted,svc_count,svc_prune;
    wire [1:0] svc_query;wire [3:0] svc_price;
    reg [31:0] svc_reply_generation=0,svc_reply_parent=0,svc_reply_position=0,svc_reply_phase=0,svc_reply_node=0,svc_status=0,svc_value=0,svc_aux=0;
    reg [1:0] svc_reply_query=0;reg [3:0] svc_reply_price=0;
    children_build_engine dut(.*);
    integer checks=0,builds=0,services=0,errors=0,hls_calls=0,hls_responses=0,blocked=0;
    integer fixture,rc,index,j,k,round,header[0:7],event_row[0:4],emitted_model,expected_gen=0,target,calls_before;
    reg [31:0] live_cookie=0,test_child=17;
    reg expected_failure=0,held_service=0,held_result=0;
    reg [261:0] saved_service;reg [131:0] saved_result;
    reg [4095:0] fixture_path;
    wire [261:0] service_packet={svc_generation,svc_parent,svc_position,svc_phase,svc_node,svc_emitted,svc_count,svc_prune,svc_query,svc_price};
    wire [131:0] result_packet={result_status,result_detail,result_cookie,result_generation,result_emitted};
    always @(posedge clk)begin
        if(rst)begin held_service<=0;held_result<=0;end
        else begin
            if(held_service&&!fault&&(!svc_valid||service_packet!==saved_service))$fatal(1,"service request unstable");
            if(held_result&&(!result_valid||result_packet!==saved_result))$fatal(1,"build result unstable");
            held_service<=svc_valid&&!svc_ready;saved_service<=service_packet;
            held_result<=result_valid&&!result_ready;saved_result<=result_packet;
            if((svc_valid||result_valid)&&(!busy||build_ready))$fatal(1,"build ownership released early");
            if(fault&&!expected_failure)$fatal(1,"unexpected build fault index=%0d state=%0d status=%0d detail=%0d",index,dut.controller.state,result_status,result_detail);
            if(dut.ap_start&&dut.ap_ready)begin hls_calls<=hls_calls+1;if(dut.hls_command[31:0]==1)hls_responses<=hls_responses+1;end
            if(svc_valid&&!svc_ready)blocked<=blocked+1;
        end
    end
    initial begin #1000000000;$fatal(1,"build engine watchdog index=%0d checks=%0d phase=%0d",index,checks,svc_phase);end
    task cold_reset;
        begin
            @(negedge clk);rst=1;build_valid=0;result_ready=0;svc_ready=0;svc_reply_valid=0;service_fault=0;
            expected_failure=0;expected_gen=0;
            repeat(6)@(negedge clk);rst=0;repeat(2)@(negedge clk);
        end
    endtask
    task launch;
        begin
            @(negedge clk);live_cookie=build_cookie;build_valid=1;
            do @(posedge clk);while(!build_ready);
            @(negedge clk);build_valid=0;build_cookie='1;build_parent='1;build_count='1;build_prune='1;build_query='1;build_price='1;
            repeat(3)begin if(build_ready||!busy)$fatal(1,"build context not retained");@(negedge clk);end
        end
    endtask
    task claim_service;
        begin
            wait(svc_valid);@(negedge clk);repeat(2)@(negedge clk);
            svc_reply_generation=svc_generation;svc_reply_parent=svc_parent;svc_reply_position=svc_position;
            svc_reply_phase=svc_phase;svc_reply_node=svc_node;svc_reply_query=svc_query;svc_reply_price=svc_price;
            svc_ready=1;@(negedge clk);svc_ready=0;svc_status=0;svc_value=0;svc_aux=0;
        end
    endtask
    task send_reply;
        begin
            repeat(2)@(negedge clk);svc_reply_valid=1;
            do @(posedge clk);while(!svc_reply_ready);
            @(negedge clk);svc_reply_valid=0;
        end
    endtask
    task retire(input integer status,detail,success_emitted);
        begin
            wait(result_valid);repeat(4)@(negedge clk);
            if(result_status!==status||result_detail!==detail||result_cookie!==live_cookie)$fatal(1,"result mismatch got=%0d/%0d want=%0d/%0d cookie=%h want=%h",result_status,result_detail,status,detail,result_cookie,live_cookie);
            if(status==0&&(fault||result_generation!==expected_gen||result_emitted!==success_emitted))$fatal(1,"successful build mismatch gen=%0d expected=%0d emitted=%0d expected=%0d",result_generation,expected_gen,result_emitted,success_emitted);
            result_ready=1;@(negedge clk);result_ready=0;checks=checks+1;
        end
    endtask
    task assert_stopped;
        begin repeat(8)@(negedge clk);if(!fault||build_ready||svc_valid||dut.call_valid||!busy)$fatal(1,"failed build continued");errors=errors+1;end
    endtask
    task start_manual;
        begin
            build_cookie=32'hbad00000+errors;build_parent=16;build_count=1;build_prune=1;build_query=2;build_price=5;
            launch;expected_gen=expected_gen+1;
        end
    endtask
    task normal_manual_reply;
        begin
            claim_service;
            if(svc_phase==0)begin svc_value=test_child;svc_aux=1;end
            if(svc_phase==5)svc_value=1;
            send_reply;
        end
    endtask
    initial begin
        if(!$value$plusargs("fixture=%s",fixture_path))$fatal(1,"missing fixture");
`ifdef GEN3
        for(round=0;round<2;round=round+1)begin
`else
        for(round=0;round<1;round=round+1)begin
`endif
            cold_reset;fixture=$fopen(fixture_path,"r");if(!fixture)$fatal(1,"fixture open");
`ifdef GEN3
            for(index=0;index<7;index=index+1)begin
`else
            for(index=0;index<NORMAL_LIMIT;index=index+1)begin
`endif
                for(j=0;j<8;j=j+1)begin rc=$fscanf(fixture,"%h",header[j]);if(rc!=1)$fatal(1,"short header");end
                build_parent=header[0];build_count=header[1];build_prune=header[2];build_query=header[3];build_price=header[4];build_cookie=header[7];
                launch;expected_gen=expected_gen+1;emitted_model=0;
                for(k=0;k<header[6];k=k+1)begin
                    for(j=0;j<5;j=j+1)begin rc=$fscanf(fixture,"%h",event_row[j]);if(rc!=1)$fatal(1,"short service");end
                    wait(svc_valid);@(negedge clk);
                    if(svc_generation!==expected_gen||svc_parent!==header[0]||svc_position!==event_row[1]||svc_phase!==event_row[0]||svc_node!==event_row[2]||svc_emitted!==emitted_model||svc_count!==header[1]||svc_prune!==header[2]||svc_query!==header[3][1:0]||svc_price!==header[4][3:0])$fatal(1,"service disagrees with original oracle index=%0d event=%0d phase=%0d want=%0d",index,k,svc_phase,event_row[0]);
                    claim_service;svc_value=event_row[3];svc_aux=event_row[4];send_reply;
                    if(event_row[0]==4)emitted_model=emitted_model+1;services=services+1;
                end
                retire(0,0,header[5]);builds=builds+1;
            end
            $fclose(fixture);
`ifdef GEN3
            expected_failure=1;start_manual;retire(2,5,0);assert_stopped;
`endif
        end
`ifdef GEN3
        if(builds!=14||errors!=2||services!=84||hls_calls!=100||hls_responses!=84)$fatal(1,"gen3 coverage");
        $display("CHILDREN_ENGINE_GEN3_PASS builds=%0d services=%0d hls_calls=%0d responses=%0d errors=%0d checks=%0d",builds,services,hls_calls,hls_responses,errors,checks);$finish;
`endif
        if(builds!=NORMAL_LIMIT||(NORMAL_LIMIT==93728&&services!=813439)||hls_calls!=builds+services||hls_responses!=services)$fatal(1,"normal conservation");
        // Pre-HLS input rejection leaves the session usable and generation unchanged.
        calls_before=hls_calls;build_cookie=32'hffff0001;build_parent=32'h01000000;build_prune=0;launch;retire(1,0,0);
        build_cookie=32'hffff0002;build_parent=16;build_prune=2;launch;retire(1,0,0);
        if(hls_calls!=calls_before||fault)$fatal(1,"invalid build invoked HLS or poisoned state");
        // Each wrong identity field must stop before an HLS RESPONSE is issued.
        for(target=0;target<7;target=target+1)begin
            cold_reset;start_manual;claim_service;calls_before=hls_responses;
            case(target)
                0:svc_reply_generation=svc_reply_generation+1;
                1:svc_reply_parent=svc_reply_parent+1;
                2:svc_reply_position=svc_reply_position+1;
                3:svc_reply_phase=svc_reply_phase+1;
                4:svc_reply_node=svc_reply_node+1;
                5:svc_reply_query=svc_reply_query+1;
                6:svc_reply_price=svc_reply_price+1;
            endcase
            expected_failure=1;send_reply;retire(4,svc_reply_phase,0);assert_stopped;
            if(hls_responses!=calls_before)$fatal(1,"wrong owner reached HLS");
        end
        // All eight service phases propagate a matched backend failure to HLS.
        for(target=0;target<8;target=target+1)begin
            cold_reset;start_manual;wait(svc_valid);@(negedge clk);
            while(svc_phase!=target)begin normal_manual_reply;wait(svc_valid);@(negedge clk);end
            claim_service;svc_status=10;expected_failure=1;send_reply;retire(3,10,0);assert_stopped;
        end
        // All eight phases reject noncanonical successful payloads.
        for(target=0;target<8;target=target+1)begin
            cold_reset;start_manual;wait(svc_valid);@(negedge clk);
            while(svc_phase!=target)begin normal_manual_reply;wait(svc_valid);@(negedge clk);end
            claim_service;svc_value=target==0?32'h01000000:2;expected_failure=1;send_reply;retire(2,6,0);assert_stopped;
        end
        cold_reset;start_manual;claim_service;calls_before=hls_responses;
        expected_failure=1;service_fault=1;svc_reply_valid=1;#1;
        if(svc_reply_ready||dut.call_valid)$fatal(1,"same-cycle fault admitted response");
        @(negedge clk);svc_reply_valid=0;retire(5,0,0);assert_stopped;
        if(hls_responses!=calls_before)$fatal(1,"async fault reached HLS");
        // Late fault preserves an already offered successful result; caller also checks fault.
        cold_reset;start_manual;
        while(!result_valid)begin normal_manual_reply;if(svc_reply_phase==7)wait(result_valid);end
        repeat(3)@(negedge clk);expected_failure=1;service_fault=1;repeat(3)@(negedge clk);
        if(!result_valid||result_status!=0||!fault)$fatal(1,"late fault changed held result");
        result_ready=1;@(negedge clk);result_ready=0;assert_stopped;
        cold_reset;expected_failure=1;svc_reply_valid=1;repeat(3)@(negedge clk);svc_reply_valid=0;assert_stopped;
        cold_reset;test_child=32'h00ffffff;start_manual;
        while(!result_valid)begin
            wait(svc_valid);@(negedge clk);if(svc_phase>=1&&svc_phase<=4&&svc_node!=test_child)$fatal(1,"high child truncated");
            normal_manual_reply;if(svc_reply_phase==7)wait(result_valid);
        end
        retire(0,0,1);
        if(errors!=26||fault)$fatal(1,"fault/recovery coverage");
        $display("CHILDREN_ENGINE_PASS builds=%0d services=%0d hls_calls=%0d responses=%0d errors=%0d checks=%0d blocked=%0d",builds,services,hls_calls,hls_responses,errors,checks,blocked);$finish;
    end
endmodule
