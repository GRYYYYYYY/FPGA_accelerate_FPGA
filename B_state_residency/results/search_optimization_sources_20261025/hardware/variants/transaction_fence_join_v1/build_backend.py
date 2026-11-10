from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'results/route_join_rtl_v1/sources';HERE=Path(__file__).parent/'backend'
def sources():
 result={}
 for rel in ['center/cost_center_memory_call.sv','center/cost_center_service.sv','geometry_service_v1/geometry_memory_call.sv','geometry_service_v1/geometry_service.sv','cost_service_v2/cost_memory_call.sv','cost_service_v2/cost_service.sv']:
  s=(BASE/rel).read_text();n='output wire busy,fault';assert n in s;s=s.replace(n,'output wire busy,fault,retired_idle',1)
  if 'memory_call' in rel:
   n=' assign busy=!rst&&(state!=IDLE||fault);';assert n in s;s=s.replace(n,n+'\n assign retired_idle=!rst&&state==IDLE&&ap_idle&&!owned&&!rsp_valid;')
  result[Path(rel).name]=s
 for rel,anchor,expression in [
  ('cost23/cost23_inputs.sv',' assign fault=!rst&&(stopped||fail_now);assign busy=!rst&&(owned||fault);','!rst&&state==IDLE&&ga_retired_idle&&ka_retired_idle'),
  ('priced/cost_inputs_prefetch.sv',' assign busy=!rst&&(owned||stopped);','!rst&&state==IDLE'),
  ('postprev/postprev_inputs.sv',' assign fault=!rst&&(stopped||fail_now);assign busy=!rst&&(owned||fault);','!rst&&state==IDLE&&ac_retired_idle'),
  ('frontier/frontier_hls_call.sv','    assign reply_valid=!rst && state==REPLY;','!rst&&state==IDLE&&ap_idle&&!reply_valid'),
  ('frontier/frontier_service.sv',' assign busy=!rst&&(state!=IDLE||fault);','!rst&&state==IDLE&&call_retired_idle&&!rsp_valid'),
  ('offer/query_frontier_offer.sv',' assign busy=!rst&&(control!=0||arb_busy||fs_busy||offer_pending||fault);','!rst&&control==0&&!arb_busy&&!offer_pending&&fs_retired_idle')]:
  t=(BASE/rel).read_text()
  if 'query_frontier_offer' in rel:t=t.replace('initialized,busy,fault,','initialized,busy,fault,retired_idle,',1)
  elif 'frontier_hls_call' in rel:t=t.replace('output wire fault,','output wire fault,retired_idle,',1)
  else:t=t.replace('output wire busy,fault','output wire busy,fault,retired_idle',1)
  assert anchor in t,rel;t=t.replace(anchor,anchor+'\n assign retired_idle='+expression+';',1)
  if 'cost23_inputs' in rel:
   t=t.replace('wire ga_ready,ga_valid,ga_busy,ga_fault,ka_ready,ka_valid,ka_busy,ka_fault;', 'wire ga_ready,ga_valid,ga_busy,ga_fault,ka_ready,ka_valid,ka_busy,ka_fault,ga_retired_idle,ka_retired_idle;')
   t=t.replace('.busy(ga_busy),.fault(ga_fault));','.busy(ga_busy),.fault(ga_fault),.retired_idle(ga_retired_idle));',1).replace('.busy(ka_busy),.fault(ka_fault));','.busy(ka_busy),.fault(ka_fault),.retired_idle(ka_retired_idle));',1)
  if 'postprev_inputs' in rel:
   t=t.replace('wire ac_ready,ac_valid,ac_busy,ac_fault;', 'wire ac_ready,ac_valid,ac_busy,ac_fault,ac_retired_idle;')
   t=t.replace('.busy(ac_busy),.fault(ac_fault));','.busy(ac_busy),.fault(ac_fault),.retired_idle(ac_retired_idle));',1)
  if 'frontier_service' in rel:
   t=t.replace('wire call_ready,call_reply_valid,call_fault;', 'wire call_ready,call_reply_valid,call_fault,call_retired_idle;')
   t=t.replace('.reply_ready(state==WAIT_RESULT&&!fault),', '.reply_ready(state==WAIT_RESULT&&!fault),.retired_idle(call_retired_idle),',1)
  if 'query_frontier_offer' in rel:
   t=t.replace('wire fs_active,fs_busy,fs_fault,arb_busy,arb_fault;', 'wire fs_active,fs_busy,fs_fault,arb_busy,arb_fault,fs_retired_idle;')
   t=t.replace('.busy(fs_busy),.fault(fs_fault));','.busy(fs_busy),.fault(fs_fault),.retired_idle(fs_retired_idle));',1)
  result[Path(rel).name]=t
 s=(BASE/'priced/candidate_recursive_engine.sv').read_text();n='output wire  operation_pending,';assert n in s;s=s.replace(n,n+'\noutput wire retired_idle,',1)
 n='cost_center_service center(';assert n in s;s=s.replace('\n);','\n);\nwire center_retired_idle,prefetch_retired_idle,post_retired_idle,frontier_retired_idle,k_retired_idle;',1)
 n='.busy(cc_busy),.fault(cc_fault));';assert n in s;s=s.replace(n,'.busy(cc_busy),.fault(cc_fault),.retired_idle(center_retired_idle));',1)
 s=s.replace('.busy(k_busy),.fault(k_fault),','.busy(k_busy),.fault(k_fault),.retired_idle(k_retired_idle),',1)
 s=s.replace('.busy(prefetch_busy),.fault(prefetch_fault),','.busy(prefetch_busy),.fault(prefetch_fault),.retired_idle(prefetch_retired_idle),',1).replace('.busy(post_busy),.fault(post_fault),','.busy(post_busy),.fault(post_fault),.retired_idle(post_retired_idle),',1).replace('.busy(frontier_busy),.fault(frontier_fault),','.busy(frontier_busy),.fault(frontier_fault),.retired_idle(frontier_retired_idle),',1)
 n='assign busy=core_busy||cs_busy||state_lease||frontier_busy;';assert n in s;s=s.replace(n,n+'\nassign retired_idle=!core_busy&&!cs_busy&&frontier_retired_idle&&!operation_pending&&!cost_lease&&prefetch_retired_idle&&post_retired_idle&&!q_lease&&k_retired_idle&&!commit_busy&&!offer_busy&&!center_owned&&center_retired_idle;')
 result['candidate_recursive_engine.sv']=s
 return result
if __name__=='__main__':
 HERE.mkdir(exist_ok=True)
 for name,s in sources().items():(HERE/name).write_text(s)
