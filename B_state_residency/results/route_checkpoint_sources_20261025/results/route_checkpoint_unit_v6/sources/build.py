"""Atomic saved-route checkpoint port, derived from frozen production controller."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=ROOT/'results/recovery_retry_normal_v1/sources/route_commit_controller.sv'
def rep(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def make():
 s=BASE.read_text()
 ports=''' input wire cp_valid,output wire cp_ready,input wire cp_restore,cp_safe,
 input wire[63:0]cp_design,input wire[31:0]cp_nodes,cp_nets,cp_expected_crc,
 output wire cp_busy,output wire cp_rsp_valid,input wire cp_rsp_ready,
 output reg[3:0]cp_status,output reg[31:0]cp_crc,
 input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
 output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,
'''
 s=rep(s,' input wire clk,rst,abort,active,lease,',' input wire clk,rst,abort,active,lease,\n'+ports)
 s=rep(s,'assign busy=!rst&&(owned||state!=IDLE||rsp_valid);','assign busy=!rst&&(owned||state!=IDLE||rsp_valid||cp_busy);')
 s=rep(s,'assign req_ready=!rst&&!fault&&!busy&&active&&lease;', 'assign req_ready=!rst&&!fault&&!busy&&!cp_valid&&active&&lease;')
 helper='''
 // Canonical two-slot image: valid,size,net,source,sink,design-lo,design-hi,
 // followed by MAX_PATH interior nodes, unused words zero. CRC32/IEEE LE.
 localparam CP_STRIDE=7+MAX_PATH,CP_WORDS=2*CP_STRIDE;
 localparam CP_IDLE=0,CP_EXPORT=1,CP_IMPORT=2,CP_VERIFY=3,CP_DONE=4;
 reg[2:0]cp_state;reg[31:0]cp_pos,cp_running,cp_wanted,cp_node_limit,cp_net_limit;
 reg[63:0]cp_context;reg cp_failed,cp_invalid,cp_importing,cp_check_slot;reg[$clog2(CP_STRIDE)-1:0]cp_check_field;reg[31:0]cp_stage[0:CP_WORDS-1];
 reg cp_bad;integer a,b,c;
 function automatic[31:0]crc_word(input[31:0]old_crc,input[31:0]word);
 reg[31:0]v;begin v=old_crc^word;for(integer z=0;z<32;z=z+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;crc_word=v;end endfunction
 wire cp_drift=!active||!lease||!cp_safe||active_design!=cp_context;
 assign cp_busy=!rst&&cp_state!=CP_IDLE;
 assign cp_ready=!rst&&cp_state==CP_IDLE&&!owned&&state==IDLE&&!rsp_valid&&!fault&&active&&lease&&cp_safe&&!l_rsp_valid&&!o_rsp_valid;
 assign cp_rsp_valid=!rst&&cp_state==CP_DONE;
 assign cp_s_ready=!rst&&cp_state==CP_IMPORT&&!cp_failed&&!abort&&!fault&&!cp_drift;
 assign cp_m_valid=!rst&&cp_state==CP_EXPORT;
 assign cp_m_index=cp_pos;assign cp_m_data=cp_stage[cp_pos];assign cp_m_last=cp_pos+1==CP_WORDS;
 wire[31:0]cp_scan_word=cp_check_slot?cp_stage[CP_STRIDE+cp_check_field]:cp_stage[cp_check_field];
 always @*begin
  cp_bad=0;
  if((cp_check_slot?cp_stage[CP_STRIDE]:cp_stage[0])>1)cp_bad=1;
  if((cp_check_slot?cp_stage[CP_STRIDE]:cp_stage[0])==0)begin
   if(cp_scan_word!=0)cp_bad=1;
  end else begin
   if((cp_check_slot?cp_stage[CP_STRIDE+1]:cp_stage[1])>MAX_PATH||(cp_check_slot?cp_stage[CP_STRIDE+2]:cp_stage[2])>=cp_net_limit||(cp_check_slot?cp_stage[CP_STRIDE+3]:cp_stage[3])>=cp_node_limit||(cp_check_slot?cp_stage[CP_STRIDE+4]:cp_stage[4])>=cp_node_limit||{(cp_check_slot?cp_stage[CP_STRIDE+6]:cp_stage[6]),(cp_check_slot?cp_stage[CP_STRIDE+5]:cp_stage[5])}!=cp_context)cp_bad=1;
   if(cp_check_field>=7)begin
    if(cp_check_field-7<(cp_check_slot?cp_stage[CP_STRIDE+1]:cp_stage[1]))begin
     if(cp_scan_word>=cp_node_limit||cp_scan_word==(cp_check_slot?cp_stage[CP_STRIDE+3]:cp_stage[3])||cp_scan_word==(cp_check_slot?cp_stage[CP_STRIDE+4]:cp_stage[4]))cp_bad=1;
     for(integer z=0;z<MAX_PATH;z=z+1)if(z<cp_check_field-7&&cp_scan_word==(cp_check_slot?cp_stage[CP_STRIDE+7+z]:cp_stage[7+z]))cp_bad=1;
    end else if(cp_scan_word!=0)cp_bad=1;
   end
  end
 end
'''
 s=rep(s,' always @(posedge clk)begin',helper+'\n always @(posedge clk)begin')
 s=rep(s,'   state<=IDLE;owned<=0;', "   cp_invalid<=0;cp_importing<=0;cp_check_slot<=0;cp_check_field<=0;cp_state<=CP_IDLE;cp_pos<=0;cp_running<=32'hffffffff;cp_wanted<=0;cp_node_limit<=0;cp_net_limit<=0;cp_context<=0;cp_failed<=0;cp_status<=0;cp_crc<=0;\n   state<=IDLE;owned<=0;")
 actions='''
   if(cp_busy&&(abort||fault||cp_drift))cp_failed<=1;
   case(cp_state)
    CP_IDLE:if(cp_valid&&cp_ready)begin
     cp_context<=cp_design;cp_node_limit<=cp_nodes;cp_net_limit<=cp_nets;cp_wanted<=cp_expected_crc;
     cp_invalid<=0;cp_check_slot<=0;cp_check_field<=0;cp_importing<=cp_restore;cp_pos<=0;cp_running<=32'hffffffff;cp_crc<=0;cp_status<=0;cp_failed<=0;
     if(cp_design!=active_design||cp_nodes==0||cp_nets==0)begin cp_status<=1;cp_state<=CP_DONE;end
     else if(cp_restore)cp_state<=CP_IMPORT;
     else begin
      for(a=0;a<2;a=a+1)begin
       cp_stage[a*CP_STRIDE]<=slot_valid[a]?1:0;
       cp_stage[a*CP_STRIDE+1]<=slot_valid[a]?sizes[a]:0;
       cp_stage[a*CP_STRIDE+2]<=slot_valid[a]?nets[a]:0;
       cp_stage[a*CP_STRIDE+3]<=slot_valid[a]?sources[a]:0;
       cp_stage[a*CP_STRIDE+4]<=slot_valid[a]?sinks[a]:0;
       cp_stage[a*CP_STRIDE+5]<=slot_valid[a]?designs[a][31:0]:0;
       cp_stage[a*CP_STRIDE+6]<=slot_valid[a]?designs[a][63:32]:0;
       for(b=0;b<MAX_PATH;b=b+1)cp_stage[a*CP_STRIDE+7+b]<=slot_valid[a]&&b<sizes[a]?path[a][b]:0;
      end
      cp_state<=CP_VERIFY;
     end
    end
    CP_EXPORT:if(cp_m_ready)begin
     cp_running<=crc_word(cp_running,cp_m_data);
     if(cp_m_last)begin cp_crc<=~crc_word(cp_running,cp_m_data);cp_status<=(cp_failed||abort||fault||cp_drift)?2:0;cp_state<=CP_DONE;end
     else cp_pos<=cp_pos+1;
    end
    CP_IMPORT:if(cp_failed||abort||fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_s_valid&&cp_s_ready)begin
      if(cp_s_index!=cp_pos||cp_s_last!=(cp_pos+1==CP_WORDS))begin cp_status<=1;cp_state<=CP_DONE;end
      else begin cp_stage[cp_pos]<=cp_s_data;cp_running<=crc_word(cp_running,cp_s_data);
       if(cp_s_last)begin cp_crc<=~crc_word(cp_running,cp_s_data);cp_state<=CP_VERIFY;end
       else cp_pos<=cp_pos+1;
      end
     end
    CP_VERIFY:begin
     if(cp_bad)cp_invalid<=1;
     if(cp_failed||abort||fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_check_slot&&cp_check_field+1==CP_STRIDE)begin
      if(cp_invalid||cp_bad||(cp_importing&&~cp_running!=cp_wanted))begin cp_status<=1;cp_state<=CP_DONE;end
      else if(!cp_importing)begin cp_pos<=0;cp_state<=CP_EXPORT;end
      else begin
       cp_state<=CP_DONE;
       for(a=0;a<2;a=a+1)begin
        slot_valid[a]<=cp_stage[a*CP_STRIDE][0];sizes[a]<=cp_stage[a*CP_STRIDE+1];nets[a]<=cp_stage[a*CP_STRIDE+2];sources[a]<=cp_stage[a*CP_STRIDE+3];sinks[a]<=cp_stage[a*CP_STRIDE+4];designs[a]<={cp_stage[a*CP_STRIDE+6],cp_stage[a*CP_STRIDE+5]};
        for(b=0;b<MAX_PATH;b=b+1)path[a][b]<=cp_stage[a*CP_STRIDE+7+b];
       end
      end
     end else if(cp_check_field+1==CP_STRIDE)begin cp_check_slot<=1;cp_check_field<=0;end
     else cp_check_field<=cp_check_field+1;
    end
    CP_DONE:if(cp_rsp_ready)cp_state<=CP_IDLE;
    default:begin cp_status<=2;cp_state<=CP_DONE;end
   endcase
'''
 s=rep(s,'   case(state)',actions+'\n   if(!cp_busy)case(state)')
 return s
if __name__=='__main__':(HERE/'route_commit_controller.sv').write_text(make())
