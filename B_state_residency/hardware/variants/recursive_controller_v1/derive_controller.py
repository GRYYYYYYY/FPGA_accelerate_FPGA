from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_controller #','module recursive_candidate_controller #',1)
 s=s.replace(' input wire clk,rst,enable,abort,subsystem_fault,',''' input wire[31:0]active_version,input wire[63:0]active_design,
 input wire[511:0]e_context,input wire[31:0]e_depth,output wire[511:0]e_expand_context,
 output wire[31:0]out_parent,output wire[31:0]out_root_cookie,
 input wire clk,rst,enable,abort,subsystem_fault,''',1)
 s=s.replace('DRAIN=5,FINAL=6;', 'DRAIN=5,FINAL=6,DESCEND=7,RESTORE=8;',1).replace('reg[2:0]state;','reg[3:0]state;',1)
 s=s.replace(' reg[255:0]attrs;', ''' reg[31:0]frame_cookie,cookie_counter,root_cookie,prune_word,laguna_word,held_version;
 reg[63:0]held_design;
 assign out_parent=parent;assign out_root_cookie=root_cookie;
 reg[255:0]attrs;''',1)
 s=s.replace('active_price!=price);','active_price!=price||active_version!=held_version||active_design!=held_design);',1)
 s=s.replace('assign e_expand_valid=expand_valid&&expand_ready&&!invalid;', 'assign e_expand_valid=(expand_valid&&expand_ready&&!invalid)||(!rst&&!stopped&&state==DESCEND);',1)
 old='assign e_expand_cookie=expand_cookie;assign e_expand_parent=expand_parent;assign e_expand_prune=expand_prune;assign e_expand_has_laguna=expand_has_laguna;'
 new='''assign e_expand_cookie=state==DESCEND?cookie_counter+1:expand_cookie;
 assign e_expand_parent=state==DESCEND?child:expand_parent;
 assign e_expand_prune=state==DESCEND?prune_word:expand_prune;
 assign e_expand_has_laguna=state==DESCEND?laguna_word:expand_has_laguna;
 assign e_expand_context=state==DESCEND?
 {26'b0,query,price,held_version,held_design,cookie_counter+32'd1,child,prune_word,laguna_word,sink,net,sequence_word,flags&32'h11c,xmin,xmax,ymin,ymax}:
 {26'b0,active_query,active_price,active_version,active_design,expand_cookie,expand_parent,expand_prune,expand_has_laguna,expand_sink,expand_net,expand_sequence,expand_flags,expand_xmin,expand_xmax,expand_ymin,expand_ymax};'''
 assert old in s;s=s.replace(old,new,1)
 s=s.replace('assign e_result_ready=!rst&&(state==NEXT_CHILD||(state==DRAIN&&!e_done));','assign e_result_ready=!rst&&(state==NEXT_CHILD||state==DRAIN);',1)
 s=s.replace('state<=IDLE;operation_pending<=0;', 'state<=IDLE;frame_cookie<=0;cookie_counter<=0;root_cookie<=0;prune_word<=0;laguna_word<=0;held_version<=0;held_design<=0;operation_pending<=0;',1)
 s=s.replace('if(e_expand_valid&&e_expand_ready)begin e_pending<=1;e_done<=0;end','if(e_expand_valid&&e_expand_ready)begin e_pending<=1;e_done<=0;end',1)
 s=s.replace('if(e_result_valid&&e_result_ready)begin e_pending<=0;e_done<=1;end','if(e_result_valid&&e_result_ready&&e_depth==1)begin e_pending<=0;e_done<=1;end',1)
 s=s.replace('operation_pending<=1;parent<=expand_parent;', 'operation_pending<=1;frame_cookie<=expand_cookie;cookie_counter<=expand_cookie;root_cookie<=expand_cookie;prune_word<=expand_prune;laguna_word<=expand_has_laguna;held_version<=active_version;held_design<=active_design;parent<=expand_parent;',1)
 a=s.index('     if(e_result_valid&&e_result_ready)begin',s.index('    NEXT_CHILD:begin'));b=s.index('     end else if(m_req_valid',a)
 s=s[:a]+'''     if(e_result_valid&&e_result_ready)begin
      if(e_result_cookie!=frame_cookie||e_result_status!=0)begin stopped<=1;result_status<=4;state<=e_depth==1?FINAL:DRAIN;end
      else begin
       result_expanded_count<=result_expanded_count+e_result_count;
       result_raw_count<=result_raw_count+e_result_raw_count;
       if(e_depth==1)begin result_count<=processed;result_mask<=e_result_mask;result_hit<=e_result_hit;result_early<=early;state<=FINAL;end
       else state<=RESTORE;
      end
'''+s[b:]
 s=s.replace('out_cookie<=result_cookie;out_node<=child;', 'out_cookie<=frame_cookie;out_node<=child;',1)
 old='OUTPUT:if(out_ready)begin processed<=processed+1\'b1;early<=early||out_bits[2];state<=(stopped||subsystem_fault||abort||drift||timeout||unexpected)?DRAIN:NEXT_CHILD;end'
 new='''OUTPUT:if(out_ready)begin
     processed<=processed+1'b1;early<=early||out_bits[2];
     if(stopped||subsystem_fault||abort||drift||timeout||unexpected)state<=DRAIN;
     else if(out_action==2&&!out_bits[2])begin
      if(cookie_counter==32'hffffffff)begin stopped<=1;result_status<=4;state<=DRAIN;end
      else state<=DESCEND;
     end else state<=NEXT_CHILD;
    end
    DESCEND:if(e_expand_valid&&e_expand_ready)begin
     parent<=child;cookie_counter<=cookie_counter+1;frame_cookie<=cookie_counter+1;state<=NEXT_CHILD;
    end
    RESTORE:begin
     if(e_depth==0||e_context[479:448]!=held_version||e_context[447:384]!=held_design||e_context[485:484]!=query||e_context[483:480]!=price||e_context[223:192]!=net||e_context[255:224]!=sink||e_context[191:160]!=sequence_word)fail;
     else begin
      frame_cookie<=e_context[383:352];parent<=e_context[351:320];prune_word<=e_context[319:288];laguna_word<=e_context[287:256];
      flags<=e_context[159:128]|e_context[319:288];xmin<=e_context[127:96];xmax<=e_context[95:64];ymin<=e_context[63:32];ymax<=e_context[31:0];state<=NEXT_CHILD;
     end
    end'''
 assert old in s;s=s.replace(old,new,1)
 # Drain all suspended frames; errors are terminal. No reset/replay claim.
 a=s.index('    DRAIN:begin');b=s.index('    FINAL:',a)
 s=s[:a]+'''    DRAIN:begin
     if(e_done&&!m_pending&&!a_pending)state<=FINAL;
     if(e_result_valid&&e_result_ready&&e_depth==1)begin result_count<=processed;result_early<=early;end
    end
'''+s[b:]
 return s
if __name__=='__main__':
 p=Path(__file__).parent;(p/'recursive_candidate_controller.sv').write_text(derive((ROOT/'hardware/variants/candidate_pipeline_v1/candidate_controller.sv').read_text()))
