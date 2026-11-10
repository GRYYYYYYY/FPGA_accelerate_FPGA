"""Read-only live audit: process identity plus completed replay receipts."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'results/rtl_checkpoint_stream_full_20261023'
 m=json.loads((out/'manifest.json').read_text());v=json.loads((ROOT/'results/checkpoint_vectors_full_20261023/query_audit.json').read_text())
 assert v['status']=='passed' and v['queries_verified']==38
 text=(out/'simulate.log').read_text();assert 'Fatal:' not in text
 parse=lambda line:{k:int(val) for k,val in re.findall(r'(\w+)=(\d+)',line)}
 queries=[parse(line) for line in re.findall(r'^STREAM_QUERY_DONE (.+)$',text,re.M)]
 checkpoints=[parse(line) for line in re.findall(r'^STREAM_CHECKPOINT_DONE (.+)$',text,re.M)]
 old_commands=old_time=0
 for i,row in enumerate(queries,1):
  expected=v['receipts'][i-1]
  assert row['queries']==i and row['commands']==expected['cumulative_commands'] and row['transfers']==expected['cumulative_transfers']
  cp=[c for c in checkpoints if old_commands<c['commands']<=row['commands']]
  assert len(cp)==expected['checkpoint_count'] and all(old_time<c['time_ps']<row['time_ps'] for c in cp)
  old_commands=row['commands'];old_time=row['time_ps']
 assert [c['checkpoints'] for c in checkpoints]==list(range(1,len(checkpoints)+1))
 processes=[]
 def inspect(pid):
  directory=Path('/proc')/str(pid)
  try:
   cmd=(directory/'cmdline').read_bytes().replace(b'\x00',b' ').decode(errors='replace')
   stat=(directory/'stat').read_text().rsplit(')',1)[1].split()
   children=set()
   for child_file in (directory/'task').glob('*/children'):
    try:children.update(child_file.read_text().split())
    except FileNotFoundError:pass
  except FileNotFoundError:return
  processes.append({'pid':pid,'state':stat[0],'command':cmd})
  for child in children:inspect(int(child))
 stage=m['commands'][-1]
 if m['status']=='running':
  assert stage['stage']=='simulate' and stage['exit_code'] is None
  inspect(stage['pid'])
  assert any('xsimk' in p['command'] and p['state']!='Z' for p in processes),'Live simulation kernel not confirmed; investigate without restarting'
 elif m['status']=='passed':assert stage['exit_code']==0
 else:raise AssertionError(m.get('error',m['status']))
 result={'status':'verified_live_partial' if m['status']=='running' else 'terminal_receipts_verified_final_audit_pending','completed_queries':len(queries),'checkpoint_receipts':len(checkpoints),'last_query':queries[-1] if queries else None,'last_checkpoint':checkpoints[-1] if checkpoints else None,'processes':processes,'log_bytes':len(text.encode()),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (out/'progress_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:val for k,val in result.items() if k!='processes'},indent=2))
 print('live process states',[(p['pid'],p['state']) for p in processes])
if __name__=='__main__':main()
