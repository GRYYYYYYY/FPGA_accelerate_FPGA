"""Audit the completed hash17 replay without rewriting its failed runner receipt."""
from pathlib import Path
import json,re,hashlib,csv
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/directory_hash17_full_20261024';bp=ROOT/'results/rtl_small_checkpoint_stream_full_20261023'
 m=json.loads((out/'manifest.json').read_text());b=json.loads((bp/'manifest.json').read_text());row=m['cases']['small'];d=out/'small'
 assert sha(bp/'manifest.json')==row['baseline_sha256']==json.loads((bp/'completion_audit.json').read_text())['manifest_sha256']
 spec=json.loads((ROOT/'results/initialization_observers_20261024/manifest.json').read_text())['sources']['small']
 observer=ROOT/'results/initialization_observers_20261024'/spec['output'];assert sha(observer)==row['observer_sha256']==spec['output_sha256']
 hashes={}
 for p in (d/'sources').glob('*.sv'):
  if p.name==observer.name:
   assert p.read_text()==observer.read_text().replace('TB_HASH=SMALL?2:18;','TB_HASH=SMALL?2:17;')
   assert sha(p)==row['modified_tb_sha256']
  else:
   expected=[h for n,h in b['sources'].items() if Path(n).name==p.name];assert len(expected)==1 and sha(p)==expected[0]
  hashes[p.name]=sha(p)
 assert len(hashes)==len([n for n in b['sources'] if n.endswith('.sv')])
 assert all(x['exit_code']==0 for x in row['commands'])
 # Confirm the actual compile command consumes exactly these audited sources.
 assert {Path(x).name for x in row['commands'][0]['argv'] if x.endswith('.sv')}==set(hashes)
 assert (d/'run.tcl').read_bytes()==(bp/'run.tcl').read_bytes()
 assert row['commands'][2]['argv']==b['commands'][2]['argv']
 log=(d/'simulate.log').read_text();assert 'Fatal:' not in log
 counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])}
 assert {k:v for k,v in counts.items() if k not in ('gap_cycles','host_stalls')}=={k:v for k,v in b['counts'].items() if k not in ('gap_cycles','host_stalls')}
 assert 'INDEX_ENDPOINT_PASS clear_cycles=131072 wraps=0 overflows=0' in log
 pairs=[]
 for prefix,key,n in [('STREAM_QUERY_DONE','query_receipts',38),('STREAM_CHECKPOINT_DONE','checkpoint_receipts',28)]:
  actual=re.findall('^'+prefix+r' (.+)$',log,re.M);strip=lambda x:re.sub(r' time_ps=\d+','',x)
  assert len(actual)==n and list(map(strip,actual))==list(map(strip,b[key]))
  if n==38:pairs=list(zip(b[key],actual))
 previous_a=previous_b=0;rows=[]
 for i,(a,c) in enumerate(pairs,1):
  a=int(re.search(r'time_ps=(\d+)',a)[1])//1000;c=int(re.search(r'time_ps=(\d+)',c)[1])//1000
  rows.append({'query':i,'hash18_ns':a-previous_a,'hash17_ns':c-previous_b,'delta_ns':(c-previous_b)-(a-previous_a)})
  previous_a,previous_b=a,c
 end=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]);assert previous_b==end and previous_a==b['end_ns']
 with (out/'query_timing.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 report={'status':'passed','runner_manifest_preserved_status':m['status'],'baseline_manifest_sha256':sha(bp/'manifest.json'),'candidate_manifest_sha256':sha(out/'manifest.json'),'log_sha256':sha(d/'simulate.log'),'sources':hashes,'queries':38,'checkpoints':28,'counts':counts,'hash18_end_ns':previous_a,'hash17_end_ns':end,'delta_ns':end-previous_a,'largest_interval_increases':sorted(rows,key=lambda x:x['delta_ns'],reverse=True)[:5],'scope':'Trace-specific single-factor RTL simulation; gap_cycles and host_stalls are timing statistics. No hardware resource or board performance claim.','auditor_sha256':sha(Path(__file__))}
 (out/'source_bound_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sources'},indent=2))
if __name__=='__main__':main()
