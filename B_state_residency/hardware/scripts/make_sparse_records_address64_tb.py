"""Compose unchanged high-base wrapper with audited sparse WB/RF testbenches."""
from pathlib import Path
import re
from make_sparse_records_tb import render as native_render
from make_address64_trace_tb import render as old_address_render
ROOT=Path(__file__).resolve().parents[2]
def wrap(s):
 s=s.replace('dut.','dut.core.').replace('memory_scratch_endpoint_small_staticcodec #(','memory_scratch_endpoint_address64 #(').replace('dut(.*);','dut(.m_awaddr(outer_awaddr),.m_araddr(outer_araddr),.*);')
 old=old_address_render();marker='    memory_scratch_endpoint_address64 #('
 insert=old[old.index('    localparam [63:0] BASE='):old.index(marker)]
 assert s.count(marker)==1;s=s.replace(marker,insert+marker,1)
 s=s.replace('$finish;', '''if(aw_carries==0 || ar_carries==0)$fatal(1,"carry not exercised");
        $display("SPARSE_RECORDS_ADDRESS64_PASS base=%h aw_carries=%0d ar_carries=%0d",BASE,aw_carries,ar_carries);$finish;''')
 return s

def render():
 base=native_render();pilot=base['tb_sparse_records_pilot.sv']
 pilot=re.sub(r'\nmodule tb_sparse_records_control;[^\n]*', '',pilot)
 pilot=wrap(pilot).replace('sparse_records_test','sparse_records_address64_test').replace('tb_sparse_records_','tb_sparse_records_address64_')
 stalls=base['tb_sparse_records_stalls.sv']
 # Reuse the bounded native FINISH protocol after the setup delay shifts phase.
 reference=base['tb_sparse_records_pilot.sv']
 task=reference[reference.index('    task automatic request('):reference.index('    task automatic simple(')]
 old=stalls[stalls.index('    task automatic request('):stalls.index('    task automatic simple(')]
 stalls=stalls.replace(old,task)
 stalls=stalls.replace('    localparam integer SMALL=1;','    localparam integer SMALL=1;\n    localparam integer TB_HASH=SMALL?2:15;\n    integer finish_retries=0;')
 stalls=stalls.replace('$finish;', '$display("FINISH_RETRY_COUNTS retries=%0d",finish_retries);$finish;')
 stalls=wrap(stalls).replace('tb_sparse_records_stalls','tb_sparse_records_address64_stalls')
 return {'tb_sparse_records_address64_pilot.sv':pilot,'tb_sparse_records_address64_stalls.sv':stalls}
if __name__=='__main__':
 for name,s in render().items():
  p=ROOT/'hardware/tb'/name;p.write_text(s);print(p)
