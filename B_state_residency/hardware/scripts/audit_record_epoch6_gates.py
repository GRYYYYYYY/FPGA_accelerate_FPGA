"""Bind composite checkpoint/fault gates to frozen RTL and unchanged checkers."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=ROOT/'results/rtl_epoch6_checkpoint_stream_pilot_20261023';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 bsrc={Path(n).name:h for n,h in bm['sources'].items() if n.endswith('.sv') and not Path(n).name.startswith('tb_')}
 result={'status':'passed','baseline_sha256':sha(base/'manifest.json'),'cases':{}}
 for case,name,tbname in [('stalls','record_epoch6_stalls_20261024','tb_small_endpoint_epoch6.sv'),('faults','record_epoch6_faults_20261024','tb_record_epoch6_faults.sv')]:
  out=ROOT/'results'/name;mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot'];assert r['baseline_sha256']==sha(base/'manifest.json')
  assert all(x['exit_code']==0 for x in r['commands'])
  files=[Path(s) for x in r['commands'] if x['stage']=='compile' for s in x['argv'] if s.endswith('.sv')];assert {p.name for p in files}==set(bsrc)|{'response_fallthrough_fifo.sv',tbname}
  for p in files:
   assert sha(p)==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
   if p.name in ['response_fallthrough_fifo.sv','queued_scratch_endpoint_small.sv']:assert sha(p)==sha(ROOT/'results/record_epoch6_pilot_20261024/pilot/sources'/p.name)
   elif p.name==tbname:
    if case=='stalls':
     old=ROOT/'results/rtl_small_endpoint_epoch6_20261023';om=json.loads((old/'manifest.json').read_text());assert om['status']=='passed'
     assert sha(p)==next(h for n,h in om['sources'].items() if Path(n).name==tbname)
    else:
     expected=(ROOT/'hardware/tb/tb_response_faults.sv').read_text().replace('memory_scratch_endpoint_small #(','memory_scratch_endpoint_small_staticcodec #(').replace('.EPOCH_BITS(SMALL?2:8)','.EPOCH_BITS(6)');assert p.read_text()==expected
   else:assert sha(p)==bsrc[p.name]
  lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log and '$finish' in log
  if case=='stalls':assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log and 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
  else:assert 'RESPONSE_FAULT_PASS errors=9 transfers=68 checks=267' in log
  result['cases'][case]={'manifest_sha256':sha(mp),'log_sha256':sha(lp)}
 target=ROOT/'results/record_epoch6_pilot_20261024/companion_gate_audit.json';target.write_text(json.dumps(result,indent=2)+'\n');print('COMPOSITE_CHECKPOINT_FAULT_BINDING_PASS')
if __name__=='__main__':main()
