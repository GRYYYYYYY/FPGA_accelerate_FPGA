`timescale 1ns/1ps
// Closed endpoint controller, not an AXI DMA engine. COMPLETE acknowledges an
// externally durable transfer. Fence finish requires a truthful whole-link drain.
module scratch_page_controller_small #(
    parameter integer TX_BITS=16, GENERATION_BITS=16
)(
    input wire clk, rst,
    input wire cmd_valid, output wire cmd_ready,
    input wire [3:0] cmd_op,
    input wire [4:0] cmd_slot, input wire [1:0] cmd_query,
    input wire [20:0] cmd_page,
    input wire [3:0] cmd_price,
    input wire [GENERATION_BITS-1:0] cmd_generation,
    input wire [TX_BITS-1:0] cmd_tx,
    input wire cmd_kind, cmd_present,
    input wire [2:0] cmd_offset,
    input wire [2:0] cmd_field,
    input wire [31:0] cmd_value,
    input wire [159:0] cmd_payload,
    // Synchronous adapter attestations, meaningful only at FINISH_FENCE.
    input wire peer_quiescent, ingress_empty,
    output reg rsp_valid, input wire rsp_ready,
    output reg [2:0] rsp_status,
    output reg [159:0] rsp_payload,
    output reg rsp_present, rsp_dirty,
    output reg [TX_BITS-1:0] rsp_tx,
    output reg draining
);
    localparam [3:0] QUERY=0, BIND=1, READ=2, WRITE=3, RELEASE=4,
        WRITEBACK=5, REFILL=6, BEAT=7, COMPLETE=8, EXPORT=9,
        BEGIN_FENCE=10, FINISH_FENCE=11, RF_MASK=14;
    localparam [2:0] OK=0, STALE=1, DIRTY=2, BAD=3, BUSY=4,
        EXHAUSTED=5, INCOMPLETE=6, FENCE_WAIT=7;
    localparam [1:0] FREE=0, LIVE=1, WB=2, RF=3;
    reg [1:0] phase[0:31];
    reg [31:0] dirty, pristine, generation_used, rf_sealed;
    reg [3:0] query_used;
    reg [20:0] page_tag[0:31];
    reg [1:0] query_tag[0:31];
    reg [3:0] price_tag[0:31];
    reg [GENERATION_BITS-1:0] generation_tag[0:31];
    reg [TX_BITS-1:0] transaction[0:31];
    reg [7:0] transferred[0:31];
    reg [TX_BITS:0] next_tx;
    reg active;
    reg [1:0] active_query;
    reg [3:0] active_price;
    wire binding_matches = phase[cmd_slot]!=FREE && page_tag[cmd_slot]==cmd_page
        && query_tag[cmd_slot]==cmd_query && price_tag[cmd_slot]==cmd_price
        && generation_tag[cmd_slot]==cmd_generation;
    wire current_query = active && cmd_query==active_query && cmd_price==active_price;
    wire descriptor_matches = binding_matches && transaction[cmd_slot]==cmd_tx
        && ((phase[cmd_slot]==WB && !cmd_kind) || (phase[cmd_slot]==RF && cmd_kind));
    wire [31:0] slot_free,slot_dirty;
    genvar slot_index;
    generate for(slot_index=0;slot_index<32;slot_index=slot_index+1)begin: slot_flags
        assign slot_free[slot_index]=phase[slot_index]==FREE;
        assign slot_dirty[slot_index]=phase[slot_index]==LIVE && dirty[slot_index];
    end endgenerate
    wire all_free=&slot_free;
    wire unleased_dirty=|slot_dirty;

    reg core_valid, awaiting;
    wire core_ready, core_rsp_valid;
    wire [2:0] core_status;
    wire [159:0] core_payload;
    wire core_present, core_dirty;
    reg [2:0] core_op;
    reg [3:0] pending_op;
    reg [4:0] saved_slot;reg [1:0] saved_query;
    reg [20:0] saved_page;
    reg [3:0] saved_price;
    reg [GENERATION_BITS-1:0] saved_generation;
    reg [2:0] saved_offset;
    reg [2:0] saved_field;
    reg [31:0] saved_value;
    reg [159:0] saved_payload;
    scratch_frame_store #(.SLOTS(32),.SLOT_BITS(5),.OFFSET_BITS(3),.PAGE_BITS(21),.GENERATION_BITS(GENERATION_BITS)) storage(
        .clk(clk),.rst(rst),.cmd_valid(core_valid),.cmd_ready(core_ready),
        .cmd_op(core_op),.cmd_slot(saved_slot),.cmd_page(saved_page),
        .cmd_query(saved_query),.cmd_price(saved_price),.cmd_generation(saved_generation),
        .cmd_offset(saved_offset),.cmd_field(saved_field),.cmd_value(saved_value),
        .cmd_payload(saved_payload),.rsp_valid(core_rsp_valid),.rsp_ready(awaiting),
        .rsp_status(core_status),.rsp_payload(core_payload),
        .rsp_present(core_present),.rsp_dirty(core_dirty));
    assign cmd_ready = !rst && !rsp_valid && !core_valid && !awaiting;
    integer i;
    always @(posedge clk) begin
        if(rst) begin
            rsp_valid<=0; rsp_status<=OK; rsp_payload<=0; rsp_present<=0; rsp_dirty<=0; rsp_tx<=0;
            core_valid<=0; awaiting<=0; active<=0; draining<=0;
            rf_sealed<=0; dirty<=0; pristine<=0; generation_used<=0; query_used<=0; next_tx<=0;
            active_query<=0; active_price<=0;
            for(i=0;i<32;i=i+1) begin
                phase[i]<=FREE; page_tag[i]<=0; query_tag[i]<=0; price_tag[i]<=0;
                generation_tag[i]<=0; transaction[i]<=0; transferred[i]<=0;
            end
        end else begin
            if(rsp_valid && rsp_ready) rsp_valid<=0;
            if(core_valid && core_ready) begin core_valid<=0; awaiting<=1; end
            if(awaiting && core_rsp_valid) begin
                awaiting<=0; rsp_valid<=1; rsp_status<=core_status;
                rsp_payload<=core_payload; rsp_present<=core_present; rsp_dirty<=core_dirty; rsp_tx<=0;
                if(core_status==OK) begin
                    case(pending_op)
                        BIND: begin
                            phase[saved_slot]<=LIVE; dirty[saved_slot]<=0; pristine[saved_slot]<=1;
                            page_tag[saved_slot]<=saved_page; query_tag[saved_slot]<=saved_query;
                            price_tag[saved_slot]<=saved_price; generation_tag[saved_slot]<=saved_generation;
                            generation_used[saved_slot]<=1;
                        end
                        WRITEBACK: begin
                            // Lock was established before this synchronous mask read.
                            // Absent offsets are represented by canonical codec zeros.
                            transferred[saved_slot]<=~core_payload[7:0];
                            rsp_tx<=transaction[saved_slot];
                        end
                        WRITE: begin dirty[saved_slot]<=1; pristine[saved_slot]<=0; end
                        RELEASE: begin phase[saved_slot]<=FREE; dirty[saved_slot]<=0; end
                        BEAT, EXPORT: transferred[saved_slot][saved_offset]<=1;
                        COMPLETE: begin phase[saved_slot]<=LIVE; dirty[saved_slot]<=0; end
                        default: begin end
                    endcase
                end
            end
            if(cmd_valid && cmd_ready) begin
                rsp_valid<=1; rsp_status<=OK; rsp_payload<=0; rsp_present<=0; rsp_dirty<=0; rsp_tx<=0;
                // Latched once; the core never uses unaccepted live command fields.
                pending_op<=cmd_op; saved_slot<=cmd_slot; saved_query<=cmd_query;
                saved_page<=cmd_page; saved_price<=cmd_price; saved_generation<=cmd_generation;
                saved_offset<=cmd_offset; saved_field<=cmd_field; saved_value<=cmd_value; saved_payload<=cmd_payload;
                case(cmd_op)
                    QUERY: begin
                        if(draining) rsp_status<=FENCE_WAIT;
                        else if(query_used[cmd_query]) rsp_status<=EXHAUSTED;
                        else begin
                            active<=1; active_query<=cmd_query; active_price<=cmd_price;
                            query_used[cmd_query]<=1;
                        end
                    end
                    BIND: begin
                        if(draining) rsp_status<=FENCE_WAIT;
                        else if(!current_query) rsp_status<=STALE;
                        else if(phase[cmd_slot]!=FREE) rsp_status<=BUSY;
                        else if(generation_used[cmd_slot] && cmd_generation<=generation_tag[cmd_slot]) rsp_status<=EXHAUSTED;
                        else begin core_op<=0; core_valid<=1; rsp_valid<=0; end
                    end
                    READ, WRITE: begin
                        if(!binding_matches || !current_query || draining) rsp_status<=STALE;
                        else if(phase[cmd_slot]!=LIVE) rsp_status<=BUSY;
                        else begin core_op<=(cmd_op==READ)?1:2; core_valid<=1; rsp_valid<=0; end
                    end
                    RELEASE: begin
                        if(!binding_matches) rsp_status<=STALE;
                        else if(phase[cmd_slot]!=LIVE) rsp_status<=BUSY;
                        else if(dirty[cmd_slot]) begin rsp_status<=DIRTY; rsp_dirty<=1; end
                        else begin core_op<=4; core_valid<=1; rsp_valid<=0; end
                    end
                    WRITEBACK, REFILL: begin
                        if(draining) rsp_status<=FENCE_WAIT;
                        else if(!binding_matches || (cmd_op==REFILL && !current_query)) rsp_status<=STALE;
                        else if(phase[cmd_slot]!=LIVE) rsp_status<=BUSY;
                        else if(cmd_op==REFILL && !pristine[cmd_slot]) rsp_status<=BAD;
                        else if(next_tx[TX_BITS]) rsp_status<=EXHAUSTED;
                        else begin
                            phase[cmd_slot]<=(cmd_op==WRITEBACK)?WB:RF;
                            transaction[cmd_slot]<=next_tx[TX_BITS-1:0]; rsp_tx<=next_tx[TX_BITS-1:0];
                            next_tx<=next_tx+1'b1; transferred[cmd_slot]<=0;
                            if(cmd_op==REFILL)begin pristine[cmd_slot]<=0;rf_sealed[cmd_slot]<=0;end
                            else begin core_op<=6; core_valid<=1; rsp_valid<=0; end
                        end
                    end
                    BEAT, EXPORT: begin
                        if(!descriptor_matches || (cmd_op==BEAT && !cmd_kind) || (cmd_op==EXPORT && cmd_kind)) rsp_status<=STALE;
                        else if(transferred[cmd_slot][cmd_offset]) rsp_status<=BUSY;
                        else if(cmd_op==BEAT && (cmd_payload[159:136]!=0 || !cmd_present || rf_sealed[cmd_slot])) rsp_status<=BAD;
                        else begin core_op<=(cmd_op==EXPORT)?1:5; core_valid<=1; rsp_valid<=0; end
                    end
                    RF_MASK: begin
                        // Trusted adapter sends this only after decoding all 8 offsets.
                        // Public native ingress rejects opcode14. This does not attest DMA.
                        if(!descriptor_matches || !cmd_kind) rsp_status<=STALE;
                        else if(rf_sealed[cmd_slot]) rsp_status<=BUSY;
                        else if(cmd_payload[159:8]!=0) rsp_status<=BAD;
                        else if(transferred[cmd_slot]!=cmd_payload[7:0]) rsp_status<=INCOMPLETE;
                        else begin transferred[cmd_slot]<=8'hff;rf_sealed[cmd_slot]<=1;end
                    end
                    COMPLETE: begin
                        if(!descriptor_matches) rsp_status<=STALE;
                        else if((cmd_kind && !rf_sealed[cmd_slot]) || !(&transferred[cmd_slot])) rsp_status<=INCOMPLETE;
                        else if(cmd_kind) phase[cmd_slot]<=LIVE;
                        else begin core_op<=3; core_valid<=1; rsp_valid<=0; end
                    end
                    BEGIN_FENCE: begin
                        if(draining) rsp_status<=BUSY;
                        else if(unleased_dirty) begin rsp_status<=DIRTY; rsp_dirty<=1; end
                        else begin draining<=1; active<=0; end
                    end
                    FINISH_FENCE: begin
                        if(!draining || !all_free || !peer_quiescent || !ingress_empty) rsp_status<=FENCE_WAIT;
                        else begin
                            draining<=0; query_used<=0; generation_used<=0; next_tx<=0;
                        end
                    end
                    default: rsp_status<=BAD;
                endcase
            end
        end
    end
endmodule
