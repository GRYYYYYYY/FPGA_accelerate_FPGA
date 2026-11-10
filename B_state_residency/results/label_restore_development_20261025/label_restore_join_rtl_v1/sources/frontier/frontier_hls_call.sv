`timescale 1ns/1ps
// Single ap_ctrl_hs invocation, independent output strobes, bounded completion.
module frontier_hls_call #(parameter integer MAX_CALL_CYCLES=256)(
    input wire clk,rst,abort,
    input wire call_valid,output wire call_ready,input wire [95:0] call_command,
    output wire reply_valid,input wire reply_ready,output reg [127:0] reply_data,
    output wire fault,
    output wire ap_start,input wire ap_ready,ap_done,ap_idle,
    output reg [95:0] hls_command,
    input wire [127:0] hls_reply,input wire [3:0] hls_valid
);
    localparam [1:0] IDLE=0,ACTIVE=1,REPLY=2;
    localparam integer TIMER_BITS=$clog2(MAX_CALL_CYCLES+1);
    reg [1:0] state;
    reg accepted,done_seen,stopped;
    reg [3:0] seen;
    reg [TIMER_BITS-1:0] elapsed;
    wire accepting=state==ACTIVE && !accepted && ap_ready;
    wire complete=(accepted||accepting) && (done_seen||ap_done) && (&(seen|hls_valid));
    wire events=ap_done || (|hls_valid);
    wire protocol_error=(state!=ACTIVE && events) ||
        (state==ACTIVE && ((|(seen&hls_valid)) || (done_seen&&ap_done) ||
            (events && !accepted && !accepting)));
    wire timeout=state==ACTIVE && elapsed==MAX_CALL_CYCLES-1 && !complete;
    assign fault=!rst && (stopped || abort || protocol_error || timeout);
    assign call_ready=!rst && !fault && state==IDLE && ap_idle;
    // ap_ready may depend combinationally on ap_start in the generated HLS.
    // Do not feed ready-dependent protocol/timeout checks back into ap_start.
    // External abort stops immediately; internal faults latch at the clock edge.
    assign ap_start=!rst && !stopped && !abort && state==ACTIVE && !accepted;
    assign reply_valid=!rst && state==REPLY;
    integer i;
    always @(posedge clk) begin
        if(rst)begin
            state<=IDLE;accepted<=0;done_seen<=0;stopped<=0;
            seen<=0;elapsed<=0;hls_command<=0;reply_data<=0;
        end else begin
            if(state==REPLY && reply_ready)state<=IDLE;
            if(fault)stopped<=1;
            else case(state)
                IDLE:if(call_valid&&call_ready)begin
                    hls_command<=call_command;state<=ACTIVE;
                    accepted<=0;done_seen<=0;seen<=0;elapsed<=0;reply_data<=0;
                end
                ACTIVE:begin
                    elapsed<=elapsed+1'b1;
                    if(accepting)accepted<=1;
                    if(ap_done)done_seen<=1;
                    seen<=seen|hls_valid;
                    for(i=0;i<4;i=i+1)if(hls_valid[i])reply_data[i*32+:32]<=hls_reply[i*32+:32];
                    if(complete)state<=REPLY;
                end
                default:begin end
            endcase
        end
    end
endmodule
