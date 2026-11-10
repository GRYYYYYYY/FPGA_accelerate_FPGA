"""Verify the unchanged nine-fault checker with only EPOCH_BITS widened."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_epoch16_faults_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot'];assert all(x['exit_code']==0 for x in r['commands'])
 old=ROOT/'results/record_epoch6_faults_20261024';om=json.loads((old/'manifest.json').read_text());assert om['status']=='passed'
 files=[Path(x) for s in r['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')]
 old_files={p.name:sha(p) for p in (old/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_')}
 assert {p.name for p in files}==set(old_files)|{'tb_record_epoch16_faults.sv'}
 for p in files:
  assert sha(p)==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
  if p.name.startswith('tb_'):assert p.read_text()==(old/'pilot/sources/tb_record_epoch6_faults.sv').read_text().replace('.EPOCH_BITS(6)','.EPOCH_BITS(16)')
  else:assert sha(p)==old_files[p.name]
 lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log and '$finish' in log and 'RESPONSE_FAULT_PASS errors=9 transfers=68 checks=267' in log
 result={'status':'passed','manifest_sha256':sha(mp),'epoch6_fault_manifest_sha256':sha(old/'manifest.json'),'errors_exercised':9,'checks':267,'scope':'epoch16 fault isolation, leases and read drain; no full-design performance proof'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('EPOCH16_FAULT_SOURCE_BOUND_PASS')
if __name__=='__main__':main()
