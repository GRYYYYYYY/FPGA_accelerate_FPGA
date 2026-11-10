"""Independent frozen-source and semantic-receipt audit for record bypass."""
from pathlib import Path
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 full=False
 name='record_epoch6_pilot_20261024'
 out=ROOT/'results'/name;mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed',m['status']
 base=ROOT/'results'/'rtl_epoch6_checkpoint_stream_pilot_20261023';bm=json.loads((base/'manifest.json').read_text())
 row=m['cases']['pilot'];assert sha(base/'manifest.json')==row['baseline_sha256']
 d=out/'pilot';log=(d/'simulate.log').read_text();assert sha(d/'simulate.log')==row['log_sha256']
 compiled=[Path(x) for step in row['commands'] if step['stage']=='compile' for x in step['argv'] if x.endswith('.sv')]
 baseline=[Path(x) for step in bm['commands'] if step['stage']=='compile' for x in step['argv'] if x.endswith('.sv')]
 assert sorted(p.name for p in compiled)==sorted([p.name for p in baseline]+['response_fallthrough_fifo.sv'])
 for p in compiled:
  source=next(Path(n) for n in row['sources'] if Path(n).name==p.name)
  assert sha(p)==row['sources'][str(source)]
  if p.name=='response_fallthrough_fifo.sv':continue
  b=next(x for x in baseline if x.name==p.name)
  assert sha(b)==next(h for n,h in bm['sources'].items() if Path(n).name==b.name)
  expected=b.read_text()
  if p.name=='queued_scratch_endpoint_small.sv':
   old='bounded_sync_fifo #(.WIDTH(RSP_WIDTH),.DEPTH(QUEUE_DEPTH)) responses('
   assert expected.count(old)==1
   expected=expected.replace(old,'record_response_fallthrough_fifo #(.WIDTH(RSP_WIDTH),.DEPTH(QUEUE_DEPTH)) responses(')
   old='.out_valid(rsp_valid),.out_ready(rsp_ready),.out_data(response_data),.count(response_count));'
   assert expected.count(old)==1
   expected=expected.replace(old,'.out_valid(rsp_valid),.out_ready(rsp_ready),.out_data(response_data),.count(response_count),\n        .bypass_enable(pending_op==7 || pending_op==9));')
  assert p.read_text()==expected,p.name
 for prefix,key in [('STREAM_QUERY_DONE','query_receipts'),('STREAM_CHECKPOINT_DONE','checkpoint_receipts')]:
  strip=lambda s:re.sub(r' ?time_ps=\d+','',s)
  assert [strip(s) for s in re.findall('^'+prefix+r' (.+)$',log,re.M)]==[strip(s) for s in bm[key]]
 counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])}
 assert counts.keys()==bm['counts'].keys()
 assert all(counts[k]==v for k,v in bm['counts'].items() if k not in ('gap_cycles','host_stalls'))
 assert 'Fatal:' not in log
 end=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]);assert end==row['end_ns']
 result={'status':'passed','manifest_sha256':sha(mp),'baseline_sha256':sha(base/'manifest.json'),'end_ns':end,'baseline_end_ns':bm['end_ns'],'time_reduction_percent':100*(bm['end_ns']-end)/bm['end_ns'],'scope':'endpoint RTL replay; no physical timing or board result'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
