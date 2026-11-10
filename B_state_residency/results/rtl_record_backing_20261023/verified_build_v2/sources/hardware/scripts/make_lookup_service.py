"""Create versioned directory/service adding nonallocating owner lookup.
Original verified modules are never edited; each replacement must be unique.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def edit(s,old,new):
 if s.count(old)!=1:raise ValueError('Nonunique source '+old)
 return s.replace(old,new)
def main():
 d=ROOT/'hardware/rtl';s=(d/'backing_frame_directory.sv').read_text()
 replacements=[('module backing_frame_directory #(', 'module backing_frame_directory_lookup #('),
 ('RETIRE=3,RECYCLE=4;', 'RETIRE=3,RECYCLE=4,LOOKUP=5;'),
 ('reg tx_used;reg [15:0] last_tx;', 'reg tx_used;reg [15:0] last_tx;reg lookup_only;'),
 ('tx_used<=0;last_tx<=0;index<=0;', 'tx_used<=0;last_tx<=0;lookup_only<=0;index<=0;'),
 ('else if(allocated<FRAMES)state<=ALLOCATE;', 'else if(lookup_only)begin rsp_valid<=1;rsp_status<=UNREADY;state<=IDLE;end\n                    else if(allocated<FRAMES)state<=ALLOCATE;'),
 ('RESERVE:begin owner<=cmd_owner;index<=0;rsp_valid<=0;state<=allocated==0?ALLOCATE:SCAN_READ;end',
 '''RESERVE,LOOKUP:begin
                        owner<=cmd_owner;index<=0;lookup_only<=cmd_op==LOOKUP;
                        if(cmd_op==LOOKUP && allocated==0)rsp_status<=UNREADY;
                        else begin rsp_valid<=0;state<=allocated==0?ALLOCATE:SCAN_READ;end
                    end''')]
 for a,b in replacements:s=edit(s,a,b)
 s=s.replace('// BRAM owner directory.', '// LOOKUP opcode5 returns UNREADY on miss without changing allocation or leases.\n// BRAM owner directory.',1)
 p=d/'backing_frame_directory_lookup.sv'
 if p.exists():raise FileExistsError(p)
 p.write_text(s)
 s=(d/'backing_page_service.sv').read_text()
 replacements=[('module backing_page_service #(', 'module backing_page_service_lookup #('),
 ('input wire [1:0] cmd_op', 'input wire [2:0] cmd_op'),
 ('backing_frame_directory #(', 'backing_frame_directory_lookup #('),
 ('if(cmd_op==1 && fault)', 'if(cmd_op>4)begin rsp_valid<=1;rsp_status<=3;end\n                else if(cmd_op==1 && fault)'),
 ('case(cmd_op)0:dir_op<=0;1:dir_op<=1;2:dir_op<=3;3:dir_op<=4;endcase', 'case(cmd_op)0:dir_op<=0;1:dir_op<=1;2:dir_op<=3;3:dir_op<=4;4:dir_op<=5;default:dir_op<=7;endcase')]
 for a,b in replacements:s=edit(s,a,b)
 s=s.replace('// cmd 0=reserve owner', '// cmd4=lookup owner without allocation (UNREADY on miss); 5..7 invalid.\n// cmd 0=reserve owner',1)
 p=d/'backing_page_service_lookup.sv'
 if p.exists():raise FileExistsError(p)
 p.write_text(s)
if __name__=='__main__':main()
