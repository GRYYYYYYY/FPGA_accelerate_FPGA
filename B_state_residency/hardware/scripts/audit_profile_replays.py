"""Bind passive profile replay results to frozen RTL, vectors and receipts."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 bp=ROOT/'results/rtl_small_checkpoint_stream_full_20261023';b=json.loads((bp/'manifest.json').read_text())
 assert sha(bp/'manifest.json')==json.loads((bp/'completion_audit.json').read_text())['manifest_sha256']
 for kind in ['service','command']:
  p=ROOT/'results'/f'{kind}_profile_full_20261024';m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed';r=m['cases']['small'];d=p/'small'
  assert r['baseline_sha256']==sha(bp/'manifest.json') and all(x['exit_code']==0 for x in r['commands'])
  spec=json.loads((ROOT/'results'/f'{kind}_profile_observers_20261024/manifest.json').read_text())['sources']['small'];tb=ROOT/'results'/f'{kind}_profile_observers_20261024'/spec['output']
  assert sha(tb)==spec['output_sha256']==r['observer_sha256']
  sources={}
  for src in (d/'sources').glob('*.sv'):
   if src.name==tb.name:assert src.read_bytes()==tb.read_bytes()
   else:
    hh=[v for k,v in b['sources'].items() if Path(k).name==src.name];assert len(hh)==1 and sha(src)==hh[0]
   sources[src.name]=sha(src)
  assert {Path(x).name for x in r['commands'][0]['argv'] if x.endswith('.sv')}==set(sources)
  assert len(sources)==len([x for x in b['sources'] if x.endswith('.sv')])
  assert r['commands'][2]['argv']==b['commands'][2]['argv'] and (d/'run.tcl').read_bytes()==(bp/'run.tcl').read_bytes()
  log=(d/'simulate.log').read_text();assert sha(d/'simulate.log')==r['log_sha256'] and 'Fatal:' not in log
  for prefix,key in [('STREAM_QUERY_DONE','query_receipts'),('STREAM_CHECKPOINT_DONE','checkpoint_receipts')]:assert re.findall('^'+prefix+r' (.+)$',log,re.M)==b[key]
  counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])};assert counts==b['counts']
  assert int(re.search(r'\$finish called at time : (\d+) ns',log)[1])==b['end_ns']==r['end_ns']
  # Verify simulator vector bytes against their completed vector manifest.
  vectors=ROOT/'results/small_checkpoint_vectors_full_20261023';v=json.loads((vectors/'manifest.json').read_text())
  assert sha(vectors/'manifest.json')==b['vector_manifest_sha256']
  for fn in ['actual.txt','pages.hex']:assert sha(vectors/fn)==v['artifacts'][fn]
  report={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'baseline_sha256':sha(bp/'manifest.json'),'sources':sources,'vector_manifest_sha256':sha(vectors/'manifest.json'),'log_sha256':sha(d/'simulate.log'),'auditor_sha256':sha(Path(__file__))}
  (p/'source_bound_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(kind,'SOURCE_BOUND_PROFILE_AUDIT_PASS')
if __name__=='__main__':main()
