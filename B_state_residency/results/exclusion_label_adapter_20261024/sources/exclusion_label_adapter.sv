`timescale 1ns/1ps
// One outstanding read. Resolver must retain the page lease through completion.
// fault is a fail-stop abort, not a retry/reset protocol. See CONTRACT.md.
module exclusion_label_adapter #(
    parameter integer TOKEN_BITS=32
)(
    input wire clk, rst,
    input wire req_valid, output wire req_ready,
    input wire [31:0] req_node, req_generation, req_phase,
    input wire [1:0] req_query, input wire [3:0] req_price,
    output wire resolve_valid, input wire resolve_ready,
    output wire [31:0] resolve_token, resolve_generation, resolve_phase,
    output wire [20:0] resolve_page,
    output wire [1:0] resolve_query, output wire [3:0] resolve_price,
    input wire map_valid, output wire map_ready,
    input wire [31:0] map_token, map_generation, map_phase,
    input wire [20:0] map_page, input wire [1:0] map_query,
    input wire [3:0] map_price, map_status,
    input wire [4:0] map_slot, input wire [15:0] map_binding_generation,
    output wire native_cmd_valid, input wire native_cmd_ready,
    output wire [3:0] native_cmd_op, native_cmd_price,
    output wire [4:0] native_cmd_slot, output wire [1:0] native_cmd_query,
    output wire [20:0] native_cmd_page,
    output wire [15:0] native_cmd_generation,
    output wire [2:0] native_cmd_offset, native_cmd_field,
    output wire [31:0] native_cmd_value,
    input wire native_rsp_valid, output wire native_rsp_ready,
    input wire [3:0] native_rsp_status,
    input wire [159:0] native_rsp_payload,
    input wire native_rsp_present, native_fault,
    output wire rsp_valid, input wire rsp_ready,
    output reg [3:0] rsp_status, rsp_service_status,
    output wire [31:0] rsp_generation, rsp_phase,
    output reg [31:0] rsp_value, output reg rsp_present,
    output reg fault
);
    localparam [2:0] IDLE=0, RESOLVE_SEND=1, RESOLVE_WAIT=2,
        NATIVE_SEND=3, NATIVE_WAIT=4, REPLY=5;
    localparam [3:0] OK=0, BAD_REQUEST=1, RESOLVER_ERROR=2,
        COOKIE_ERROR=3, NATIVE_ERROR=4, SERVICE_FAULT=5, TOKEN_EXHAUSTED=6;
    localparam [31:0] TOKEN_MAX=32'hffffffff >> (32-TOKEN_BITS);
    reg [2:0] state;
    reg [31:0] token, node, generation, phase;
    reg [1:0] query_id;
    reg [3:0] price;
    reg [4:0] slot;
    reg [15:0] binding_generation;
    wire bad_cookie = map_token!=token || map_generation!=generation ||
        map_phase!=phase || map_page!=node[23:3] || map_query!=query_id || map_price!=price;
    // Services must only produce replies after accepting their command. An
    // unsolicited/duplicate reply cannot be silently attached to a later read.
    wire unexpected_reply = (map_valid && state!=RESOLVE_WAIT) ||
        (native_rsp_valid && state!=NATIVE_WAIT);
    wire abort_now = native_fault || unexpected_reply;
    assign req_ready=!rst && !fault && !abort_now && state==IDLE;
    assign resolve_valid=!rst && !fault && !abort_now && state==RESOLVE_SEND;
    assign resolve_token=token;
    assign resolve_generation=generation;
    assign resolve_phase=phase;
    assign resolve_page=node[23:3];
    assign resolve_query=query_id;
    assign resolve_price=price;
    assign map_ready=!rst && !fault && !abort_now && state==RESOLVE_WAIT;
    assign native_cmd_valid=!rst && !fault && !abort_now && state==NATIVE_SEND;
    assign native_cmd_op=4'd2;
    assign native_cmd_slot=slot;
    assign native_cmd_query=query_id;
    assign native_cmd_price=price;
    assign native_cmd_page=node[23:3];
    assign native_cmd_generation=binding_generation;
    assign native_cmd_offset=node[2:0];
    assign native_cmd_field=(phase==1 || phase==4)?3'd2:3'd3;
    assign native_cmd_value=0;
    assign native_rsp_ready=!rst && !fault && !abort_now && state==NATIVE_WAIT;
    assign rsp_valid=!rst && state==REPLY;
    assign rsp_generation=generation;
    assign rsp_phase=phase;

    always @(posedge clk) begin
        if(rst) begin
            state<=IDLE; token<=0; node<=0; generation<=0; phase<=0;
            query_id<=0; price<=0; slot<=0; binding_generation<=0;
            rsp_status<=OK; rsp_service_status<=0; rsp_value<=0;
            rsp_present<=0; fault<=0;
        end else begin
            // Preserve an already offered reply even when abort arrives under
            // backpressure. Caller must also observe fault before HLS RESPONSE.
            if(state==REPLY && rsp_ready) state<=IDLE;
            if(!fault && abort_now) begin
                fault<=1;
                if(state!=IDLE && state!=REPLY) begin
                    state<=REPLY; rsp_status<=SERVICE_FAULT;
                    rsp_service_status<=0; rsp_value<=0; rsp_present<=0;
                end
            end else if(!fault) begin
                case(state)
                    IDLE: if(req_valid && req_ready) begin
                        node<=req_node; generation<=req_generation; phase<=req_phase;
                        query_id<=req_query; price<=req_price;
                        rsp_value<=0; rsp_present<=0; rsp_service_status<=0;
                        if(req_node[31:24]!=0 || req_generation==0 || req_phase<1 || req_phase>4) begin
                            rsp_status<=BAD_REQUEST; state<=REPLY;
                        end else if(token==TOKEN_MAX) begin
                            rsp_status<=TOKEN_EXHAUSTED; state<=REPLY;
                        end else begin
                            token<=token+1'b1; state<=RESOLVE_SEND; rsp_status<=OK;
                        end
                    end
                    RESOLVE_SEND: if(resolve_ready) state<=RESOLVE_WAIT;
                    RESOLVE_WAIT: if(map_valid && map_ready) begin
                        if(bad_cookie) begin
                            fault<=1; rsp_status<=COOKIE_ERROR; state<=REPLY;
                        end else if(map_status!=0) begin
                            rsp_status<=RESOLVER_ERROR; rsp_service_status<=map_status; state<=REPLY;
                        end else begin
                            slot<=map_slot; binding_generation<=map_binding_generation; state<=NATIVE_SEND;
                        end
                    end
                    NATIVE_SEND: if(native_cmd_ready) state<=NATIVE_WAIT;
                    NATIVE_WAIT: if(native_rsp_valid && native_rsp_ready) begin
                        state<=REPLY;
                        rsp_service_status<=native_rsp_status;
                        if(native_rsp_status!=0) begin
                            rsp_status<=NATIVE_ERROR; rsp_value<=0; rsp_present<=0;
                        end else begin
                            rsp_status<=OK; rsp_present<=native_rsp_present;
                            rsp_value<=(phase==1 || phase==4)?native_rsp_payload[95:64]:native_rsp_payload[127:96];
                        end
                    end
                    default: begin end
                endcase
            end
        end
    end
endmodule
