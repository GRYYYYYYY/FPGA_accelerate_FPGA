from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def make():
 s=runpy.run_path(str(ROOT/'hardware/variants/owner_g3_publish_v1/build_tb.py'))['make']()
 s=s.replace('cumulative_owner_snapshot #(.MAX_DIRTY(64)) g3_writer(', 'cumulative_owner_snapshot #(.MAX_DIRTY(64),.KEEP_RECEIPT_ON_BUSY(1)) g3_writer(',1)
 s=s.replace('.source_protocol_ok(!owner_watch_fault),', '.source_protocol_ok(!owner_watch_fault),.source_integrity_fault(abort||owner_watch_fault||f_fault||fault||rc_fault||k_fault||cf_fault||lr_fault||qc_fault||ss_fault),',1)
 s=s.replace('.selected_design(design_id),.selected_generation(64\'h100000003),.selected_checkpoint(32\'d19),.selected_version(query_version),.selected_query(p_active_query),.selected_price(p_active_price)', '.selected_design(system.jp_design),.selected_generation(system.jp_generation),.selected_checkpoint(system.jp_checkpoint),.selected_version(system.jp_version),.selected_query(system.jp_query),.selected_price(system.jp_price)',1)
 return s
if __name__=='__main__':(HERE/'tb_g3_fixed.sv').write_text(make())
