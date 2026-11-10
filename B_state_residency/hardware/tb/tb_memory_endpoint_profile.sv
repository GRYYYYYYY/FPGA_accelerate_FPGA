`timescale 1ns/1ps
// Passive observer only: no force, drive, delay, or mutation of the frozen test.
module tb_memory_endpoint_profile;
    memory_endpoint_test #(.SMALL(0)) test();
    longint unsigned samples=0,unassigned=0,accepted=0,retired=0;
    longint unsigned endpoint_cycles[0:20],op_cycles[0:15][0:20];
    longint unsigned directory_cycles[0:6],codec_cycles[0:13],axi_cycles[0:4],service_cycles[0:7];
    longint unsigned q_accepted=0,q_retired=0,q_core_accepted=0,q_core_retired=0;
    longint unsigned q_busy=0,q_request_nonempty=0,q_work_nonempty=0,q_response_nonempty=0;
    longint unsigned record_inputs=0,record_outputs=0,host_response_stalls=0;
    longint unsigned aw_stalls=0,w_stalls=0,ar_stalls=0,r_stalls=0;
    longint unsigned start_cycle=0,available_cycle=0;
    reg pending=0,seen_response=0;
    integer pending_op=0,pending_query=0,pending_page=0;
    integer csv,hist,i,j;reg [4095:0] prefix;
    initial begin
        if(!$value$plusargs("PROFILE=%s",prefix))$fatal(1,"missing PROFILE prefix");
        csv=$fopen($sformatf("%0s.commands.csv",prefix),"w");
        hist=$fopen($sformatf("%0s.counts.csv",prefix),"w");
        if(!csv || !hist)$fatal(1,"cannot open profile output");
        $fdisplay(csv,"index,op,query,page,accept_cycle,response_cycle,retire_cycle");
        $fdisplay(hist,"group,op,index,cycles");
        for(i=0;i<21;i=i+1)begin endpoint_cycles[i]=0;for(j=0;j<16;j=j+1)op_cycles[j][i]=0;end
        for(i=0;i<7;i=i+1)directory_cycles[i]=0;
        for(i=0;i<14;i=i+1)codec_cycles[i]=0;
        for(i=0;i<5;i=i+1)axi_cycles[i]=0;
        for(i=0;i<8;i=i+1)service_cycles[i]=0;
    end
    always @(posedge test.clk)if(!test.rst)begin
        samples=samples+1;
        if(test.dut.state>20 || test.dut.memory.codec.state>13 || test.dut.memory.memory_service.directory.state>6 || test.dut.memory.memory_service.dma.state>4 || test.dut.memory.state>7)$fatal(1,"unknown observed state");
        endpoint_cycles[test.dut.state]=endpoint_cycles[test.dut.state]+1;
        directory_cycles[test.dut.memory.memory_service.directory.state]=directory_cycles[test.dut.memory.memory_service.directory.state]+1;
        codec_cycles[test.dut.memory.codec.state]=codec_cycles[test.dut.memory.codec.state]+1;
        axi_cycles[test.dut.memory.memory_service.dma.state]=axi_cycles[test.dut.memory.memory_service.dma.state]+1;
        service_cycles[test.dut.memory.state]=service_cycles[test.dut.memory.state]+1;
        if(test.cmd_valid && test.cmd_ready)begin
            if(pending)$fatal(1,"overlapping profile commands");
            pending=1;seen_response=0;start_cycle=samples;available_cycle=0;
            pending_op=test.cmd_op;pending_query=test.cmd_query;pending_page=test.cmd_page;accepted=accepted+1;
        end
        if(pending)op_cycles[pending_op][test.dut.state]=op_cycles[pending_op][test.dut.state]+1;
        else unassigned=unassigned+1;
        if(test.rsp_valid && !seen_response)begin
            if(!pending)$fatal(1,"response without command");
            available_cycle=samples;seen_response=1;
        end
        if(test.rsp_valid && test.rsp_ready)begin
            if(!pending || !seen_response)$fatal(1,"unpaired response");
            $fdisplay(csv,"%0d,%0d,%0d,%0d,%0d,%0d,%0d",retired,pending_op,pending_query,pending_page,start_cycle,available_cycle,samples);
            retired=retired+1;pending=0;
        end
        if(test.dut.q_send && test.dut.q_ready)q_accepted=q_accepted+1;
        if(test.dut.q_valid && test.dut.q_receive)q_retired=q_retired+1;
        if(test.dut.pages.core_valid && test.dut.pages.core_ready)q_core_accepted=q_core_accepted+1;
        if(test.dut.pages.core_rsp_valid && test.dut.pages.busy && !test.dut.pages.local_pending && test.dut.pages.response_in_ready)q_core_retired=q_core_retired+1;
        if(test.dut.pages.busy)q_busy=q_busy+1;
        if(test.dut.pages.request_count!=0)q_request_nonempty=q_request_nonempty+1;
        if(test.dut.pages.work_count!=0)q_work_nonempty=q_work_nonempty+1;
        if(test.dut.pages.response_count!=0)q_response_nonempty=q_response_nonempty+1;
        if(test.dut.memory.record_in_valid && test.dut.memory.record_in_ready)record_inputs=record_inputs+1;
        if(test.dut.memory.record_out_valid && test.dut.memory.record_out_ready)record_outputs=record_outputs+1;
        if(test.rsp_valid && !test.rsp_ready)host_response_stalls=host_response_stalls+1;
        if(test.m_awvalid && !test.m_awready)aw_stalls=aw_stalls+1;
        if(test.m_wvalid && !test.m_wready)w_stalls=w_stalls+1;
        if(test.m_arvalid && !test.m_arready)ar_stalls=ar_stalls+1;
        if(test.m_rvalid && !test.m_rready)r_stalls=r_stalls+1;
    end
    final begin
        for(i=0;i<21;i=i+1)begin
            $fdisplay(hist,"endpoint,-1,%0d,%0d",i,endpoint_cycles[i]);
            for(j=0;j<16;j=j+1)$fdisplay(hist,"operation,%0d,%0d,%0d",j,i,op_cycles[j][i]);
        end
        for(i=0;i<7;i=i+1)$fdisplay(hist,"directory,-1,%0d,%0d",i,directory_cycles[i]);
        for(i=0;i<14;i=i+1)$fdisplay(hist,"codec,-1,%0d,%0d",i,codec_cycles[i]);
        for(i=0;i<5;i=i+1)$fdisplay(hist,"axi,-1,%0d,%0d",i,axi_cycles[i]);
        for(i=0;i<8;i=i+1)$fdisplay(hist,"service,-1,%0d,%0d",i,service_cycles[i]);
        $fdisplay(hist,"scalar,-1,0,%0d",samples);$fdisplay(hist,"scalar,-1,1,%0d",unassigned);
        $fdisplay(hist,"scalar,-1,2,%0d",accepted);$fdisplay(hist,"scalar,-1,3,%0d",retired);
        $fdisplay(hist,"scalar,-1,4,%0d",q_accepted);$fdisplay(hist,"scalar,-1,5,%0d",q_retired);
        $fdisplay(hist,"scalar,-1,6,%0d",q_core_accepted);$fdisplay(hist,"scalar,-1,7,%0d",q_core_retired);
        $fdisplay(hist,"scalar,-1,8,%0d",q_busy);$fdisplay(hist,"scalar,-1,9,%0d",q_request_nonempty);
        $fdisplay(hist,"scalar,-1,10,%0d",q_work_nonempty);$fdisplay(hist,"scalar,-1,11,%0d",q_response_nonempty);
        $fdisplay(hist,"scalar,-1,12,%0d",record_inputs);$fdisplay(hist,"scalar,-1,13,%0d",record_outputs);
        $fdisplay(hist,"scalar,-1,14,%0d",host_response_stalls);$fdisplay(hist,"scalar,-1,15,%0d",aw_stalls);
        $fdisplay(hist,"scalar,-1,16,%0d",w_stalls);$fdisplay(hist,"scalar,-1,17,%0d",ar_stalls);$fdisplay(hist,"scalar,-1,18,%0d",r_stalls);
        $fclose(csv);$fclose(hist);
        if(test.checks==77099 && accepted==77099 && retired==77099 && !pending)
            $display("PROFILE_PASS samples=%0d accepted=%0d retired=%0d",samples,accepted,retired);
        else $display("PROFILE_INCOMPLETE checks=%0d accepted=%0d retired=%0d pending=%b",test.checks,accepted,retired,pending);
    end
endmodule
