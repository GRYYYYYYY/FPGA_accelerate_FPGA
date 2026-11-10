`timescale 1ns/1ps
// Standalone controller contract. External COMPLETE remains a trusted durability
// attestation here; composed native endpoint tests prove AXI/codec ordering.
module tb_sparse_writeback_boundaries;
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
        cmd_value=0;issue(3,0,0,0,0,1,1,0);
        cmd_value=7;issue(3,7,0,0,7,1,1,0);
        issue(5,0,0,0,8'h81,0,0,0);
        issue(8,0,0,6,0,0,0,0); // both present offsets still outstanding
        issue(9,1,0,4,0,0,0,0); // absent is already represented, cannot export it
        issue(9,0,0,0,0,1,1,0); // present zero must still be acknowledged
        issue(9,0,0,4,0,0,0,0); // duplicate
        issue(9,7,1,1,0,0,0,0); // wrong transaction
        cmd_generation=1;issue(9,7,0,1,0,0,0,0);cmd_generation=0;
        issue(3,7,0,4,0,0,0,0); // mutation blocked while snapshot leased
        issue(8,0,0,6,0,0,0,0); // offset7 still missing
        issue(9,7,0,0,7,1,1,0);
        issue(8,0,0,0,0,0,0,0);issue(4,0,0,0,0,0,0,0);
        cmd_slot=1;issue(1,0,0,0,0,0,0,0);
        issue(5,0,0,0,0,0,0,1); // no stale bitmap from prior slot
        issue(8,0,1,0,0,0,0,0);issue(4,0,0,0,0,0,0,0);
        issue(1,0,0,5,0,0,0,0); // generation quarantine unchanged
        issue(14,0,0,3,0,0,0,0); // no new public/controller mask opcode
        if(checks!=22 || draining)$fatal(1,"boundary coverage");
        $display("SPARSE_WB_BOUNDARIES_PASS checks=22 early_complete_rejections=2 duplicates=1 stale_descriptors=2 mutation_rejections=1");
        $finish;
    end
endmodule
