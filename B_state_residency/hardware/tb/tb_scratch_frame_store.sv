`timescale 1ns/1ps
module tb_scratch_frame_store;
    reg clk=0; always #5 clk=~clk;
    reg rst=1, cmd_valid=0, rsp_ready=0;
    wire cmd_ready, rsp_valid, rsp_present, rsp_dirty;
    reg [2:0] cmd_op=0, cmd_field=0;
    reg [1:0] cmd_slot=0, cmd_query=0;
    reg [17:0] cmd_page=0;
    reg [3:0] cmd_price=0;
    reg [15:0] cmd_generation=0;
    reg [5:0] cmd_offset=0;
    reg [31:0] cmd_value=0;
    reg [159:0] cmd_payload=0;
    wire [2:0] rsp_status;
    wire [159:0] rsp_payload;
    scratch_frame_store dut(.*);
    integer checks=0, stalls=0, real_commands=0;
    task automatic transact(
        input integer op, slot, page, query_id, price, generation, offset, field,
        input reg [31:0] value,
        input reg [159:0] payload,
        input integer expected_status,
        input reg [159:0] expected_payload,
        input integer expected_present, expected_dirty
    );
        integer held;
        begin
            @(negedge clk);
            cmd_valid=1;cmd_op=op;cmd_slot=slot;cmd_page=page;cmd_query=query_id;
            cmd_price=price;cmd_generation=generation;cmd_offset=offset;cmd_field=field;
            cmd_value=value;cmd_payload=payload;
            @(posedge clk); while(!cmd_ready) @(posedge clk);
            @(negedge clk);cmd_valid=0;
            while(!rsp_valid) @(negedge clk);
            if (rsp_status !== expected_status[2:0] || rsp_payload !== expected_payload
                || rsp_present !== expected_present[0] || rsp_dirty !== expected_dirty[0])
                $fatal(1,"response mismatch check=%0d op=%0d slot=%0d page=%0d gen=%0d status=%h/%h payload=%h/%h present=%b/%b dirty=%b/%b",checks,op,slot,page,generation,rsp_status,expected_status,rsp_payload,expected_payload,rsp_present,expected_present,rsp_dirty,expected_dirty);
            if(checks%17==0) begin
                for(held=0;held<3;held=held+1) begin
                    @(negedge clk);
                    if(!rsp_valid || cmd_ready || rsp_status !== expected_status[2:0]
                       || rsp_payload !== expected_payload || rsp_present !== expected_present[0] || rsp_dirty !== expected_dirty[0])
                        $fatal(1,"response changed under backpressure check=%0d",checks);
                    stalls=stalls+1;
                end
            end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
    endtask

    integer fd, fields, op,slot,page,qid,price,gen,offset,field,status,present,dirty;
    reg [31:0] value;
    reg [159:0] payload,expected,word;
    reg [4095:0] vector_path;
    initial begin
        #100000000;
        $fatal(1,"watchdog timeout checks=%0d",checks);
    end
    initial begin
        repeat(3) @(negedge clk);rst=0;
        transact(1,0,7,1,2,1,0,0,0,0,1,0,0,0); // unbound
        transact(0,0,7,1,2,1,0,0,0,0,0,0,0,0);
        transact(0,0,7,1,2,1,0,0,0,0,4,0,0,0); // bound cannot be overwritten
        transact(1,0,7,1,2,1,0,0,0,0,0,0,0,0); // no RAM reset required
        word=0;word[31:0]=32'h7fc12345;
        transact(2,0,7,1,2,1,0,0,32'h7fc12345,0,0,word,1,1);
        word[63:32]=32'h80000000;
        transact(2,0,7,1,2,1,0,1,32'h80000000,0,0,word,1,1);
        word[95:64]=32'hffffffff;
        transact(2,0,7,1,2,1,0,2,32'hffffffff,0,0,word,1,1);
        word[127:96]=32'h7fffffff;
        transact(2,0,7,1,2,1,0,3,32'h7fffffff,0,0,word,1,1);
        word[135:128]=8'hff;
        transact(2,0,7,1,2,1,0,4,255,0,0,word,1,1);
        transact(4,0,7,1,2,1,0,0,0,0,2,0,0,1); // dirty unbind blocked
        transact(3,0,7,1,2,0,0,0,0,0,1,0,0,0); // stale CLEAN cannot clear dirty
        transact(4,0,7,1,2,1,0,0,0,0,2,0,0,1);
        transact(1,0,7,1,3,1,0,0,0,0,1,0,0,0); // price mismatch
        transact(1,0,7,2,2,1,0,0,0,0,1,0,0,0); // query mismatch
        transact(1,0,8,1,2,1,0,0,0,0,1,0,0,0); // page mismatch
        transact(2,0,7,1,2,1,0,5,1,0,3,0,0,0); // illegal field
        transact(2,0,7,1,2,1,0,4,256,0,3,0,0,0); // target must fit byte
        transact(5,0,7,1,2,1,0,0,0,0,2,0,0,1); // LOAD cannot clobber dirty page
        transact(1,0,7,1,2,1,0,0,0,0,0,word,1,1);
        transact(3,0,7,1,2,1,0,0,0,0,0,0,0,0);
        transact(4,0,7,1,2,1,0,0,0,0,0,0,0,0);
        transact(0,0,7,1,2,2,0,0,0,0,0,0,0,0);
        transact(1,0,7,1,2,1,0,0,0,0,1,0,0,0); // old generation
        transact(1,0,7,1,2,2,0,0,0,0,0,0,0,0); // old RAM hidden by bitmap
        payload=word;payload[159]=1;
        transact(5,0,7,1,2,2,0,0,0,payload,3,0,0,0); // canonical padding
        transact(5,0,7,1,2,2,0,0,0,word,0,word,1,0);
        transact(1,0,7,1,2,2,0,0,0,0,0,word,1,0);
        transact(6,0,7,1,2,2,0,0,0,0,3,0,0,0); // invalid opcode
        transact(4,0,7,1,2,2,0,0,0,0,0,0,0,0);
        if(!$value$plusargs("VECTORS=%s",vector_path)) vector_path="actual_vectors.txt";
        fd=$fopen(vector_path,"r");
        if(!fd)$fatal(1,"actual vector file missing");
        while(!$feof(fd)) begin
            fields=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h %h %h\n",op,slot,page,qid,price,gen,offset,field,value,payload,status,expected,present,dirty);
            if(fields==14) begin
                transact(op,slot,page,qid,price,gen,offset,field,value,payload,status,expected,present,dirty);
                real_commands=real_commands+1;
            end else if(fields!=-1)$fatal(1,"malformed actual vector fields=%0d",fields);
        end
        $fclose(fd);
        if(real_commands==0 || stalls==0)$fatal(1,"required stimulus unused");
        $display("TEST_PASS scratch_frame_store checks=%0d actual_commands=%0d stalled_cycles=%0d",checks,real_commands,stalls);
        $finish;
    end
endmodule
