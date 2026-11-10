`timescale 1ns/1ps
module tb_frontier_hls_call;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,abort=0,call_valid=0,reply_ready=0;
    wire call_ready,reply_valid,fault,ap_start;
    reg [95:0] call_command=0;wire [95:0] hls_command;
    wire [127:0] reply_data;reg [127:0] hls_reply=0;
    reg [3:0] hls_valid=0;reg ap_ready=0,ap_done=0,ap_idle=1;
    frontier_hls_call #(.MAX_CALL_CYCLES(32)) dut(.*);
    integer checks=0,permutations=0,fault_cases=0,a,b,c,d,e,f,j,k,n,tmp,missing,seq[0:4];
    reg [31:0] rng=32'h824bd31a;
    reg [127:0] expected,held_packet;reg held=0;
    reg [95:0] expected_command;
    always @(posedge clk)begin
        if(rst)held<=0;
        else begin
            if(held&&(!reply_valid||reply_data!==held_packet))$fatal(1,"collector reply changed under backpressure");
            held<=reply_valid&&!reply_ready;held_packet<=reply_data;
        end
    end
    initial begin #10000000;$fatal(1,"collector watchdog");end
    task reset_all;
        begin
            @(negedge clk);rst=1;abort=0;call_valid=0;reply_ready=0;hls_valid=0;ap_done=0;ap_ready=0;
            repeat(3)@(negedge clk);rst=0;
        end
    endtask
    task launch(input integer accept_start);
        begin
            @(negedge clk);call_command={3{32'habc00000+checks}};expected_command=call_command;call_valid=1;
            do @(posedge clk);while(!call_ready);
            @(negedge clk);call_valid=0;call_command='1;
            repeat(3)begin
                if(!ap_start||hls_command!==expected_command||reply_valid||call_ready)$fatal(1,"collector start contract");
                @(negedge clk);
            end
            if(accept_start)begin ap_ready=1;@(negedge clk);ap_ready=0;
                if(ap_start)$fatal(1,"collector repeated accepted start");end
            for(j=0;j<4;j=j+1)expected[j*32+:32]=32'h12000000+checks*16+j;
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
        // All 120 permutations of four output strobes and done.
        for(n=0;n<120;n=n+1)begin
            case(n)
              0:begin seq[0]=0;seq[1]=1;seq[2]=2;seq[3]=3;seq[4]=4; end
              1:begin seq[0]=0;seq[1]=1;seq[2]=2;seq[3]=4;seq[4]=3; end
              2:begin seq[0]=0;seq[1]=1;seq[2]=3;seq[3]=2;seq[4]=4; end
              3:begin seq[0]=0;seq[1]=1;seq[2]=3;seq[3]=4;seq[4]=2; end
              4:begin seq[0]=0;seq[1]=1;seq[2]=4;seq[3]=2;seq[4]=3; end
              5:begin seq[0]=0;seq[1]=1;seq[2]=4;seq[3]=3;seq[4]=2; end
              6:begin seq[0]=0;seq[1]=2;seq[2]=1;seq[3]=3;seq[4]=4; end
              7:begin seq[0]=0;seq[1]=2;seq[2]=1;seq[3]=4;seq[4]=3; end
              8:begin seq[0]=0;seq[1]=2;seq[2]=3;seq[3]=1;seq[4]=4; end
              9:begin seq[0]=0;seq[1]=2;seq[2]=3;seq[3]=4;seq[4]=1; end
              10:begin seq[0]=0;seq[1]=2;seq[2]=4;seq[3]=1;seq[4]=3; end
              11:begin seq[0]=0;seq[1]=2;seq[2]=4;seq[3]=3;seq[4]=1; end
              12:begin seq[0]=0;seq[1]=3;seq[2]=1;seq[3]=2;seq[4]=4; end
              13:begin seq[0]=0;seq[1]=3;seq[2]=1;seq[3]=4;seq[4]=2; end
              14:begin seq[0]=0;seq[1]=3;seq[2]=2;seq[3]=1;seq[4]=4; end
              15:begin seq[0]=0;seq[1]=3;seq[2]=2;seq[3]=4;seq[4]=1; end
              16:begin seq[0]=0;seq[1]=3;seq[2]=4;seq[3]=1;seq[4]=2; end
              17:begin seq[0]=0;seq[1]=3;seq[2]=4;seq[3]=2;seq[4]=1; end
              18:begin seq[0]=0;seq[1]=4;seq[2]=1;seq[3]=2;seq[4]=3; end
              19:begin seq[0]=0;seq[1]=4;seq[2]=1;seq[3]=3;seq[4]=2; end
              20:begin seq[0]=0;seq[1]=4;seq[2]=2;seq[3]=1;seq[4]=3; end
              21:begin seq[0]=0;seq[1]=4;seq[2]=2;seq[3]=3;seq[4]=1; end
              22:begin seq[0]=0;seq[1]=4;seq[2]=3;seq[3]=1;seq[4]=2; end
              23:begin seq[0]=0;seq[1]=4;seq[2]=3;seq[3]=2;seq[4]=1; end
              24:begin seq[0]=1;seq[1]=0;seq[2]=2;seq[3]=3;seq[4]=4; end
              25:begin seq[0]=1;seq[1]=0;seq[2]=2;seq[3]=4;seq[4]=3; end
              26:begin seq[0]=1;seq[1]=0;seq[2]=3;seq[3]=2;seq[4]=4; end
              27:begin seq[0]=1;seq[1]=0;seq[2]=3;seq[3]=4;seq[4]=2; end
              28:begin seq[0]=1;seq[1]=0;seq[2]=4;seq[3]=2;seq[4]=3; end
              29:begin seq[0]=1;seq[1]=0;seq[2]=4;seq[3]=3;seq[4]=2; end
              30:begin seq[0]=1;seq[1]=2;seq[2]=0;seq[3]=3;seq[4]=4; end
              31:begin seq[0]=1;seq[1]=2;seq[2]=0;seq[3]=4;seq[4]=3; end
              32:begin seq[0]=1;seq[1]=2;seq[2]=3;seq[3]=0;seq[4]=4; end
              33:begin seq[0]=1;seq[1]=2;seq[2]=3;seq[3]=4;seq[4]=0; end
              34:begin seq[0]=1;seq[1]=2;seq[2]=4;seq[3]=0;seq[4]=3; end
              35:begin seq[0]=1;seq[1]=2;seq[2]=4;seq[3]=3;seq[4]=0; end
              36:begin seq[0]=1;seq[1]=3;seq[2]=0;seq[3]=2;seq[4]=4; end
              37:begin seq[0]=1;seq[1]=3;seq[2]=0;seq[3]=4;seq[4]=2; end
              38:begin seq[0]=1;seq[1]=3;seq[2]=2;seq[3]=0;seq[4]=4; end
              39:begin seq[0]=1;seq[1]=3;seq[2]=2;seq[3]=4;seq[4]=0; end
              40:begin seq[0]=1;seq[1]=3;seq[2]=4;seq[3]=0;seq[4]=2; end
              41:begin seq[0]=1;seq[1]=3;seq[2]=4;seq[3]=2;seq[4]=0; end
              42:begin seq[0]=1;seq[1]=4;seq[2]=0;seq[3]=2;seq[4]=3; end
              43:begin seq[0]=1;seq[1]=4;seq[2]=0;seq[3]=3;seq[4]=2; end
              44:begin seq[0]=1;seq[1]=4;seq[2]=2;seq[3]=0;seq[4]=3; end
              45:begin seq[0]=1;seq[1]=4;seq[2]=2;seq[3]=3;seq[4]=0; end
              46:begin seq[0]=1;seq[1]=4;seq[2]=3;seq[3]=0;seq[4]=2; end
              47:begin seq[0]=1;seq[1]=4;seq[2]=3;seq[3]=2;seq[4]=0; end
              48:begin seq[0]=2;seq[1]=0;seq[2]=1;seq[3]=3;seq[4]=4; end
              49:begin seq[0]=2;seq[1]=0;seq[2]=1;seq[3]=4;seq[4]=3; end
              50:begin seq[0]=2;seq[1]=0;seq[2]=3;seq[3]=1;seq[4]=4; end
              51:begin seq[0]=2;seq[1]=0;seq[2]=3;seq[3]=4;seq[4]=1; end
              52:begin seq[0]=2;seq[1]=0;seq[2]=4;seq[3]=1;seq[4]=3; end
              53:begin seq[0]=2;seq[1]=0;seq[2]=4;seq[3]=3;seq[4]=1; end
              54:begin seq[0]=2;seq[1]=1;seq[2]=0;seq[3]=3;seq[4]=4; end
              55:begin seq[0]=2;seq[1]=1;seq[2]=0;seq[3]=4;seq[4]=3; end
              56:begin seq[0]=2;seq[1]=1;seq[2]=3;seq[3]=0;seq[4]=4; end
              57:begin seq[0]=2;seq[1]=1;seq[2]=3;seq[3]=4;seq[4]=0; end
              58:begin seq[0]=2;seq[1]=1;seq[2]=4;seq[3]=0;seq[4]=3; end
              59:begin seq[0]=2;seq[1]=1;seq[2]=4;seq[3]=3;seq[4]=0; end
              60:begin seq[0]=2;seq[1]=3;seq[2]=0;seq[3]=1;seq[4]=4; end
              61:begin seq[0]=2;seq[1]=3;seq[2]=0;seq[3]=4;seq[4]=1; end
              62:begin seq[0]=2;seq[1]=3;seq[2]=1;seq[3]=0;seq[4]=4; end
              63:begin seq[0]=2;seq[1]=3;seq[2]=1;seq[3]=4;seq[4]=0; end
              64:begin seq[0]=2;seq[1]=3;seq[2]=4;seq[3]=0;seq[4]=1; end
              65:begin seq[0]=2;seq[1]=3;seq[2]=4;seq[3]=1;seq[4]=0; end
              66:begin seq[0]=2;seq[1]=4;seq[2]=0;seq[3]=1;seq[4]=3; end
              67:begin seq[0]=2;seq[1]=4;seq[2]=0;seq[3]=3;seq[4]=1; end
              68:begin seq[0]=2;seq[1]=4;seq[2]=1;seq[3]=0;seq[4]=3; end
              69:begin seq[0]=2;seq[1]=4;seq[2]=1;seq[3]=3;seq[4]=0; end
              70:begin seq[0]=2;seq[1]=4;seq[2]=3;seq[3]=0;seq[4]=1; end
              71:begin seq[0]=2;seq[1]=4;seq[2]=3;seq[3]=1;seq[4]=0; end
              72:begin seq[0]=3;seq[1]=0;seq[2]=1;seq[3]=2;seq[4]=4; end
              73:begin seq[0]=3;seq[1]=0;seq[2]=1;seq[3]=4;seq[4]=2; end
              74:begin seq[0]=3;seq[1]=0;seq[2]=2;seq[3]=1;seq[4]=4; end
              75:begin seq[0]=3;seq[1]=0;seq[2]=2;seq[3]=4;seq[4]=1; end
              76:begin seq[0]=3;seq[1]=0;seq[2]=4;seq[3]=1;seq[4]=2; end
              77:begin seq[0]=3;seq[1]=0;seq[2]=4;seq[3]=2;seq[4]=1; end
              78:begin seq[0]=3;seq[1]=1;seq[2]=0;seq[3]=2;seq[4]=4; end
              79:begin seq[0]=3;seq[1]=1;seq[2]=0;seq[3]=4;seq[4]=2; end
              80:begin seq[0]=3;seq[1]=1;seq[2]=2;seq[3]=0;seq[4]=4; end
              81:begin seq[0]=3;seq[1]=1;seq[2]=2;seq[3]=4;seq[4]=0; end
              82:begin seq[0]=3;seq[1]=1;seq[2]=4;seq[3]=0;seq[4]=2; end
              83:begin seq[0]=3;seq[1]=1;seq[2]=4;seq[3]=2;seq[4]=0; end
              84:begin seq[0]=3;seq[1]=2;seq[2]=0;seq[3]=1;seq[4]=4; end
              85:begin seq[0]=3;seq[1]=2;seq[2]=0;seq[3]=4;seq[4]=1; end
              86:begin seq[0]=3;seq[1]=2;seq[2]=1;seq[3]=0;seq[4]=4; end
              87:begin seq[0]=3;seq[1]=2;seq[2]=1;seq[3]=4;seq[4]=0; end
              88:begin seq[0]=3;seq[1]=2;seq[2]=4;seq[3]=0;seq[4]=1; end
              89:begin seq[0]=3;seq[1]=2;seq[2]=4;seq[3]=1;seq[4]=0; end
              90:begin seq[0]=3;seq[1]=4;seq[2]=0;seq[3]=1;seq[4]=2; end
              91:begin seq[0]=3;seq[1]=4;seq[2]=0;seq[3]=2;seq[4]=1; end
              92:begin seq[0]=3;seq[1]=4;seq[2]=1;seq[3]=0;seq[4]=2; end
              93:begin seq[0]=3;seq[1]=4;seq[2]=1;seq[3]=2;seq[4]=0; end
              94:begin seq[0]=3;seq[1]=4;seq[2]=2;seq[3]=0;seq[4]=1; end
              95:begin seq[0]=3;seq[1]=4;seq[2]=2;seq[3]=1;seq[4]=0; end
              96:begin seq[0]=4;seq[1]=0;seq[2]=1;seq[3]=2;seq[4]=3; end
              97:begin seq[0]=4;seq[1]=0;seq[2]=1;seq[3]=3;seq[4]=2; end
              98:begin seq[0]=4;seq[1]=0;seq[2]=2;seq[3]=1;seq[4]=3; end
              99:begin seq[0]=4;seq[1]=0;seq[2]=2;seq[3]=3;seq[4]=1; end
              100:begin seq[0]=4;seq[1]=0;seq[2]=3;seq[3]=1;seq[4]=2; end
              101:begin seq[0]=4;seq[1]=0;seq[2]=3;seq[3]=2;seq[4]=1; end
              102:begin seq[0]=4;seq[1]=1;seq[2]=0;seq[3]=2;seq[4]=3; end
              103:begin seq[0]=4;seq[1]=1;seq[2]=0;seq[3]=3;seq[4]=2; end
              104:begin seq[0]=4;seq[1]=1;seq[2]=2;seq[3]=0;seq[4]=3; end
              105:begin seq[0]=4;seq[1]=1;seq[2]=2;seq[3]=3;seq[4]=0; end
              106:begin seq[0]=4;seq[1]=1;seq[2]=3;seq[3]=0;seq[4]=2; end
              107:begin seq[0]=4;seq[1]=1;seq[2]=3;seq[3]=2;seq[4]=0; end
              108:begin seq[0]=4;seq[1]=2;seq[2]=0;seq[3]=1;seq[4]=3; end
              109:begin seq[0]=4;seq[1]=2;seq[2]=0;seq[3]=3;seq[4]=1; end
              110:begin seq[0]=4;seq[1]=2;seq[2]=1;seq[3]=0;seq[4]=3; end
              111:begin seq[0]=4;seq[1]=2;seq[2]=1;seq[3]=3;seq[4]=0; end
              112:begin seq[0]=4;seq[1]=2;seq[2]=3;seq[3]=0;seq[4]=1; end
              113:begin seq[0]=4;seq[1]=2;seq[2]=3;seq[3]=1;seq[4]=0; end
              114:begin seq[0]=4;seq[1]=3;seq[2]=0;seq[3]=1;seq[4]=2; end
              115:begin seq[0]=4;seq[1]=3;seq[2]=0;seq[3]=2;seq[4]=1; end
              116:begin seq[0]=4;seq[1]=3;seq[2]=1;seq[3]=0;seq[4]=2; end
              117:begin seq[0]=4;seq[1]=3;seq[2]=1;seq[3]=2;seq[4]=0; end
              118:begin seq[0]=4;seq[1]=3;seq[2]=2;seq[3]=0;seq[4]=1; end
              119:begin seq[0]=4;seq[1]=3;seq[2]=2;seq[3]=1;seq[4]=0; end
            endcase
            launch(1);
            for(j=0;j<5;j=j+1)begin
                hls_reply='1;hls_valid=0;ap_done=0;
                if(seq[j]==4)ap_done=1;
                else begin hls_valid[seq[j]]=1;hls_reply[seq[j]*32+:32]=expected[seq[j]*32+:32];end
                @(negedge clk);hls_valid=0;ap_done=0;
                if(j<4&&reply_valid)$fatal(1,"collector replied before complete set");
                @(negedge clk);
            end
            retire;permutations=permutations+1;
        end
        // All outputs and done on the start-acceptance cycle are coherent too.
        launch(0);ap_ready=1;ap_done=1;hls_valid=15;hls_reply=expected;
        @(negedge clk);ap_ready=0;ap_done=0;hls_valid=0;retire;
        reset_all;launch(1);hls_valid=1;@(negedge clk);hls_valid=0;@(negedge clk);hls_valid=1;expect_fault;
        reset_all;launch(1);ap_done=1;@(negedge clk);ap_done=0;@(negedge clk);ap_done=1;expect_fault;
        reset_all;hls_valid=1;expect_fault;
        reset_all;ap_done=1;expect_fault;
        reset_all;launch(0);hls_valid=1;expect_fault;
        reset_all;launch(0);repeat(35)@(negedge clk);expect_fault;
        reset_all;launch(1);hls_valid=15;hls_reply=expected;@(negedge clk);hls_valid=0;repeat(35)@(negedge clk);expect_fault;
        for(missing=0;missing<4;missing=missing+1)begin
            reset_all;launch(1);ap_done=1;hls_valid=15^(1<<missing);
            @(negedge clk);ap_done=0;hls_valid=0;repeat(35)@(negedge clk);expect_fault;
        end
        reset_all;launch(1);hls_reply=expected;hls_valid=15;ap_done=1;@(negedge clk);hls_valid=0;ap_done=0;
        wait(reply_valid);@(negedge clk);abort=1;expect_fault;
        if(reply_data!==expected||!reply_valid)$fatal(1,"abort altered held collector reply");
        if(permutations!=120||checks!=121||fault_cases!=12)$fatal(1,"collector coverage incomplete");
        $display("FRONTIER_CALL_PASS permutations=%0d coherent_calls=%0d fault_cases=%0d",permutations,checks,fault_cases);$finish;
    end
endmodule
