`timescale 1ns/1ps
// One exclusive lease, bounded saved connection paths, registered backends.
module route_commit_controller #(parameter integer FACTORED_STAGE_WRITES=0,FACTORED_PATH_WRITES=0,PATH_SLOTS=2,PATH_SLOT_BITS=(PATH_SLOTS<=2?1:$clog2(PATH_SLOTS)),MAX_PATH=32,MAX_CYCLES=1048576)(
 input wire clk,rst,abort,active,lease,
 input wire cp_valid,output wire cp_ready,input wire cp_restore,cp_safe,
 input wire[63:0]cp_design,input wire[31:0]cp_nodes,cp_nets,cp_expected_crc,
 output wire cp_busy,output wire cp_rsp_valid,input wire cp_rsp_ready,
 output reg[3:0]cp_status,output reg[31:0]cp_crc,
 input wire cp_s_valid,output wire cp_s_ready,input wire[31:0]cp_s_index,cp_s_data,input wire cp_s_last,
 output wire cp_m_valid,input wire cp_m_ready,output wire[31:0]cp_m_index,cp_m_data,output wire cp_m_last,

 input wire[1:0]active_query,input wire[3:0]active_price,input wire[31:0]active_version,input wire[63:0]active_design,
 input wire req_valid,output wire req_ready,input wire req_op,input wire[PATH_SLOT_BITS-1:0]req_slot,
 input wire[31:0]req_cookie,req_source,req_sink,req_net,req_sequence,
 output reg rsp_valid,input wire rsp_ready,output reg[3:0]rsp_status,
 output reg[31:0]rsp_cookie,rsp_nodes,rsp_acked,output wire busy,fault,idle_fault,output reg[PATH_SLOTS-1:0]slot_valid,
 output wire l_valid,input wire l_ready,output wire[31:0]l_node,
 input wire l_rsp_valid,output wire l_rsp_ready,input wire[3:0]l_status,input wire l_present,input wire[159:0]l_payload,
 output wire o_valid,input wire o_ready,output wire[2:0]o_op,output wire[31:0]o_node,o_net,o_cookie,
 input wire o_rsp_valid,output wire o_rsp_ready,input wire[3:0]o_status,input wire[31:0]o_rsp_cookie
);
 localparam IDLE=0,LS=1,LW=2,OS=3,OW=4;
 reg[2:0]state;reg owned,stopped,operation;reg[PATH_SLOT_BITS-1:0]slot;reg[3:0]error_code;
 reg[31:0]source,sink,net,sequence_id,current,length,index,elapsed;
 reg[1:0]q;reg[3:0]price;reg[31:0]version;reg[63:0]ctx_design;
 reg[31:0]path[0:PATH_SLOTS-1][0:MAX_PATH-1];reg[31:0]sizes[0:PATH_SLOTS-1],nets[0:PATH_SLOTS-1],sources[0:PATH_SLOTS-1],sinks[0:PATH_SLOTS-1];
 reg[63:0]designs[0:PATH_SLOTS-1];
 integer i;reg duplicate;
 always @* begin duplicate=0;for(integer k=0;k<MAX_PATH;k=k+1)if(k<length&&path[slot][k]==current)duplicate=1;end
 wire drift=owned&&(!active||!lease||q!=active_query||price!=active_price||version!=active_version||ctx_design!=active_design);
 wire timed_out=owned&&!rsp_valid&&!stopped&&elapsed>=MAX_CYCLES-1;
 wire bad_l=state==LW&&l_rsp_valid&&(l_status!=0||!l_present);
 wire bad_o=state==OW&&o_rsp_valid&&(o_status!=0||o_rsp_cookie!=rsp_cookie);
 wire unexpected=(l_rsp_valid&&state!=LW&&!(state==LS&&l_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));
 wire fail_now=abort||drift||timed_out||bad_l||bad_o||unexpected;
 // This reduced term is for the host adapter's !held && !busy branch only.
 // Full fault below retains unexpected responses, drift, timeout and errors.
 assign idle_fault=!rst&&(stopped||abort);
 assign fault=!rst&&(stopped||fail_now);
 assign busy=!rst&&(owned||state!=IDLE||rsp_valid||cp_busy);
 assign req_ready=!rst&&!fault&&!busy&&!cp_valid&&active&&lease;
 // Preserve every exposed request through backpressure, including on failure.
 assign l_valid=!rst&&state==LS;assign l_node=current;assign l_rsp_ready=!rst&&state==LW;
 assign o_valid=!rst&&state==OS;assign o_op=operation?3'd2:3'd1;
 assign o_node=path[slot][index];assign o_net=net;assign o_cookie=rsp_cookie;assign o_rsp_ready=!rst&&state==OW;
 task finish(input[3:0]status);begin rsp_status<=status;rsp_valid<=1;state<=IDLE;rsp_nodes<=length;end endtask
 task fatal_finish(input[3:0]status);begin stopped<=1;error_code<=status;finish(status);end endtask

 // Canonical PATH_SLOTS-slot image (default two-slot bytes unchanged): valid,size,net,source,sink,design-lo,design-hi,
 // followed by MAX_PATH interior nodes, unused words zero. CRC32/IEEE LE.
 localparam CP_STRIDE=7+MAX_PATH,CP_WORDS=PATH_SLOTS*CP_STRIDE;
 localparam CP_IDLE=0,CP_EXPORT=1,CP_IMPORT=2,CP_VERIFY=3,CP_DONE=4,CP_DUP=5;
 reg[2:0]cp_state;reg[31:0]cp_pos,cp_running,cp_wanted,cp_node_limit,cp_net_limit;
 reg[63:0]cp_context;reg[$clog2(MAX_PATH+1)-1:0]cp_dup_pos;reg cp_failed,cp_invalid,cp_importing;reg[PATH_SLOT_BITS-1:0]cp_check_slot;reg[$clog2(CP_STRIDE)-1:0]cp_check_field;reg[31:0]cp_stage[0:CP_WORDS-1];
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
 always @*begin
  cp_bad=0;
  if(cp_stage[cp_check_slot*CP_STRIDE]>1)cp_bad=1;
  if(cp_stage[cp_check_slot*CP_STRIDE]==0)begin
   if(cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]!=0)cp_bad=1;
  end else begin
   if(cp_stage[cp_check_slot*CP_STRIDE+1]>MAX_PATH||cp_stage[cp_check_slot*CP_STRIDE+2]>=cp_net_limit||cp_stage[cp_check_slot*CP_STRIDE+3]>=cp_node_limit||cp_stage[cp_check_slot*CP_STRIDE+4]>=cp_node_limit||{cp_stage[cp_check_slot*CP_STRIDE+6],cp_stage[cp_check_slot*CP_STRIDE+5]}!=cp_context)cp_bad=1;
   if(cp_check_field>=7)begin
    if(cp_check_field-7<cp_stage[cp_check_slot*CP_STRIDE+1])begin
     if(cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]>=cp_node_limit||cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]==cp_stage[cp_check_slot*CP_STRIDE+3]||cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]==cp_stage[cp_check_slot*CP_STRIDE+4])cp_bad=1;

    end else if(cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]!=0)cp_bad=1;
   end
  end
 end
 task cp_advance;begin
  if(cp_check_slot==PATH_SLOTS-1&&cp_check_field+1==CP_STRIDE)begin
   if(cp_importing&&~cp_running!=cp_wanted)begin cp_status<=1;cp_state<=CP_DONE;end
   else if(!cp_importing)begin cp_pos<=0;cp_state<=CP_EXPORT;end
   else begin
    cp_state<=CP_DONE;
    for(a=0;a<PATH_SLOTS;a=a+1)begin
     slot_valid[a]<=cp_stage[a*CP_STRIDE][0];sizes[a]<=cp_stage[a*CP_STRIDE+1];nets[a]<=cp_stage[a*CP_STRIDE+2];sources[a]<=cp_stage[a*CP_STRIDE+3];sinks[a]<=cp_stage[a*CP_STRIDE+4];designs[a]<={cp_stage[a*CP_STRIDE+6],cp_stage[a*CP_STRIDE+5]};
     if(FACTORED_PATH_WRITES==0)for(b=0;b<MAX_PATH;b=b+1)path[a][b]<=cp_stage[a*CP_STRIDE+7+b];
    end
   end
  end else begin
   cp_state<=CP_VERIFY;
   if(cp_check_field+1==CP_STRIDE)begin cp_check_slot<=cp_check_slot+1'b1;cp_check_field<=0;end
   else cp_check_field<=cp_check_field+1;
  end
 end endtask

 always @(posedge clk)begin
  if(rst)begin
   cp_dup_pos<=0;cp_invalid<=0;cp_importing<=0;cp_check_slot<=0;cp_check_field<=0;cp_state<=CP_IDLE;cp_pos<=0;cp_running<=32'hffffffff;cp_wanted<=0;cp_node_limit<=0;cp_net_limit<=0;cp_context<=0;cp_failed<=0;cp_status<=0;cp_crc<=0;
   state<=IDLE;owned<=0;stopped<=0;operation<=0;slot<=0;error_code<=0;slot_valid<=0;
   source<=0;sink<=0;net<=0;sequence_id<=0;current<=0;length<=0;index<=0;elapsed<=0;
   q<=0;price<=0;version<=0;ctx_design<=0;rsp_valid<=0;rsp_status<=0;rsp_cookie<=0;rsp_nodes<=0;rsp_acked<=0;
   for(i=0;i<PATH_SLOTS;i=i+1)begin sizes[i]<=0;nets[i]<=0;sources[i]<=0;sinks[i]<=0;designs[i]<=0;end
  end else begin
   if(rsp_valid&&rsp_ready)begin rsp_valid<=0;owned<=0;end
   if(owned&&!rsp_valid&&!stopped)elapsed<=elapsed+1'b1;
   if(fail_now&&!stopped)begin stopped<=1;error_code<=bad_l?4:bad_o?5:6;end

   if(cp_busy&&(abort||fault||cp_drift))cp_failed<=1;
   case(cp_state)
    CP_IDLE:if(cp_valid&&cp_ready)begin
     cp_context<=cp_design;cp_node_limit<=cp_nodes;cp_net_limit<=cp_nets;cp_wanted<=cp_expected_crc;
     cp_invalid<=0;cp_check_slot<=0;cp_check_field<=0;cp_importing<=cp_restore;cp_pos<=0;cp_running<=32'hffffffff;cp_crc<=0;cp_status<=0;cp_failed<=0;
     if(cp_design!=active_design||cp_nodes==0||cp_nets==0)begin cp_status<=1;cp_state<=CP_DONE;end
     else if(cp_restore)cp_state<=CP_IMPORT;
     else begin
      if(FACTORED_STAGE_WRITES==0)begin
      for(a=0;a<PATH_SLOTS;a=a+1)begin
       cp_stage[a*CP_STRIDE]<=slot_valid[a]?1:0;
       cp_stage[a*CP_STRIDE+1]<=slot_valid[a]?sizes[a]:0;
       cp_stage[a*CP_STRIDE+2]<=slot_valid[a]?nets[a]:0;
       cp_stage[a*CP_STRIDE+3]<=slot_valid[a]?sources[a]:0;
       cp_stage[a*CP_STRIDE+4]<=slot_valid[a]?sinks[a]:0;
       cp_stage[a*CP_STRIDE+5]<=slot_valid[a]?designs[a][31:0]:0;
       cp_stage[a*CP_STRIDE+6]<=slot_valid[a]?designs[a][63:32]:0;
       for(b=0;b<MAX_PATH;b=b+1)cp_stage[a*CP_STRIDE+7+b]<=slot_valid[a]&&b<sizes[a]?path[a][b]:0;
      end
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
      else begin if(FACTORED_STAGE_WRITES==0)cp_stage[cp_pos]<=cp_s_data;cp_running<=crc_word(cp_running,cp_s_data);
       if(cp_s_last)begin cp_crc<=~crc_word(cp_running,cp_s_data);cp_state<=CP_VERIFY;end
       else cp_pos<=cp_pos+1;
      end
     end
    CP_VERIFY:begin
     if(cp_failed||abort||fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_bad)begin cp_status<=1;cp_state<=CP_DONE;end
     else if(cp_stage[cp_check_slot*CP_STRIDE]==1&&cp_check_field>7&&cp_check_field-7<cp_stage[cp_check_slot*CP_STRIDE+1])begin cp_dup_pos<=0;cp_state<=CP_DUP;end
     else cp_advance;
    end
    CP_DUP:begin
     if(cp_failed||abort||fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end
     else if(cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]==cp_stage[cp_check_slot*CP_STRIDE+7+cp_dup_pos])begin cp_status<=1;cp_state<=CP_DONE;end
     else if(cp_dup_pos+1==cp_check_field-7)cp_advance;
     else cp_dup_pos<=cp_dup_pos+1;
    end
    CP_DONE:if(cp_rsp_ready)cp_state<=CP_IDLE;
    default:begin cp_status<=2;cp_state<=CP_DONE;end
   endcase

   if(!cp_busy)case(state)
    IDLE:if(req_valid&&req_ready)begin
     owned<=1;operation<=req_op;slot<=req_slot;source<=req_source;sink<=req_sink;net<=req_net;sequence_id<=req_sequence;
     q<=active_query;price<=active_price;version<=active_version;ctx_design<=active_design;
     rsp_cookie<=req_cookie;rsp_status<=0;rsp_nodes<=0;rsp_acked<=0;elapsed<=0;length<=0;index<=0;
     if(req_slot>=PATH_SLOTS)begin rsp_status<=1;rsp_valid<=1;end
     else if((!req_op&&slot_valid[req_slot])||(req_op&&(!slot_valid[req_slot]||nets[req_slot]!=req_net||sources[req_slot]!=req_source||sinks[req_slot]!=req_sink||designs[req_slot]!=active_design)))begin rsp_status<=1;rsp_valid<=1;end
     else if(req_op)begin
      length<=sizes[req_slot];
      if(sizes[req_slot]==0)begin slot_valid[req_slot]<=0;rsp_valid<=1;end else state<=OS;
     end else begin current<=req_sink;state<=LS;end
    end
    LS:if(l_ready)state<=LW;
    LW:if(l_rsp_valid)begin
     if(stopped||fail_now)finish(stopped?error_code:(bad_l?4:6));
     else if((current==sink&&(l_payload[128]!=1||l_payload[127:96]!=sequence_id))||duplicate)fatal_finish(2);
     else if(current==source)begin
      if(l_payload[95:64]!=32'hffffffff)fatal_finish(2);
      else if(length==0)begin slot_valid[slot]<=1;sizes[slot]<=0;nets[slot]<=net;sources[slot]<=source;sinks[slot]<=sink;designs[slot]<=ctx_design;finish(0);end
      else begin index<=0;state<=OS;end
     end else if(l_payload[95:64]==32'hffffffff||l_payload[95:64]==sink||current==32'hffffffff)fatal_finish(2);
     else if(current!=sink&&length==MAX_PATH)fatal_finish(3);
     else begin
      if(current!=sink)begin if(FACTORED_PATH_WRITES==0)path[slot][length]<=current;length<=length+1'b1;end
      current<=l_payload[95:64];state<=LS;
     end
    end
    OS:if(o_ready)state<=OW;
    OW:if(o_rsp_valid)begin
     // Count only confirmed successful modifications, even after late abort.
     if(o_status==0&&o_rsp_cookie==rsp_cookie)rsp_acked<=rsp_acked+1'b1;
     if(stopped||fail_now)finish(stopped?error_code:(bad_o?5:6));
     else if(index+1==length)begin
      if(operation)slot_valid[slot]<=0;
      else begin slot_valid[slot]<=1;sizes[slot]<=length;nets[slot]<=net;sources[slot]<=source;sinks[slot]<=sink;designs[slot]<=ctx_design;end
      finish(0);
     end else begin index<=index+1'b1;state<=OS;end
    end
    default:fatal_finish(6);
   endcase
  end
 end
 // Same-cycle publication qualifiers, including all original validation gates.
 wire pw_cancel=cp_failed||abort||fault||cp_drift;
 wire pw_verify_advance=cp_state==CP_VERIFY&&!cp_bad&&!(cp_stage[cp_check_slot*CP_STRIDE]==1&&cp_check_field>7&&cp_check_field-7<cp_stage[cp_check_slot*CP_STRIDE+1]);
 wire pw_dup_advance=cp_state==CP_DUP&&cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]!=cp_stage[cp_check_slot*CP_STRIDE+7+cp_dup_pos]&&cp_dup_pos+1==cp_check_field-7;
 wire pw_cp_write=!rst&&!pw_cancel&&(pw_verify_advance||pw_dup_advance)&&cp_check_slot==PATH_SLOTS-1&&cp_check_field+1==CP_STRIDE&&cp_importing&&~cp_running==cp_wanted;
 wire pw_node_write=!rst&&!cp_busy&&state==LW&&l_rsp_valid&&!stopped&&!fail_now&&!duplicate&&current!=sink&&current!=source&&current!=32'hffffffff&&l_payload[95:64]!=32'hffffffff&&l_payload[95:64]!=sink&&length!=MAX_PATH;
 genvar pw_slot,pw_word;
 generate if(FACTORED_PATH_WRITES!=0)begin:factored_path_bank
  for(pw_slot=0;pw_slot<PATH_SLOTS;pw_slot=pw_slot+1)begin:slots
   for(pw_word=0;pw_word<MAX_PATH;pw_word=pw_word+1)begin:words
    always @(posedge clk)begin
     if(pw_cp_write)path[pw_slot][pw_word]<=cp_stage[pw_slot*CP_STRIDE+7+pw_word];
     else if(pw_node_write&&slot==pw_slot&&length==pw_word)path[pw_slot][pw_word]<=current;
    end
   end
  end
 end endgenerate

 // Preserve the original nested control tree, including invalid-frame guards.
 // The stage bank has no reset initialization in either implementation.
 reg sw_capture,sw_import;
 always @*begin
  sw_capture=0;sw_import=0;
  if(rst)begin end
  else begin
   case(cp_state)
    CP_IDLE:if(cp_valid&&cp_ready)begin
     if(cp_design!=active_design||cp_nodes==0||cp_nets==0)begin end
     else if(cp_restore)begin end
     else sw_capture=1;
    end
    CP_IMPORT:if(cp_failed||abort||fault||cp_drift)begin end
     else if(cp_s_valid&&cp_s_ready)begin
      if(cp_s_index!=cp_pos||cp_s_last!=(cp_pos+1==CP_WORDS))begin end
      else sw_import=1;
     end
    default:begin end
   endcase
  end
 end
 genvar sw_slot,sw_field;
 generate if(FACTORED_STAGE_WRITES!=0)begin:factored_stage_bank
  for(sw_slot=0;sw_slot<PATH_SLOTS;sw_slot=sw_slot+1)begin:slots
   for(sw_field=0;sw_field<CP_STRIDE;sw_field=sw_field+1)begin:words
    wire[31:0]export_word;
    if(sw_field==0)assign export_word=slot_valid[sw_slot]?1:0;
    else if(sw_field==1)assign export_word=slot_valid[sw_slot]?sizes[sw_slot]:0;
    else if(sw_field==2)assign export_word=slot_valid[sw_slot]?nets[sw_slot]:0;
    else if(sw_field==3)assign export_word=slot_valid[sw_slot]?sources[sw_slot]:0;
    else if(sw_field==4)assign export_word=slot_valid[sw_slot]?sinks[sw_slot]:0;
    else if(sw_field==5)assign export_word=slot_valid[sw_slot]?designs[sw_slot][31:0]:0;
    else if(sw_field==6)assign export_word=slot_valid[sw_slot]?designs[sw_slot][63:32]:0;
    else assign export_word=slot_valid[sw_slot]&&sw_field-7<sizes[sw_slot]?path[sw_slot][sw_field-7]:0;
    always @(posedge clk)begin
     if(sw_capture)cp_stage[sw_slot*CP_STRIDE+sw_field]<=export_word;
     else if(sw_import&&cp_pos==sw_slot*CP_STRIDE+sw_field)cp_stage[sw_slot*CP_STRIDE+sw_field]<=cp_s_data;
    end
   end
  end
 end endgenerate

endmodule
