"""Trusted RF seal boundary tests; native tests separately gate untrusted op14."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=(ROOT/'hardware/tb/tb_sparse_writeback_boundaries.sv').read_text()
 s=s[:s.index('    initial begin\n        repeat(3)')].replace('tb_sparse_writeback_boundaries','tb_sparse_records_boundaries')
 return s+'''    initial begin
        repeat(3)@(negedge clk);rst=0;
        issue(0,0,0,0,0,0,0,0);issue(1,0,0,0,0,0,0,0);
        cmd_kind=1;issue(6,0,0,0,0,0,0,0);
        issue(8,0,0,6,0,0,0,0); // even empty refill needs explicit seal
        cmd_kind=0;issue(14,0,0,1,0,0,0,0);cmd_kind=1;
        issue(14,0,1,1,0,0,0,0);
        cmd_generation=1;issue(14,0,0,1,0,0,0,0);cmd_generation=0;
        cmd_payload=256;issue(14,0,0,3,0,0,0,0); // noncanonical high bits
        cmd_payload=8'h81;issue(14,0,0,6,0,0,0,0); // missing both present records
        cmd_payload=0;cmd_present=0;issue(7,0,0,3,0,0,0,0); // absent BEAT forbidden
        cmd_present=1;issue(7,0,0,0,0,1,0,0); // present zero is loaded and counted
        issue(7,0,0,4,0,0,0,0); // duplicate record
        issue(14,0,0,6,0,0,0,0); // empty mask omits already loaded present0
        cmd_payload=8'h81;issue(14,0,0,6,0,0,0,0); // offset7 still missing
        cmd_payload=7;issue(7,7,0,0,7,1,0,0);
        issue(2,7,0,4,0,0,0,0); // not visible before COMPLETE
        issue(8,0,0,6,0,0,0,0); // all present loaded but no seal yet
        cmd_payload=8'h81;issue(14,0,0,0,0,0,0,0);
        issue(14,0,0,4,0,0,0,0); // duplicate seal
        cmd_payload=1;issue(7,1,0,4,0,0,0,0); // no records after seal
        issue(8,0,0,0,0,0,0,0);
        issue(2,0,0,0,0,1,0,0);issue(2,7,0,0,7,1,0,0);
        issue(6,0,0,3,0,0,0,0); // cannot refill nonpristine binding
        issue(4,0,0,0,0,0,0,0);
        cmd_slot=1;issue(1,0,0,0,0,0,0,0);
        issue(6,0,0,0,0,0,0,1); // new RF lease clears sealed state
        cmd_payload=0;issue(14,0,1,0,0,0,0,0); // valid trusted empty representation
        issue(8,0,1,0,0,0,0,0);
        issue(2,0,0,0,0,0,0,0); // old data/bitmap from slot0 not visible
        issue(4,0,0,0,0,0,0,0);
        issue(1,0,0,5,0,0,0,0); // generation quarantine retained
        cmd_query=1;cmd_generation=1;issue(1,0,0,1,0,0,0,0);
        if(checks!=33 || draining)$fatal(1,"RF boundary coverage checks=%0d",checks);
        $display("SPARSE_RF_BOUNDARIES_PASS checks=33");$finish;
    end
endmodule
'''
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_sparse_records_boundaries.sv';p.write_text(render());print(p)
