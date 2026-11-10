"""Keep the independent burst-slave model from the frozen service regression."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 original=(ROOT/'hardware/tb/tb_backing_page_service.sv').read_text()
 axi=original[original.index('    wire [31:0] m_awaddr'):original.index('    backing_page_service #')]
 slave=original[original.index('    reg aw_pending=0'):original.index('    function automatic [63:0] make_cookie')]
 slave=slave.replace('integer cycle=0,aw_count=0','integer aw_count=0')
 slave=slave.replace(',held_out=0','').replace('    reg [511:0] saved_out;','').replace(';held_out<=0','')
 slave=slave.replace('            if(held_out && (!out_valid || out_data!==saved_out))$fatal(1,"read stream changed under backpressure");\n','').replace('            held_out<=out_valid&&!out_ready;saved_out<=out_data;\n','')
 header='''`timescale 1ns/1ps
module memory_endpoint_test #(parameter integer SMALL=0);
    localparam integer TB_TX=SMALL?3:16,TB_GEN=SMALL?3:16,TB_TAG=SMALL?1:2;
    localparam integer TB_FRAMES=SMALL?4:512,TB_INDEX=SMALL?2:9;
    reg clk=0;always #5 clk=~clk;
    reg rst=1,cmd_valid=0,rsp_ready=0;wire cmd_ready,rsp_valid;
    reg [3:0] cmd_op=0,cmd_price=0;reg [1:0] cmd_slot=0,cmd_query=0;
    reg [17:0] cmd_page=0;reg [TB_GEN-1:0] cmd_generation=0;
    reg [5:0] cmd_offset=0;reg [2:0] cmd_field=0;reg [31:0] cmd_value=0;
    wire [3:0] rsp_status;wire [159:0] rsp_payload;wire rsp_present,rsp_dirty;
    wire [TB_TX-1:0] rsp_tx;wire fault,draining;
    wire [3:0] page_leases,memory_leases;wire [TB_INDEX:0] allocated;wire [TB_TAG-1:0] fence_tag;
    wire dispatch_enable,execute_enable,fence_service_enable,ack_receive_enable;
'''
 body='''    memory_scratch_endpoint #(.TX_BITS(TB_TX),.GENERATION_BITS(TB_GEN),.TAG_BITS(TB_TAG),.FRAMES(TB_FRAMES),.INDEX_BITS(TB_INDEX)) dut(.*);
    reg [511:0] memory[0:TB_FRAMES*21-1],write_words[0:20],expected[0:20];
    reg [511:0] raw_expected[0:127805];
    reg [159:0] golden[0:63];reg [63:0] golden_bitmap=0;
    integer cycle=0;
    integer active_op=0,stream_write=0,stream_read=0,record_acks=0,completed_transfers=0,completed_fences=0;
    integer closure_gap_cycles=0,starts=0,tag_wraps=0,host_stalls=0,read_bytes_check=1;
    reg memory_completed=0,page_completed=0,page_fence_completed=0,held_rsp=0;
    reg [165+TB_TX:0] saved_rsp;
    reg [TB_TAG-1:0] previous_tag=0;
    assign dispatch_enable=cycle%5!=0;
    assign execute_enable=cycle%7>=2;
    assign fence_service_enable=cycle%11>=4;
    assign ack_receive_enable=cycle%13>=5;
'''
 p=ROOT/'hardware/tb/tb_memory_endpoint.sv'
 if p.exists():raise FileExistsError(p)
 p.write_text(header+axi+body+slave+(ROOT/'hardware/tb/memory_endpoint_stimulus.svh').read_text()+'''
endmodule
module tb_memory_endpoint_small;memory_endpoint_test #(.SMALL(1)) test();endmodule
module tb_memory_endpoint_actual;memory_endpoint_test #(.SMALL(0)) test();endmodule
''')
if __name__=='__main__':main()
