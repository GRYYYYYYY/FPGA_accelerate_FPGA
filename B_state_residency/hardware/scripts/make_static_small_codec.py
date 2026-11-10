"""Constant-slice alternative; preserve protocol and state transitions."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate(source):
 s=source.replace('module scratch_page_codec_small(','module scratch_page_codec_small_static(')
 a=' wire [159:0] selected=page[8+node*160 +:160];'
 b=' reg [159:0] selected;\n reg [511:0] selected_beat;\n always @* begin\n  selected=0;\n  case(node)\n'
 b+=''.join(f"   3'd{i}:selected=page[{8+i*160} +:160];\n" for i in range(8))
 b+='  endcase\n  selected_beat=0;\n  case(beat)\n'+''.join(f"   2'd{i}:selected_beat=page[{i*512} +:512];\n" for i in range(3))+'  endcase\n end'
 assert a in s;s=s.replace(a,b).replace('assign raw_out_data=page[beat*512 +:512];','assign raw_out_data=selected_beat;')
 a='page[node]<=record_in_present;page[8+node*160 +:160]<=record_in_payload;'
 b='case(node)\n'+''.join(f"       3'd{i}:begin page[{i}]<=record_in_present;page[{8+i*160} +:160]<=record_in_payload;end\n" for i in range(8))+'      endcase'
 assert a in s;s=s.replace(a,b)
 a='page[beat*512 +:512]<=raw_in_data;';b='case(beat)\n'+''.join(f"      2'd{i}:page[{i*512} +:512]<=raw_in_data;\n" for i in range(3))+'     endcase'
 assert a in s;s=s.replace(a,b);return s
if __name__=='__main__':
 src=ROOT/'hardware/rtl/scratch_page_codec_small.sv';dst=ROOT/'hardware/rtl/scratch_page_codec_small_static.sv';s=generate(src.read_text())
 if dst.exists():assert dst.read_text()==s
 else:dst.write_text(s)
