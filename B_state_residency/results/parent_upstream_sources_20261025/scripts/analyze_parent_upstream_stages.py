"""Exact partition of the actual first-to-target POLL window using event boundaries."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();base=ROOT/'results/natural_query_rtl_v1';m=json.loads((out/'manifest.json').read_text());a=json.loads((out/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed' and a['manifest_sha256']==sha(out/'manifest.json')
 cases={}
 for case in ['full','pressure']:
  p=out/case;legacy=['design.bin','labels.bin','owners.bin','cost.bin']
  for name in legacy:assert sha(p/name)==sha(base/case/name),(case,name)
  rows=[l.split()for l in(p/'natural_trace.txt').read_text().splitlines()];stage=[l.split()for l in(p/'stage_trace.txt').read_text().splitlines()]
  by=lambda tag:[t for t in rows if t[0]==tag];sb=lambda tag:[t for t in stage if t[0]==tag]
  P,E,S,M,O,Q=[by(t)for t in ['P','E','S','M','O','Q']];X,Q0,Q1,QM,MR,D=[sb(t)for t in ['X','Q0','Q1','QM','MR','D']]
  assert all(len(v)==72 for v in [E,S,X,Q0,Q1,QM]) and all(len(v)==271 for v in [M,O,MR,D]) and len(P)==73
  tags=['PF0','PF1','PO0','PO1','K0','K1','LC0','LC1','OF0','OF1'];pushstages={tag:sb(tag)for tag in tags};assert all(len(v)==171 for v in pushstages.values())
  totals=Counter();samples={};intervals=[];windows=[];state_slack=[];qi=pi=0
  def add(name,start,end):
   assert start<=end,(case,name,start,end)
   totals[name]+=end-start;samples.setdefault(name,[]).append(end-start);intervals.append((start,end,name))
  for fi in range(72):
   pc,ec,sc,qc=[int(t[1])for t in [P[fi],E[fi],S[fi],Q[fi]]];cookie=100+fi
   assert all(int(v[fi][2])==cookie for v in [X,Q0,Q1,QM])
   xc,q0c,q1c,qmc=[int(v[fi][1])for v in [X,Q0,Q1,QM]];assert pc<xc<=q0c<q1c<qmc
   assert int(E[fi][3])==int(P[fi][2]);state_slack.append(dict(cookie=cookie,request_to_reply=q1c-q0c,reply_to_seal=sc-q1c,metadata_ready_to_seal=sc-qmc))
   add('poll_label_and_expand_admission',pc,ec);add('children_build_to_result',ec,sc)
   begin=qi
   while qi<len(M)and int(M[qi][2])==cookie:qi+=1
   assert qi>begin
   add('children_result_to_metadata_dispatch',sc,int(M[begin][1]))
   for j in range(begin,qi):
    mc,mrc,dc,oc=[int(t[1])for t in [M[j],MR[j],D[j],O[j]]]
    par,node,action=int(O[j][3]),int(O[j][4]),int(O[j][5])
    assert [int(M[j][3]),int(M[j][4])]==[par,node] and int(MR[j][3])==node and [int(D[j][2]),int(D[j][3]),int(D[j][4])]==[par,node,action]
    add('metadata',mc,mrc);add('access_decision',mrc,dc)
    if action==0:add('skip_output_dispatch',dc,oc)
    else:
     assert action==1
     times=[int(pushstages[tag][pi][1])for tag in tags]
     for tag in tags:assert list(map(int,pushstages[tag][pi][2:]))==[par,node]
     boundaries=[dc,*times,oc]
     names=['decision_to_prefetch_dispatch','owner_history_price_net_prefetch','prefetch_to_post_dispatch','prev_geometry_center_post','post_to_cost_dispatch','geometry_and_cost','cost_to_commit_dispatch','three_label_commit','commit_to_offer_dispatch','heap_offer','offer_to_output_dispatch']
     assert len(boundaries)==len(names)+1
     for name,start,end in zip(names,boundaries,boundaries[1:]):add(name,start,end)
     pi+=1
    if j+1<qi:add('output_retire_and_next_candidate',oc,int(M[j+1][1]))
   add('last_output_to_expand_result',int(O[qi-1][1]),qc);add('result_to_next_poll',qc,int(P[fi+1][1]))
   windows.append(int(P[fi+1][1])-pc)
  assert qi==271 and pi==171
  intervals.sort();assert intervals[0][0]==int(P[0][1]) and intervals[-1][1]==int(P[-1][1])
  assert all(x[1]==y[0] for x,y in zip(intervals,intervals[1:])),('gap/overlap',case)
  window=int(P[-1][1])-int(P[0][1]);assert sum(totals.values())==window==sum(windows)
  # No optimistic overlap subtraction: only disjoint serialized intervals above.
  assert min(s['metadata_ready_to_seal']for s in state_slack)>0
  ranked=[dict(stage=k,cycles=v,fraction=v/window,calls=len(samples[k]),minimum=min(samples[k]),maximum=max(samples[k]))for k,v in totals.most_common()]
  cases[case]=dict(search_window_cycles=window,total_cycles=a['counts'][case]['cycles'],partition=ranked,state_requests=72,state_request_to_reply_min=min(s['request_to_reply']for s in state_slack),state_request_to_reply_max=max(s['request_to_reply']for s in state_slack),state_ready_before_seal_min=min(s['metadata_ready_to_seal']for s in state_slack),state_ready_before_seal_max=max(s['metadata_ready_to_seal']for s in state_slack),expanded_windows=windows,state_slack=state_slack,state_files_byte_identical=True,stage_trace_sha256=sha(p/'stage_trace.txt'))
 r=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),primary_audit_sha256=sha(out/'source_bound_audit.json'),analyzer_sha256=sha(Path(__file__)),cases=cases,scope='Parent-upstream variant exact disjoint observed stage partition, same final state and actual work. No board performance or STA path claim.')
 dest=ROOT/'results/parent_upstream_stages_20261025.json';dest.write_text(json.dumps(r,indent=2)+'\n')
 for case,v in cases.items():print(json.dumps(dict(case=case,window=v['search_window_cycles'],top=v['partition'][:6],min_state_ready_margin=v['state_ready_before_seal_min']),indent=2))
if __name__=='__main__':main()
