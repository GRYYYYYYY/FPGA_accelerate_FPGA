"""Isolated error-retirement paths, derived from the frozen real-query stack."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
BASE=ROOT/'results/query_lifecycle_join_v2/sources'

def replace(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)

def make():
    outputs={}
    s=(BASE/'capture/children_frames.sv').read_text()
    s=replace(s,'reg capturing,discarding;','reg capturing,discarding;reg presented[0:DEPTH-1];')
    s=replace(s,'assign frame_context=frame_valid?contexts[top]:{CONTEXT_BITS{1\'b0}};',
        "assign frame_context=(frame_valid||(has_frame&&presented[top]))?contexts[top]:{CONTEXT_BITS{1'b0}};")
    s=replace(s,'assign item_valid=frame_valid&&cursors[top]<counts[top];',
        'assign item_valid=!rst&&!capturing&&has_frame&&!push&&((frame_valid&&cursors[top]<counts[top])||presented[top]);')
    s=replace(s,'assign frame_done=frame_valid&&cursors[top]==counts[top];',
        'assign frame_done=!rst&&!capturing&&has_frame&&!push&&((fault||abort)?!presented[top]:cursors[top]==counts[top]);')
    s=replace(s,'if(rst)begin level<=0;capturing<=0;discarding<=0;fault<=0;error_code<=0;end',
        'if(rst)begin level<=0;capturing<=0;discarding<=0;fault<=0;error_code<=0;for(integer i=0;i<DEPTH;i=i+1)presented[i]<=0;end')
    s=replace(s,'contexts[level]<=begin_context;counts[level]<=0;cursors[level]<=0;',
        'contexts[level]<=begin_context;counts[level]<=0;cursors[level]<=0;presented[level]<=0;')
    s=replace(s,'if(item_valid&&item_ready)cursors[top]<=cursors[top]+1;',
        'if(item_valid)begin presented[top]<=!item_ready;if(item_ready)cursors[top]<=cursors[top]+1;end')
    s=replace(s,'if(pop_valid&&pop_ready)level<=level-1;',
        'if(pop_valid&&pop_ready)begin level<=level-1;presented[top]<=0;end')
    outputs['capture/children_frames.sv']=s
    s=(BASE/'capture/expansion_capture.sv').read_text()
    s=replace(s,'assign {result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}=depth!=0?results[depth-1]:165\'b0;',
        '''wire[164:0] saved_result=depth!=0?results[depth-1]:165'b0;
 wire[164:0] corrected_result={((fault&&saved_result[164:161]==0)?4'd4:saved_result[164:161]),saved_result[160:0]};
 reg[164:0] offered_result;
 assign {result_status,result_detail,result_cookie,result_count,result_raw_count,result_mask,result_hit}=result_offered?offered_result:corrected_result;
 always @(posedge clk)begin
  if(rst)offered_result<=0;
  else if(result_valid&&!result_offered)offered_result<=corrected_result;
 end''')
    s=replace(s,'assign result_valid=frame_done&&state==0&&(!expand_valid||result_offered);',
        'assign result_valid=frame_done&&state==0&&(fault||!expand_valid||result_offered);')
    s=replace(s,'if(depth<DEPTH)state<=1;',
        "if(depth<DEPTH)begin state<=1;results[depth]<={4'd4,32'd0,expand_cookie,32'd0,32'd0,32'd0,1'b0};end")
    s=replace(s,'results[depth-1]<={e_result_status,e_result_detail,e_result_cookie,e_result_count,e_result_raw_count,e_result_mask,e_result_hit};',
        'results[depth-1]<={e_result_status,e_result_detail,cookie,e_result_count,e_result_raw_count,e_result_mask,e_result_hit};')
    outputs['capture/expansion_capture.sv']=s
    s=(BASE/'expansion_20261024/expansion/expansion_controller.sv').read_text()
    for a in ['assign g_req_valid=allow_io','assign g_rsp_ready=allow_io','assign d_req_valid=allow_io','assign d_rsp_ready=allow_io',
              'assign b_build_valid=allow_io','assign b_result_ready=allow_io','assign b_svc_ready=allow_io','assign b_svc_reply_valid=allow_io',
              'assign p_edge_valid=allow_io','assign p_result_ready=allow_io']:
        s=replace(s,a,a.replace('allow_io','!rst'))
    s=replace(s,'assign b_service_fault=!rst&&(stopped||external_fault);',
        '''// An accepted children step receives an error service reply, then its
 // real HLS completion is retired. Do not poison its unaccepted command.
 assign b_service_fault=!rst&&(stopped||external_fault)&&!b_inflight&&state!=B_SEND;''')
    s=replace(s,'reg stopped;', '''reg b_inflight,b_service_owned;
 always @(posedge clk)begin
  if(rst)begin b_inflight<=0;b_service_owned<=0;end
  else begin
   if(b_build_valid&&b_build_ready)b_inflight<=1;
   if(b_result_valid&&b_result_ready)b_inflight<=0;
   if(b_svc_valid&&b_svc_ready)b_service_owned<=1;
   if(b_svc_reply_valid&&b_svc_reply_ready)b_service_owned<=0;
  end
 end
 task fail_service;
  begin
   if(b_inflight&&b_service_owned)begin b_svc_status<=1;b_svc_value<=0;b_svc_aux<=0;state<=SVC_REPLY;end
   else if(b_inflight)state<=B_WAIT;
   else state<=RESULT;
  end
 endtask
 reg stopped;''')
    old='''if(!stopped&&abort_now)begin
    stopped<=1;
    if(state!=RESULT&&state!=IDLE)begin result_status<=4;result_detail<=0;if(state!=OUTPUT)state<=RESULT;end
   end else if(!stopped)case(state)'''
    new='''if(abort_now)stopped<=1;
   if((stopped||abort_now)&&state!=IDLE&&state!=RESULT)begin
    stopped<=1;result_status<=4;result_detail<=0;result_count<=delivered;
    case(state)
     G_SEND:if(g_req_ready)state<=G_WAIT;
     G_WAIT:if(g_rsp_valid&&g_rsp_ready)fail_service;
     D_SEND:if(d_req_ready)state<=D_WAIT;
     D_WAIT:if(d_rsp_valid&&d_rsp_ready)fail_service;
     P_SEND:if(p_edge_ready)state<=P_WAIT;
     P_WAIT:if(p_result_valid&&p_result_ready)fail_service;
     B_SEND:if(b_build_ready)state<=B_WAIT;
     B_WAIT:begin
      if(b_result_valid&&b_result_ready)state<=RESULT;
      else if(b_svc_valid&&b_svc_ready)begin
       b_svc_reply_generation<=b_svc_generation;b_svc_reply_parent<=b_svc_parent;b_svc_reply_position<=b_svc_position;b_svc_reply_phase<=b_svc_phase;b_svc_reply_node<=b_svc_node;b_svc_reply_query<=b_svc_query;b_svc_reply_price<=b_svc_price;
       b_svc_status<=1;b_svc_value<=0;b_svc_aux<=0;state<=SVC_REPLY;
      end
     end
     SVC_REPLY:if(b_svc_reply_ready)state<=B_WAIT;
     OUTPUT:if(out_ready)begin delivered<=delivered+1;result_count<=delivered+1;fail_service;end
     default:fail_service;
    endcase
   end else if(!stopped)case(state)'''
    s=replace(s,old,new)
    outputs['expansion_20261024/expansion/expansion_controller.sv']=s
    s=(BASE/'priced/candidate_recursive_engine.sv').read_text()
    # Keep each exposed stage request until accepted. Abort becomes local only
    # after that stage owns the command; an unaccepted offer must still enter.
    definitions=[]
    stages=[('prep','prefetch_ready','prep_started','raw_seen&&raw_out_valid&&out_action!=0&&!prep_started'),
            ('post','post_req_ready','post_started','q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_prep_valid&&!post_started'),
            ('k','k_ready','k_started','q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_prep_valid&&out_post_valid&&!k_started'),
            ('commit','commit_ready','commit_started','!fault&&out_cost_status==0&&q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_cost_valid&&!commit_started'),
            ('offer','offer_ready','offer_started','!fault&&q_meta_valid&&raw_seen&&raw_out_valid&&out_action==1&&out_cost_valid&&out_cost_status==0&&out_commit_valid&&out_commit_status==0&&out_commit_acked==7&&!offer_started')]
    for stage,ready,started,expr in stages:
        valid=stage+'_req_valid'
        if stage=='prep':
            s=replace(s,'.req_valid('+expr+')','.req_valid(prep_req_valid)')
            s=replace(s,'else if('+expr+'&&prefetch_ready)prep_started<=1;','else if(prep_req_valid&&prefetch_ready)prep_started<=1;')
            definitions.append('wire prep_req_valid;')
        else:s=replace(s,'assign '+valid+'='+expr+';','')
        definitions.append(f'''reg {stage}_offered;
 assign {valid}=!rst&&({stage}_offered||(!fault&&!abort&&({expr})));
 always @(posedge clk)begin
  if(rst){stage}_offered<=0;
  else if({valid}){stage}_offered<=!{ready};
 end''')
    for instance,started in [('prefetch','prep_started'),('post_inputs','post_started'),('cost_inputs','k_started'),('commit_inputs','commit_started'),('offer_inputs','offer_started')]:
        # Instance declarations have whitespace variations; bind only its abort.
        a=s.index(' '+instance+'(');b=s.index(');',a)
        part=s[a:b];part=replace(part,'.abort(abort||fence_stopped)',f'.abort((abort||fence_stopped)&&{started})');s=s[:a]+part+s[b:]
    definitions.append('''wire failed_candidate_retired=fault&&
 !prep_req_valid&&(!prep_started||out_prep_valid)&&
 !post_req_valid&&(!post_started||out_post_valid)&&
 !k_req_valid&&(!k_started||out_cost_valid)&&
 !commit_req_valid&&(!commit_started||out_commit_valid)&&
 !offer_req_valid&&(!offer_started||out_offer_valid);''')
    s=replace(s,'assign out_valid=q_meta_valid&&raw_seen&&raw_out_valid&&(out_action==0||(out_prep_valid&&out_post_valid&&out_cost_valid&&out_commit_valid&&(out_action==2||(out_offer_valid&&out_offer_status==0))));',
        '\n'.join(definitions)+'\nassign out_valid=q_meta_valid&&raw_seen&&raw_out_valid&&(failed_candidate_retired||out_action==0||(out_prep_valid&&out_post_valid&&out_cost_valid&&out_commit_valid&&(out_action==2||(out_offer_valid&&out_offer_status==0))));')
    outputs['priced/candidate_recursive_engine.sv']=s
    outputs['query_residency_system.sv']=(ROOT/'hardware/variants/query_recovery_v2/query_residency_system.sv').read_text()
    return outputs

if __name__=='__main__':
    for name,s in make().items():
        p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
