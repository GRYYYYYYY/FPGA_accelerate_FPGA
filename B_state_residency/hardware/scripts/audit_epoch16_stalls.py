"""Bind epoch16 checkpoint/backpressure gate to the frozen epoch6 checker."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_epoch16_stalls_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot'];assert all(x['exit_code']==0 for x in r['commands'])
 parent=ROOT/'results/record_epoch6_stalls_20261024';pm=json.loads((parent/'manifest.json').read_text());assert pm['status']=='passed'
 expected={p.name:sha(p) for p in (parent/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_')}
 files=[Path(x) for s in r['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')];assert {p.name for p in files}==set(expected)|{'tb_record_epoch16_stalls.sv'}
 for p in files:
  assert sha(p)==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
  if p.name.startswith('tb_'):
   source=(parent/'pilot/sources/tb_small_endpoint_epoch6.sv').read_text().replace('module tb_small_endpoint_epoch6;','module tb_record_epoch16_stalls;').replace('.EPOCH_BITS(6)','.EPOCH_BITS(16)').replace("6'd1","16'd1");assert p.read_text()==source
  else:assert sha(p)==expected[p.name]
 lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log and '$finish' in log
 assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log and 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
 result={'status':'passed','manifest_sha256':sha(mp),'epoch6_stall_manifest_sha256':sha(parent/'manifest.json'),'checks':1778,'checkpoints':8,'blocked_cycles':800,'scope':'epoch16 checkpoint/fence/backpressure; not default-capacity full-design performance'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('EPOCH16_STALL_SOURCE_BOUND_PASS')
if __name__=='__main__':main()
