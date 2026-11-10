"""Adapt the frozen actual-value trace checker to external high addresses."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 src=ROOT/'results/record_epoch6_pilot_20261024/pilot/sources/tb_epoch6_endpoint_checkpoint_stream.sv'
 s=src.read_text().replace('epoch6_endpoint_checkpoint_stream','address64_endpoint_checkpoint_stream').replace('dut.','dut.core.')
 s=s.replace('memory_scratch_endpoint_small_staticcodec #(','memory_scratch_endpoint_address64 #(').replace('dut(.*);','dut(.m_awaddr(outer_awaddr),.m_araddr(outer_araddr),.*);')
 marker='    memory_scratch_endpoint_address64 #('
 insert='''    localparam [63:0] BASE=64'h00000012fffff000;
    wire [63:0] outer_awaddr,outer_araddr;
    wire cfg_base_ready,cfg_rsp_valid,configured;wire [1:0] cfg_rsp_status;
    reg [5:0] config_delay=0;
    always @(posedge clk)if(rst)config_delay<=0;else if(config_delay<23)config_delay<=config_delay+1'b1;
    wire cfg_base_valid=!rst && config_delay>=20;
    wire [63:0] cfg_base_address=BASE;wire cfg_rsp_ready=1'b1;
    assign m_awaddr=outer_awaddr-BASE;
    assign m_araddr=outer_araddr-BASE;
    integer aw_carries=0,ar_carries=0;
    always @(posedge clk)if(!rst)begin
        if(!configured && (cmd_ready || m_awvalid || m_arvalid || m_wvalid))$fatal(1,"unconfigured ingress or AXI traffic");
        if(cfg_rsp_valid && cfg_rsp_status!=0)$fatal(1,"valid base rejected");
        if(m_awvalid && (outer_awaddr!=BASE+{32'b0,m_awaddr} || outer_awaddr<BASE || m_awaddr+m_awlen*64+64>TB_FRAMES*192))$fatal(1,"bad 64bit AW rebase");
        if(m_arvalid && (outer_araddr!=BASE+{32'b0,m_araddr} || outer_araddr<BASE || m_araddr+m_arlen*64+64>TB_FRAMES*192))$fatal(1,"bad 64bit AR rebase");
        if(m_awvalid && m_awready && outer_awaddr[63:32]!=BASE[63:32])aw_carries=aw_carries+1;
        if(m_arvalid && m_arready && outer_araddr[63:32]!=BASE[63:32])ar_carries=ar_carries+1;
    end
'''
 i=s.index(marker);s=s[:i]+insert+s[i:]
 marker='        $display("TEST_PASS memory_endpoint '
 i=s.index(marker);s=s[:i]+'''        if(aw_carries==0 || ar_carries==0)$fatal(1,"high address carry not exercised");
        $display("ADDRESS64_TRACE_PASS base=%h aw_carries=%0d ar_carries=%0d",BASE,aw_carries,ar_carries);
'''+s[i:]
 return s
if __name__=='__main__':
 (ROOT/'hardware/tb/tb_address64_endpoint_checkpoint_stream.sv').write_text(render())
