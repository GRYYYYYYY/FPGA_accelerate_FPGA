"""Compose sparse WB/RF representation checks with real 16-bit epoch wrap."""
from pathlib import Path
from make_sparse_writeback_tb import adapt
from make_sparse_records_tb import adapt_rf
ROOT=Path(__file__).resolve().parents[2]
def render():
 s=(ROOT/'hardware/tb/tb_record_epoch16_wrap.sv').read_text()
 return adapt_rf(adapt(s)).replace('tb_record_epoch16_wrap','tb_sparse_records_wrap').replace('response_fault_test','sparse_records_wrap_test')
if __name__=='__main__':
 p=ROOT/'hardware/tb/tb_sparse_records_wrap.sv';p.write_text(render());print(p)
