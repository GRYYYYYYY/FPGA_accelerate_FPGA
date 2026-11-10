"""Derive small-page service layers without changing frozen retained baselines."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate(source,record=False):
 s=source.replace('record_backing_service_retained','record_backing_service_small').replace('backing_page_service_retained','backing_page_service_small').replace('backing_frame_directory_retained','backing_frame_directory_small')
 s=s.replace('FRAMES=23405,INDEX_BITS=15,HASH_BITS=15','FRAMES=163840,INDEX_BITS=18,HASH_BITS=18')
 for name in ['cmd_owner','owner']:s=s.replace('[23:0] '+name,'[26:0] '+name)
 for name in ['cmd_cookie','rsp_cookie','cookie','dma_cookie','service_cookie']:s=s.replace('[63:0] '+name,'[71:0] '+name)
 s=s.replace('[3:0] leased','[31:0] leased').replace('cookie[58]','cookie[64]')
 s=s.replace('scratch_page_axi dma','scratch_page_axi_small dma')
 if record:
  s=s.replace('scratch_page_codec_wide codec','scratch_page_codec_small codec')
  s=s.replace('[5:0] record_in_offset','[2:0] record_in_offset').replace('[5:0] record_out_offset','[2:0] record_out_offset')
  s=s.replace('// cmd4=lookup owner without allocation (UNREADY on miss); 5..7 invalid.', '// cmd4=lookup owner; cmd5=trusted retained-ID recycle; 6..7 invalid.')
 return s
if __name__=='__main__':
 for name,record in [('backing_page_service',False),('record_backing_service',True)]:
  src=ROOT/'hardware/rtl'/f'{name}_retained.sv';dst=ROOT/'hardware/rtl'/f'{name}_small.sv';s=generate(src.read_text(),record)
  if dst.exists():assert dst.read_text()==s
  else:dst.write_text(s)
