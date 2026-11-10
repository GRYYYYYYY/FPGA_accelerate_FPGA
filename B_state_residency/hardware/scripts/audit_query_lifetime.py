"""Bind both lifecycle test executions to frozen native RTL and generated TB."""
from pathlib import Path
import hashlib,json,re
from make_query_lifetime_tb import render
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/query_lifetime_20261024'
 manifest=out/'manifest.json';m=json.loads(manifest.read_text());assert m['status']=='passed'
 base=ROOT/'results/record_epoch16_pilot_20261024'
 assert sha(base/'manifest.json')==m['baseline_manifest_sha256']
 bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert sha(ROOT/'hardware/scripts/run_query_lifetime.py')==m['runner_sha256']
 assert sha(ROOT/'hardware/scripts/make_query_lifetime_tb.py')==m['generator_sha256']
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items() if not Path(k).name.startswith('tb_')}
 expected['tb_query_lifetime.sv']=hashlib.sha256(render().encode()).hexdigest()
 results={}
 for bits in (6,16):
  d=out/str(bits);row=m['cases'][str(bits)];assert row['status']=='passed' and row['sources']==expected
  for name,digest in expected.items():assert sha(d/'sources'/name)==digest
  assert [s['stage'] for s in row['commands']]==['compile','elaborate','simulate']
  for step in row['commands']:assert step['exit_code']==0
  compiled=[Path(x) for x in row['commands'][0]['argv'] if x.endswith('.sv')]
  assert set(compiled)=={d/'sources'/name for name in expected}
  assert row['commands'][1]['argv'][1]==f'tb_query_lifetime{bits}'
  log=(d/'simulate.log').read_text();assert sha(d/'simulate.log')==row['log_sha256']
  assert 'Fatal:' not in log and '$finish' in log
  match=re.search(r'LIFETIME_DOMAINS_PASS epoch_bits=(\d+) retained_query_ids=4 transfers=8 full_recycles=1 checkpoint_rejections=2 namespace_exhaustions=2 checks=(\d+) retries=(\d+)',log)
  assert match and int(match[1])==bits
  results[str(bits)]={'checks':int(match[2]),'finish_retries':int(match[3])}
 result={'status':'passed','manifest_sha256':sha(manifest),'auditor_sha256':sha(Path(__file__)),'cases':results,'scope':'Four bounded public query lifetimes, same page distinct payloads, fail-closed checkpoint and ID exhaustion, full-fence namespace reset. 32 frames/hash6; not whole-design batching or throughput.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
