"""Independent full-trace frontier demand and provenance audit."""
from pathlib import Path
from collections import Counter
from itertools import zip_longest
import sys,json,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from build_frontier_profile import generate
from profile_real import parse_log

def main():
 out=ROOT/'results/frontier_real_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed'
 base=ROOT/'results/real_trace_20261022T165136Z';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed' and sha(base/'manifest.json')==m['baseline_manifest_sha256']
 assert sha(ROOT/'scripts/profile_frontier_real.py')==m['runner_sha256']==sha(out/'profile_frontier_real.py')
 assert sha(ROOT/'adapters/build_frontier_profile.py')==m['generator_sha256']==sha(out/'build_frontier_profile.py')
 for name,digest in m['sources'].items():assert sha(out/name)==digest
 src=(out/'original_trace.cpp').read_text();header=(out/'original_real_trace.hpp').read_text();hooks=(out/'original_real_router_hooks.inc').read_text()
 assert sha(out/'original_trace.cpp')==bm['build']['trace']['source_sha256']
 generated=generate(src,header,hooks)
 for name,text in generated.items():assert (out/'sources'/name).read_text()==text
 assert src.count('\n')==(out/'sources/trace.cpp').read_text().count('\n')
 assert sha(out/'original_real_trace.hpp')==bm['build']['inputs'][str(ROOT/'adapters/real_trace.hpp')]
 assert sha(out/'original_real_router_hooks.inc')==bm['build']['inputs'][str(ROOT/'adapters/real_router_hooks.inc')]
 assert sha(out/'sources/real_profile.hpp')==bm['build']['inputs'][str(ROOT/'adapters/real_profile.hpp')]
 assert [x['stage'] for x in m['commands']]==['build','route'] and all(x['exit_code']==0 for x in m['commands'])
 assert m['commands'][0]['argv'][-3:]==[str(out/'sources/trace.cpp'),'-o',str(out/'router_frontier')]
 assert m['commands'][1]['argv'][-3:]==[str(out/'router_frontier'),str(ROOT/bm['config']['input']),str(out/'trace.result')]
 assert m['environment']==dict(bm['config']['environment'],B_TRACE_PREFIX=str(out/'trace'),B_TRACE_STRIDE=str(bm['config']['trace_stride']),B_PROFILE_PREFIX=str(out/'trace'))
 assert sha(out/'router_frontier')==m['binary_sha256']
 assert sha(out/'trace.result')==m['result_sha256']==bm['runs'][0]['result_sha256']
 assert sha(out/'trace.accesses')==m['accesses_sha256']==sha(base/'trace_0.accesses')
 assert sha(out/'trace.jsonl')==m['metadata_sha256'] and sha(out/'frontier_analysis.json')==m['analysis_sha256']
 metrics=parse_log((out/'trace.log').read_text());assert metrics==m['metrics'] and metrics['convergence']==bm['runs'][0]['metrics']['convergence']
 fields=('frontier_pushes','frontier_polls','frontier_peak','frontier_cleared');rows=[];hist=Counter();total=Counter();label_sum=0
 with (out/'trace.jsonl').open() as new,(base/'trace_0.jsonl').open() as old:
  for index,(n,o) in enumerate(zip_longest(new,old),1):
   assert n is not None and o is not None
   row,reference=json.loads(n),json.loads(o);f={key:row.pop(key) for key in fields}
   assert row==reference and row['attempt']==index
   assert f['frontier_polls']==row['pops'] and f['frontier_pushes']==f['frontier_polls']+f['frontier_cleared']
   assert 1<=f['frontier_peak']<=f['frontier_pushes'];total.update(f);hist[f['frontier_peak']]+=1;label_sum+=row['label_accesses']
   rows.append({'attempt':index,'iteration':row['iteration'],'connection_id':row['connection_id'],'labels':row['label_accesses'],**f})
 assert len(rows)==570286==m['attempts'] and total['frontier_pushes']==metrics['pushes']==130334832
 a=json.loads((out/'frontier_analysis.json').read_text());assert a['status']=='passed' and a['attempts']==len(rows)
 assert a['totals']==dict(total) and a['peak_histogram']=={str(k):v for k,v in sorted(hist.items())}
 peaks=sorted(x['frontier_peak'] for x in rows)
 quantiles={str(p):peaks[max(0,(len(peaks)*p+99)//100-1)] for p in [50,90,99,100]};assert a['peak_quantiles']==quantiles
 top=sorted(rows,key=lambda x:x['frontier_peak'],reverse=True)[:20]
 assert a['top20']==[{k:v for k,v in row.items() if k!='labels'} for row in top]
 coverage=[]
 for original in a['capacity_coverage']:
  cap=original['capacity_entries'];affected=[x for x in rows if x['frontier_peak']>cap];overflow=len(affected);assert original['overflow_attempts']==overflow and original['payload_bytes']==cap*8
  coverage.append({**original,'overflow_attempt_fraction':overflow/len(rows),'affected_heap_pushes':sum(x['frontier_pushes'] for x in affected),'affected_heap_push_fraction':sum(x['frontier_pushes'] for x in affected)/total['frontier_pushes'],'affected_pops':sum(x['frontier_polls'] for x in affected),'affected_pop_fraction':sum(x['frontier_polls'] for x in affected)/total['frontier_polls'],'affected_label_access_fraction':sum(x['labels'] for x in affected)/label_sum})
 log=(out/'trace.log').read_text();observed=[]
 for stage,*numbers in re.findall(r'FRONTIER_GRAPH stage=(before|after) entry_bytes=(\d+) heap_arity=(\d+) nodes=(\d+) edges=(\d+) edge_sum=(\d+) max_degree=(\d+) lazy=(\d+)',log):
  observed.append({'stage':stage,**dict(zip(['entry_bytes','heap_arity','nodes','edges','edge_sum','max_degree','lazy'],map(int,numbers)))})
 assert observed==a['graph_layout'] and observed[0]['nodes']==9089009 and observed[0]['edges']==40469536 and observed[0]['max_degree']==18 and observed[0]['lazy']==0
 assert {k:v for k,v in observed[0].items() if k!='stage'}=={k:v for k,v in observed[1].items() if k!='stage'}
 result={'status':'passed','manifest_sha256':sha(mp),'auditor_sha256':sha(Path(__file__)),'attempts':len(rows),'peak_quantiles':quantiles,'maximum_live_entries':peaks[-1],'maximum_live_entry_payload_bytes':peaks[-1]*8,'capacity_sensitivity':coverage,'entry_bytes':8,'heap_arity':8,'raw_graph_layout':observed[0],'raw_csr32_offset_and_ids_payload_bytes':(9089009+1+40469536)*4,'all_original_metadata_fields_equal':True,'result_hash_equal':True,'label_access_binary_equal':True,'scope':'Complete real serial CPU demand audit. Fixed64K frontier covers this observed trace, not unseen designs or a hardware throughput guarantee. CSR byte count excludes attributes/filter state and is not an exported device image. totals.frontier_peak in raw analysis is a sum of per-attempt peaks, not a capacity.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='capacity_sensitivity'},indent=2));print(json.dumps(coverage,indent=2))
if __name__=='__main__':main()
