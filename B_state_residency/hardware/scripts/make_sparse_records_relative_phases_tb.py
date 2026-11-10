"""Vary channel-relative phases, not only a common schedule time translation."""
from pathlib import Path
import re
from make_sparse_records_phase_tb import render as common_render,PHASES
ROOT=Path(__file__).resolve().parents[2]
WEIGHTS=(1,3,5,7,11,13,17,19) # dispatch, execute, fence, ACK, AW, W, AR, R issue

def render():
 s=common_render();assert s.count('(cycle+PHASE)%')==8
 weights=iter(WEIGHTS)
 s=re.sub(r'\(cycle\+PHASE\)%',lambda _:f'(cycle+{next(weights)}*PHASE)%',s)
 return s.replace('sparse_records_phase_test','sparse_records_relative_phase_test').replace('tb_sparse_records_phase_','tb_sparse_records_relative_phase_')
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_sparse_records_relative_phases.sv';p.write_text(render());print(p)
