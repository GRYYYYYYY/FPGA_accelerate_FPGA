"""Derive a separate three-beat/72-bit-cookie AXI engine from frozen baseline."""
from pathlib import Path
import re,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def generate(source):
 s=source.replace('module scratch_page_axi(','module scratch_page_axi_small(')
 s=s.replace('21 x 512-bit','3 x 512-bit')
 for a,b in [('input wire [63:0] req_cookie','input wire [71:0] req_cookie'),('output reg [63:0] done_cookie','output reg [71:0] done_cookie'),("32'hfffffac0","32'hffffff40")]:
  assert s.count(a)==1;s=s.replace(a,b)
 s,n=re.subn(r'\b21\b','3',s);assert n==9,n
 return s
if __name__=='__main__':
 src=ROOT/'hardware/rtl/scratch_page_axi.sv';dst=ROOT/'hardware/rtl/scratch_page_axi_small.sv'
 result=generate(src.read_text())
 if dst.exists():assert dst.read_text()==result
 else:dst.write_text(result)
 print(hashlib.sha256(result.encode()).hexdigest())
