"""Equal-work natural result comparison and request-level parent reuse audit."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 old=BASE/'mcml_query_baseline_v1';new=BASE/'mcml_query_cached_v1';bounds=BASE/'parent_upstream_bounds_v1';gates={}
 for p in [old,new,bounds]:
  m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and a['manifest_sha256']==sha(p/'manifest.json');gates[p.name]=sha(p/'source_bound_audit.json')
 oa=json.loads((old/'source_bound_audit.json').read_text());na=json.loads((new/'source_bound_audit.json').read_text());os=json.loads((ROOT/'results/mcml_stages_baseline_20261025.json').read_text());ns=json.loads((ROOT/'results/mcml_stages_cached_20261025.json').read_text());assert ns['primary_audit_sha256']==gates[new.name]
 inp=BASE/'mcml_query_inputs_v1';cost=[l.split()for l in(inp/'cost_vectors.txt').read_text().splitlines()];result={}
 for case in ['full','pressure']:
  for name in ['design.bin','labels.bin','owners.bin','cost.bin']:assert sha(old/case/name)==sha(new/case/name),name
  oldrows=[l.split()for l in(old/case/'natural_trace.txt').read_text().splitlines()];newrows=[l.split()for l in(new/case/'natural_trace.txt').read_text().splitlines()]
  for tag in ['E','S','M','V','O','C','W','A','F','R','P','I','Q','FQ','FR']:
   x=[r[:1]+r[2:]for r in oldrows if r[0]==tag];y=[r[:1]+r[2:]for r in newrows if r[0]==tag];assert x==y,(case,tag)
  # Natural EARLY must not expose the remaining captured child as a decision.
  assert not any(t[0]=='M'and t[3:5]==['2178064','124201']for t in newrows)
  assert not any(t[0]=='O'and t[3:5]==['2178064','124201']for t in newrows)
  records={int(t[2]):int(t[3],16)for t in newrows if t[0]=='R'}
  path=[];node=41981
  while node!=0xffffffff:
   assert node in records and node not in path;path.append(node);node=(records[node]>>64)&0xffffffff
  assert len(path)==8 and path[-1]==41486
  N=[l.split()for l in(new/case/'parent_trace.txt').read_text().splitlines()];expected=[];parent=None
  for row in cost:
   p,c=map(int,row[:2]);expected.append([p,c,c,1,p])
   if p!=parent:expected.append([p,c,p,0,0]);parent=p
  actual=[[int(t[2]),int(t[3]),int(t[4]),int(t[5]),int(t[6],16)]for t in N];assert actual==expected
  assert sum(t[3]==0 for t in actual)==59 and sum(t[3]==1 for t in actual)==178
  oc=oa['counts'][case];nc=na['counts'][case];ow=os['cases'][case]['search_window_cycles'];nw=ns['cases'][case]['search_window_cycles'];assert nw<ow and nc['cycles']<oc['cycles']
  stagesold={r['stage']:r['cycles']for r in os['cases'][case]['partition']};stagesnew={r['stage']:r['cycles']for r in ns['cases'][case]['partition']}
  result[case]=dict(final_label_prev_chain_sink_to_source=path,early_unprocessed_child=124201,parent_reads_before=178,parent_reads_after=59,parent_reads_saved=119,prev_writes=178,baseline_total_cycles=oc['cycles'],cached_total_cycles=nc['cycles'],baseline_observed_window=ow,cached_observed_window=nw,window_cycles_saved=ow-nw,window_reduction_fraction=(ow-nw)/ow,total_cycles_saved=oc['cycles']-nc['cycles'],total_reduction_fraction=(oc['cycles']-nc['cycles'])/oc['cycles'],baseline_label_memory=oc['memory']['label'],cached_label_memory=nc['memory']['label'],stage_cycles_saved={k:stagesold[k]-stagesnew[k]for k in stagesold},final_labels_sha256=sha(new/case/'labels.bin'))
 r=dict(status='passed',auditor_sha256=sha(Path(__file__)),audits=gates,stage_analysis_sha256=sha(ROOT/'results/mcml_stages_cached_20261025.json'),cases=result,scope='MCML natural query, same protocol workload and semantic event payloads, isolated post-module change. Behavioral simulation cycles include TB observation. No board speed, resource cost, multi-query or broad routing-quality claim.')
 (ROOT/'results/mcml_parent_upstream_20261025.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({case:{k:v[k]for k in ['baseline_observed_window','cached_observed_window','window_reduction_fraction','baseline_total_cycles','cached_total_cycles','total_reduction_fraction']}for case,v in result.items()},indent=2))
if __name__=='__main__':main()
