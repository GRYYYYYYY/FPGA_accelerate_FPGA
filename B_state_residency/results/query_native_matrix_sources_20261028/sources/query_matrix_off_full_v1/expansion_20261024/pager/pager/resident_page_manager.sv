`timescale 1ns/1ps
// Exclusive native owner; serial page lease, bounded resident slots, automatic CP.
module resident_page_manager #(
    parameter integer SLOTS=32,TX_BITS=16,GEN_BITS=16,ENABLE_BASELINE=0
)(
    input wire clk,rst,client_quiescent,
    input wire baseline_restore_write,
input wire baseline_raw_probe,
input wire baseline_permit,input wire[63:0]baseline_epoch,
    output wire baseline_req_valid,input wire baseline_req_ready,
    output wire[31:0]baseline_req_node,output wire[63:0]baseline_req_epoch,
    input wire baseline_rsp_valid,output wire baseline_rsp_ready,
    input wire[3:0]baseline_rsp_status,input wire[31:0]baseline_rsp_node,
    input wire[63:0]baseline_rsp_epoch,input wire[159:0]baseline_rsp_payload,
    input wire ctrl_valid,output wire ctrl_ready,input wire [1:0] ctrl_op,ctrl_query,
    input wire [3:0] ctrl_price,output wire ctrl_rsp_valid,input wire ctrl_rsp_ready,
    output reg [3:0] ctrl_status,
    input wire io_valid,output wire io_ready,input wire io_write,
    input wire [31:0] io_node,io_value,input wire [2:0] io_field,
    input wire [1:0] io_query,input wire [3:0] io_price,
    output wire io_rsp_valid,input wire io_rsp_ready,output reg [3:0] io_status,
    output reg [159:0] io_payload,output reg io_present,
    input wire resolve_valid,output wire resolve_ready,
    input wire [31:0] resolve_token,resolve_generation,resolve_phase,
    input wire [20:0] resolve_page,input wire [1:0] resolve_query,input wire [3:0] resolve_price,
    output wire map_valid,input wire map_ready,
    output wire [31:0] map_token,map_generation,map_phase,
    output wire [20:0] map_page,output wire [1:0] map_query,output wire [3:0] map_price,
    output reg [3:0] map_status,output wire [4:0] map_slot,output wire [15:0] map_binding_generation,
    input wire client_cmd_valid,output wire client_cmd_ready,
    input wire [3:0] client_cmd_op,client_cmd_price,input wire [4:0] client_cmd_slot,
    input wire [1:0] client_cmd_query,input wire [20:0] client_cmd_page,
    input wire [15:0] client_cmd_generation,input wire [2:0] client_cmd_offset,client_cmd_field,
    input wire [31:0] client_cmd_value,
    output wire client_rsp_valid,input wire client_rsp_ready,
    output reg [3:0] client_rsp_status,output reg [159:0] client_rsp_payload,output reg client_rsp_present,
    output wire native_cmd_valid,input wire native_cmd_ready,
    output reg [3:0] native_cmd_op,native_cmd_price,output reg [4:0] native_cmd_slot,
    output reg [1:0] native_cmd_query,output reg [20:0] native_cmd_page,
    output reg [15:0] native_cmd_generation,output reg [2:0] native_cmd_offset,native_cmd_field,
    output reg [31:0] native_cmd_value,
    input wire native_rsp_valid,output wire native_rsp_ready,input wire [3:0] native_rsp_status,
    input wire [159:0] native_rsp_payload,input wire native_rsp_present,native_fault,
    output reg active,output reg [1:0] active_query,output reg [3:0] active_price,
    output wire idle,fault,output wire snapshot_clean
);
    localparam [3:0] IDLE=0,PREPARE=1,FIND=2,VICTIM=3,SEND=4,WAIT_RSP=5,
        MAP_REPLY=6,CLIENT_WAIT=7,CLIENT_REPLY=8,IO_REPLY=9,CTRL_REPLY=10,FLUSH=11,BASE_SEND=12,BASE_WAIT=13;
    localparam [3:0] OPEN=1,EVICT_WB=2,EVICT_RELEASE=3,BIND=4,REFILL=5,
        ACCESS=6,FLUSH_WB=7,FLUSH_RELEASE=8,CHECKPOINT=9,BEGIN_CLOSE=10,FINISH_CLOSE=11,CLIENT=12,SEED=13,PROBE=14;
    localparam integer TX_LIMIT=1<<TX_BITS;
    localparam [15:0] GEN_MAX=16'hffff>>(16-GEN_BITS);
    reg [3:0] state,action;
    reg [1:0] owner; // 0 resolver, 1 generic access, 2 lifecycle
    reg stopped,leased,free_found,resume_request,closing;
    reg [31:0] valid_slots,dirty_slots;
    reg [20:0] pages[0:31];reg [15:0] generations[0:31];
    reg [5:0] scan;
    reg [4:0] chosen,first_free,replacement;
    reg [TX_BITS:0] tx_used;
    reg [31:0] token,edge_generation,phase,value;
    reg [20:0] page;
    reg [1:0] query_id;reg [3:0] price;reg [2:0] offset,field;
    reg restore_write;reg raw_probe;reg writing;
    reg baseline_poison;reg[63:0]active_baseline_epoch;reg[159:0]seed_payload;reg[2:0]seed_field;
    assign baseline_req_valid=!rst&&state==BASE_SEND;
    assign baseline_req_node={8'b0,page,offset};
    assign baseline_req_epoch=active_baseline_epoch;
    assign baseline_rsp_ready=!rst&&state==BASE_WAIT;
    task original_access;
     begin launch(writing?4'd3:4'd2,chosen,page,generations[chosen],offset,field,value,leased?CLIENT:ACCESS);end
    endtask
    task probe_access(input[4:0]sl,input[15:0]gen);
     begin launch(2,sl,page,gen,offset,field,0,PROBE);end
    endtask
    wire [4:0] victim=({1'b0,replacement}+scan)&(SLOTS-1);
    wire unexpected=native_rsp_valid&&state!=WAIT_RSP;
    wire abort_now=native_fault||unexpected;
    assign fault=!rst&&(stopped||abort_now);
    assign idle=!rst&&!fault&&state==IDLE;
    assign ctrl_ready=idle&&client_quiescent;
    assign io_ready=idle&&client_quiescent&&!ctrl_valid&&!resolve_valid;
    assign resolve_ready=idle&&!(ctrl_valid&&client_quiescent);
    assign ctrl_rsp_valid=!rst&&state==CTRL_REPLY;
    assign io_rsp_valid=!rst&&state==IO_REPLY;
    assign map_valid=!rst&&state==MAP_REPLY;
    assign map_token=token;assign map_generation=edge_generation;assign map_phase=phase;
    assign map_page=page;assign map_query=query_id;assign map_price=price;
    assign map_slot=chosen;assign map_binding_generation=generations[chosen];
    assign client_cmd_ready=!rst&&!fault&&state==CLIENT_WAIT;
    assign client_rsp_valid=!rst&&state==CLIENT_REPLY;
    assign native_cmd_valid=!rst&&!fault&&state==SEND;
    assign native_rsp_ready=!rst&&!fault&&state==WAIT_RSP;
    task launch(input [3:0] op,input [4:0] sl,input [20:0] pg,input [15:0] gen,
                input [2:0] off,fi,input [31:0] val,input [3:0] next_action);
        begin
            native_cmd_op<=op;native_cmd_slot<=sl;native_cmd_page<=pg;native_cmd_generation<=gen;
            native_cmd_query<=active_query;native_cmd_price<=active_price;
            native_cmd_offset<=off;native_cmd_field<=fi;native_cmd_value<=val;action<=next_action;state<=SEND;
        end
    endtask
    task bind_slot(input [4:0] sl);
        begin
            chosen<=sl;replacement<=(sl+1'b1)&(SLOTS-1);
            launch(1,sl,page,generations[sl]+1'b1,0,0,0,BIND);
        end
    endtask
    task bound_ready;
        begin
            if(owner==0)begin map_status<=0;state<=MAP_REPLY;end
            else if(ENABLE_BASELINE&&!raw_probe&&!restore_write)probe_access(chosen,generations[chosen]);
            else launch(writing?4'd3:4'd2,chosen,page,generations[chosen],offset,field,value,ACCESS);
        end
    endtask
    task fail_request(input [3:0] status);
        begin
            stopped<=1;
            if(leased)begin client_rsp_status<=status;client_rsp_payload<=0;client_rsp_present<=0;state<=CLIENT_REPLY;end
            else if(owner==0)begin map_status<=status;state<=MAP_REPLY;end
            else if(owner==1)begin io_status<=status;io_payload<=0;io_present<=0;state<=IO_REPLY;end
            else begin ctrl_status<=status;state<=CTRL_REPLY;end
        end
    endtask
    integer i;
    initial begin
        if(SLOTS<1||SLOTS>32||(SLOTS&(SLOTS-1))!=0||GEN_BITS<1||GEN_BITS>16||TX_BITS<2||TX_BITS>16||SLOTS+2>TX_LIMIT)
            $fatal(1,"unsupported pager parameters");
    end
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;action<=0;owner<=2;stopped<=0;leased<=0;free_found<=0;
            resume_request<=0;closing<=0;valid_slots<=0;dirty_slots<=0;scan<=0;chosen<=0;first_free<=0;replacement<=0;tx_used<=0;
            active<=0;active_query<=0;active_price<=0;token<=0;edge_generation<=0;phase<=0;value<=0;
            page<=0;query_id<=0;price<=0;offset<=0;field<=0;writing<=0;raw_probe<=0;restore_write<=0;
            baseline_poison<=0;active_baseline_epoch<=0;seed_payload<=0;seed_field<=0;
            ctrl_status<=0;io_status<=0;io_payload<=0;io_present<=0;map_status<=0;
            client_rsp_status<=0;client_rsp_payload<=0;client_rsp_present<=0;
            native_cmd_op<=0;native_cmd_slot<=0;native_cmd_page<=0;native_cmd_generation<=0;
            native_cmd_query<=0;native_cmd_price<=0;native_cmd_offset<=0;native_cmd_field<=0;native_cmd_value<=0;
            for(i=0;i<32;i=i+1)begin pages[i]<=0;generations[i]<=0;end
        end else begin
            if(state==CTRL_REPLY&&ctrl_rsp_ready)state<=IDLE;
            if(state==IO_REPLY&&io_rsp_ready)state<=IDLE;
            if(state==CLIENT_REPLY&&client_rsp_ready)begin leased<=0;state<=IDLE;end
            if(abort_now&&(state==BASE_SEND||state==BASE_WAIT))baseline_poison<=1;
            if(!stopped&&abort_now&&state!=BASE_SEND&&state!=BASE_WAIT)begin
                stopped<=1;
                if(state!=IDLE&&state!=CTRL_REPLY&&state!=IO_REPLY&&state!=CLIENT_REPLY&&state!=MAP_REPLY)fail_request(10);
            end else if(!stopped)case(state)
                IDLE:begin
                    if(ctrl_valid&&ctrl_ready)begin
                        owner<=2;ctrl_status<=0;resume_request<=0;closing<=ctrl_op==2;
                        if(ctrl_op==0)begin
                            if(active)begin ctrl_status<=4;state<=CTRL_REPLY;end
                            else if(ENABLE_BASELINE&&(!baseline_permit||baseline_epoch==0))begin ctrl_status<=1;state<=CTRL_REPLY;end
                            else begin
                                active_baseline_epoch<=baseline_epoch;
                                launch(0,0,0,0,0,0,0,OPEN);
                                native_cmd_query<=ctrl_query;native_cmd_price<=ctrl_price;
                            end
                        end else if(ctrl_op>2)begin ctrl_status<=3;state<=CTRL_REPLY;end
                        else if(!active)begin ctrl_status<=1;state<=CTRL_REPLY;end
                        else begin scan<=0;state<=FLUSH;end
                    end else if(resolve_valid&&resolve_ready)begin
                        owner<=0;token<=resolve_token;edge_generation<=resolve_generation;phase<=resolve_phase;
                        page<=resolve_page;query_id<=resolve_query;price<=resolve_price;map_status<=0;
                        if(!active||resolve_query!=active_query||resolve_price!=active_price)begin map_status<=1;state<=MAP_REPLY;end
                        else if(resolve_token==0||resolve_generation==0||resolve_phase<1||resolve_phase>4)begin map_status<=3;state<=MAP_REPLY;end
                        else state<=PREPARE;
                    end else if(io_valid&&io_ready)begin
                        owner<=1;page<=io_node[23:3];offset<=io_node[2:0];field<=io_field;value<=io_value;
                        restore_write<=ENABLE_BASELINE&&(baseline_restore_write===1'b1)&&io_write;
                        raw_probe<=ENABLE_BASELINE&&baseline_raw_probe;writing<=io_write;query_id<=io_query;price<=io_price;io_status<=0;io_payload<=0;io_present<=0;
                        if(!active||io_query!=active_query||io_price!=active_price)begin io_status<=1;state<=IO_REPLY;end
                        else if(ENABLE_BASELINE&&(baseline_restore_write===1'b1)&&!io_write)begin io_status<=3;state<=IO_REPLY;end
                        else if(ENABLE_BASELINE&&baseline_raw_probe&&io_write)begin io_status<=3;state<=IO_REPLY;end
                        else if(io_node[31:24]!=0||io_field>4||(io_write&&io_field==4&&io_value>255))begin io_status<=3;state<=IO_REPLY;end
                        else state<=PREPARE;
                    end
                end
                PREPARE:begin
                    scan<=0;free_found<=0;
                    if(tx_used+SLOTS+2>TX_LIMIT)begin resume_request<=1;closing<=0;state<=FLUSH;end
                    else state<=FIND;
                end
                FIND:begin
                    if(valid_slots[scan]&&pages[scan]==page)begin
                        chosen<=scan[4:0];
                        if(owner==0)begin map_status<=0;state<=MAP_REPLY;end
                        else if(ENABLE_BASELINE&&!raw_probe&&!restore_write)probe_access(scan[4:0],generations[scan]);
                        else launch(writing?4'd3:4'd2,scan[4:0],page,generations[scan],offset,field,value,ACCESS);
                    end else begin
                        if(!valid_slots[scan]&&generations[scan]<GEN_MAX&&!free_found)begin first_free<=scan[4:0];free_found<=1;end
                        if(scan==SLOTS-1)begin
                            if(free_found)bind_slot(first_free);
                            else if(!valid_slots[scan]&&generations[scan]<GEN_MAX)bind_slot(scan[4:0]);
                            else begin scan<=0;state<=VICTIM;end
                        end else scan<=scan+1'b1;
                    end
                end
                VICTIM:begin
                    if(generations[victim]<GEN_MAX)begin
                        chosen<=victim;replacement<=(victim+1'b1)&(SLOTS-1);
                        if(!valid_slots[victim])bind_slot(victim);
                        else launch(dirty_slots[victim]?4'd5:4'd4,victim,pages[victim],generations[victim],0,0,0,dirty_slots[victim]?EVICT_WB:EVICT_RELEASE);
                    end else if(scan==SLOTS-1)begin scan<=0;resume_request<=1;closing<=0;state<=FLUSH;end
                    else scan<=scan+1'b1;
                end
                MAP_REPLY:if(map_ready)begin
                    if(map_status==0)begin leased<=1;state<=CLIENT_WAIT;end
                    else state<=IDLE;
                end
                CLIENT_WAIT:if(client_cmd_valid&&client_cmd_ready)begin
                    if(client_cmd_op!=2||client_cmd_slot!=chosen||client_cmd_page!=page||client_cmd_generation!=generations[chosen]||
                       client_cmd_query!=active_query||client_cmd_price!=active_price||client_cmd_value!=0||
                       client_cmd_field!=((phase==1||phase==4)?3'd2:3'd3))fail_request(3);
                    else begin
                        if(ENABLE_BASELINE)begin
                         offset<=client_cmd_offset;field<=client_cmd_field;writing<=0;raw_probe<=0;restore_write<=0;value<=0;
                         launch(2,chosen,page,generations[chosen],client_cmd_offset,client_cmd_field,0,PROBE);
                        end else launch(2,chosen,page,generations[chosen],client_cmd_offset,client_cmd_field,0,CLIENT);
                    end
                end
                SEND:if(native_cmd_ready)state<=WAIT_RSP;
                WAIT_RSP:if(native_rsp_valid&&native_rsp_ready)begin
                    if(native_rsp_status!=0&&!(action==REFILL&&native_rsp_status==8)&&!(action==FINISH_CLOSE&&native_rsp_status==7))fail_request(native_rsp_status);
                    else case(action)
                        OPEN:begin active<=1;active_query<=native_cmd_query;active_price<=native_cmd_price;ctrl_status<=0;state<=CTRL_REPLY;end
                        EVICT_WB:begin tx_used<=tx_used+1'b1;dirty_slots[chosen]<=0;launch(4,chosen,pages[chosen],generations[chosen],0,0,0,EVICT_RELEASE);end
                        EVICT_RELEASE:begin valid_slots[chosen]<=0;bind_slot(chosen);end
                        BIND:begin
                            valid_slots[chosen]<=1;dirty_slots[chosen]<=0;pages[chosen]<=page;generations[chosen]<=native_cmd_generation;
                            launch(6,chosen,page,native_cmd_generation,0,0,0,REFILL);
                        end
                        REFILL:begin if(native_rsp_status==0)tx_used<=tx_used+1'b1;bound_ready;end
                        PROBE:begin
                            if(!native_rsp_present)begin baseline_poison<=0;state<=BASE_SEND;end
                            else if(writing)original_access;
                            else if(leased)begin client_rsp_status<=0;client_rsp_payload<=native_rsp_payload;client_rsp_present<=1;state<=CLIENT_REPLY;end
                            else begin io_status<=0;io_payload<=native_rsp_payload;io_present<=1;state<=IO_REPLY;end
                        end
                        SEED:begin
                            dirty_slots[chosen]<=1;
                            if(seed_field==4)original_access;
                            else begin
                             seed_field<=seed_field+1'b1;
                             launch(3,chosen,page,generations[chosen],offset,seed_field+1'b1,seed_payload[(seed_field+1)*32+:32],SEED);
                            end
                        end
                        ACCESS:begin
                            if(writing)dirty_slots[chosen]<=1;
                            io_status<=0;io_payload<=native_rsp_payload;io_present<=native_rsp_present;state<=IO_REPLY;
                        end
                        CLIENT:begin client_rsp_status<=0;client_rsp_payload<=native_rsp_payload;client_rsp_present<=native_rsp_present;state<=CLIENT_REPLY;end
                        FLUSH_WB:begin
                            tx_used<=tx_used+1'b1;dirty_slots[scan]<=0;
                            launch(4,scan[4:0],pages[scan],generations[scan],0,0,0,FLUSH_RELEASE);
                        end
                        FLUSH_RELEASE:begin valid_slots[scan]<=0;scan<=scan+1'b1;state<=FLUSH;end
                        CHECKPOINT:begin
                            valid_slots<=0;dirty_slots<=0;tx_used<=0;replacement<=0;
                            for(i=0;i<32;i=i+1)generations[i]<=0;
                            if(resume_request)begin resume_request<=0;state<=PREPARE;end
                            else begin ctrl_status<=0;state<=CTRL_REPLY;end
                        end
                        BEGIN_CLOSE:launch(11,0,0,0,0,0,0,FINISH_CLOSE);
                        FINISH_CLOSE:begin
                            if(native_rsp_status==7)launch(11,0,0,0,0,0,0,FINISH_CLOSE);
                            else begin
                                active<=0;valid_slots<=0;dirty_slots<=0;tx_used<=0;replacement<=0;
                                for(i=0;i<32;i=i+1)generations[i]<=0;
                                ctrl_status<=0;state<=CTRL_REPLY;
                            end
                        end
                        default:fail_request(3);
                    endcase
                end
                BASE_SEND:if(baseline_req_ready)state<=BASE_WAIT;
                BASE_WAIT:if(baseline_rsp_valid&&baseline_rsp_ready)begin
                    if(baseline_poison||abort_now||baseline_rsp_status!=0||baseline_rsp_node!={8'b0,page,offset}||
                       baseline_rsp_epoch!=active_baseline_epoch||baseline_rsp_payload[159:136]!=0)fail_request(10);
                    else begin
                     seed_payload<=baseline_rsp_payload;seed_field<=0;
                     launch(3,chosen,page,generations[chosen],offset,0,baseline_rsp_payload[31:0],SEED);
                    end
                end
                FLUSH:begin
                    if(scan==SLOTS)launch(closing?4'd10:4'd12,0,0,0,0,0,0,closing?BEGIN_CLOSE:CHECKPOINT);
                    else if(valid_slots[scan])launch(dirty_slots[scan]?4'd5:4'd4,scan[4:0],pages[scan],generations[scan],0,0,0,dirty_slots[scan]?FLUSH_WB:FLUSH_RELEASE);
                    else scan<=scan+1'b1;
                end
                default:begin end
            endcase
        end
    end
assign snapshot_clean=!rst&&state==IDLE&&active&&valid_slots==0&&dirty_slots==0;
endmodule
