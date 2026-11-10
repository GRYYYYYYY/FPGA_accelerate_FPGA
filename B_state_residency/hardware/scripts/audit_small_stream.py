"""Per-query independent-plan audit for small-page RTL streaming replay."""
from pathlib import Path
import argparse,json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--full',action='store_true');ap.add_argument('--progress',action='store_true');a=ap.parse_args();out=a.directory.resolve()
 vp=ROOT/('results/small_checkpoint_vectors_'+('full' if a.full else 'pilot')+'_20261023')
 v=json.loads((vp/'manifest.json').read_text());qa=json.loads((vp/'query_audit.json').read_text())
 assert v['status']=='passed' and qa['status']=='passed' and qa['manifest_snapshot_sha256']==sha(vp/'manifest.json')
 mp=out/'manifest.json';snapshot=mp.read_bytes();m=json.loads(snapshot);assert m['status'] in ['running','passed']
 assert m['vector_manifest_sha256']==sha(vp/'manifest.json')
 log=(out/'simulate.log').read_text();assert 'Fatal:' not in log
 def rows(prefix):return [{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)} for line in log.splitlines() if line.startswith(prefix)]
 queries=rows('STREAM_QUERY_DONE ');cps=rows('STREAM_CHECKPOINT_DONE ');previous_time=0;cp_count=0
 for i,(actual,expected) in enumerate(zip(queries,qa['receipts']),1):
  assert actual['queries']==i
  assert (actual['commands'],actual['transfers'])==(expected['cumulative_commands'],expected['cumulative_transfers'])
  assert actual['time_ps']>previous_time
  within=[c for c in cps if previous_time<c['time_ps']<actual['time_ps']]
  assert len(within)==expected['checkpoint_count'];cp_count+=len(within);previous_time=actual['time_ps']
 assert len(queries)<=len(qa['receipts'])
 for i,c in enumerate(cps,1):
  assert c['checkpoints']==i
  if i>1:assert all(c[k]>cps[i-2][k] for k in ['commands','time_ps']) and c['transfers']>=cps[i-2]['transfers']
 for n,h in m['sources'].items():assert sha(Path(n))==h
 if not a.progress:
  assert m['status']=='passed' and sha(mp)==json.loads((out/'completion_audit.json').read_text())['manifest_sha256']
  assert len(queries)==v['queries'] and len(cps)==v['counts'].get('12',0)==cp_count
  assert all(c['exit_code']==0 for c in m['commands'])
  assert queries[-1]['time_ps']==m['end_ns']*1000
  for n,h in m['artifacts'].items():assert sha(out/n)==h
  for n,h in v['artifacts'].items():assert sha(vp/n)==h
  live=[]
 else:
  live=[];pending=[r['pid'] for r in m['commands'] if r['exit_code'] is None];seen=set()
  while pending:
   pid=pending.pop()
   if pid in seen:continue
   seen.add(pid);proc=Path('/proc')/str(pid)
   if not proc.exists():continue
   command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   live.append({'pid':pid,'command':command})
   for task in (proc/'task').iterdir():
    try:pending.extend(map(int,(task/'children').read_text().split()))
    except FileNotFoundError:pass
  assert m['status']=='passed' or any('xsimk' in r['command'] for r in live),'no live simulation kernel verified'
 result={'status':'passed' if not a.progress else 'verified_partial','queries_verified':len(queries),'total_queries':v['queries'],'checkpoint_receipts':len(cps),'last_query':queries[-1] if queries else None,'manifest_snapshot_sha256':hashlib.sha256(snapshot).hexdigest(),'vector_manifest_sha256':sha(vp/'manifest.json'),'source_sha256':sha(Path(__file__)),'live_processes':live,'board_performance':None}
 (out/('progress_audit.json' if a.progress else 'final_audit.json')).write_text(json.dumps(result,indent=2)+'\n')
 print(result['status'],len(queries),'queries',len(cps),'checkpoints')
if __name__=='__main__':main()
