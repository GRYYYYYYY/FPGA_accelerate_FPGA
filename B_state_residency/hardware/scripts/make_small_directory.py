"""Independent small-page directory variant, preserving authoritative owner checks."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate(s):
 s=s.replace('backing_frame_directory_retained','backing_frame_directory_small')
 s=s.replace('FRAMES=23405, INDEX_BITS=15, HASH_BITS=15','FRAMES=163840, INDEX_BITS=18, HASH_BITS=18')
 s=s.replace('// Cookie: slot[1:0], page[19:2], query[21:20], price[25:22], generation[41:26],\n// tx[57:42], kind[58] (0=writeback,1=refill), reserved[63:59]=0.', '// Cookie72: slot[4:0], owner[31:5], generation[47:32], tx[63:48],\n// kind[64], reserved[71:65]=0; owner={price4,query2,page21}.')
 # Expand each named storage/field exactly; avoid broad replacement of cookie slices.
 for a,b in [('[23:0] cmd_owner','[26:0] cmd_owner'),('[23:0] owner','[26:0] owner'),('[24:0] owners','[27:0] owners'),('[24:0] read_word','[27:0] read_word'),('[24:0] write_word','[27:0] write_word'),('[63:0] cmd_cookie','[71:0] cmd_cookie'),('[63:0] cookie','[71:0] cookie'),('[63:0] lease_cookie','[71:0] lease_cookie'),('[3:0] leased','[31:0] leased'),('[0:3]','[0:31]'),('wire [1:0] slot=cmd_cookie[1:0]','wire [4:0] slot=cmd_cookie[4:0]'),('cookie[1:0]','cookie[4:0]'),('cookie[25:2]','cookie[31:5]'),('cookie[57:42]','cookie[63:48]'),('cookie[63:59]','cookie[71:65]'),('cookie[58]','cookie[64]'),('read_word[23:0]','read_word[26:0]'),('read_word[24]','read_word[27]'),("{8'b0,cmd_owner}","{5'b0,cmd_owner}"),('(frame32<<10)+(frame32<<8)+(frame32<<6)','(frame32<<7)+(frame32<<6)'),('i<4;','i<32;')]:
  assert a in s,a;s=s.replace(a,b)
 a=s.index('    wire frame_leased=');b=s.index('    assign cmd_ready=',a)
 s=s[:a]+'''    wire [31:0] same_frame,failed;
    genvar slot_index;
    generate for(slot_index=0;slot_index<32;slot_index=slot_index+1)begin: lease_flags
        assign leased[slot_index]=lease_phase[slot_index]!=FREE;
        assign same_frame[slot_index]=leased[slot_index] && lease_frame[slot_index]==cmd_frame;
        assign failed[slot_index]=lease_phase[slot_index]==FAILED;
    end endgenerate
    wire frame_leased=|same_frame;
    assign any_fault=|failed;
'''+s[b:]
 return s
if __name__=='__main__':
 p=ROOT/'hardware/rtl/backing_frame_directory_small.sv';s=generate((ROOT/'hardware/rtl/backing_frame_directory_retained.sv').read_text())
 if p.exists():assert p.read_text()==s
 else:p.write_text(s)
