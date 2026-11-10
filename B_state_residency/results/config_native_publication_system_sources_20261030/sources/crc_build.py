from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
BASE=Path('/tmp/B_state_residency_offer_20261025/runtime_label_snapshot_full_v3/sources')
PARENTS=['query_residency_system.sv','search_residency_system.sv','residency_system.sv']
def make():
 s=(BASE/'label_restore_controller.sv').read_text().replace('MAX_RECORDS=512,','MAX_RECORDS=512,CHECK_SOURCE_CRC=0,')
 s=s.replace(' input wire s_valid,', ' input wire[31:0]start_source_crc,output reg[31:0]rsp_source_crc,\n input wire s_valid,')
 s=s.replace(' localparam IDLE', ''' reg[31:0]running_crc,expected_crc;
 function[31:0]word_crc(input[31:0]c0,w);reg[31:0]c;integer j;begin c=c0;for(j=0;j<32;j=j+1)c=(c[0]^w[j])?((c>>1)^32'hedb88320):(c>>1);word_crc=c;end endfunction
 function[31:0]row_crc(input[31:0]c0,node,input[159:0]v);reg[31:0]c;integer j;begin c=word_crc(c0,node);for(j=0;j<5;j=j+1)c=word_crc(c,v[j*32+:32]);row_crc=c;end endfunction
 localparam IDLE''')
 s=s.replace('if(rst)begin state<=IDLE;',"if(rst)begin running_crc<=32'hffffffff;expected_crc<=0;rsp_source_crc<=0;state<=IDLE;")
 s=s.replace('elapsed<=0;rsp_cookie<=start_cookie;',"running_crc<=32'hffffffff;expected_crc<=start_source_crc;rsp_source_crc<=0;elapsed<=0;rsp_cookie<=start_cookie;")
 before='else begin rows[index]<={s_node,s_payload};node<=s_node;payload<=s_payload;field<=0;state<=WS;end'
 after='''else begin
      if(CHECK_SOURCE_CRC!=0)begin running_crc<=row_crc(running_crc,s_node,s_payload);rsp_source_crc<=~row_crc(running_crc,s_node,s_payload);end
      if(CHECK_SOURCE_CRC!=0&&s_last&&~row_crc(running_crc,s_node,s_payload)!=expected_crc)fail(8);
      else begin rows[index]<={s_node,s_payload};node<=s_node;payload<=s_payload;field<=0;state<=WS;end
     end'''
 assert s.count(before)==1;s=s.replace(before,after);(HERE/'label_restore_controller.sv').write_text(s)
 for n in PARENTS:
  s=(BASE/n).read_text();pos=s.index('#(')+2;s=s[:pos]+'parameter integer CHECK_LABEL_CRC=0,'+s[pos:]
  pos=s.index(');',s.index('input wire'));s=s[:pos].rstrip()+',input wire[31:0]snapshot_label_crc,output wire[31:0]lr_source_crc\n'+s[pos:]
  if n!='residency_system.sv':
   child='search_residency_system'if n=='query_residency_system.sv'else'residency_system'
   pos=re.search(r'\b'+child+r'\s*#\(',s).end();s=s[:pos]+'.CHECK_LABEL_CRC(CHECK_LABEL_CRC),'+s[pos:]
   pos=s.index('.snapshot_count(snapshot_count)',pos);s=s[:pos]+'.snapshot_label_crc(snapshot_label_crc),.lr_source_crc(lr_source_crc),'+s[pos:]
  else:
   s=s.replace('reg [31:0] snapshot_count_held;', 'reg [31:0] snapshot_count_held;reg[31:0]snapshot_label_crc_held;')
   s=s.replace('snapshot_count_held<=0;', 'snapshot_count_held<=0;snapshot_label_crc_held<=0;').replace('snapshot_count_held<=snapshot_count;', 'snapshot_count_held<=snapshot_count;snapshot_label_crc_held<=snapshot_label_crc;')
   s=s.replace('label_restore_controller #(.MAX_RECORDS(RESTORE_RECORDS),','label_restore_controller #(.MAX_RECORDS(RESTORE_RECORDS),.CHECK_SOURCE_CRC(CHECK_LABEL_CRC),')
   s=s.replace(')label_restore(.clk(clk)', ')label_restore(.start_source_crc(snapshot_label_crc_held),.rsp_source_crc(lr_source_crc),.clk(clk)')
  (HERE/n).write_text(s)
if __name__=='__main__':make()
