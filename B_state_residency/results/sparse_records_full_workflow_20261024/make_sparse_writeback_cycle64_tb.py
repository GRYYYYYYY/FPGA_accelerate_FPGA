"""New unsigned64 replay clock; preserve audited signed32 pilot artifacts."""
from pathlib import Path
from make_sparse_writeback_retry_tb import render as retry_render
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=retry_render();assert s.count('integer cycle=0;')==1
 return s.replace('integer cycle=0;','longint unsigned cycle=0;').replace('sparse_writeback_checkpoint_retry','sparse_writeback_cycle64').replace('tb_sparse_writeback_retry_control','tb_sparse_writeback_cycle64_control')
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_sparse_writeback_cycle64.sv';p.write_text(render());print(p)
