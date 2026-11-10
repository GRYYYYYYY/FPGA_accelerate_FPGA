"""Derive the same integration checker at a low-32-bit carry boundary."""
from pathlib import Path
from make_address64_endpoint import testbench,ROOT
def render():
 s=testbench().replace('module tb_address64_endpoint;','module tb_address64_endpoint_carry;').replace("64'h0000001234567000","64'h00000012fffff000")
 i=s.index('    reg [511:0] memory[')
 s=s[:i]+'''    integer aw_carries=0,ar_carries=0;
    always @(posedge clk)if(!rst)begin
        if(m_awvalid && m_awready && outer_awaddr[63:32]!=BASE[63:32])aw_carries=aw_carries+1;
        if(m_arvalid && m_arready && outer_araddr[63:32]!=BASE[63:32])ar_carries=ar_carries+1;
    end
'''+s[i:]
 return s.replace('$display("ADDRESS64_ENDPOINT_PASS base=%h",BASE);','if(aw_carries==0 || ar_carries==0)$fatal(1,"64bit carry not exercised");\n        $display("ADDRESS64_CARRY_PASS aw=%0d ar=%0d",aw_carries,ar_carries);\n        $display("ADDRESS64_ENDPOINT_PASS base=%h",BASE);')
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_address64_endpoint_carry.sv';assert p.read_text()==render();print('CARRY_CHECKER_RECONSTRUCTION_PASS')
