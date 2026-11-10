`timescale 1ns/1ps
// Independent serial word oracle versus queued requests with periodic stalls.
module tb_queued_ordering;
    localparam integer N=6144;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;
    wire cmd_ready,rsp_valid,rsp_present,rsp_dirty,draining;
    reg [3:0] cmd_op=0,cmd_price=0;
    reg [1:0] cmd_slot=0,cmd_query=0;
    reg [17:0] cmd_page=0;
    reg [15:0] cmd_generation=0,cmd_tx=0;
    reg cmd_kind=0,cmd_present=0;
    reg [5:0] cmd_offset=0;
    reg [2:0] cmd_field=0;
    reg [31:0] cmd_value=0;
    reg [159:0] cmd_payload=0;
    wire [2:0] rsp_status;
    wire [159:0] rsp_payload;
    wire [15:0] rsp_tx;
    reg dispatch_enable=1,execute_enable=1,fence_service_enable=1,ack_receive_enable=1;
    wire fence_active,peer_sealed,acknowledged;
    wire [1:0] fence_tag;
    wire [3:0] leases;
    wire [2:0] request_count,work_count,response_count;
    wire [1:0] fence_request_count,fence_ack_count;
    queued_scratch_endpoint dut(.*);
    reg [159:0] reference_words[0:63],expected_words[0:N-1];
    reg [63:0] reference_present=0;
    reg expected_present[0:N-1];
    reg [3:0] operations[0:N-1];
    reg [5:0] offsets[0:N-1];
    reg [2:0] fields[0:N-1];
    reg [31:0] values[0:N-1];
    reg running=0,holding=0;
    reg [180:0] held_response;
    integer cycle=0,received=0,sent=0,stalls=0,req_full=0,work_full=0,rsp_full=0;
    integer i,k,f,deadline;
    reg [31:0] state=32'h20261023,v;
    always @(negedge clk) if(running) begin
        dispatch_enable=(cycle%17)>=4;
        execute_enable=(cycle%29)>=8;
        // Long bursts of output backpressure fill all pipeline stages.
        rsp_ready=(cycle%101)>=70 && (cycle%11)!=0;
    end
    always @(posedge clk) begin
        cycle=cycle+1;
        if(running) begin
            if(request_count==4)req_full=req_full+1;
            if(work_count==4)work_full=work_full+1;
            if(response_count==4)rsp_full=rsp_full+1;
            if(holding && (!rsp_valid || {rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx}!==held_response))
                $fatal(1,"queued output changed under hold index=%0d",received);
            holding=rsp_valid && !rsp_ready;
            if(holding)begin held_response={rsp_status,rsp_payload,rsp_present,rsp_dirty,rsp_tx};stalls=stalls+1;end
            if(cmd_valid && cmd_ready)sent=sent+1;
            if(rsp_valid && rsp_ready) begin
                if(received>=N || received>=sent || rsp_status!==3'd0 || rsp_payload!==expected_words[received]
                    || rsp_present!==expected_present[received] || rsp_dirty!==1'b1 || rsp_tx!==16'd0)
                    $fatal(1,"FIFO ordering/value mismatch index=%0d sent=%0d status=%h word=%h expected=%h",received,sent,rsp_status,rsp_payload,expected_words[received]);
                received=received+1;
            end
        end
    end
    task automatic setup(input integer op);
        begin
            @(negedge clk);cmd_op=op;cmd_valid=1;
            @(posedge clk);while(!cmd_ready)@(posedge clk);
            @(negedge clk);cmd_valid=0;while(!rsp_valid)@(negedge clk);
            if(rsp_status!=0)$fatal(1,"setup failed");
            rsp_ready=1;@(posedge clk);@(negedge clk);rsp_ready=0;
        end
    endtask
    initial begin #100000000;$fatal(1,"ordering watchdog sent=%0d received=%0d",sent,received);end
    initial begin
        for(i=0;i<64;i=i+1)reference_words[i]=0;
        // Precompute the full expected serial history, before any DUT command.
        for(i=0;i<N;i=i+1) begin
            state=state^(state<<13);state=state^(state>>17);state=state^(state<<5);
            k=state[5:0];f=(state>>6)%5;v=state ^ (32'h9e3779b9*i);
            operations[i]=(i%3==2 || i>=N-128)?2:3;
            offsets[i]=i>=N-128?(i%64):k;fields[i]=f;values[i]=f==4?(v&255):v;
            k=offsets[i];
            if(operations[i]==3) begin
                case(f)
                    0:reference_words[k][31:0]=values[i];
                    1:reference_words[k][63:32]=values[i];
                    2:reference_words[k][95:64]=values[i];
                    3:reference_words[k][127:96]=values[i];
                    4:reference_words[k][135:128]=values[i][7:0];
                endcase
                reference_present[k]=1;
            end
            expected_words[i]=reference_words[k];expected_present[i]=reference_present[k];
        end
        repeat(3)@(negedge clk);rst=0;setup(0);setup(1);running=1;
        for(i=0;i<N;i=i+1) begin
            @(negedge clk);cmd_valid=1;cmd_op=operations[i];cmd_offset=offsets[i];cmd_field=fields[i];cmd_value=values[i];
            deadline=0;@(posedge clk);
            while(!cmd_ready)begin @(posedge clk);deadline=deadline+1;if(deadline>300)$fatal(1,"input stuck");end
            @(negedge clk);cmd_valid=0;cmd_op=15;cmd_offset=63;cmd_field=7;cmd_value='1;
        end
        while(received<N)@(negedge clk);
        @(negedge clk);running=0;rsp_ready=0;
        if(sent!=N || request_count!=0 || work_count!=0 || response_count!=0 || !req_full || !work_full || !rsp_full)
            $fatal(1,"missing queue pressure or unretired responses");
        $display("TEST_PASS queued_ordering checks=%0d stalled_cycles=%0d request_full=%0d work_full=%0d response_full=%0d",received,stalls,req_full,work_full,rsp_full);
        $finish;
    end
endmodule
