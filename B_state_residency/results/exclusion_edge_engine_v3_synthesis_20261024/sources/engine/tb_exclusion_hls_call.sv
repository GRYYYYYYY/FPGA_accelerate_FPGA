`timescale 1ns/1ps
module tb_exclusion_hls_call;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,abort=0,call_valid=0,reply_ready=0;
    wire call_ready,reply_valid,fault,ap_start;
    reg [287:0] call_command=0;wire [287:0] hls_command;
    wire [159:0] reply_data;reg [159:0] hls_reply=0;
    reg [4:0] hls_valid=0;reg ap_ready=0,ap_done=0,ap_idle=1;
    exclusion_hls_call #(.MAX_CALL_CYCLES(32)) dut(.*);
    integer checks=0,permutations=0,fault_cases=0,a,b,c,d,e,f,j,seq[0:5];
    reg [159:0] expected,held_packet;reg held=0;
    reg [287:0] expected_command;
    always @(posedge clk)begin
        if(rst)held<=0;
        else begin
            if(held&&(!reply_valid||reply_data!==held_packet))$fatal(1,"collector reply changed under backpressure");
            held<=reply_valid&&!reply_ready;held_packet<=reply_data;
        end
    end
    initial begin #1000000;$fatal(1,"collector watchdog");end
    task reset_all;
        begin
            @(negedge clk);rst=1;abort=0;call_valid=0;reply_ready=0;hls_valid=0;ap_done=0;ap_ready=0;
            repeat(3)@(negedge clk);rst=0;
        end
    endtask
    task launch(input integer accept_start);
        begin
            @(negedge clk);call_command={9{32'habc00000+checks}};expected_command=call_command;call_valid=1;
            do @(posedge clk);while(!call_ready);
            @(negedge clk);call_valid=0;call_command='1;
            repeat(3)begin
                if(!ap_start||hls_command!==expected_command||reply_valid||call_ready)$fatal(1,"collector start contract");
                @(negedge clk);
            end
            if(accept_start)begin ap_ready=1;@(negedge clk);ap_ready=0;
                if(ap_start)$fatal(1,"collector repeated accepted start");end
            for(j=0;j<5;j=j+1)expected[j*32+:32]=32'h12000000+checks*8+j;
        end
    endtask
    task retire;
        begin
            wait(reply_valid);repeat(4)@(negedge clk);
            if(reply_data!==expected||fault||ap_start||call_ready)$fatal(1,"collector incoherent reply");
            reply_ready=1;@(negedge clk);reply_ready=0;checks=checks+1;
        end
    endtask
    task expect_fault;
        begin
            #1;if(!fault)$fatal(1,"collector fault not visible before sampling case=%0d",fault_cases);
            repeat(2)@(negedge clk);abort=0;hls_valid=0;ap_done=0;ap_ready=0;
            repeat(3)@(negedge clk);
            if(!fault||call_ready||ap_start)$fatal(1,"collector fault did not latch");
            fault_cases=fault_cases+1;
        end
    endtask
    initial begin
        reset_all;
        // Six events: five independent output strobes and ap_done, in all 720 orders.
        for(a=0;a<6;a=a+1)for(b=0;b<6;b=b+1)if(b!=a)
        for(c=0;c<6;c=c+1)if(c!=a&&c!=b)
        for(d=0;d<6;d=d+1)if(d!=a&&d!=b&&d!=c)
        for(e=0;e<6;e=e+1)if(e!=a&&e!=b&&e!=c&&e!=d)
        for(f=0;f<6;f=f+1)if(f!=a&&f!=b&&f!=c&&f!=d&&f!=e)begin
            launch(1);seq[0]=a;seq[1]=b;seq[2]=c;seq[3]=d;seq[4]=e;seq[5]=f;
            for(j=0;j<6;j=j+1)begin
                hls_reply='1;hls_valid=0;ap_done=0;
                if(seq[j]==5)ap_done=1;
                else begin hls_valid[seq[j]]=1;hls_reply[seq[j]*32+:32]=expected[seq[j]*32+:32];end
                @(negedge clk);hls_valid=0;ap_done=0;
                if(j<5&&reply_valid)$fatal(1,"collector replied before complete set");
                @(negedge clk);
            end
            retire;permutations=permutations+1;
        end
        // All outputs and done on the start-acceptance cycle are coherent too.
        launch(0);ap_ready=1;ap_done=1;hls_valid=31;hls_reply=expected;
        @(negedge clk);ap_ready=0;ap_done=0;hls_valid=0;retire;
        reset_all;launch(1);hls_valid=1;@(negedge clk);hls_valid=0;@(negedge clk);hls_valid=1;expect_fault;
        reset_all;launch(1);ap_done=1;@(negedge clk);ap_done=0;@(negedge clk);ap_done=1;expect_fault;
        reset_all;hls_valid=1;expect_fault;
        reset_all;ap_done=1;expect_fault;
        reset_all;launch(0);hls_valid=1;expect_fault;
        reset_all;launch(0);repeat(35)@(negedge clk);expect_fault;
        reset_all;launch(1);hls_valid=31;hls_reply=expected;@(negedge clk);hls_valid=0;repeat(35)@(negedge clk);expect_fault;
        reset_all;launch(1);ap_done=1;hls_valid=15;@(negedge clk);ap_done=0;hls_valid=0;repeat(35)@(negedge clk);expect_fault;
        reset_all;launch(1);hls_reply=expected;hls_valid=31;ap_done=1;@(negedge clk);hls_valid=0;ap_done=0;
        wait(reply_valid);@(negedge clk);abort=1;expect_fault;
        if(reply_data!==expected||!reply_valid)$fatal(1,"abort altered held collector reply");
        if(permutations!=720||checks!=721||fault_cases!=9)$fatal(1,"collector coverage incomplete");
        $display("HLS_CALL_PASS permutations=%0d coherent_calls=%0d fault_cases=%0d",permutations,checks,fault_cases);$finish;
    end
endmodule
