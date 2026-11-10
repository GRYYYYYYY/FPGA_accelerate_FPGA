`timescale 1ns/1ps
module tb_children_reset;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,ap_start=0;
    wire ap_ready,ap_done,ap_idle;
    reg [31:0] op=0,parent=0,count=0,prune=0,query=0,price=0,generation=0,position=0,phase=0,node=0,value_r=0,aux=0,service_status=0;
    wire [351:0] result;wire [10:0] valid;
    reg [351:0] held=0;reg [10:0] seen=0;reg done_seen=0;
    integer calls=0,resets=0,i,target;
    children_step dut(.ap_clk(clk),.ap_rst(rst),.ap_start(ap_start),.ap_ready(ap_ready),.ap_done(ap_done),.ap_idle(ap_idle),
        .op(op),.parent(parent),.count(count),.prune(prune),.query(query),.price(price),.generation(generation),.position(position),.phase(phase),.node(node),.value_r(value_r),.aux(aux),.service_status(service_status),
        .status(result[31:0]),.result_generation(result[63:32]),.request(result[95:64]),.result_position(result[127:96]),.result_node(result[159:128]),
        .result_parent(result[191:160]),.result_query(result[223:192]),.result_price(result[255:224]),.emitted(result[287:256]),.active_r(result[319:288]),.fault(result[351:320]),
        .status_ap_vld(valid[0]),.result_generation_ap_vld(valid[1]),.request_ap_vld(valid[2]),.result_position_ap_vld(valid[3]),.result_node_ap_vld(valid[4]),
        .result_parent_ap_vld(valid[5]),.result_query_ap_vld(valid[6]),.result_price_ap_vld(valid[7]),.emitted_ap_vld(valid[8]),.active_r_ap_vld(valid[9]),.fault_ap_vld(valid[10]));
    always @(posedge clk)begin
        if(rst)begin seen<=0;done_seen<=0;held<=0;end
        else begin
            if(ap_done)done_seen<=1;
            for(i=0;i<11;i=i+1)if(valid[i])begin held[i*32+:32]<=result[i*32+:32];seen[i]<=1;end
        end
    end
    task call(input [31:0] expected_status);
        begin
            @(negedge clk);seen=0;done_seen=0;ap_start=1;
            do @(posedge clk);while(!ap_ready);
            @(negedge clk);ap_start=0;
            wait(done_seen&&(&seen));@(negedge clk);
            if(held[31:0]!==expected_status)$fatal(1,"status call=%0d got=%0d want=%0d",calls,held[31:0],expected_status);
            calls=calls+1;
        end
    endtask
    task reset_and_snapshot;
        begin
            @(negedge clk);rst=1;ap_start=0;repeat(6)@(negedge clk);rst=0;resets=resets+1;
            op=2;call(0);
            if(held!=={256'b0,32'd8,64'b0})$fatal(1,"static state did not reset at target=%0d value=%h",target,held);
        end
    endtask
    task start_build;
        begin
            op=0;parent=16;count=1;prune=1;query=2;price=7;service_status=0;call(0);
            if(held[63:32]!=1||held[95:64]!=0||held[127:96]!=0||held[159:128]!=16||held[191:160]!=16||held[223:192]!=2||held[255:224]!=7||held[287:256]!=0||held[319:288]!=1||held[351:320]!=0)$fatal(1,"new build after reset wrong");
        end
    endtask
    task respond;
        begin
            op=1;generation=held[63:32];position=held[127:96];phase=held[95:64];node=held[159:128];value_r=0;aux=0;service_status=0;
            if(phase==0)begin value_r=17;aux=1;end
            if(phase==5)value_r=1;
            call(0);
        end
    endtask
    initial begin #100000;$fatal(1,"children reset watchdog");end
    initial begin
        for(target=0;target<8;target=target+1)begin
            reset_and_snapshot;start_build;
            while(held[95:64]!=target)respond;
            if(held[319:288]!=1)$fatal(1,"not active at reset boundary");
        end
        reset_and_snapshot;start_build;
        while(held[95:64]!=8)respond;
        if(held[287:256]!=1||held[319:288]!=0)$fatal(1,"publish did not complete");
        op=0;call(0);if(held[63:32]!=2)$fatal(1,"generation not monotonic");
        op=1;generation=2;position=0;phase=0;node=16;service_status=10;call(8);
        if(held[351:320]!=1||held[319:288]!=1)$fatal(1,"service error not latched");
        op=0;call(9);
        reset_and_snapshot;start_build;
        op=1;generation=1;position=0;phase=0;node=16;value_r=32'h00ffffff;aux=0;service_status=0;call(0);
        if(held[159:128]!=32'h00ffffff||held[95:64]!=1)$fatal(1,"24-bit child upper boundary lost");
        reset_and_snapshot;
        op=0;parent=32'h00ffffff;count=0;prune=0;query=3;price=15;call(0);
        if(held[159:128]!=32'h00ffffff||held[191:160]!=32'h00ffffff||held[95:64]!=7||held[223:192]!=3||held[255:224]!=15)$fatal(1,"24-bit parent upper boundary lost");
        respond;if(held[319:288]!=0)$fatal(1,"empty high-parent publish failed");
        $display("CHILDREN_RESET_PASS phases=8 resets=%0d calls=%0d fault_recovery=1 high_boundary=1",resets,calls);$finish;
    end
endmodule
