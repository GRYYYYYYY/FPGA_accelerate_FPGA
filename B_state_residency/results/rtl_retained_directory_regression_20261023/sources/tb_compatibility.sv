`timescale 1ns/1ps
module tb_indexed_directory #(
    parameter integer FRAMES=16, INDEX_BITS=4, HASH_BITS=4, PROBE_LIMIT=2, EPOCH_BITS=2, DIFFERENTIAL=1
);
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0,memory_success=0,fence_retired=0;
    reg [2:0] cmd_op=0;reg [23:0] cmd_owner=0;reg [INDEX_BITS-1:0] cmd_frame=0;reg [63:0] cmd_cookie=0;
    wire cmd_ready,rsp_valid,rsp_published,any_fault;
    wire [2:0] rsp_status;wire [INDEX_BITS-1:0] rsp_frame;wire [31:0] rsp_address;
    wire [INDEX_BITS:0] allocated;wire [3:0] leased;
    backing_frame_directory_retained #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),
        .PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) dut(.*);
    wire ref_ready,ref_valid,ref_pub,ref_fault;
    wire [2:0] ref_status;wire [INDEX_BITS-1:0] ref_frame;wire [31:0] ref_address;
    wire [INDEX_BITS:0] ref_allocated;wire [3:0] ref_leased;
    generate if(DIFFERENTIAL)begin:linear
        backing_frame_directory_lookup #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS)) reference_dir(
            .clk(clk),.rst(rst),.cmd_valid(cmd_valid),.cmd_ready(ref_ready),
            .cmd_op(cmd_op),.cmd_owner(cmd_owner),.cmd_frame(cmd_frame),.cmd_cookie(cmd_cookie),
            .memory_success(memory_success),.fence_retired(fence_retired),.rsp_valid(ref_valid),.rsp_ready(rsp_ready),
            .rsp_status(ref_status),.rsp_frame(ref_frame),.rsp_address(ref_address),.rsp_published(ref_pub),
            .allocated(ref_allocated),.leased(ref_leased),.any_fault(ref_fault));
    end else begin:no_reference
        assign ref_ready=cmd_ready;assign ref_valid=rsp_valid;assign ref_status=rsp_status;
        assign ref_frame=rsp_frame;assign ref_address=rsp_address;assign ref_pub=rsp_published;
        assign ref_allocated=allocated;assign ref_leased=leased;assign ref_fault=any_fault;
    end endgenerate
    integer fd,rc,checks=0,cycles=0,start_cycle=0,first_dut=0,first_ref=0;
    integer dut_cycles=0,ref_cycles=0,hold_cycles=0,initial_clear=0,wrap_clears=0;
    integer fallback_allocations=0,scan_cycles=0,empty_fallbacks=0,index_hits=0;
    integer op,owner,fr,success,fence,es,ef,ep,ea,el,ex,h,deadline;
    reg [63:0] token;reg [4095:0] vector_path;
    reg [3:0] prior_state=0;
    always @(posedge clk)begin
        cycles<=cycles+1;
        if(!rst)begin
            if(dut.state==14 && !dut.clear_response)initial_clear<=initial_clear+1;
            if(dut.state==14 && dut.clear_response && prior_state!=14)wrap_clears<=wrap_clears+1;
            if(dut.state==3 && !dut.insertion_slot)fallback_allocations<=fallback_allocations+1;
            if(dut.state==1)scan_cycles<=scan_cycles+1;
            if(dut.state==11 && dut.index_word[EPOCH_BITS+INDEX_BITS-1:INDEX_BITS]!=dut.epoch
               && !dut.index_complete && allocated!=0)empty_fallbacks<=empty_fallbacks+1;
            if(dut.state==13 && {1'b0,dut.indexed_frame}<allocated && dut.read_word[23:0]==dut.owner)
                index_hits<=index_hits+1;
            if(dut.state==14 && (cmd_ready || rsp_valid))$fatal(1,"exposed incomplete index scrub");
        end
        prior_state<=dut.state;
    end
    task automatic check_outputs;
        begin
            if(!rsp_valid || rsp_status!==es[2:0] || rsp_frame!==ef[INDEX_BITS-1:0]
               || rsp_address!==32'(ef*1344) || rsp_published!==ep[0]
               || allocated!==ea[INDEX_BITS:0] || leased!==el[3:0] || any_fault!==ex[0])
                $fatal(1,"indexed mismatch check=%0d op=%0d owner=%h status=%0d/%0d frame=%0d/%0d pub=%0d/%0d alloc=%0d/%0d leases=%h/%h fault=%b/%b",
                    checks,op,owner,rsp_status,es,rsp_frame,ef,rsp_published,ep,allocated,ea,leased,el,any_fault,ex);
            if(!ref_valid || {ref_status,ref_frame,ref_address,ref_pub,ref_allocated,ref_leased,ref_fault}
                !=={rsp_status,rsp_frame,rsp_address,rsp_published,allocated,leased,any_fault})
                $fatal(1,"linear/indexed difference check=%0d",checks);
            if(cmd_ready || ref_ready)$fatal(1,"accepted command while response stalled");
        end
    endtask
    initial begin
        if(!$value$plusargs("VECTORS=%s",vector_path))$fatal(1,"missing VECTORS");
        fd=$fopen(vector_path,"r");if(!fd)$fatal(1,"cannot read vectors");
        repeat(4)@(negedge clk);rst=0;
        while(!$feof(fd))begin
            rc=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h\n",op,owner,fr,token,success,fence,es,ef,ep,ea,el,ex);
            if(rc!=12)$fatal(1,"vector parse count=%0d rc=%0d",checks,rc);
            deadline=0;
            while(!cmd_ready || !ref_ready)begin
                @(negedge clk);deadline=deadline+1;if(deadline>2*(2**HASH_BITS)+10)$fatal(1,"ready timeout");
            end
            cmd_valid=1;cmd_op=op;cmd_owner=owner;cmd_frame=fr;cmd_cookie=token;
            memory_success=success;fence_retired=fence;
            @(posedge clk);start_cycle=cycles;
            @(negedge clk);cmd_valid=0;cmd_op=7;cmd_owner='1;cmd_frame='1;cmd_cookie='1;
            memory_success=0;fence_retired=0;first_dut=-1;first_ref=-1;deadline=0;
            while(first_dut<0 || first_ref<0)begin
                if(rsp_valid && first_dut<0)first_dut=cycles-start_cycle;
                if(ref_valid && first_ref<0)first_ref=cycles-start_cycle;
                if(first_dut<0 || first_ref<0)@(negedge clk);
                deadline=deadline+1;if(deadline>4*FRAMES+2**HASH_BITS+1000)$fatal(1,"response timeout check=%0d",checks);
            end
            dut_cycles=dut_cycles+first_dut;ref_cycles=ref_cycles+first_ref;
            for(h=0;h<3+(checks%4);h=h+1)begin check_outputs();@(negedge clk);hold_cycles=hold_cycles+1;end
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;checks=checks+1;
        end
        $fclose(fd);
        if(initial_clear!=2**HASH_BITS || fallback_allocations==0 || index_hits==0 || empty_fallbacks==0)
            $fatal(1,"missing index coverage clear=%0d overflow=%0d hit=%0d empty_fallback=%0d",initial_clear,fallback_allocations,index_hits,empty_fallbacks);
        if(DIFFERENTIAL && wrap_clears<2)$fatal(1,"missing epoch wraps");
        $display("TEST_PASS indexed_directory differential=%0d checks=%0d dut_cycles=%0d ref_cycles=%0d holds=%0d initial_clear=%0d wraps=%0d overflow=%0d scans=%0d empty_fallbacks=%0d hits=%0d",
            DIFFERENTIAL,checks,dut_cycles,ref_cycles,hold_cycles,initial_clear,wrap_clears,fallback_allocations,scan_cycles,empty_fallbacks,index_hits);
        $finish;
    end
    initial begin #1000000000;$fatal(1,"watchdog");end
endmodule

module tb_indexed_directory_small;
    tb_indexed_directory test();
endmodule
module tb_indexed_directory_large;
    tb_indexed_directory #(.FRAMES(23405),.INDEX_BITS(15),.HASH_BITS(15),.PROBE_LIMIT(64),.EPOCH_BITS(8),.DIFFERENTIAL(0)) test();
endmodule
