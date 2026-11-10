`timescale 1ns/1ps
// Standalone controller contract. External COMPLETE remains a trusted durability
// attestation here; composed native endpoint tests prove AXI/codec ordering.
module tb_sparse_records_boundaries;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;
    wire cmd_ready,rsp_valid;
    reg [3:0] cmd_op=0,cmd_price=0;
    reg [4:0] cmd_slot=0;reg [1:0] cmd_query=0;
    reg [20:0] cmd_page=42;
    reg [15:0] cmd_generation=0,cmd_tx=0;
    reg cmd_kind=0,cmd_present=0;
    reg [2:0] cmd_offset=0,cmd_field=0;
    reg [31:0] cmd_value=0;
    reg [159:0] cmd_payload=0;
    reg peer_quiescent=1,ingress_empty=1;
    wire [2:0] rsp_status;wire [159:0] rsp_payload;
    wire rsp_present,rsp_dirty,draining;wire [15:0] rsp_tx;
    scratch_page_controller_small dut(.*);
    integer checks=0,timeout_count;
    task automatic issue(input integer op,off,tx,status,input reg [159:0] payload,input integer present,dirty,rtx);
        begin
            @(negedge clk);cmd_op=op;cmd_offset=off;cmd_tx=tx;cmd_valid=1;
            timeout_count=0;@(posedge clk);
            while(!cmd_ready)begin @(posedge clk);timeout_count=timeout_count+1;if(timeout_count>100)$fatal(1,"command timeout");end
            @(negedge clk);cmd_valid=0;
            timeout_count=0;
            while(!rsp_valid)begin @(negedge clk);timeout_count=timeout_count+1;if(timeout_count>100)$fatal(1,"response timeout");end
            repeat(3)begin
                if(rsp_status!==status[2:0] || rsp_payload!==payload || rsp_present!==present[0] || rsp_dirty!==dirty[0] || rsp_tx!==rtx[15:0])
                    $fatal(1,"boundary mismatch check=%0d op=%0d status=%0d/%0d payload=%h/%h",checks,op,rsp_status,status,rsp_payload,payload);
                @(negedge clk);
            end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
    endtask
    initial begin #100000;$fatal(1,"boundary watchdog");end
    initial begin
        repeat(3)@(negedge clk);rst=0;
        issue(0,0,0,0,0,0,0,0);issue(1,0,0,0,0,0,0,0);
        cmd_kind=1;issue(6,0,0,0,0,0,0,0);
        issue(8,0,0,6,0,0,0,0); // even empty refill needs explicit seal
        cmd_kind=0;issue(14,0,0,1,0,0,0,0);cmd_kind=1;
        issue(14,0,1,1,0,0,0,0);
        cmd_generation=1;issue(14,0,0,1,0,0,0,0);cmd_generation=0;
        cmd_payload=256;issue(14,0,0,3,0,0,0,0); // noncanonical high bits
        cmd_payload=8'h81;issue(14,0,0,6,0,0,0,0); // missing both present records
        cmd_payload=0;cmd_present=0;issue(7,0,0,3,0,0,0,0); // absent BEAT forbidden
        cmd_present=1;issue(7,0,0,0,0,1,0,0); // present zero is loaded and counted
        issue(7,0,0,4,0,0,0,0); // duplicate record
        issue(14,0,0,6,0,0,0,0); // empty mask omits already loaded present0
        cmd_payload=8'h81;issue(14,0,0,6,0,0,0,0); // offset7 still missing
        cmd_payload=7;issue(7,7,0,0,7,1,0,0);
        issue(2,7,0,4,0,0,0,0); // not visible before COMPLETE
        issue(8,0,0,6,0,0,0,0); // all present loaded but no seal yet
        cmd_payload=8'h81;issue(14,0,0,0,0,0,0,0);
        issue(14,0,0,4,0,0,0,0); // duplicate seal
        cmd_payload=1;issue(7,1,0,4,0,0,0,0); // no records after seal
        issue(8,0,0,0,0,0,0,0);
        issue(2,0,0,0,0,1,0,0);issue(2,7,0,0,7,1,0,0);
        issue(6,0,0,3,0,0,0,0); // cannot refill nonpristine binding
        issue(4,0,0,0,0,0,0,0);
        cmd_slot=1;issue(1,0,0,0,0,0,0,0);
        issue(6,0,0,0,0,0,0,1); // new RF lease clears sealed state
        cmd_payload=0;issue(14,0,1,0,0,0,0,0); // valid trusted empty representation
        issue(8,0,1,0,0,0,0,0);
        issue(2,0,0,0,0,0,0,0); // old data/bitmap from slot0 not visible
        issue(4,0,0,0,0,0,0,0);
        issue(1,0,0,5,0,0,0,0); // generation quarantine retained
        cmd_query=1;cmd_generation=1;issue(1,0,0,1,0,0,0,0);
        if(checks!=33 || draining)$fatal(1,"RF boundary coverage checks=%0d",checks);
        $display("SPARSE_RF_BOUNDARIES_PASS checks=33");$finish;
    end
endmodule
