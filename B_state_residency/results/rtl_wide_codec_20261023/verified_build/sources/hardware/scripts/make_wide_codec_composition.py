"""Wire a new codec through exact clones of the frozen composition and tests.
Only module references change; baseline RTL, oracle and stimulus are immutable.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 variants={
 'hardware/rtl/record_backing_service_wide.sv':('hardware/rtl/record_backing_service.sv', [('module record_backing_service #(', 'module record_backing_service_wide #('),('scratch_page_codec codec(', 'scratch_page_codec_wide codec(')]),
 'hardware/rtl/memory_scratch_endpoint_wide.sv':('hardware/rtl/memory_scratch_endpoint.sv',[('module memory_scratch_endpoint #(', 'module memory_scratch_endpoint_wide #('),('record_backing_service #(', 'record_backing_service_wide #(')]),
 'hardware/tb/tb_scratch_page_codec_wide.sv':('hardware/tb/tb_scratch_page_codec.sv',[('module tb_scratch_page_codec;', 'module tb_scratch_page_codec_wide;'),('scratch_page_codec dut(.*);','scratch_page_codec_wide dut(.*);')]),
 'hardware/tb/tb_memory_endpoint_wide.sv':('hardware/tb/tb_memory_endpoint.sv',[('memory_endpoint_test','memory_endpoint_wide_test'),('memory_scratch_endpoint #(', 'memory_scratch_endpoint_wide #('),('module tb_memory_endpoint_small;', 'module tb_memory_endpoint_wide_small;'),('module tb_memory_endpoint_actual;', 'module tb_memory_endpoint_wide_actual;')]),
 'hardware/tb/tb_memory_endpoint_wide_profile.sv':('hardware/tb/tb_memory_endpoint_profile.sv',[('module tb_memory_endpoint_profile;', 'module tb_memory_endpoint_wide_profile;'),('memory_endpoint_test #(', 'memory_endpoint_wide_test #(')])}
 for dest,(src,replacements) in variants.items():
  p=ROOT/dest
  if p.exists():raise FileExistsError(p)
  text=(ROOT/src).read_text()
  for old,new in replacements:
   if old not in text:raise ValueError('Missing substitution '+old)
   text=text.replace(old,new)
  p.write_text(text)
if __name__=='__main__':main()
