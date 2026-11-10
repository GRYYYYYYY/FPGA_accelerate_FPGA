from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/authority_query_v4/sources/query_lifecycle.sv')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
PORTS=''' input wire[63:0]active_generation,
 input wire cp_valid,cp_restore,cp_safe,output wire cp_ready,cp_busy,
 input wire[31:0]cp_expected_crc,output wire cp_rsp_valid,input wire cp_rsp_ready,output reg[3:0]cp_status,output reg[31:0]cp_crc,
 input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
 output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,
'''
def make():
 s=BASE.read_text();s=rep(s,' input wire clk,rst,abort,admit,backend_fault,backend_drained,active,host_label_edit,',' input wire clk,rst,abort,admit,backend_fault,backend_drained,active,host_label_edit,\n'+PORTS)
 s=rep(s,'assign busy=!rst&&owned;', 'assign busy=!rst&&(owned||cp_busy);')
 s=rep(s,'assign cmd_ready=!rst&&state==IDLE', 'assign cmd_ready=!rst&&!cp_busy&&!cp_valid&&state==IDLE')
 helper='''
 localparam CP_IDLE=0,CP_LOAD=1,CP_CHECK=2,CP_SEND=3,CP_DONE=4;
 reg[2:0]cp_state;reg[3:0]cp_pos;reg[31:0]cp_stage[0:9];reg[31:0]cp_running,cp_wanted,cp_ctx_version;
 reg[63:0]cp_ctx_design,cp_ctx_generation;reg[1:0]cp_ctx_query;reg[3:0]cp_ctx_price;reg cp_importing,cp_failed;
 wire cp_drift=!active||!cp_safe||!backend_drained||host_label_edit||active_design!=cp_ctx_design||active_generation!=cp_ctx_generation||active_version!=cp_ctx_version||active_query!=cp_ctx_query||active_price!=cp_ctx_price;
 wire cp_bad=cp_stage[0]!=32'h51435031||cp_stage[1]!=1||{cp_stage[3],cp_stage[2]}!=cp_ctx_design||{cp_stage[5],cp_stage[4]}!=cp_ctx_generation||cp_stage[6]!=cp_ctx_version||cp_stage[7][31:8]!=0||cp_stage[7][1:0]!=cp_ctx_query||cp_stage[7][5:2]!=cp_ctx_price||cp_stage[9]!=0||(cp_stage[7][6]?(cp_stage[8]==0):(cp_stage[8]!=0));
 function automatic[31:0]cp_crc_word(input[31:0]crc,word);reg[31:0]v;begin v=crc^word;for(integer k=0;k<32;k=k+1)v=v[0]?(v>>1)^32'hedb88320:v>>1;cp_crc_word=v;end endfunction
 assign cp_ready=!rst&&cp_state==CP_IDLE&&state==IDLE&&!stopped&&!abort&&!backend_fault&&backend_drained&&active&&cp_safe&&!service_rsp_valid&&!search_rsp_valid&&!route_rsp_valid;
 assign cp_busy=!rst&&cp_state!=CP_IDLE;
 assign cp_rsp_valid=!rst&&cp_state==CP_DONE;
 assign cp_s_ready=!rst&&cp_state==CP_LOAD&&!cp_failed&&!abort&&!backend_fault&&!cp_drift;
 assign cp_m_valid=!rst&&cp_state==CP_SEND;
 assign cp_m_index=cp_pos;assign cp_m_data=cp_stage[cp_pos];assign cp_m_last=cp_pos==9;
'''
 s=rep(s,' reg[447:0]v;',helper+'\n reg[447:0]v;')
 reset='''   cp_state<=CP_IDLE;cp_pos<=0;cp_running<=32'hffffffff;cp_wanted<=0;cp_ctx_version<=0;cp_ctx_design<=0;cp_ctx_generation<=0;cp_ctx_query<=0;cp_ctx_price<=0;cp_importing<=0;cp_failed<=0;cp_status<=0;cp_crc<=0;
   for(integer k=0;k<10;k=k+1)cp_stage[k]<=0;
'''
 s=rep(s,'  if(rst)begin\n', '  if(rst)begin\n'+reset)
 cp='''   if(cp_busy&&(abort||backend_fault||cp_drift))cp_failed<=1;
   case(cp_state)
    CP_IDLE:if(cp_valid&&cp_ready)begin
     cp_ctx_design<=active_design;cp_ctx_generation<=active_generation;cp_ctx_version<=active_version;cp_ctx_query<=active_query;cp_ctx_price<=active_price;
     cp_running<=32'hffffffff;cp_wanted<=cp_expected_crc;cp_pos<=0;cp_importing<=cp_restore;cp_failed<=0;cp_status<=0;cp_crc<=0;
     if(active_design==0||active_generation==0||active_version==0)begin cp_status<=1;cp_state<=CP_DONE;end
     else if(cp_restore)cp_state<=CP_LOAD;
     else if(sequence_seen&&(last_design!=active_design||last_version!=active_version||last_query!=active_query||last_price!=active_price))begin cp_status<=1;cp_state<=CP_DONE;end
     else begin
      cp_stage[0]<=32'h51435031;cp_stage[1]<=1;cp_stage[2]<=active_design[31:0];cp_stage[3]<=active_design[63:32];cp_stage[4]<=active_generation[31:0];cp_stage[5]<=active_generation[63:32];cp_stage[6]<=active_version;
      cp_stage[7]<={24'd0,label_state_dirty,sequence_seen,active_price,active_query};cp_stage[8]<=sequence_seen?last_sequence:0;cp_stage[9]<=0;cp_state<=CP_CHECK;
     end
    end
    CP_LOAD:if(cp_failed||abort||backend_fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_s_valid&&cp_s_ready)begin
      if(cp_s_index!=cp_pos||cp_s_last!=(cp_pos==9))begin cp_status<=1;cp_state<=CP_DONE;end
      else begin
       cp_stage[cp_pos]<=cp_s_data;cp_running<=cp_crc_word(cp_running,cp_s_data);
       if(cp_pos==9)begin cp_crc<=~cp_crc_word(cp_running,cp_s_data);cp_state<=CP_CHECK;end else cp_pos<=cp_pos+1;
      end
     end
    CP_CHECK:if(cp_failed||abort||backend_fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_bad||(cp_importing&&(~cp_running!=cp_wanted||(label_state_dirty&&!cp_stage[7][7])||(sequence_seen&&(!cp_stage[7][6]||cp_stage[8]<last_sequence)))))begin cp_status<=1;cp_state<=CP_DONE;end
     else if(!cp_importing)begin cp_pos<=0;cp_state<=CP_SEND;end
     else begin
      // Publish the complete anti-replay ledger in one edge; never partial state.
      sequence_seen<=cp_stage[7][6];label_state_dirty<=cp_stage[7][7];last_sequence<=cp_stage[8];last_design<=cp_stage[7][6]?cp_ctx_design:0;last_version<=cp_stage[7][6]?cp_ctx_version:0;last_query<=cp_stage[7][6]?cp_ctx_query:0;last_price<=cp_stage[7][6]?cp_ctx_price:0;
      cp_status<=0;cp_state<=CP_DONE;
     end
    CP_SEND:if(cp_m_ready)begin
     cp_running<=cp_crc_word(cp_running,cp_m_data);
     if(cp_pos==9)begin cp_crc<=~cp_crc_word(cp_running,cp_m_data);cp_status<=(cp_failed||abort||backend_fault||cp_drift)?2:0;cp_state<=CP_DONE;end else cp_pos<=cp_pos+1;
    end
    CP_DONE:if(cp_rsp_ready)cp_state<=CP_IDLE;
    default:begin cp_status<=2;cp_state<=CP_DONE;end
   endcase
'''
 s=rep(s,'   case(state)\n',cp+'   if(!cp_busy)case(state)\n')
 # An idle host write must not race with ledger publication; cp_drift rejects it.
 return s
if __name__=='__main__':(HERE/'query_lifecycle.sv').write_text(make())
