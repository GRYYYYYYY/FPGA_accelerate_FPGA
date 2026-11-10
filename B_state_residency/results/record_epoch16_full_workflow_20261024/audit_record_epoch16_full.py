"""Audit full epoch16 replay against frozen pilot sources and full golden trace."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_epoch16_full_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed';r=m['cases']['pilot'];assert all(s['exit_code']==0 for s in r['commands'])
 pilot=ROOT/'results/record_epoch16_pilot_20261024';pm=json.loads((pilot/'manifest.json').read_text());pa=json.loads((pilot/'source_bound_audit.json').read_text());assert pa['status']=='passed' and sha(pilot/'manifest.json')==pa['manifest_sha256']
 files=[Path(x) for s in r['commands'] if s['stage']=='compile' for x in s['argv'] if x.endswith('.sv')]
 expected={p.name:sha(p) for p in (pilot/'pilot/sources').glob('*.sv')};assert {p.name for p in files}==set(expected)
 for p in files:
  assert sha(p)==expected[p.name]==next(h for n,h in r['sources'].items() if Path(n).name==p.name)
 assert next(s['argv'][1] for s in r['commands'] if s['stage']=='elaborate')=='tb_epoch16_endpoint_checkpoint_stream_large'
 base=ROOT/'results/rtl_epoch6_checkpoint_stream_full_20261023';b=json.loads((base/'manifest.json').read_text());assert b['status']=='passed' and sha(base/'manifest.json')==r['baseline_sha256']
 assert sha(base/'manifest.json')==json.loads((base/'completion_audit.json').read_text())['manifest_sha256']
 vdir=ROOT/'results/small_checkpoint_vectors_full_20261023';v=json.loads((vdir/'manifest.json').read_text());assert v['status']=='passed' and sha(vdir/'manifest.json')==b['vector_manifest_sha256']==m['vector_manifest_sha256']
 for name in ['actual.txt','pages.hex']:assert sha(vdir/name)==v['artifacts'][name]
 args=next(s['argv'] for s in r['commands'] if s['stage']=='simulate');oldargs=next(s['argv'] for s in b['commands'] if s['stage']=='simulate');assert args[0]==oldargs[0] and args[1]=='ablation' and args[2:]==oldargs[2:]
 assert (out/'pilot/run.tcl').read_text()=='run all\nquit\n'
 lp=out/'pilot/simulate.log';log=lp.read_text();assert sha(lp)==r['log_sha256'] and 'Fatal:' not in log
 for prefix,key,expected_count in [('STREAM_QUERY_DONE','query_receipts',38),('STREAM_CHECKPOINT_DONE','checkpoint_receipts',28)]:
  rows=re.findall('^'+prefix+r' (.+)$',log,re.M);strip=lambda s:re.sub(r' ?time_ps=\d+','',s);assert len(rows)==expected_count and [strip(s) for s in rows]==[strip(s) for s in b[key]]
 counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])};assert counts.keys()==b['counts'].keys() and all(counts[k]==x for k,x in b['counts'].items() if k not in ['gap_cycles','host_stalls'])
 end=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]);assert end==r['end_ns']
 result={'status':'passed','manifest_sha256':sha(mp),'baseline_sha256':sha(base/'manifest.json'),'epoch16_pilot_sha256':sha(pilot/'manifest.json'),'end_ns':end,'baseline_end_ns':b['end_ns'],'time_reduction_percent':100*(b['end_ns']-end)/b['end_ns'],'epoch6_record_time_equivalence':m['cycle_comparison'],'scope':'38-query actual-value epoch16 endpoint replay; no complete-design recycle lifecycle or board performance'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
