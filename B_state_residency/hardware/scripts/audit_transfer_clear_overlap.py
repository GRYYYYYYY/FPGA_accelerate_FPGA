"""Audit passive transfer-state overlap replay against frozen pilot receipts."""
from pathlib import Path
import hashlib,json,re
from make_transfer_clear_overlap_tb import render
ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/transfer_state_overlap_pilot_20261024'
 mp=out/'manifest.json'; m=json.loads(mp.read_text());assert m['status']=='passed'
 row=m['cases']['small']; lp=out/'small/simulate.log';log=lp.read_text();assert sha(lp)==row['log_sha256']
 tb=out/'small/sources/tb_small_endpoint_transfer_state_overlap.sv'
 assert tb.read_text()==render() and sha(tb)==row['observer_sha256']

 base=ROOT/'results/rtl_small_checkpoint_stream_pilot_v3_20261023';bm=json.loads((base/'manifest.json').read_text());assert sha(base/'manifest.json')==row['baseline_sha256']
 frozen_sources={Path(name).name:digest for name,digest in bm['sources'].items()}
 compiled=[Path(x) for step in row['commands'] if step['stage']=='compile' for x in step['argv'] if x.endswith('.sv')]
 baseline_inputs=[Path(x) for step in bm['commands'] if step['stage']=='compile' for x in step['argv'] if x.endswith('.sv')]
 assert sorted(p.name for p in compiled if p!=tb)==sorted(p.name for p in baseline_inputs if not p.name.startswith('tb_'))
 for source in compiled:
  if source!=tb:assert sha(source)==frozen_sources[source.name]
 assert (out/'small/run.tcl').read_bytes()==(base/'run.tcl').read_bytes()
 assert next(s['argv'] for s in row['commands'] if s['stage']=='simulate')==next(s['argv'] for s in bm['commands'] if s['stage']=='simulate')
 for prefix,key in [('STREAM_QUERY_DONE','query_receipts'),('STREAM_CHECKPOINT_DONE','checkpoint_receipts')]:assert re.findall('^'+prefix+r' (.+)$',log,re.M)==bm[key]
 assert int(re.search(r'\$finish called at time : (\d+) ns',log)[1])==bm['end_ns']
 counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])};assert counts==bm['counts']
 states={};ops={};overlaps={}
 for q,op,s,n in re.findall(r'^TRANSFER_STATE_PROFILE queries=(\d+) op=(\d+) state=(\d+) cycles=(\d+)$',log,re.M):
  key=tuple(map(int,(q,op,s)));assert key not in states;states[key]=int(n)
 for q,op,n in re.findall(r'^COMMAND_OP_PROFILE queries=(\d+) op=(\d+) busy=(\d+)$',log,re.M):ops[int(q),int(op)]=int(n)
 for q,w,r in re.findall(r'^TRANSFER_CLEAR_OVERLAP queries=(\d+) wb_lookup=(\d+) rf_lookup=(\d+)$',log,re.M):
  q=int(q);assert q not in overlaps;overlaps[q]=(int(w),int(r))
 assert sorted(overlaps)==list(range(1,20));assert len(states)==19*64
 previous=(0,0)
 for q,pair in overlaps.items():
  for i,op in enumerate((5,6)):
   assert sum(states[q,op,s] for s in range(32))==ops[q,op]
   assert previous[i]<=pair[i]<=states[q,op,4]
  previous=pair
 clear=int(re.search(r'^INIT_DIRECTORY_READY .*clear_samples=(\d+)',log,re.M)[1]);assert sum(previous)<=clear
 last={'directory_clear_cycles':clear,'wb_lookup_cycles':states[19,5,4],'clear_in_wb_lookup':previous[0],'clear_in_rf_lookup':previous[1],'clear_outside_transfer_lookup':clear-sum(previous),'wb_lookup_excluding_clear_overlap':states[19,5,4]-previous[0],'rf_lookup_excluding_clear_overlap':states[19,6,4]-previous[1]}
 result={'status':'passed','scope':'19-query pilot; state residency, not causal latency savings','manifest_sha256':sha(mp),'log_sha256':sha(lp),'queries':19,'state_bins':len(states),'final':last}
 (out/'overlap_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
