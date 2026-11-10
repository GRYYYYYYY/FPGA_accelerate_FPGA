`timescale 1ns/1ps
// One first-touch build, stable owner until final result retirement.
module children_build_controller(
    input wire clk,rst,
    input wire build_valid,output wire build_ready,
    input wire [31:0] build_cookie,build_parent,build_count,build_prune,
    input wire [1:0] build_query,input wire [3:0] build_price,
    output wire result_valid,input wire result_ready,
    output reg [3:0] result_status,output reg [31:0] result_detail,result_cookie,result_generation,result_emitted,
    output wire fault,busy,
    output wire call_valid,input wire call_ready,output reg [415:0] call_command,
    input wire call_reply_valid,output wire call_reply_ready,input wire [351:0] call_reply_data,input wire call_fault,
    output wire svc_valid,input wire svc_ready,
    output reg [31:0] svc_generation,svc_parent,svc_position,svc_phase,svc_node,svc_emitted,svc_count,svc_prune,
    output reg [1:0] svc_query,output reg [3:0] svc_price,
    input wire svc_reply_valid,output wire svc_reply_ready,
    input wire [31:0] svc_reply_generation,svc_reply_parent,svc_reply_position,svc_reply_phase,svc_reply_node,
    input wire [1:0] svc_reply_query,input wire [3:0] svc_reply_price,
    input wire [31:0] svc_status,svc_value,svc_aux,input wire service_fault
);
    localparam [2:0] IDLE=0,CALL_SEND=1,CALL_WAIT=2,SERVICE_SEND=3,SERVICE_WAIT=4,RESULT=5;
    localparam [3:0] OK=0,BAD_BUILD=1,HLS_ERROR=2,SERVICE_ERROR=3,PROTOCOL_ERROR=4,ASYNC_FAULT=5;
    reg [2:0] state;
    reg stopped,starting,any_alive;
    reg [31:0] last_generation,expected_phase,expected_position,expected_node,expected_emitted,pending_status;
    wire [31:0] h_status=call_reply_data[31:0],h_generation=call_reply_data[63:32],h_phase=call_reply_data[95:64],
        h_position=call_reply_data[127:96],h_node=call_reply_data[159:128],h_parent=call_reply_data[191:160],
        h_query=call_reply_data[223:192],h_price=call_reply_data[255:224],h_emitted=call_reply_data[287:256],
        h_active=call_reply_data[319:288],h_fault=call_reply_data[351:320];
    wire unexpected=(call_reply_valid&&state!=CALL_WAIT)||(svc_reply_valid&&state!=SERVICE_WAIT);
    wire abort_now=call_fault||service_fault||unexpected;
    assign fault=!rst&&(stopped||abort_now);
    assign busy=!rst&&(state!=IDLE||stopped);
    assign build_ready=!rst&&!fault&&state==IDLE;
    assign result_valid=!rst&&state==RESULT;
    assign call_valid=!rst&&!fault&&state==CALL_SEND;
    assign call_reply_ready=!rst&&!fault&&state==CALL_WAIT;
    assign svc_valid=!rst&&!fault&&state==SERVICE_SEND;
    assign svc_reply_ready=!rst&&!fault&&state==SERVICE_WAIT;
    wire h_bad_generation=h_generation==0||(starting?(last_generation==32'hffffffff||h_generation!=last_generation+1'b1):h_generation!=svc_generation);
    wire h_bad_state=h_phase!=expected_phase||h_position!=expected_position||h_node!=expected_node||h_emitted!=expected_emitted||
        h_parent!=svc_parent||h_query!={30'b0,svc_query}||h_price!={28'b0,svc_price}||h_fault!=0||h_active!=(expected_phase==8?0:1);
    wire bad_owner=svc_reply_generation!=svc_generation||svc_reply_parent!=svc_parent||svc_reply_position!=svc_position||
        svc_reply_phase!=svc_phase||svc_reply_node!=svc_node||svc_reply_query!=svc_query||svc_reply_price!=svc_price;
    task advance;
        begin
            expected_position<=svc_position+1'b1;expected_node<=svc_parent;
            if(svc_position+1'b1<svc_count)expected_phase<=0;
            else expected_phase<=svc_prune&&!any_alive?5:7;
        end
    endtask
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;stopped<=0;starting<=0;any_alive<=0;last_generation<=0;
            expected_phase<=8;expected_position<=0;expected_node<=0;expected_emitted<=0;pending_status<=0;
            result_status<=0;result_detail<=0;result_cookie<=0;result_generation<=0;result_emitted<=0;call_command<=0;
            svc_generation<=0;svc_parent<=0;svc_position<=0;svc_phase<=0;svc_node<=0;svc_emitted<=0;
            svc_count<=0;svc_prune<=0;svc_query<=0;svc_price<=0;
        end else begin
            if(state==RESULT&&result_ready)state<=IDLE;
            if(!stopped&&abort_now)begin
                stopped<=1;
                if(state!=IDLE&&state!=RESULT)begin state<=RESULT;result_status<=ASYNC_FAULT;result_detail<=0;end
            end else if(!stopped)case(state)
                IDLE:if(build_valid&&build_ready)begin
                    result_cookie<=build_cookie;result_status<=OK;result_detail<=0;result_generation<=0;result_emitted<=0;
                    svc_parent<=build_parent;svc_count<=build_count;svc_prune<=build_prune;svc_query<=build_query;svc_price<=build_price;
                    svc_generation<=0;svc_position<=0;svc_phase<=0;svc_node<=0;svc_emitted<=0;pending_status<=0;any_alive<=0;
                    if(build_parent[31:24]!=0||build_prune>1)begin state<=RESULT;result_status<=BAD_BUILD;end
                    else begin
                        expected_phase<=build_count==0?(build_prune?5:7):0;expected_position<=0;expected_node<=build_parent;expected_emitted<=0;
                        starting<=1;state<=CALL_SEND;
                        call_command<={224'b0,28'b0,build_price,30'b0,build_query,build_prune,build_count,build_parent,32'd0};
                    end
                end
                CALL_SEND:if(call_ready)state<=CALL_WAIT;
                CALL_WAIT:if(call_reply_valid&&call_reply_ready)begin
                    if(h_status!=0||h_fault!=0)begin
                        stopped<=1;state<=RESULT;
                        result_status<=pending_status!=0&&h_status==8&&h_fault==1?SERVICE_ERROR:HLS_ERROR;
                        result_detail<=pending_status!=0?pending_status:h_status;
                    end else if(h_bad_generation||h_bad_state)begin
                        stopped<=1;state<=RESULT;result_status<=PROTOCOL_ERROR;result_detail<=h_phase;
                    end else begin
                        if(starting)last_generation<=h_generation;
                        starting<=0;result_generation<=h_generation;result_emitted<=h_emitted;
                        if(h_phase==8)state<=RESULT;
                        else begin
                            svc_generation<=h_generation;svc_position<=h_position;svc_phase<=h_phase;svc_node<=h_node;svc_emitted<=h_emitted;
                            state<=SERVICE_SEND;
                        end
                    end
                end
                SERVICE_SEND:if(svc_ready)state<=SERVICE_WAIT;
                SERVICE_WAIT:if(svc_reply_valid&&svc_reply_ready)begin
                    if(bad_owner)begin stopped<=1;state<=RESULT;result_status<=PROTOCOL_ERROR;result_detail<=svc_reply_phase;end
                    else begin
                        pending_status<=svc_status;
                        call_command<={svc_status,svc_aux,svc_value,svc_node,svc_phase,svc_position,svc_generation,28'b0,svc_price,30'b0,svc_query,64'b0,svc_parent,32'd1};
                        state<=CALL_SEND;
                        if(svc_status==0)case(svc_phase)
                            0:begin expected_phase<=1;expected_node<=svc_value;if(svc_prune&&svc_aux==0)any_alive<=1;end
                            1:if(svc_value!=0)advance;else expected_phase<=2;
                            2:expected_phase<=3;
                            3:if(svc_value!=0||(svc_prune&&svc_aux!=0))advance;else expected_phase<=4;
                            4:begin expected_emitted<=svc_emitted+1'b1;advance;end
                            5:expected_phase<=svc_value!=0?6:7;
                            6:expected_phase<=7;
                            7:begin expected_phase<=8;expected_node<=0;end
                            default:begin end
                        endcase
                    end
                end
                default:begin end
            endcase
        end
    end
endmodule
