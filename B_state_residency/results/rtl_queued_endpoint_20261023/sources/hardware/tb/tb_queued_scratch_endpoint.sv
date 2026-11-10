`timescale 1ns/1ps
module queued_endpoint_test #(parameter integer SMALL=0, TAG_BITS=2);
    localparam integer TX_BITS=SMALL?3:16, GENERATION_BITS=SMALL?3:16;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;
    wire cmd_ready,rsp_valid,rsp_present,rsp_dirty,draining;
    reg [3:0] cmd_op=0,cmd_price=0;
    reg [1:0] cmd_slot=0,cmd_query=0;
    reg [17:0] cmd_page=0;
    reg [GENERATION_BITS-1:0] cmd_generation=0;
    reg [TX_BITS-1:0] cmd_tx=0;
    reg cmd_kind=0,cmd_present=0;
    reg [5:0] cmd_offset=0;
    reg [2:0] cmd_field=0;
    reg [31:0] cmd_value=0;
    reg [159:0] cmd_payload=0;
    wire [2:0] rsp_status;
    wire [159:0] rsp_payload;
    wire [TX_BITS-1:0] rsp_tx;
    reg dispatch_enable=1,execute_enable=1,fence_service_enable=1,ack_receive_enable=1;
    wire fence_active,peer_sealed,acknowledged;
    wire [TAG_BITS-1:0] fence_tag;
    wire [3:0] leases;
    wire [2:0] request_count,work_count,response_count;
    wire [1:0] fence_request_count,fence_ack_count;
    queued_scratch_endpoint #(.TX_BITS(TX_BITS),.GENERATION_BITS(GENERATION_BITS),.TAG_BITS(TAG_BITS)) dut(.*);
    integer checks=0,sent=0,stalls=0,retries=0,wraps=0,cycles=0;
    integer status_seen[0:7];
    reg [2:0] got_status;
    reg [159:0] got_payload;
    reg got_present,got_dirty;
    reg [TX_BITS-1:0] got_tx;
    always @(posedge clk) begin
        cycles<=cycles+1;
        if(!rst && (request_count>4 || work_count>4 || response_count>4 || fence_request_count>2 || fence_ack_count>2))
            $fatal(1,"FIFO overflow");
    end
    task automatic send_cmd(input integer op,slot,page,qid,price,gen,tx,kind,present,offset,field,
        input reg [31:0] value,input reg [159:0] payload);
        integer deadline;
        begin
            @(negedge clk);cmd_valid=1;cmd_op=op;cmd_slot=slot;cmd_page=page;cmd_query=qid;cmd_price=price;
            cmd_generation=gen;cmd_tx=tx;cmd_kind=kind;cmd_present=present;cmd_offset=offset;
            cmd_field=field;cmd_value=value;cmd_payload=payload;
            deadline=0;@(posedge clk);
            while(!cmd_ready) begin @(posedge clk);deadline=deadline+1;if(deadline>200)$fatal(1,"send timeout op=%0d",op);end
            sent=sent+1;@(negedge clk);cmd_valid=0;
            cmd_op=15;cmd_slot=3;cmd_page='1;cmd_query=3;cmd_price=15;cmd_generation='1;
            cmd_tx='1;cmd_kind=1;cmd_present=1;cmd_offset=63;cmd_field=7;cmd_value='1;cmd_payload='1;
        end
    endtask
    task automatic receive_rsp(input integer expected_status,input reg [159:0] expected,
        input integer expected_present,expected_dirty,expected_tx,input integer hold_cycles);
        integer deadline,held;
        begin
            deadline=0;
            while(!rsp_valid) begin @(negedge clk);deadline=deadline+1;if(deadline>200)$fatal(1,"response timeout check=%0d",checks);end
            got_status=rsp_status;got_payload=rsp_payload;got_present=rsp_present;got_dirty=rsp_dirty;got_tx=rsp_tx;
            if(expected_status>=0 && (rsp_status!==expected_status[2:0] || rsp_payload!==expected
                || rsp_present!==expected_present[0] || rsp_dirty!==expected_dirty[0] || rsp_tx!==expected_tx[TX_BITS-1:0]))
                $fatal(1,"response mismatch check=%0d status=%0d/%0d payload=%h/%h present=%b/%b dirty=%b/%b tx=%0d/%0d",checks,rsp_status,expected_status,rsp_payload,expected,rsp_present,expected_present,rsp_dirty,expected_dirty,rsp_tx,expected_tx);
            for(held=0;held<hold_cycles;held=held+1) begin
                @(negedge clk);
                if(!rsp_valid || {rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx} !== {got_status,got_payload,got_present,got_dirty,got_tx})
                    $fatal(1,"response changed under backpressure");
                stalls=stalls+1;
            end
            status_seen[got_status]=status_seen[got_status]+1;
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
    endtask
    task automatic simple(input integer op,expected_status);
        begin send_cmd(op,0,7,0,0,0,0,0,0,0,0,0,0);receive_rsp(expected_status,0,0,expected_status==2,0,2);end
    endtask
    task automatic finish_fence;
        integer tries,old_tag;
        begin
            old_tag=fence_tag;tries=0;
            send_cmd(11,0,0,0,0,0,0,0,0,0,0,0,0);receive_rsp(-1,0,0,0,0,0);
            while(got_status==7) begin
                retries=retries+1;tries=tries+1;if(tries>30)$fatal(1,"fence stuck");
                send_cmd(11,0,0,0,0,0,0,0,0,0,0,0,0);receive_rsp(-1,0,0,0,0,0);
            end
            if(got_status!=0 || got_payload!=0 || got_present || got_dirty || got_tx!=0 || draining || fence_active
               || acknowledged || peer_sealed || leases!=0 || request_count!=0 || work_count!=0 || response_count!=0
               || fence_request_count!=0 || fence_ack_count!=0 || fence_tag!==((old_tag+1)&((1<<TAG_BITS)-1)))
                $fatal(1,"invalid fence retirement tag=%0d old=%0d status=%0d",fence_tag,old_tag,got_status);
            if(fence_tag==0)wraps=wraps+1;
        end
    endtask
    integer fd,fields,op,slot,page,qid,price,gen,tx,kind,present,offset,field,peer,empty;
    integer status,expected_present,expected_dirty,expected_tx,expected_draining;
    reg [31:0] value;
    reg [159:0] payload,expected,word;
    reg [4095:0] vector_path;
    integer i,j,epoch,n,deadline,actual_commands=0;
    task automatic boundary_test;
        begin
            simple(12,3);simple(13,3);simple(11,7);
            // Fill request and work queues independently; every input must survive
            // FIFO wrap and stalled downstream execution in original order.
            dispatch_enable=0;execute_enable=0;
            for(i=0;i<4;i=i+1)send_cmd(15,0,0,0,0,0,0,0,0,0,0,0,0);
            repeat(5)@(negedge clk);
            if(request_count!=4 || cmd_ready || work_count!=0)$fatal(1,"request full gate failed");
            dispatch_enable=1;repeat(8)@(negedge clk);
            if(work_count!=4 || request_count!=0)$fatal(1,"work fill failed");
            for(i=0;i<4;i=i+1)send_cmd(15,0,0,0,0,0,0,0,0,0,0,0,0);
            if(request_count!=4 || cmd_ready)$fatal(1,"work pressure not propagated");
            execute_enable=1;repeat(40)@(negedge clk);
            if(response_count!=4)$fatal(1,"response FIFO did not fill");
            for(i=0;i<8;i=i+1)receive_rsp(3,0,0,0,0,3);
            // Nonzero tags and repeated wrap, with blocked ACK/control queues.
            for(epoch=0;epoch<24;epoch=epoch+1) begin
                simple(0,0);simple(1,0);
                send_cmd(3,0,7,0,0,0,0,0,0,0,0,32'h7fc12345+epoch,0);
                word=32'h7fc12345+epoch;receive_rsp(0,word,1,1,0,1);
                simple(10,2);simple(5,0);
                if(leases!=1)$fatal(1,"missing writeback lease");
                fence_service_enable=0;ack_receive_enable=0;
                simple(10,0);simple(12,0);simple(12,4);
                if(fence_request_count!=2)$fatal(1,"control request full gate");
                fence_service_enable=1;repeat(8)@(negedge clk);
                if(peer_sealed || fence_ack_count!=0)$fatal(1,"peer sealed with outstanding lease");
                simple(11,7);simple(8,6);
                for(j=0;j<64;j=j+1) begin
                    send_cmd(9,0,7,0,0,0,0,0,0,j,0,0,0);
                    receive_rsp(0,j==0?word:160'b0,j==0,1,0,j%7==0?2:0);
                end
                simple(8,0);simple(8,1);
                if(leases!=0)$fatal(1,"completion did not release lease");
                simple(4,0);
                repeat(8)@(negedge clk);
                if(!peer_sealed || acknowledged || fence_ack_count!=2)$fatal(1,"expected queued ACKs");
                simple(13,4);simple(11,7);
                // Consume exactly one ACK; the duplicate remains and forbids finish.
                @(negedge clk);ack_receive_enable=1;@(posedge clk);@(negedge clk);ack_receive_enable=0;
                if(!acknowledged || fence_ack_count!=1)$fatal(1,"first ACK receipt failed");
                simple(11,7);simple(13,0);
                if(fence_ack_count!=2)$fatal(1,"duplicate ACK queueing failed");
                ack_receive_enable=1;repeat(6)@(negedge clk);
                // A successfully acknowledged fence cannot recycle while an old
                // command response is still buffered, even if its command failed.
                send_cmd(15,0,0,0,0,0,0,0,0,0,0,0,0);
                repeat(10)@(negedge clk);
                send_cmd(11,0,0,0,0,0,0,0,0,0,0,0,0);
                repeat(10)@(negedge clk);
                if(!draining || !fence_active)$fatal(1,"retired with old response buffered");
                receive_rsp(3,0,0,0,0,3);receive_rsp(7,0,0,0,0,1);
                // Work queued behind FINISH also prevents early token reuse.
                execute_enable=0;
                send_cmd(11,0,0,0,0,0,0,0,0,0,0,0,0);
                send_cmd(15,0,0,0,0,0,0,0,0,0,0,0,0);
                repeat(6)@(negedge clk);execute_enable=1;
                receive_rsp(7,0,0,0,0,0);receive_rsp(3,0,0,0,0,0);
                // Exercise the same-cycle ingress race exactly: FINISH already
                // at the work head, another request handshakes on its issue edge.
                execute_enable=0;send_cmd(11,0,0,0,0,0,0,0,0,0,0,0,0);
                repeat(6)@(negedge clk);
                @(negedge clk);execute_enable=1;cmd_valid=1;cmd_op=15;
                @(posedge clk);if(!cmd_ready)$fatal(1,"race setup failed");sent=sent+1;
                @(negedge clk);cmd_valid=0;
                receive_rsp(7,0,0,0,0,0);receive_rsp(3,0,0,0,0,0);
                finish_fence();
                // New epoch may reuse tx=0 and generation=0 only now; old RAM hidden.
                simple(0,0);simple(1,0);simple(2,0);simple(4,0);simple(10,0);finish_fence();
            end
            if(wraps!=48/(1<<TAG_BITS))$fatal(1,"missing finite tag wrap");
        end
    endtask
    initial begin #1000000000;$fatal(1,"watchdog checks=%0d",checks);end
    initial begin
        for(n=0;n<8;n=n+1)status_seen[n]=0;
        repeat(3)@(negedge clk);rst=0;
        if(SMALL)boundary_test();
        else begin
            if(!$value$plusargs("VECTORS=%s",vector_path))$fatal(1,"missing VECTORS");
            fd=$fopen(vector_path,"r");if(!fd)$fatal(1,"cannot open VECTORS");
            while(!$feof(fd)) begin
                fields=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",op,slot,page,qid,price,gen,tx,kind,present,offset,field,value,payload,peer,empty,status,expected,expected_present,expected_dirty,expected_tx,expected_draining);
                if(fields!=21)$fatal(1,"malformed vector");
                if(op==11)finish_fence();
                else begin
                    send_cmd(op,slot,page,qid,price,gen,tx,kind,present,offset,field,value,payload);
                    receive_rsp(status,expected,expected_present,expected_dirty,expected_tx,actual_commands%13==0?4:0);
                    if(draining!==expected_draining[0])$fatal(1,"wrong draining state");
                end
                actual_commands=actual_commands+1;
            end
            $fclose(fd);
            if(actual_commands!=472689)$fatal(1,"incomplete real workload");
        end
        if(sent!=checks || request_count!=0 || work_count!=0 || response_count!=0 || leases!=0 || draining || fence_active)
            $fatal(1,"unretired work at finish sent=%0d checks=%0d",sent,checks);
        $display("TEST_PASS queued_scratch_endpoint small=%0d tag_bits=%0d checks=%0d actual_commands=%0d stalls=%0d retries=%0d wraps=%0d",SMALL,TAG_BITS,checks,actual_commands,stalls,retries,wraps);
        $finish;
    end
endmodule
module tb_queued_small;queued_endpoint_test #(.SMALL(1),.TAG_BITS(1)) test();endmodule
module tb_queued_actual;queued_endpoint_test test();endmodule
