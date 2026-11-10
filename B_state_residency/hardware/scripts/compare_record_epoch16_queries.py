"""Compare completed per-query receipt intervals; checkpoints remain inclusive."""
from pathlib import Path
import json,hashlib,re,csv,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pilot=False
 name='record_epoch16_full_20261024'
 out=ROOT/'results'/name;mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed','Replay incomplete'
 audit=json.loads((out/'source_bound_audit.json').read_text());assert audit['status']=='passed' and audit['manifest_sha256']==sha(mp)
 base=ROOT/'results'/'rtl_epoch6_checkpoint_stream_full_20261023';b=json.loads((base/'manifest.json').read_text());assert audit['baseline_sha256']==sha(base/'manifest.json')
 log=(out/'pilot/simulate.log').read_text();new=re.findall(r'^STREAM_QUERY_DONE (.+)$',log,re.M);old=b['query_receipts'];assert len(new)==len(old)==(19 if pilot else 38)
 prev_old=prev_new=0;rows=[]
 for old_line,new_line in zip(old,new):
  parse=lambda s:{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',s)}
  o,n=parse(old_line),parse(new_line);assert {k:v for k,v in o.items() if k!='time_ps'}=={k:v for k,v in n.items() if k!='time_ps'}
  od=o['time_ps']-prev_old;nd=n['time_ps']-prev_new;assert od>0 and nd>0
  rows.append({'query':o['queries'],'baseline_interval_ns':od/1000,'candidate_interval_ns':nd/1000,'delta_ns':(nd-od)/1000,'change_percent':100*(nd-od)/od})
  prev_old=o['time_ps'];prev_new=n['time_ps']
 assert prev_old==b['end_ns']*1000 and prev_new==m['cases']['pilot']['end_ns']*1000
 with (out/'query_intervals.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 report={'status':'passed','manifest_sha256':sha(mp),'source_bound_audit_sha256':sha(out/'source_bound_audit.json'),'queries':len(rows),'faster_queries':sum(r['delta_ns']<0 for r in rows),'slower_queries':sum(r['delta_ns']>0 for r in rows),'unchanged_queries':sum(r['delta_ns']==0 for r in rows),'total_reduction_percent':audit['time_reduction_percent'],'scope':'query receipt intervals include checkpoint preflush, protocol and TB pacing; not isolated service latency'}
 (out/'query_comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
