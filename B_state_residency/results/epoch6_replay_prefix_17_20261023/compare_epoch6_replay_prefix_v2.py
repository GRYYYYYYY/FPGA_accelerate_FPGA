"""Compare only independently audited, completed queries of active full runs."""
from pathlib import Path
import json,re,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);a=ap.parse_args();a.output.mkdir()
 folders=[ROOT/'results'/s for s in ['rtl_small_checkpoint_stream_full_20261023','rtl_epoch6_checkpoint_stream_full_20261023']]
 data=[]
 for folder in folders:
  m=json.loads((folder/'manifest.json').read_text());audit=json.loads((folder/'progress_audit.json').read_text())
  assert m['status'] in ['running','passed'] and audit['status']=='verified_partial'
  for p,h in m['sources'].items():assert sha(Path(p))==h
  log=(folder/'simulate.log').read_text();assert 'Fatal:' not in log
  rows=[{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)} for line in log.splitlines() if line.startswith('STREAM_QUERY_DONE ')]
  rows=rows[:audit['queries_verified']];assert len(rows)==audit['queries_verified'] and rows[-1]==audit['last_query']
  data.append((m,rows,audit))
 assert data[0][0]['vector_manifest_sha256']==data[1][0]['vector_manifest_sha256']
 count=min(len(x[1]) for x in data)
 for i in range(count):assert data[0][1][i]==data[1][1][i],f'query {i+1} mismatch'
 checkpoints=[]
 for folder in folders:
  log=(folder/'simulate.log').read_text()
  cp=[{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)} for line in log.splitlines() if line.startswith('STREAM_CHECKPOINT_DONE ')]
  checkpoints.append([row for row in cp if row['time_ps']<=data[0][1][count-1]['time_ps']])
 assert checkpoints[0]==checkpoints[1],'checkpoint mismatch within completed prefix'
 result={'status':'matched_completed_prefix','queries_compared':count,'checkpoints_compared':len(checkpoints[0]),'checkpoint_receipts':checkpoints[0],'total_queries':38,'last_common_query':data[0][1][count-1],'vector_manifest_sha256':data[0][0]['vector_manifest_sha256'],'scope':'Dynamic codec/epoch8 versus static codec/epoch6. Completed prefix only; remaining queries unproven. Simulation cycles, not wall-clock or board performance.','audit_snapshots':[x[2] for x in data],'source_sha256':sha(Path(__file__))}
 (a.output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(a.output/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('matched',count,'queries',result['last_common_query'])
if __name__=='__main__':main()
