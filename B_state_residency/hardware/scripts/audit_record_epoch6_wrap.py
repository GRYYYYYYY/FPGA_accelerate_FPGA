"""Audit composed lifecycle wrap evidence, including stale-page miss and bytes."""
from pathlib import Path
import hashlib,json,re
from make_record_epoch6_wrap_tb import render
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_epoch6_wrap_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot'];assert all(s['exit_code']==0 for s in r['commands'])
 base=ROOT/'results/rtl_epoch6_checkpoint_stream_pilot_20261023';bp=base/'manifest.json';b=json.loads(bp.read_text());assert sha(bp)==r['baseline_sha256']
 compiled=[Path(x) for s in r['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')]
 expected={Path(n).name:h for n,h in b['sources'].items() if n.endswith('.sv') and not Path(n).name.startswith('tb_')}
 assert {p.name for p in compiled}==set(expected)|{'response_fallthrough_fifo.sv','tb_record_epoch6_wrap.sv'}
 for p in compiled:
  assert sha(p)==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
  if p.name=='tb_record_epoch6_wrap.sv':assert p.read_text()==render()
  elif p.name in ['queued_scratch_endpoint_small.sv','response_fallthrough_fifo.sv']:assert sha(p)==sha(ROOT/'results/record_epoch6_pilot_20261024/pilot/sources'/p.name)
  else:assert sha(p)==expected[p.name]
 lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log and '$finish' in log
 lines=re.findall(r'^COMPOSITE_WRAP_PASS (.+)$',log,re.M);assert len(lines)==1
 counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',lines[0])}
 for k,v in [('queries',70),('transfers',140),('tag_wraps',17),('epoch_wraps',1),('clear_cycles',128)]:assert counts[k]==v
 assert counts['checks']==911+counts['retries']
 result={'status':'passed','manifest_sha256':sha(mp),'baseline_sha256':sha(bp),'counts':counts,'log_sha256':sha(lp),'generator_sha256':sha(ROOT/'hardware/scripts/make_record_epoch6_wrap_tb.py'),'scope':'32-frame, hash6, epoch6 composed endpoint; data and protocol monitors enabled; not full default-capacity trace or board proof'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(counts))
if __name__=='__main__':main()
