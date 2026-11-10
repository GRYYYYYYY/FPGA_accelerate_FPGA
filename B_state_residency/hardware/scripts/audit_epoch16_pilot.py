"""Prove parameter-only pilot composition and exact observed time equivalence."""
from pathlib import Path
import hashlib,json,re
from make_epoch16_pilot_tb import render,ROOT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_epoch16_pilot_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot']
 parent=ROOT/'results/record_epoch6_pilot_20261024';pm=json.loads((parent/'manifest.json').read_text());assert pm['status']=='passed'
 expected={p.name:sha(p) for p in (parent/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_')}
 compiled=[Path(x) for s in r['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')];assert {p.name for p in compiled}==set(expected)|{'tb_epoch16_endpoint_checkpoint_stream.sv'}
 for p in compiled:
  assert sha(p)==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
  if p.name.startswith('tb_'):assert p.read_text()==render()
  else:assert sha(p)==expected[p.name]
 assert all(s['exit_code']==0 for s in r['commands'])
 lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log
 previous=(parent/'pilot/simulate.log').read_text()
 for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint']:assert re.findall('^'+prefix+r' (.+)$',log,re.M)==re.findall('^'+prefix+r' (.+)$',previous,re.M)
 assert len(re.findall(r'^STREAM_QUERY_DONE ',log,re.M))==19
 end=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]);assert end==20603280==pm['cases']['pilot']['end_ns']
 result={'status':'passed','manifest_sha256':sha(mp),'epoch6_manifest_sha256':sha(parent/'manifest.json'),'queries':19,'end_ns':end,'exact_receipts_and_time_equal':True,'scope':'parameter-only epoch16 pilot, not full-design throughput or physical timing'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('EPOCH16_PILOT_SOURCE_BOUND_PASS')
if __name__=='__main__':main()
