from pathlib import Path
from collections import Counter
import csv,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();controls=Path(sys.argv[2]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h,n
 for n,h in m['artifacts'].items():assert sha(out/n)==h,n
 original=(out/'sources/original.cpp').read_text();restored=(out/'sources/router.cpp').read_text()
 for before,after in reversed(json.loads((out/'sources/changes.json').read_text())):assert restored.count(after)==1;restored=restored.replace(after,before,1)
 assert restored==original
 build=json.loads((ROOT/'build/real_trace/build.json').read_text());assert sha(out/'sources/original.cpp')==build['original']['source_sha256']
 for p in(out/'sources/include').iterdir():assert sha(p)==sha(ROOT/'results/graph_image_20261024/reference/include'/p.name)
 cm=json.loads((controls/'manifest.json').read_text());cg=json.loads((controls/'source_bound_audit.json').read_text());assert cm['status']==cg['status']=='passed'and cg['manifest_sha256']==sha(controls/'manifest.json')
 cb=Path(cm['commands'][0]['argv'][8][2:]) if False else Path(sys.argv[3]).resolve() if len(sys.argv)>3 else out
 for n in ['router.cpp','recursive_census.hpp']:assert sha(out/'sources'/n)==sha(cb/'sources'/n)
 assert cg['positive']['lookahead']==1 and cg['positive']['lookahead_with_siblings']==1 and cg['positive']['max_depth']==2 and cg['negative']['lookahead']==0
 assert all(c['exit_code']==0 for c in m['commands'])
 assert sha(Path(m['input']))==m['input_sha256']and sha(Path(m['reference_result']))==m['reference_result_sha256']==sha(out/'router.result')
 log=(out/'execute.log').read_text();loaded=re.search(r'loaded (\d+) nodes, (\d+) nets, (\d+) connections',log);assert loaded;N,NETS,CONNS=map(int,loaded.groups())
 totals=Counter();by_iter=Counter();depths=Counter();raw_hist=Counter();positive=[];eligible=[];states=Counter()
 with(out/'attempts.txt').open()as f:
  reader=csv.DictReader(f,delimiter=' ')
  assert len(reader.fieldnames)==34
  for i,row in enumerate(reader,1):
   assert None not in row and None not in row.values();r={k:int(v)for k,v in row.items()}
   assert r['attempt']==r['sequence']==i and 0<=r['connection_index']<CONNS and 0<=r['net']<NETS
   assert 0<=r['source']<N and 0<=r['sink']<N and r['found']in[0,1]and r['aborted']in[0,1]and not(r['found']and r['aborted'])
   assert r['expansions']==r['pops']-r['found']-r['aborted']+r['lookahead']
   assert r['lookahead_with_siblings']<=r['lookahead']<=r['pushes']
   if not r['lookahead']:assert r['max_depth']==int(r['expansions']>0)
   if r['lookahead_with_siblings']:
    assert 0<=r['first_parent']<N and 0<=r['first_child']<N and r['first_remaining']==r['first_degree']-r['first_position']-1>0
   else:assert all(r[k]==-1 for k in ['first_parent','first_child','first_position','first_remaining','first_degree'])
   by_iter[r['iteration']]+=1;depths[r['max_depth']]+=1;raw_hist[r['max_raw_degree']]+=1;states[(r['share_bits'],r['wl_bits'],r['heuristic_bits'],r['cross'],r['landmark'])]+=1
   for key in ['expansions','pushes','lookahead','lookahead_with_siblings','pops']:totals[key]+=r[key]
   totals['attempts']+=1;totals['queries_with_lookahead']+=bool(r['lookahead']);totals['routed']+=bool(r['routed']);totals['found']+=r['found'];totals['aborted']+=r['aborted']
   if r['lookahead'] and len(positive)<16:positive.append(r)
   if len(eligible)<8 and not r['cross']and not r['landmark']and r['routed']and r['found']and not r['aborted']and r['initial_queue']==r['targets']==1 and 0<r['expansions']<=128 and r['pushes']<=512 and r['max_raw_degree']<=32 and r['max_filtered_degree']<=32 and r['max_depth']<=4:eligible.append(r)
 summary=re.search(r'RECURSION_CENSUS_FINISHED attempts=(\d+) expansions=(\d+) pushes=(\d+) lookahead=(\d+) orphan_pushes=(\d+)',log);assert summary
 assert list(map(int,summary.groups()))==[totals[k]for k in ['attempts','expansions','pushes','lookahead']]+[0]
 assert totals['pushes']==m['metrics']['pushes']and dict(by_iter)=={v[0]:v[-1]for v in m['metrics']['convergence']}
 from profile_real import parse_log
 ref_log=Path(m['reference_result']).with_suffix('.log');assert sha(ref_log)==m['reference_log_sha256'];baseline=parse_log(ref_log.read_text());observed=parse_log(log)
 assert all(observed[k]==baseline[k]for k in ['iterations','overused','pushes','used_nodes','wire_length','convergence'])
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'controls_audit_sha256':sha(controls/'source_bound_audit.json'),'source_recovered_byte_identical':True,'totals':dict(totals),'attempts_by_iteration':dict(by_iter),'max_depth_histogram':dict(depths),'max_raw_degree_histogram':dict(raw_hist),'state_profiles':[{'share_bits':s[0],'wl_bits':s[1],'heuristic_bits':s[2],'cross':s[3],'landmark':s[4],'attempts':n}for s,n in sorted(states.items())],'natural_lookahead_examples':positive,'small_real_query_candidates':eligible,'scope':m['scope'],'limitation':'Query-level census only; labels/owners/history/queue and child-level event snapshots have not been exported for RTL replay. Zero observed lookahead is specific to this dataset and serial configuration.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':'passed','totals':r['totals'],'small_real_query_candidates':[(c['attempt'],c['connection_index'],c['expansions'],c['pushes'])for c in eligible]},indent=2))
if __name__=='__main__':main()
