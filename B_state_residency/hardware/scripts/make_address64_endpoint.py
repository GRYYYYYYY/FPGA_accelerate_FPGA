"""Wrap the unchanged static-codec endpoint with a locked 64-bit base."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=(ROOT/'hardware/rtl/memory_scratch_endpoint_small_staticcodec.sv').read_text();head=s[:s.index('\n);')]
 head=head.replace('module memory_scratch_endpoint_small_staticcodec #(','module memory_scratch_endpoint_address64 #(').replace('output reg','output wire').replace('output wire [31:0] m_awaddr','output wire [63:0] m_awaddr').replace('output wire [31:0] m_araddr','output wire [63:0] m_araddr')
 return head+''',
    input wire cfg_base_valid,output wire cfg_base_ready,input wire [63:0] cfg_base_address,
    output wire cfg_rsp_valid,input wire cfg_rsp_ready,output wire [1:0] cfg_rsp_status,
    output wire configured
);
    wire [63:0] backing_base;
    wire [31:0] relative_awaddr,relative_araddr;
    wire core_cmd_ready;
    wire core_cmd_valid;
    assign core_cmd_valid=cmd_valid && configured;
    assign cmd_ready=core_cmd_ready && configured;
    assign m_awaddr=backing_base+{32'b0,relative_awaddr};
    assign m_araddr=backing_base+{32'b0,relative_araddr};
    backing_base_config #(.FRAMES(FRAMES)) base_config(
        .clk(clk),.rst(rst),.cfg_base_valid(cfg_base_valid),.cfg_base_ready(cfg_base_ready),
        .cfg_base_address(cfg_base_address),.cfg_rsp_valid(cfg_rsp_valid),.cfg_rsp_ready(cfg_rsp_ready),
        .cfg_rsp_status(cfg_rsp_status),.configured(configured),.backing_base(backing_base));
    memory_scratch_endpoint_small_staticcodec #(
        .TX_BITS(TX_BITS),.GENERATION_BITS(GENERATION_BITS),.TAG_BITS(TAG_BITS),
        .FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),
        .PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS)) core(
        .cmd_valid(core_cmd_valid),.cmd_ready(core_cmd_ready),
        .m_awaddr(relative_awaddr),.m_araddr(relative_araddr),.*);
endmodule
'''
def testbench():
 s=(ROOT/'hardware/tb/tb_small_endpoint_epoch6.sv').read_text().replace('module tb_small_endpoint_epoch6;','module tb_address64_endpoint;').replace('dut.','dut.core.')
 s=s.replace('memory_scratch_endpoint_small_staticcodec #(','memory_scratch_endpoint_address64 #(').replace('dut(.*);','dut(.m_awaddr(outer_awaddr),.m_araddr(outer_araddr),.*);')
 marker='    memory_scratch_endpoint_address64 #('
 insert='''    localparam [63:0] BASE=64'h0000001234567000;
    wire [63:0] outer_awaddr,outer_araddr;
    wire cfg_base_ready,cfg_rsp_valid,configured;wire [1:0] cfg_rsp_status;
    reg [5:0] config_delay=0;
    always @(posedge clk)if(rst)config_delay<=0;else if(config_delay<23)config_delay<=config_delay+1'b1;
    wire cfg_base_valid=!rst && config_delay>=20;
    wire [63:0] cfg_base_address=BASE;wire cfg_rsp_ready=1'b1;
    assign m_awaddr=outer_awaddr-BASE;
    assign m_araddr=outer_araddr-BASE;
    always @(posedge clk)if(!rst)begin
        if(!configured && (cmd_ready || m_awvalid || m_arvalid || m_wvalid))$fatal(1,"unconfigured ingress or AXI traffic");
        if(cfg_rsp_valid && cfg_rsp_status!=0)$fatal(1,"valid base rejected");
        if(m_awvalid && (outer_awaddr!=BASE+{32'b0,m_awaddr} || outer_awaddr<BASE || m_awaddr+m_awlen*64+64>TB_FRAMES*192))$fatal(1,"bad 64bit AW rebase");
        if(m_arvalid && (outer_araddr!=BASE+{32'b0,m_araddr} || outer_araddr<BASE || m_araddr+m_arlen*64+64>TB_FRAMES*192))$fatal(1,"bad 64bit AR rebase");
    end
'''
 i=s.index(marker);s=s[:i]+insert+s[i:]
 s=s.replace('$display("SMALL_STALLS_PASS cases=8 blocked_cycles=800");','$display("ADDRESS64_ENDPOINT_PASS base=%h",BASE);\n        $display("SMALL_STALLS_PASS cases=8 blocked_cycles=800");')
 return s
if __name__=='__main__':
 (ROOT/'hardware/variants/address64/memory_scratch_endpoint_address64.sv').write_text(render())
 (ROOT/'hardware/tb/tb_address64_endpoint.sv').write_text(testbench())
