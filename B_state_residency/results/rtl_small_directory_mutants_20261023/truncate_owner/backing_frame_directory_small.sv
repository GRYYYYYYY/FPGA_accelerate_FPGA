`timescale 1ns/1ps
// LOOKUP opcode5 returns UNREADY on miss without changing allocation or leases.
// Authoritative owner BRAM plus a bounded, non-authoritative frame index.
// A miss falls back to the owner scan whenever any allocation is unindexed.
// Cookie72: slot[4:0], owner[31:5], generation[47:32], tx[63:48],
// kind[64], reserved[71:65]=0; owner={price4,query2,page21}.
module backing_frame_directory_small #(
    parameter integer FRAMES=163840, INDEX_BITS=18, HASH_BITS=18, PROBE_LIMIT=64, EPOCH_BITS=8
)(
    input wire clk,rst,input wire cmd_valid,output wire cmd_ready,
    input wire [2:0] cmd_op,input wire [26:0] cmd_owner,
    input wire [INDEX_BITS-1:0] cmd_frame,input wire [71:0] cmd_cookie,
    input wire memory_success,input wire fence_retired,
    output reg rsp_valid,input wire rsp_ready,output reg [2:0] rsp_status,
    output reg [INDEX_BITS-1:0] rsp_frame,output wire [31:0] rsp_address,
    output reg rsp_published,output reg [INDEX_BITS:0] allocated,
    output wire [31:0] leased,output wire any_fault
);
    localparam [2:0] RESERVE=0,PIN=1,MEMORY_DONE=2,RETIRE=3,RECYCLE=4,LOOKUP=5,RECYCLE_TX=6;
    localparam [2:0] OK=0,STALE=1,BUSY=2,BAD=3,FULL=4,OLD_TX=5,UNREADY=6,IO_ERROR=7;
    localparam [3:0] IDLE=0,SCAN_READ=1,SCAN_CHECK=2,ALLOCATE=3,PIN_READ=4,PIN_CHECK=5,PIN_COMMIT=6;
    localparam [1:0] FREE=0,INFLIGHT=1,COMPLETE=2,FAILED=3;
    localparam [3:0] HASH_1=7,HASH_2=8,HASH_3=9,PROBE_READ=10,PROBE_CHECK=11,
        OWNER_READ=12,OWNER_CHECK=13,CLEAR_INDEX=14;
    localparam integer HASH_SLOTS=2**HASH_BITS;
    reg [3:0] state;
    (* ram_style="block" *) reg [EPOCH_BITS+INDEX_BITS-1:0] frame_index[0:HASH_SLOTS-1];
    reg [EPOCH_BITS+INDEX_BITS-1:0] index_word;
    reg [EPOCH_BITS-1:0] epoch;
    reg [HASH_BITS-1:0] bucket, clear_index;
    reg [31:0] hash_word;
    reg [HASH_BITS:0] probes;
    reg [INDEX_BITS-1:0] indexed_frame;
    reg insertion_slot, index_complete, clear_response;
    wire index_write=!rst && (state==CLEAR_INDEX || (state==ALLOCATE && insertion_slot));
    wire [HASH_BITS-1:0] index_write_address=state==CLEAR_INDEX?clear_index:bucket;
    wire [EPOCH_BITS+INDEX_BITS-1:0] index_write_word=state==CLEAR_INDEX?'0:{epoch,allocated[INDEX_BITS-1:0]};
    always @(posedge clk) begin
        if(index_write)frame_index[index_write_address]<=index_write_word;
        if(!rst && state==PROBE_READ)index_word<=frame_index[bucket];
    end
    (* ram_style="block" *) reg [27:0] owners[0:FRAMES-1];
    reg [27:0] read_word;
    reg [26:0] owner;
    reg [INDEX_BITS-1:0] index,frame;
    reg [71:0] cookie;
    reg [1:0] lease_phase[0:31];
    reg [71:0] lease_cookie[0:31];
    reg [INDEX_BITS-1:0] lease_frame[0:31];
    reg tx_used;reg [15:0] last_tx;reg lookup_only;
    wire [4:0] slot=cmd_cookie[4:0];
    wire lease_match=lease_phase[slot]!=FREE && lease_cookie[slot]==cmd_cookie && lease_frame[slot]==cmd_frame;
    wire [31:0] same_frame,failed;
    genvar slot_index;
    generate for(slot_index=0;slot_index<32;slot_index=slot_index+1)begin: lease_flags
        assign leased[slot_index]=lease_phase[slot_index]!=FREE;
        assign same_frame[slot_index]=leased[slot_index] && lease_frame[slot_index]==cmd_frame;
        assign failed[slot_index]=lease_phase[slot_index]==FAILED;
    end endgenerate
    wire frame_leased=|same_frame;
    assign any_fault=|failed;
    assign cmd_ready=!rst && state==IDLE && !rsp_valid;
    wire accept=cmd_valid && cmd_ready;
    wire successful_wb=accept && cmd_op==MEMORY_DONE && lease_match && lease_phase[slot]==INFLIGHT && memory_success && !cmd_cookie[64];
    wire mem_write=!rst && (state==ALLOCATE || (state==PIN_COMMIT && !cookie[64]) || successful_wb);
    wire [INDEX_BITS-1:0] write_index=state==ALLOCATE?allocated[INDEX_BITS-1:0]:(successful_wb?cmd_frame:frame);
    wire [27:0] write_word=state==ALLOCATE?{1'b0,owner}:(successful_wb?{1'b1,cmd_cookie[31:5]}:{1'b0,cookie[31:5]});
    wire mem_read=!rst && (state==SCAN_READ || state==PIN_READ || state==OWNER_READ);
    wire [INDEX_BITS-1:0] read_index=state==SCAN_READ?index:(state==OWNER_READ?indexed_frame:frame);
    always @(posedge clk) begin
        if(mem_write)owners[write_index]<=write_word;
        if(mem_read)read_word<=owners[read_index];
    end
    wire [31:0] frame32={{(32-INDEX_BITS){1'b0}},rsp_frame};
    assign rsp_address=(frame32<<7)+(frame32<<6);
    integer i;
    always @(posedge clk) begin
        if(rst)begin
            state<=CLEAR_INDEX;allocated<=0;rsp_valid<=0;rsp_status<=OK;rsp_frame<=0;rsp_published<=0;
            tx_used<=0;last_tx<=0;lookup_only<=0;index<=0;frame<=0;owner<=0;cookie<=0;
            epoch<=1;clear_index<=0;clear_response<=0;bucket<=0;hash_word<=0;probes<=0;
            indexed_frame<=0;insertion_slot<=0;index_complete<=1;
            for(i=0;i<32;i=i+1)begin lease_phase[i]<=FREE;lease_cookie[i]<=0;lease_frame[i]<=0;end
        end else begin
            if(rsp_valid && rsp_ready)rsp_valid<=0;
            case(state)
                CLEAR_INDEX:begin
                    if(clear_index==HASH_SLOTS-1)begin
                        state<=IDLE;rsp_valid<=clear_response;clear_response<=0;
                    end else clear_index<=clear_index+1'b1;
                end
                HASH_1:begin hash_word<=(hash_word^(hash_word>>16))*32'h85ebca6b;state<=HASH_2;end
                HASH_2:begin hash_word<=(hash_word^(hash_word>>13))*32'hc2b2ae35;state<=HASH_3;end
                HASH_3:begin bucket<=hash_word^(hash_word>>16);probes<=1;state<=PROBE_READ;end
                PROBE_READ:state<=PROBE_CHECK;
                PROBE_CHECK:begin
                    if(index_word[EPOCH_BITS+INDEX_BITS-1:INDEX_BITS]!=epoch)begin
                        insertion_slot<=1;
                        if(!index_complete && allocated!=0)begin index<=0;state<=SCAN_READ;end
                        else if(lookup_only)begin rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;end
                        else if(allocated<FRAMES)state<=ALLOCATE;
                        else begin rsp_valid<=1;rsp_status<=FULL;state<=IDLE;end
                    end else begin indexed_frame<=index_word[INDEX_BITS-1:0];state<=OWNER_READ;end
                end
                OWNER_READ:state<=OWNER_CHECK;
                OWNER_CHECK:begin
                    if({1'b0,indexed_frame}<allocated && read_word[23:0]==owner)begin
                        rsp_valid<=1;rsp_frame<=indexed_frame;rsp_published<=read_word[27];state<=IDLE;
                    end else if(probes>=PROBE_LIMIT || probes>=HASH_SLOTS)begin
                        index<=0;state<=SCAN_READ;
                    end else begin bucket<=bucket+1'b1;probes<=probes+1'b1;state<=PROBE_READ;end
                end
                SCAN_READ:state<=SCAN_CHECK;
                SCAN_CHECK:begin
                    if(read_word[23:0]==owner)begin rsp_valid<=1;rsp_frame<=index;rsp_published<=read_word[27];state<=IDLE;end
                    else if({1'b0,index}+1'b1<allocated)begin index<=index+1'b1;state<=SCAN_READ;end
                    else if(lookup_only)begin rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;end
                    else if(allocated<FRAMES)state<=ALLOCATE;
                    else begin rsp_valid<=1;rsp_status<=FULL;state<=IDLE;end
                end
                ALLOCATE:begin
                    rsp_valid<=1;rsp_frame<=allocated[INDEX_BITS-1:0];rsp_published<=0;
                    allocated<=allocated+1'b1;state<=IDLE;if(!insertion_slot)index_complete<=0;
                end
                PIN_READ:state<=PIN_CHECK;
                PIN_CHECK:begin
                    if(read_word[26:0]!=cookie[31:5])begin rsp_valid<=1;rsp_status<=STALE;state<=IDLE;end
                    else if(cookie[64] && !read_word[27])begin rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;end
                    else state<=PIN_COMMIT;
                end
                PIN_COMMIT:begin
                    lease_phase[cookie[4:0]]<=INFLIGHT;lease_cookie[cookie[4:0]]<=cookie;lease_frame[cookie[4:0]]<=frame;
                    tx_used<=1;last_tx<=cookie[63:48];rsp_valid<=1;rsp_frame<=frame;
                    rsp_published<=cookie[64];state<=IDLE;
                end
                default:begin end
            endcase
            if(accept)begin
                rsp_valid<=1;rsp_status<=OK;rsp_frame<=0;rsp_published<=0;
                case(cmd_op)
                    RESERVE,LOOKUP:begin
                        owner<=cmd_owner;index<=0;lookup_only<=cmd_op==LOOKUP;
                        hash_word<={5'b0,cmd_owner};insertion_slot<=0;
                        if(cmd_op==LOOKUP && allocated==0)rsp_status<=UNREADY;
                        else begin rsp_valid<=0;state<=HASH_1;end
                    end
                    PIN:begin
                        if(cmd_cookie[71:65]!=0)rsp_status<=BAD;
                        else if({1'b0,cmd_frame}>=allocated)rsp_status<=STALE;
                        else if(lease_phase[slot]!=FREE || frame_leased)rsp_status<=BUSY;
                        else if(tx_used && cmd_cookie[63:48]<=last_tx)rsp_status<=OLD_TX;
                        else begin cookie<=cmd_cookie;frame<=cmd_frame;state<=PIN_READ;rsp_valid<=0;end
                    end
                    MEMORY_DONE:begin
                        if(!lease_match || lease_phase[slot]!=INFLIGHT)rsp_status<=STALE;
                        else begin
                            lease_phase[slot]<=memory_success?COMPLETE:FAILED;
                            if(!memory_success)rsp_status<=IO_ERROR;
                            else begin rsp_frame<=cmd_frame;rsp_published<=1;end
                        end
                    end
                    RETIRE:begin
                        if(!lease_match)rsp_status<=STALE;
                        else if(lease_phase[slot]!=COMPLETE)rsp_status<=UNREADY;
                        else begin lease_phase[slot]<=FREE;rsp_frame<=cmd_frame;rsp_published<=1;end
                    end
                    // Internal only: caller proves exclusive query and full drain.
                    // Free leases alone do not establish end-to-end quiescence.
                    RECYCLE_TX:begin
                        if(leased!=0 || !fence_retired)rsp_status<=BUSY;
                        else begin tx_used<=0;last_tx<=0;end
                    end
                    RECYCLE:begin
                        if(leased!=0 || !fence_retired)rsp_status<=BUSY;
                        else begin
                            allocated<=0;tx_used<=0;last_tx<=0;index_complete<=1;insertion_slot<=0;
                            if(&epoch)begin
                                epoch<=1;clear_index<=0;clear_response<=1;state<=CLEAR_INDEX;rsp_valid<=0;
                            end else epoch<=epoch+1'b1;
                        end
                    end
                    default:rsp_status<=BAD;
                endcase
            end
        end
    end
endmodule
