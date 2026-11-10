from pathlib import Path
from make_retained_stall_tb import generate as original
ROOT=Path(__file__).resolve().parents[2]
def generate():
 text=original();declaration='    reg [TB_TAG-1:0] blocked_tag;\n'
 assert text.count(declaration)==1
 text=text.replace(declaration,'')
 anchor='    localparam integer TB_TX=SMALL?3:16,TB_GEN=SMALL?3:16,TB_TAG=SMALL?1:2;\n'
 assert text.count(anchor)==1
 return text.replace(anchor,anchor+declaration).replace('module tb_retained_endpoint_stalls;','module tb_retained_endpoint_stalls_v2;')
if __name__=='__main__':(ROOT/'hardware/tb/tb_retained_endpoint_stalls_v2.sv').write_text(generate())
