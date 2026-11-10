`timescale 1ns/1ps
// Single-owner primitive. The external controller must authorize CLEAN only
// after writeback, and quarantine finite binding IDs until a complete fence.
// Reset is cold/destructive, not an in-flight recovery protocol.
module scratch_frame_store #(
    parameter integer SLOTS = 4,
    parameter integer SLOT_BITS = 2,
    parameter integer OFFSET_BITS = 6,
    parameter integer PAGE_BITS = 18,
    parameter integer QUERY_BITS = 2,
    parameter integer PRICE_BITS = 4,
    parameter integer GENERATION_BITS = 16
)(
    input wire clk, input wire rst,
    input wire cmd_valid, output wire cmd_ready,
    input wire [2:0] cmd_op,
    input wire [SLOT_BITS-1:0] cmd_slot,
    input wire [PAGE_BITS-1:0] cmd_page,
    input wire [QUERY_BITS-1:0] cmd_query,
    input wire [PRICE_BITS-1:0] cmd_price,
    input wire [GENERATION_BITS-1:0] cmd_generation,
    input wire [OFFSET_BITS-1:0] cmd_offset,
    input wire [2:0] cmd_field,
    input wire [31:0] cmd_value,
    input wire [159:0] cmd_payload,
    output reg rsp_valid, input wire rsp_ready,
    output reg [2:0] rsp_status,
    output reg [159:0] rsp_payload,
    output reg rsp_present, output reg rsp_dirty
);
    localparam integer NODES = 1 << OFFSET_BITS;
    localparam [2:0] BIND=0, READ=1, WRITE=2, CLEAN=3, UNBIND=4, LOAD=5;
    localparam [2:0] OK=0, STALE=1, DIRTY=2, BAD=3, BUSY=4;
    reg [SLOTS-1:0] bound, dirty;
    reg [PAGE_BITS-1:0] page_tag [0:SLOTS-1];
    reg [QUERY_BITS-1:0] query_tag [0:SLOTS-1];
    reg [PRICE_BITS-1:0] price_tag [0:SLOTS-1];
    reg [GENERATION_BITS-1:0] generation_tag [0:SLOTS-1];
    reg [NODES-1:0] present [0:SLOTS-1];
    (* ram_style = "block" *) reg [135:0] data [0:SLOTS*NODES-1];
    reg accessing, pending_write, read_present;
    reg [135:0] read_word;
    reg [SLOT_BITS-1:0] access_slot;
    reg [OFFSET_BITS-1:0] access_offset;
    reg [2:0] access_field;
    reg [31:0] access_value;
    reg [135:0] merged;
    integer index;
    wire slot_ok = cmd_slot < SLOTS;
    wire matches = slot_ok && bound[cmd_slot] && page_tag[cmd_slot]==cmd_page
        && query_tag[cmd_slot]==cmd_query && price_tag[cmd_slot]==cmd_price
        && generation_tag[cmd_slot]==cmd_generation;
    assign cmd_ready = !rst && !accessing && !rsp_valid;

    always @* begin
        merged = read_present ? read_word : 136'b0;
        case (access_field)
            0: merged[31:0] = access_value;
            1: merged[63:32] = access_value;
            2: merged[95:64] = access_value;
            3: merged[127:96] = access_value;
            4: merged[135:128] = access_value[7:0];
            default: merged = merged;
        endcase
    end

    always @(posedge clk) begin
        if (rst) begin
            bound <= 0; dirty <= 0; accessing <= 0; rsp_valid <= 0;
            rsp_status <= OK; rsp_payload <= 0; rsp_present <= 0; rsp_dirty <= 0;
            for (index=0; index<SLOTS; index=index+1) begin
                present[index] <= 0;
                page_tag[index] <= 0; query_tag[index] <= 0;
                price_tag[index] <= 0; generation_tag[index] <= 0;
            end
            // RAM contents deliberately not reset; present[] gates every read.
        end else begin
            if (rsp_valid && rsp_ready) rsp_valid <= 0;
            if (accessing) begin
                accessing <= 0; rsp_valid <= 1; rsp_status <= OK;
                if (pending_write) begin
                    data[access_slot*NODES+access_offset] <= merged;
                    present[access_slot][access_offset] <= 1;
                    dirty[access_slot] <= 1;
                    rsp_payload <= {24'b0,merged}; rsp_present <= 1; rsp_dirty <= 1;
                end else begin
                    rsp_payload <= read_present ? {24'b0,read_word} : 160'b0;
                    rsp_present <= read_present; rsp_dirty <= dirty[access_slot];
                end
            end
            if (cmd_valid && cmd_ready) begin
                rsp_valid <= 1; rsp_status <= OK; rsp_payload <= 0; rsp_present <= 0; rsp_dirty <= 0;
                if (!slot_ok || cmd_op > LOAD) rsp_status <= BAD;
                else if (cmd_op==BIND) begin
                    if (bound[cmd_slot]) rsp_status <= BUSY;
                    else begin
                        bound[cmd_slot] <= 1; dirty[cmd_slot] <= 0; present[cmd_slot] <= 0;
                        page_tag[cmd_slot] <= cmd_page; query_tag[cmd_slot] <= cmd_query;
                        price_tag[cmd_slot] <= cmd_price; generation_tag[cmd_slot] <= cmd_generation;
                    end
                end else if (!matches) rsp_status <= STALE;
                else if (cmd_op==READ || cmd_op==WRITE) begin
                    if (cmd_op==WRITE && (cmd_field>4 || (cmd_field==4 && cmd_value[31:8]!=0))) rsp_status <= BAD;
                    else begin
                        rsp_valid <= 0; accessing <= 1; pending_write <= (cmd_op==WRITE);
                        access_slot <= cmd_slot; access_offset <= cmd_offset;
                        access_field <= cmd_field; access_value <= cmd_value;
                        read_word <= data[cmd_slot*NODES+cmd_offset];
                        read_present <= present[cmd_slot][cmd_offset];
                    end
                end else if (cmd_op==UNBIND) begin
                    if (dirty[cmd_slot]) begin rsp_status <= DIRTY; rsp_dirty <= 1; end
                    else bound[cmd_slot] <= 0;
                end else if (cmd_op==CLEAN) begin
                    dirty[cmd_slot] <= 0;
                end else if (cmd_op==LOAD) begin
                    if (dirty[cmd_slot]) begin rsp_status <= DIRTY; rsp_dirty <= 1; end
                    else if (cmd_payload[159:136]!=0) rsp_status <= BAD;
                    else begin
                        data[cmd_slot*NODES+cmd_offset] <= cmd_payload[135:0];
                        present[cmd_slot][cmd_offset] <= 1;
                        rsp_payload <= cmd_payload; rsp_present <= 1;
                    end
                end
            end
        end
    end
endmodule
