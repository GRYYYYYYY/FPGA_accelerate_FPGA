`timescale 1ns/1ps
// Canonical scratch page: bitmap64 + 64 x 160-bit records + 448 zero tail bits.
// Decode holds all records until full-page validation AND explicit commit_ok.
// cancel is a local abort protocol; caller must separately drain any AXI work.
module scratch_page_codec(
    input wire clk,rst,
    input wire start_valid,output wire start_ready,input wire start_decode,
    input wire cancel,output wire busy,
    input wire record_in_valid,output wire record_in_ready,
    input wire [5:0] record_in_offset,input wire record_in_present,input wire [159:0] record_in_payload,
    output reg record_out_valid,input wire record_out_ready,
    output reg [5:0] record_out_offset,output reg record_out_present,output reg [159:0] record_out_payload,
    input wire raw_in_valid,output wire raw_in_ready,input wire [511:0] raw_in_data,
    output reg raw_out_valid,input wire raw_out_ready,output reg [511:0] raw_out_data,output wire raw_out_last,
    input wire commit_valid,output wire commit_ready,input wire commit_ok,
    output reg done_valid,input wire done_ready,output reg done_error
);
    localparam [3:0] IDLE=0,E_ACCEPT=1,E_STORE=2,E_WORD=3,E_READ=4,E_CAPTURE=5,E_OUTPUT=6,
        D_ACCEPT=7,D_UNPACK=8,D_CHECK=9,D_COMMIT=10,D_READ=11,D_CAPTURE=12,D_OUTPUT=13;
    reg [3:0] state;
    reg [63:0] bitmap;
    reg [159:0] record_buffer;
    reg [511:0] raw_buffer;
    reg [5:0] node;
    reg [2:0] field;
    reg [8:0] record_word,global_word;
    reg [4:0] beat;
    reg bad_page;
    (* ram_style="block" *) reg [31:0] words[0:319];
    reg [31:0] read_word;
    wire [31:0] unpack_word=raw_buffer[global_word[3:0]*32 +: 32];
    wire data_word=global_word>=2 && global_word<322;
    wire mem_write=!rst && !cancel && (state==E_STORE || (state==D_UNPACK && data_word));
    wire [8:0] write_address=state==E_STORE?record_word:global_word-9'd2;
    wire [31:0] write_data=state==E_STORE?record_buffer[field*32 +: 32]:unpack_word;
    wire mem_read=!rst && !cancel && (state==E_READ || state==D_READ);
    wire [8:0] read_address=state==E_READ?global_word-9'd2:record_word;
    always @(posedge clk)begin
        if(mem_write)words[write_address]<=write_data;
        if(mem_read)read_word<=words[read_address];
    end
    assign busy=state!=IDLE || done_valid;
    assign start_ready=!rst && !cancel && state==IDLE && !done_valid;
    assign record_in_ready=!rst && !cancel && state==E_ACCEPT;
    assign raw_in_ready=!rst && !cancel && state==D_ACCEPT;
    assign commit_ready=!rst && !cancel && state==D_COMMIT;
    assign raw_out_last=beat==20;
    always @(posedge clk)begin
        if(rst)begin
            state<=IDLE;bitmap<=0;node<=0;field<=0;record_word<=0;global_word<=0;beat<=0;bad_page<=0;
            record_out_valid<=0;record_out_offset<=0;record_out_present<=0;record_out_payload<=0;
            raw_out_valid<=0;raw_out_data<=0;done_valid<=0;done_error<=0;record_buffer<=0;raw_buffer<=0;
        end else if(1'b0)begin
            state<=IDLE;record_out_valid<=0;raw_out_valid<=0;done_valid<=1;done_error<=1;
        end else begin
            if(done_valid && done_ready)done_valid<=0;
            if(start_valid && start_ready)begin
                state<=start_decode?D_ACCEPT:E_ACCEPT;bitmap<=0;node<=0;field<=0;record_word<=0;global_word<=0;beat<=0;bad_page<=0;
                record_out_valid<=0;raw_out_valid<=0;done_error<=0;
            end
            case(state)
                E_ACCEPT:if(record_in_valid && record_in_ready)begin
                    if(record_in_offset!=node || record_in_payload[159:136]!=0 || (!record_in_present && record_in_payload!=0))begin
                        state<=IDLE;done_valid<=1;done_error<=1;
                    end else begin
                        bitmap[node]<=record_in_present;record_buffer<=record_in_payload;field<=0;state<=E_STORE;
                    end
                end
                E_STORE:begin
                    record_word<=record_word+1'b1;
                    if(field==4)begin
                        if(node==63)begin state<=E_WORD;global_word<=0;beat<=0;end
                        else begin node<=node+1'b1;state<=E_ACCEPT;end
                    end else field<=field+1'b1;
                end
                E_WORD:begin
                    if(data_word)state<=E_READ;
                    else begin
                        raw_out_data[global_word[3:0]*32 +: 32]<=global_word==0?bitmap[31:0]:(global_word==1?bitmap[63:32]:32'b0);
                        if(global_word[3:0]==15)begin raw_out_valid<=1;state<=E_OUTPUT;end
                        else global_word<=global_word+1'b1;
                    end
                end
                E_READ:state<=E_CAPTURE;
                E_CAPTURE:begin
                    raw_out_data[global_word[3:0]*32 +: 32]<=read_word;
                    if(global_word[3:0]==15)begin raw_out_valid<=1;state<=E_OUTPUT;end
                    else begin global_word<=global_word+1'b1;state<=E_WORD;end
                end
                E_OUTPUT:if(raw_out_valid && raw_out_ready)begin
                    raw_out_valid<=0;
                    if(beat==20)begin state<=IDLE;done_valid<=1;end
                    else begin beat<=beat+1'b1;global_word<=global_word+1'b1;state<=E_WORD;end
                end
                D_ACCEPT:if(raw_in_valid && raw_in_ready)begin raw_buffer<=raw_in_data;state<=D_UNPACK;end
                D_UNPACK:begin
                    if(global_word==0)bitmap[31:0]<=unpack_word;
                    else if(global_word==1)bitmap[63:32]<=unpack_word;
                    else if(data_word)begin
                        if((!bitmap[node] && unpack_word!=0) || (field==4 && unpack_word[31:8]!=0))bad_page<=1;
                        if(field==4)begin field<=0;node<=node+1'b1;end else field<=field+1'b1;
                    end else if(unpack_word!=0)bad_page<=1;
                    if(global_word==335)state<=D_CHECK;
                    else begin
                        global_word<=global_word+1'b1;
                        if(global_word[3:0]==15)begin beat<=beat+1'b1;state<=D_ACCEPT;end
                    end
                end
                D_CHECK:begin
                    if(bad_page)begin state<=IDLE;done_valid<=1;done_error<=1;end
                    else state<=D_COMMIT;
                end
                D_COMMIT:if(commit_valid && commit_ready)begin
                    if(!commit_ok)begin state<=IDLE;done_valid<=1;done_error<=1;end
                    else begin node<=0;field<=0;record_word<=0;state<=D_READ;end
                end
                D_READ:state<=D_CAPTURE;
                D_CAPTURE:begin
                    record_buffer[field*32 +: 32]<=read_word;record_word<=record_word+1'b1;
                    if(field==4)begin
                        record_out_payload<={read_word,record_buffer[127:0]};record_out_offset<=node;
                        record_out_present<=bitmap[node];record_out_valid<=1;state<=D_OUTPUT;
                    end else begin field<=field+1'b1;state<=D_READ;end
                end
                D_OUTPUT:if(record_out_valid && record_out_ready)begin
                    record_out_valid<=0;
                    if(node==63)begin state<=IDLE;done_valid<=1;end
                    else begin node<=node+1'b1;field<=0;state<=D_READ;end
                end
                default:begin end
            endcase
        end
    end
endmodule
