"""Bind actual-value high-address pilot to frozen native RTL and vectors."""
from pathlib import Path
import hashlib,json,re
from make_address64_trace_tb import render,ROOT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/address64_trace_pilot_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot']
 ref=ROOT/'results/record_epoch6_pilot_20261024';rp=ref/'manifest.json';b=json.loads(rp.read_text());assert b['status']=='passed' and sha(rp)==m['reference_sha256']
 assert all(s['exit_code']==0 for s in r['commands']);compiled=[Path(x) for s in r['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')]
 old={p.name:sha(p) for p in (ref/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_')}
 assert {p.name for p in compiled}==set(old)|{'backing_base_config.sv','memory_scratch_endpoint_address64.sv','tb_address64_endpoint_checkpoint_stream.sv'}
 for p in compiled:
  assert sha(p)==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
  if p.name in old:assert sha(p)==old[p.name]
  elif p.name.startswith('tb_'):assert p.read_text()==render()
  else:assert sha(p)==sha(ROOT/'results/address64_endpoint_v3_20261024/endpoint/sources'/p.name)
 assert next(s['argv'] for s in r['commands'] if s['stage']=='simulate')==next(s['argv'] for s in b['cases']['pilot']['commands'] if s['stage']=='simulate')
 assert (out/'pilot/run.tcl').read_bytes()==(ref/'pilot/run.tcl').read_bytes()
 lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log
 prior=(ref/'pilot/simulate.log').read_text();equal={}
 for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint']:
  a=re.findall('^'+prefix+r' (.+)$',log,re.M);o=re.findall('^'+prefix+r' (.+)$',prior,re.M);strip=lambda x:re.sub(r' ?time_ps=\d+','',x)
  assert [strip(x) for x in a]==[strip(x) for x in o];equal[prefix]=a==o
 assert len(re.findall(r'^STREAM_QUERY_DONE ',log,re.M))==19
 end=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]);assert end==r['end_ns'];equal['end_ns']=end==b['cases']['pilot']['end_ns']
 markers=re.findall(r'^ADDRESS64_TRACE_PASS base=([\da-f]+) aw_carries=(\d+) ar_carries=(\d+)$',log,re.M);assert len(markers)==1
 base,aw,ar=markers[0];assert int(base,16)==0x12fffff000 and int(aw)>0 and int(ar)>0
 vdir=ROOT/'results/small_checkpoint_vectors_pilot_20261023';v=json.loads((vdir/'manifest.json').read_text());assert v['status']=='passed'
 native=json.loads((ROOT/'results/rtl_epoch6_checkpoint_stream_pilot_20261023/manifest.json').read_text());assert sha(vdir/'manifest.json')==native['vector_manifest_sha256']
 for name in ['actual.txt','pages.hex']:assert sha(vdir/name)==v['artifacts'][name]
 result={'status':'passed','manifest_sha256':sha(mp),'reference_sha256':sha(rp),'end_ns':end,'exact_time_equality':equal,'aw_carries':int(aw),'ar_carries':int(ar),'vector_manifest_sha256':sha(vdir/'manifest.json'),'generator_sha256':sha(ROOT/'hardware/scripts/make_address64_trace_tb.py'),'scope':'19-query actual-value RTL pilot at high base; not full trace, physical timing or board performance'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
