`timescale 1ns/1ps
// Own an edge from START through all label RESPONSEs; no hot cancellation.
module exclusion_edge_controller(
    input wire clk,rst,
    input wire edge_valid,output wire edge_ready,
    input wire [31:0] edge_cookie,edge_parent,edge_child,edge_flags,edge_created,edge_has_laguna,
    input wire [1:0] edge_query,input wire [3:0] edge_price,
    output wire result_valid,input wire result_ready,
    output reg [3:0] result_status,output reg [31:0] result_detail,result_cookie,result_generation,
    output reg result_excluded,output wire fault,
    output wire call_valid,input wire call_ready,output reg [287:0] call_command,
    input wire call_reply_valid,output wire call_reply_ready,input wire [159:0] call_reply_data,
    input wire call_fault,
    output wire label_valid,input wire label_ready,
    output reg [31:0] label_node,label_generation,label_phase,
    output reg [1:0] label_query,output reg [3:0] label_price,
    input wire label_reply_valid,output wire label_reply_ready,
    input wire [3:0] label_status,label_service_status,
    input wire [31:0] label_reply_generation,label_reply_phase,label_value,
    input wire label_fault
);
    localparam [2:0] IDLE=0,CALL_SEND=1,CALL_WAIT=2,LABEL_SEND=3,LABEL_WAIT=4,RESULT=5;
    localparam [3:0] OK=0,BAD_EDGE=1,HLS_ERROR=2,LABEL_ERROR=3,PROTOCOL_ERROR=4,SERVICE_FAULT=5;
    reg [2:0] state;
    reg stopped,starting;
    reg [31:0] parent,child,last_generation;
    reg [4:1] phase_seen;
    wire [31:0] h_status=call_reply_data[31:0],h_generation=call_reply_data[63:32],
        h_phase=call_reply_data[95:64],h_node=call_reply_data[127:96],h_excluded=call_reply_data[159:128];
    wire unexpected=(call_reply_valid && state!=CALL_WAIT) || (label_reply_valid && state!=LABEL_WAIT);
    wire abort_now=call_fault||label_fault||unexpected;
    assign fault=!rst && (stopped||abort_now);
    assign edge_ready=!rst&&!fault&&state==IDLE;
    assign result_valid=!rst&&state==RESULT;
    assign call_valid=!rst&&!fault&&state==CALL_SEND;
    assign call_reply_ready=!rst&&!fault&&state==CALL_WAIT;
    assign label_valid=!rst&&!fault&&state==LABEL_SEND;
    assign label_reply_ready=!rst&&!fault&&state==LABEL_WAIT;
    wire h_bad_generation=h_generation==0 || (starting ?
        (last_generation==32'hffffffff || h_generation!=last_generation+1'b1) : h_generation!=label_generation);
    wire h_bad_request=h_phase>4 || (h_phase==0 ? (h_node!=0 || h_excluded>1) :
        (h_excluded!=0 || h_node!=((h_phase==3)?parent:child) || phase_seen[h_phase[2:0]]));
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;stopped<=0;starting<=0;parent<=0;child<=0;last_generation<=0;phase_seen<=0;
            result_status<=0;result_detail<=0;result_cookie<=0;result_generation<=0;result_excluded<=0;
            call_command<=0;label_node<=0;label_generation<=0;label_phase<=0;label_query<=0;label_price<=0;
        end else begin
            if(state==RESULT&&result_ready)state<=IDLE;
            if(!stopped&&abort_now)begin
                stopped<=1;
                if(state!=IDLE&&state!=RESULT)begin
                    state<=RESULT;result_status<=SERVICE_FAULT;result_excluded<=0;
                    result_detail<={24'b0,label_status,label_service_status};
                end
            end else if(!stopped)case(state)
                IDLE:if(edge_valid&&edge_ready)begin
                    result_cookie<=edge_cookie;result_status<=OK;result_detail<=0;result_excluded<=0;result_generation<=0;
                    parent<=edge_parent;child<=edge_child;label_query<=edge_query;label_price<=edge_price;
                    phase_seen<=0;label_generation<=0;label_phase<=0;
                    if(edge_parent[31:24]!=0||edge_child[31:24]!=0||edge_flags>255||edge_created>1||edge_has_laguna>1)begin
                        state<=RESULT;result_status<=BAD_EDGE;
                    end else begin
                        starting<=1;state<=CALL_SEND;
                        call_command<={96'b0,edge_has_laguna,edge_created,edge_flags,edge_child,edge_parent,32'd0};
                    end
                end
                CALL_SEND:if(call_ready)state<=CALL_WAIT;
                CALL_WAIT:if(call_reply_valid&&call_reply_ready)begin
                    if(h_status!=0)begin
                        stopped<=1;state<=RESULT;result_status<=HLS_ERROR;result_detail<=h_status;result_excluded<=0;
                    end else if(h_bad_generation||h_bad_request)begin
                        stopped<=1;state<=RESULT;result_status<=PROTOCOL_ERROR;result_detail<=h_phase;result_excluded<=0;
                    end else begin
                        if(starting)last_generation<=h_generation;
                        starting<=0;result_generation<=h_generation;
                        if(h_phase==0)begin
                            state<=RESULT;result_excluded<=h_excluded[0];
                        end else begin
                            label_generation<=h_generation;label_phase<=h_phase;label_node<=h_node;
                            phase_seen[h_phase[2:0]]<=1;state<=LABEL_SEND;
                        end
                    end
                end
                LABEL_SEND:if(label_ready)state<=LABEL_WAIT;
                LABEL_WAIT:if(label_reply_valid&&label_reply_ready)begin
                    if(label_status!=0)begin
                        stopped<=1;state<=RESULT;result_status<=LABEL_ERROR;
                        result_detail<={24'b0,label_status,label_service_status};result_excluded<=0;
                    end else if(label_reply_generation!=label_generation||label_reply_phase!=label_phase)begin
                        stopped<=1;state<=RESULT;result_status<=PROTOCOL_ERROR;result_detail<=label_reply_phase;result_excluded<=0;
                    end else begin
                        call_command<={label_value,label_phase,label_generation,160'b0,32'd1};state<=CALL_SEND;
                    end
                end
                default:begin end
            endcase
        end
    end
endmodule
