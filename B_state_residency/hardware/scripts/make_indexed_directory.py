"""Derive a new bounded-index directory without editing the frozen linear RTL."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def generate(text):
    def replace(before, after):
        nonlocal text
        if text.count(before) != 1:
            raise ValueError('Ambiguous source anchor: ' + before[:70])
        text = text.replace(before, after)
    replace('module backing_frame_directory_lookup #(', 'module backing_frame_directory_indexed #(')
    replace('parameter integer FRAMES=23405, INDEX_BITS=15',
            'parameter integer FRAMES=23405, INDEX_BITS=15, HASH_BITS=15, PROBE_LIMIT=64, EPOCH_BITS=8')
    replace('// BRAM owner directory. Linear owner lookup is deliberate, not a performance claim.',
            '// Authoritative owner BRAM plus a bounded, non-authoritative frame index.\n'
            '// A miss falls back to the owner scan whenever any allocation is unindexed.')
    replace('reg [3:0] state;', '''localparam [3:0] HASH_1=7,HASH_2=8,HASH_3=9,PROBE_READ=10,PROBE_CHECK=11,
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
    end''')
    replace('(state==SCAN_READ || state==PIN_READ)', '(state==SCAN_READ || state==PIN_READ || state==OWNER_READ)')
    replace('read_index=state==SCAN_READ?index:frame;',
            'read_index=state==SCAN_READ?index:(state==OWNER_READ?indexed_frame:frame);')
    replace('state<=IDLE;allocated<=0;rsp_valid<=0;', 'state<=CLEAR_INDEX;allocated<=0;rsp_valid<=0;')
    replace('tx_used<=0;last_tx<=0;lookup_only<=0;index<=0;frame<=0;owner<=0;cookie<=0;', '''tx_used<=0;last_tx<=0;lookup_only<=0;index<=0;frame<=0;owner<=0;cookie<=0;
            epoch<=1;clear_index<=0;clear_response<=0;bucket<=0;hash_word<=0;probes<=0;
            indexed_frame<=0;insertion_slot<=0;index_complete<=1;''')
    replace('case(state)\n                SCAN_READ:', '''case(state)
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
                        rsp_valid<=1;rsp_frame<=indexed_frame;rsp_published<=read_word[24];state<=IDLE;
                    end else if(probes>=PROBE_LIMIT || probes>=HASH_SLOTS)begin
                        index<=0;state<=SCAN_READ;
                    end else begin bucket<=bucket+1'b1;probes<=probes+1'b1;state<=PROBE_READ;end
                end
                SCAN_READ:''')
    replace('allocated<=allocated+1\'b1;state<=IDLE;',
            "allocated<=allocated+1'b1;state<=IDLE;if(!insertion_slot)index_complete<=0;")
    replace('''if(cmd_op==LOOKUP && allocated==0)rsp_status<=UNREADY;
                        else begin rsp_valid<=0;state<=allocated==0?ALLOCATE:SCAN_READ;end''',
            '''hash_word<={8'b0,cmd_owner};insertion_slot<=0;
                        if(cmd_op==LOOKUP && allocated==0)rsp_status<=UNREADY;
                        else begin rsp_valid<=0;state<=HASH_1;end''')
    replace('else begin allocated<=0;tx_used<=0;last_tx<=0;end', '''else begin
                            allocated<=0;tx_used<=0;last_tx<=0;index_complete<=1;insertion_slot<=0;
                            if(&epoch)begin
                                epoch<=1;clear_index<=0;clear_response<=1;state<=CLEAR_INDEX;rsp_valid<=0;
                            end else epoch<=epoch+1'b1;
                        end''')
    return text


if __name__ == '__main__':
    source = ROOT / 'hardware/rtl/backing_frame_directory_lookup.sv'
    (ROOT / 'hardware/rtl/backing_frame_directory_indexed.sv').write_text(generate(source.read_text()))
