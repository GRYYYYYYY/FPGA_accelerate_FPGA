`timescale 1ns/1ps
module tb_reset_generation;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,abort=0,call_valid=0,reply_ready=0;
    reg [287:0] call_command=0;
    wire call_ready,reply_valid,fault,ap_start,ap_ready,ap_done,ap_idle;
    wire [287:0] hls_command;wire [159:0] reply_data,hls_reply;wire [4:0] hls_valid;
    integer calls=0,resets=0;
    exclusion_hls_call collector(.*);
    exclusion_step hls(
        .ap_clk(clk),.ap_rst(rst),.ap_start(ap_start),.ap_ready(ap_ready),.ap_done(ap_done),.ap_idle(ap_idle),
        .op(hls_command[31:0]),.parent(hls_command[63:32]),.child(hls_command[95:64]),
        .flags(hls_command[127:96]),.created(hls_command[159:128]),.has_laguna(hls_command[191:160]),
        .generation(hls_command[223:192]),.phase(hls_command[255:224]),.value_r(hls_command[287:256]),
        .status(hls_reply[31:0]),.result_generation(hls_reply[63:32]),.request(hls_reply[95:64]),
        .node(hls_reply[127:96]),.excluded(hls_reply[159:128]),
        .status_ap_vld(hls_valid[0]),.result_generation_ap_vld(hls_valid[1]),.request_ap_vld(hls_valid[2]),
        .node_ap_vld(hls_valid[3]),.excluded_ap_vld(hls_valid[4]));
    task cold_reset;
        begin @(negedge clk);rst=1;repeat(6)@(negedge clk);rst=0;resets=resets+1;end
    endtask
    task start_edge(input [31:0] created,expected_generation,expected_phase);
        begin
            @(negedge clk);call_command={96'b0,32'd0,created,32'd0,32'd17,32'd16,32'd0};call_valid=1;
            do @(posedge clk);while(!call_ready);
            @(negedge clk);call_valid=0;wait(reply_valid);@(negedge clk);
            $display("RESET_OBSERVATION call=%0d resets=%0d status=%0d generation=%0d phase=%0d",calls,resets,reply_data[31:0],reply_data[63:32],reply_data[95:64]);
            if(fault||reply_data[31:0]!=0||reply_data[63:32]!=expected_generation||reply_data[95:64]!=expected_phase)
                $fatal(1,"RESET_CONTRACT_FAIL expected_generation=%0d actual_generation=%0d expected_phase=%0d actual_phase=%0d",expected_generation,reply_data[63:32],expected_phase,reply_data[95:64]);
            reply_ready=1;@(negedge clk);reply_ready=0;calls=calls+1;
        end
    endtask
    initial begin #100000;$fatal(1,"reset test watchdog");end
    initial begin
        cold_reset;start_edge(0,1,0);
        cold_reset;start_edge(0,1,0);
        start_edge(1,2,1); // leave a pending Machine label request across reset
        cold_reset;start_edge(0,1,0);
        $display("RESET_CONTRACT_PASS calls=%0d resets=%0d",calls,resets);$finish;
    end
endmodule
