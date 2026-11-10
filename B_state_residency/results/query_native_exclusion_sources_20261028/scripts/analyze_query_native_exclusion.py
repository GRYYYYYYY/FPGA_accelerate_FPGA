"""Source-bound two-state exclusion analysis; not RTL simulation or formal proof."""
from pathlib import Path
from itertools import product
import json
from run_checkpoint_authority import ROOT, sha

p=Path('/tmp/B_state_residency_offer_20261025/native_retirement_synth_v1')
m=json.loads((p/'manifest.json').read_text())
a=json.loads((p/'source_bound_audit.json').read_text())
assert a['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json')
required={
 'transaction_fence.sv':[
  'localparam IDLE=0,LREQ=1,LRSP=2,LDRAIN=3,ROUTE=4,RDRAIN=5,BLOCKED=6,RECWAIT=7,RECSEND=8,RECRUN=9,RECDRAIN=10;',
  's_ready=0;s_rsp_valid=0;', 'if(choice>=0)s_ready[choice]=1;',
  's_rsp_valid[selected]=!primary_front_done&&d_rsp_valid[selected];',
  'if(DEPENDENT_MASK[i]&&i!=selected&&!dep_owned[i]&&s_valid[i]&&(i!=HOST_FLAG_LANE||!s_payload[i*REQ_BITS]))begin s_ready[i]=1;dep_accept[i]=1;end',
  'if(state==LRSP||state==LDRAIN)begin',
  'if(dep_owned[i])begin', 's_rsp_valid[i]=dep_sent[i]&&d_rsp_valid[i];',
  'assign route_ready=!rst&&state==IDLE&&!recover_valid&&!fault&&!normal_fault&&work_permit&&clean;',
  'assign route_rsp_valid=!rst&&state==ROUTE&&route_started&&backend_route_rsp_valid;'],
 'search_host_fence.sv':[
  'assign h_ready=host_open?s_ready:16\'d0;assign h_rsp_valid=host_open?s_rsp_valid:16\'d0;',
  'assign h_route_ready=host_open&&s_route_ready;'],
 'search_scheduler.sv':[
  'assign start_ready=!rst&&state==IDLE&&!stopped&&!abort&&!backend_fault&&admit&&active;',
  'assign rsp_valid=!rst&&state==DONE;'],
 'query_residency_system.sv':[
  'assign c_route_ready=qc_busy&&b_rc_req_ready;assign c_route_rsp_valid=qc_busy&&b_rc_rsp_valid;',
  'assign c_service_ready=qc_busy&&(c_service_lane==8?b_f_sr[8]:b_f_sr[6]);assign c_service_rsp_valid=qc_busy&&(c_service_lane==8?b_f_srv[8]:b_f_srv[6]);',
  '.service_ready(c_service_ready)', '.service_rsp_valid(c_service_rsp_valid)',
  '.search_ready(ss_start_ready)', '.search_rsp_valid(ss_rsp_valid)',
  '.route_ready(c_route_ready)', '.route_rsp_valid(c_route_rsp_valid)'],
 'residency_system.sv':[
  '.s_ready(f_sr)', '.s_rsp_valid(f_srv)', '.route_ready(rc_req_ready)', '.route_rsp_valid(rc_rsp_valid)'],
 'search_residency_system.sv':[
  '.f_sr(b_f_sr)', '.f_srv(b_f_srv)', '.rc_req_ready(b_rc_req_ready)', '.rc_rsp_valid(rc_rsp_valid)',
  '.h_ready(f_sr)', '.h_rsp_valid(f_srv)', '.s_ready(b_f_sr)', '.s_rsp_valid(b_f_srv)',
  '.h_route_ready(rc_req_ready)', '.s_route_ready(b_rc_req_ready)',
  '.start_ready(ss_start_ready)', '.rsp_valid(ss_rsp_valid)'],
 'query_lifecycle.sv':[
  'localparam IDLE=0,SS=1,SW=2,QS=3,QW=4,RS=5,RW=6,DRAIN=7,DONE=8;',
  'wire unexpected=(service_rsp_valid&&state!=SW&&!(state==SS&&service_ready))||(search_rsp_valid&&state!=QW&&!(state==QS&&search_ready))||(route_rsp_valid&&state!=RW&&!(state==RS&&route_ready));']}
for name,expressions in required.items():
 s=(p/'sources'/name).read_text()
 assert sha(p/'sources'/name)==m['sources'][name]
 for expression in expressions: assert expression in s,(name,expression)

# For a particular lane, every possible selected relation, ownership and input
# qualifier is admitted. Dependency readiness gates are deliberately overapproximated.
count=0; pairs=set()
for state in range(16):
 for rst,selected_here,owned,sent,dv,front_done,idle_choice,dep_gate in product([False,True],repeat=8):
  ready=not rst and ((state==0 and idle_choice) or (state==2 and dep_gate and not selected_here and not owned))
  valid=False
  if not rst:
   if state==2 and selected_here: valid=not front_done and dv
   if state in (2,3) and owned: valid=sent and dv
  assert not(ready and valid)
  pairs.add((ready,valid));count+=1
assert pairs=={(False,False),(False,True),(True,False)}
# Route and search expose request/reply in distinct states. Other combinational
# gates, including faults, cancels, drain and ownership, only restrict these.
scheduler=(p/'sources/search_scheduler.sv').read_text()
import re
decl=re.search(r'localparam IDLE=(\d+),.*?DONE=(\d+);',scheduler)
assert decl and decl[1]!=decl[2]
leaf_count=0
for idle,done in [(0,4),(int(decl[1]),int(decl[2]))]:
 for state,rst,rg,vg in product(range(16),[False,True],[False,True],[False,True]):
  assert not((not rst and state==idle and rg) and (not rst and state==done and vg))
  leaf_count+=1
mux_count=0
for lane6,lane8,select8,host_open,qc_busy in product(sorted(pairs),sorted(pairs),[False,True],[False,True],[False,True]):
 ready,valid=lane8 if select8 else lane6
 assert not((qc_busy and host_open and ready) and (qc_busy and host_open and valid))
 mux_count+=1
predicate_count=0
for state,service,search,route in product(range(16),sorted(pairs),sorted(pairs),sorted(pairs)):
 old=False;new=False
 for (ready,valid),send,wait in [(service,1,2),(search,3,4),(route,5,6)]:
  old|=valid and state!=wait and not(state==send and ready)
  new|=valid and state!=wait
 assert old==new;predicate_count+=1
result=dict(status='source_bound_two_state_exclusion_not_rtl_validation',
 reference=str(p),reference_audit_sha256=sha(p/'source_bound_audit.json'),analyzer_sha256=sha(Path(__file__)),
 source_sha256={n:sha(p/'sources'/n) for n in required},checked_expressions=required,
 valuations=dict(fence_per_lane=count,route_and_search=leaf_count,service_mux=mux_count,query_predicate=predicate_count),
 scope='State-qualified native outputs and same-lane mux preserve exclusion, including arbitrary dependent ownership and residual readiness gates. Source-bound compositional model, not an RTL formal tool, X/Z proof or full-system simulation. Generic request/reply overlap remains legal and specialization must default off. No timing or implementation result.',
 next_steps=['Independent default-off query lifecycle variant','Native legal/overlap negative tests','Full-system three-interface monitoring and exact regression','Matched synthesis before claiming path improvement'])
out=ROOT/'results/query_native_exclusion_20261027.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('QUERY_NATIVE_EXCLUSION',result['valuations'])
