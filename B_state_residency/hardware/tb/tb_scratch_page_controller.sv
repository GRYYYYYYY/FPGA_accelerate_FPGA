`timescale 1ns/1ps
module controller_test #(parameter integer TX_BITS=16, GENERATION_BITS=16);
    reg clk=0; always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;
    wire cmd_ready,rsp_valid,rsp_present,rsp_dirty,draining;
    reg [3:0] cmd_op=0,cmd_price=0;
    reg [1:0] cmd_slot=0,cmd_query=0;
    reg [17:0] cmd_page=0;
    reg [GENERATION_BITS-1:0] cmd_generation=0;
    reg [TX_BITS-1:0] cmd_tx=0;
    reg cmd_kind=0,cmd_present=0,peer_quiescent=0,ingress_empty=0;
    reg [5:0] cmd_offset=0;
    reg [2:0] cmd_field=0;
    reg [31:0] cmd_value=0;
    reg [159:0] cmd_payload=0;
    wire [2:0] rsp_status;
    wire [159:0] rsp_payload;
    wire [TX_BITS-1:0] rsp_tx;
    scratch_page_controller #(.TX_BITS(TX_BITS),.GENERATION_BITS(GENERATION_BITS)) dut(.*);
    integer fd,fields,checks=0,stalls=0,held,deadline;
    integer op,slot,page,qid,price,gen,tx,kind,present,offset,field,peer,empty;
    integer status,expected_present,expected_dirty,expected_tx,expected_draining;
    reg [31:0] value;
    reg [159:0] payload,expected;
    reg [4095:0] vector_path;
    task automatic check_response;
        begin
            if(!rsp_valid || cmd_ready || rsp_status!==status[2:0] || rsp_payload!==expected
               || rsp_present!==expected_present[0] || rsp_dirty!==expected_dirty[0]
               || rsp_tx!==expected_tx[TX_BITS-1:0] || draining!==expected_draining[0])
                $fatal(1,"mismatch check=%0d op=%0d slot=%0d page=%0d q=%0d gen=%0d tx=%0d status=%0d/%0d word=%h/%h present=%b/%b dirty=%b/%b outtx=%0d/%0d drain=%b/%b",checks,op,slot,page,qid,gen,tx,rsp_status,status,rsp_payload,expected,rsp_present,expected_present,rsp_dirty,expected_dirty,rsp_tx,expected_tx,draining,expected_draining);
        end
    endtask
    initial begin #1000000000; $fatal(1,"watchdog checks=%0d",checks); end
    initial begin
        repeat(3) @(negedge clk);rst=0;
        if(!$value$plusargs("VECTORS=%s",vector_path))$fatal(1,"VECTORS required");
        fd=$fopen(vector_path,"r");if(!fd)$fatal(1,"missing vectors");
        while(!$feof(fd)) begin
            fields=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",op,slot,page,qid,price,gen,tx,kind,present,offset,field,value,payload,peer,empty,status,expected,expected_present,expected_dirty,expected_tx,expected_draining);
            if(fields!=21)$fatal(1,"bad vector line check=%0d fields=%0d",checks,fields);
            @(negedge clk);
            cmd_valid=1;cmd_op=op;cmd_slot=slot;cmd_page=page;cmd_query=qid;cmd_price=price;
            cmd_generation=gen;cmd_tx=tx;cmd_kind=kind;cmd_present=present;cmd_offset=offset;
            cmd_field=field;cmd_value=value;cmd_payload=payload;peer_quiescent=peer;ingress_empty=empty;
            @(posedge clk);while(!cmd_ready)@(posedge clk);
            @(negedge clk);cmd_valid=0;
            // Poison all live request fields after handshake. Latched commands
            // must survive this even while the synchronous RAM is processing.
            cmd_op=15;cmd_slot=3;cmd_page=18'h3ffff;cmd_generation='1;cmd_query=3;cmd_price=15;
            cmd_tx='1;cmd_kind=~kind;cmd_present=~present;cmd_offset=63;cmd_field=7;
            cmd_value='1;cmd_payload='1;peer_quiescent=0;ingress_empty=0;
            deadline=0;
            while(!rsp_valid) begin
                @(negedge clk);deadline=deadline+1;
                if(deadline>20)$fatal(1,"command stuck check=%0d op=%0d",checks,op);
            end
            check_response();
            if(checks%13==0) begin
                // Present an illegal next request during response backpressure;
                // ready must remain low and all response outputs must be stable.
                cmd_valid=1;
                for(held=0;held<4;held=held+1) begin
                    @(negedge clk);check_response();stalls=stalls+1;
                end
                cmd_valid=0;
            end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
        $fclose(fd);
        if(checks==0)$fatal(1,"empty test");
        $display("TEST_PASS scratch_page_controller tx_bits=%0d gen_bits=%0d checks=%0d stalls=%0d",TX_BITS,GENERATION_BITS,checks,stalls);
        $finish;
    end
endmodule
module tb_controller_small;
    controller_test #(.TX_BITS(3),.GENERATION_BITS(3)) test();
endmodule
module tb_controller_actual;
    controller_test test();
endmodule
