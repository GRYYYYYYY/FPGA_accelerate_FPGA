"""Vary queue/AXI periodic backpressure phase in paired 19-query pilots."""
from pathlib import Path
from make_sparse_records_tb import render as original
ROOT=Path(__file__).resolve().parents[2]
PHASES=(0,1,31)
def render():
 s=original()['tb_sparse_records_pilot.sv'];s=s[:s.index('\nmodule tb_sparse_records_small;')]
 s=s.replace('module sparse_records_test #(', 'module sparse_records_phase_test #(').replace('parameter integer SPARSE_WB=1,', 'parameter integer PHASE=0,SPARSE_WB=1,')
 assert s.count('cycle%')==8;s=s.replace('cycle%','(cycle+PHASE)%')
 for phase in PHASES:
  for label,flag in [('control',0),('candidate',1)]:
   s+=f'\nmodule tb_sparse_records_phase_{label}{phase};sparse_records_phase_test #(.PHASE({phase}),.SPARSE_WB(1),.SPARSE_RF({flag})) test();endmodule\n'
 return s
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_sparse_records_phases.sv';p.write_text(render());print(p)
