`timescale 1ns/1ps
// LOOKUP opcode5 returns UNREADY on miss without changing allocation or leases.
// BRAM owner directory. Linear owner lookup is deliberate, not a performance claim.
// Cookie: slot[1:0], page[19:2], query[21:20], price[25:22], generation[41:26],
// tx[57:42], kind[58] (0=writeback,1=refill), reserved[63:59]=0.
module backing_frame_directory_lookup #(
    parameter integer FRAMES=23405, INDEX_BITS=15
)(
    input wire clk,rst,input wire cmd_valid,output wire cmd_ready,
    input wire [2:0] cmd_op,input wire [23:0] cmd_owner,
    input wire [INDEX_BITS-1:0] cmd_frame,input wire [63:0] cmd_cookie,
    input wire memory_success,input wire fence_retired,
    output reg rsp_valid,input wire rsp_ready,output reg [2:0] rsp_status,
    output reg [INDEX_BITS-1:0] rsp_frame,output wire [31:0] rsp_address,
    output reg rsp_published,output reg [INDEX_BITS:0] allocated,
    output wire [3:0] leased,output wire any_fault
);
    localparam [2:0] RESERVE=0,PIN=1,MEMORY_DONE=2,RETIRE=3,RECYCLE=4,LOOKUP=5;
    localparam [2:0] OK=0,STALE=1,BUSY=2,BAD=3,FULL=4,OLD_TX=5,UNREADY=6,IO_ERROR=7;
    localparam [3:0] IDLE=0,SCAN_READ=1,SCAN_CHECK=2,ALLOCATE=3,PIN_READ=4,PIN_CHECK=5,PIN_COMMIT=6;
    localparam [1:0] FREE=0,INFLIGHT=1,COMPLETE=2,FAILED=3;
    reg [3:0] state;
    (* ram_style="block" *) reg [24:0] owners[0:FRAMES-1];
    reg [24:0] read_word;
    reg [23:0] owner;
    reg [INDEX_BITS-1:0] index,frame;
    reg [63:0] cookie;
    reg [1:0] lease_phase[0:3];
    reg [63:0] lease_cookie[0:3];
    reg [INDEX_BITS-1:0] lease_frame[0:3];
    reg tx_used;reg [15:0] last_tx;reg lookup_only;
    wire [1:0] slot=cmd_cookie[1:0];
    wire lease_match=lease_phase[slot]!=FREE && lease_cookie[slot]==cmd_cookie && lease_frame[slot]==cmd_frame;
    wire frame_leased=(leased[0] && lease_frame[0]==cmd_frame) || (leased[1] && lease_frame[1]==cmd_frame)
        || (leased[2] && lease_frame[2]==cmd_frame) || (leased[3] && lease_frame[3]==cmd_frame);
    assign leased={lease_phase[3]!=FREE,lease_phase[2]!=FREE,lease_phase[1]!=FREE,lease_phase[0]!=FREE};
    assign any_fault=lease_phase[0]==FAILED || lease_phase[1]==FAILED || lease_phase[2]==FAILED || lease_phase[3]==FAILED;
    assign cmd_ready=!rst && state==IDLE && !rsp_valid;
    wire accept=cmd_valid && cmd_ready;
    wire successful_wb=accept && cmd_op==MEMORY_DONE && lease_match && lease_phase[slot]==INFLIGHT && memory_success && !cmd_cookie[58];
    wire mem_write=!rst && (state==ALLOCATE || (state==PIN_COMMIT && !cookie[58]) || successful_wb);
    wire [INDEX_BITS-1:0] write_index=state==ALLOCATE?allocated[INDEX_BITS-1:0]:(successful_wb?cmd_frame:frame);
    wire [24:0] write_word=state==ALLOCATE?{1'b0,owner}:(successful_wb?{1'b1,cmd_cookie[25:2]}:{1'b0,cookie[25:2]});
    wire mem_read=!rst && (state==SCAN_READ || state==PIN_READ);
    wire [INDEX_BITS-1:0] read_index=state==SCAN_READ?index:frame;
    always @(posedge clk) begin
        if(mem_write)owners[write_index]<=write_word;
        if(mem_read)read_word<=owners[read_index];
    end
    wire [31:0] frame32={{(32-INDEX_BITS){1'b0}},rsp_frame};
    assign rsp_address=(frame32<<10)+(frame32<<8)+(frame32<<6);
    integer i;
    always @(posedge clk) begin
        if(rst)begin
            state<=IDLE;allocated<=0;rsp_valid<=0;rsp_status<=OK;rsp_frame<=0;rsp_published<=0;
            tx_used<=0;last_tx<=0;lookup_only<=0;index<=0;frame<=0;owner<=0;cookie<=0;
            for(i=0;i<4;i=i+1)begin lease_phase[i]<=FREE;lease_cookie[i]<=0;lease_frame[i]<=0;end
        end else begin
            if(rsp_valid && rsp_ready)rsp_valid<=0;
            case(state)
                SCAN_READ:state<=SCAN_CHECK;
                SCAN_CHECK:begin
                    if(read_word[23:0]==owner)begin rsp_valid<=1;rsp_frame<=index;rsp_published<=read_word[24];state<=IDLE;end
                    else if({1'b0,index}+1'b1<allocated)begin index<=index+1'b1;state<=SCAN_READ;end
                    else if(lookup_only)begin rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;end
                    else if(allocated<FRAMES)state<=ALLOCATE;
                    else begin rsp_valid<=1;rsp_status<=FULL;state<=IDLE;end
                end
                ALLOCATE:begin
                    rsp_valid<=1;rsp_frame<=allocated[INDEX_BITS-1:0];rsp_published<=0;
                    allocated<=allocated+1'b1;state<=IDLE;
                end
                PIN_READ:state<=PIN_CHECK;
                PIN_CHECK:begin
                    if(read_word[23:0]!=cookie[25:2])begin rsp_valid<=1;rsp_status<=STALE;state<=IDLE;end
                    else if(cookie[58] && !read_word[24])begin rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;end
                    else state<=PIN_COMMIT;
                end
                PIN_COMMIT:begin
                    lease_phase[cookie[1:0]]<=INFLIGHT;lease_cookie[cookie[1:0]]<=cookie;lease_frame[cookie[1:0]]<=frame;
                    tx_used<=1;last_tx<=cookie[57:42];rsp_valid<=1;rsp_frame<=frame;
                    rsp_published<=cookie[58];state<=IDLE;
                end
                default:begin end
            endcase
            if(accept)begin
                rsp_valid<=1;rsp_status<=OK;rsp_frame<=0;rsp_published<=0;
                case(cmd_op)
                    RESERVE,LOOKUP:begin
                        owner<=cmd_owner;index<=0;lookup_only<=cmd_op==LOOKUP;
                        if(1'b0)rsp_status<=UNREADY;
                        else begin rsp_valid<=0;state<=allocated==0?ALLOCATE:SCAN_READ;end
                    end
                    PIN:begin
                        if(cmd_cookie[63:59]!=0)rsp_status<=BAD;
                        else if({1'b0,cmd_frame}>=allocated)rsp_status<=STALE;
                        else if(lease_phase[slot]!=FREE || frame_leased)rsp_status<=BUSY;
                        else if(tx_used && cmd_cookie[57:42]<=last_tx)rsp_status<=OLD_TX;
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
                    RECYCLE:begin
                        if(leased!=0 || !fence_retired)rsp_status<=BUSY;
                        else begin allocated<=0;tx_used<=0;last_tx<=0;end
                    end
                    default:rsp_status<=BAD;
                endcase
            end
        end
    end
endmodule
