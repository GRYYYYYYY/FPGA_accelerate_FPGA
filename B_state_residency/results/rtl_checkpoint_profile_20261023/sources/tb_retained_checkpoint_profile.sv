`timescale 1ns/1ps
// Passive observer: never drives the frozen testbench or DUT.
module tb_retained_checkpoint_profile;
    tb_retained_endpoint_multipage test();
    longint unsigned cycle=0,begin_cycle=0,response_cycle=0;
    longint unsigned stage_cycles[21:29];
    integer fd,i,count=0;
    reg pending=0,seen_response=0;
    initial begin
        fd=$fopen("checkpoint_cycles.csv","w");
        if(!fd)$fatal(1,"cannot open checkpoint profile");
        $fdisplay(fd,"checkpoint,response_cycles,consume_cycles,begin_send,begin_wait,drain,finish_send,finish_wait,memory_send,memory_wait,query_send,query_wait");
        for(i=21;i<=29;i=i+1)stage_cycles[i]=0;
    end
    always @(posedge test.clk)begin
        cycle=cycle+1;
        if(!test.rst)begin
            if(test.cmd_valid && test.cmd_ready && test.cmd_op==12)begin
                if(pending)$fatal(1,"overlapping profiled checkpoint");
                pending=1;seen_response=0;begin_cycle=cycle;
                for(i=21;i<=29;i=i+1)stage_cycles[i]=0;
            end
            if(pending && test.dut.state>=21 && test.dut.state<=29)
                stage_cycles[test.dut.state]=stage_cycles[test.dut.state]+1;
            if(pending && test.rsp_valid && !seen_response)begin
                if(test.rsp_status!=0)$fatal(1,"profiled checkpoint failed");
                seen_response=1;response_cycle=cycle;
            end
            if(pending && test.rsp_valid && test.rsp_ready)begin
                count=count+1;
                $fdisplay(fd,"%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",count,response_cycle-begin_cycle,cycle-begin_cycle,
                    stage_cycles[21],stage_cycles[22],stage_cycles[23],stage_cycles[24],stage_cycles[25],stage_cycles[26],stage_cycles[27],stage_cycles[28],stage_cycles[29]);
                pending=0;
            end
        end
    end
    final begin
        $fclose(fd);
        if(count==8 && !pending && test.checks==221)$display("CHECKPOINT_PROFILE_PASS checkpoints=%0d checks=%0d",count,test.checks);
        else $display("CHECKPOINT_PROFILE_INCOMPLETE count=%0d pending=%b checks=%0d",count,pending,test.checks);
    end
endmodule
