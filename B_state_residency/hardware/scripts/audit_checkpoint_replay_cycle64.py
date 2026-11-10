"""Final per-query and per-checkpoint audit for complete real RTL replay."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=ROOT/'results/rtl_checkpoint_stream_cycle64_full_20261023';vp=ROOT/'results/checkpoint_vectors_full_20261023'
 mp=out/'manifest.json';m=json.loads(mp.read_text());v=json.loads((vp/'manifest.json').read_text());audit=json.loads((vp/'query_audit.json').read_text())
 assert m['status']==v['status']==audit['status']=='passed'
 assert sha(mp)==json.loads((out/'completion_audit.json').read_text())['manifest_sha256']
 assert sha(vp/'manifest.json')==m['vector_manifest_sha256']==audit['manifest_snapshot_sha256']
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 for path,digest in m['sources'].items():assert sha(Path(path))==digest==sha(out/'sources'/Path(path).name)
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest
 for name,digest in v['artifacts'].items():assert sha(vp/name)==digest
 parse=lambda line:{k:int(val) for k,val in re.findall(r'(\w+)=(\d+)',line)}
 queries=list(map(parse,m['query_receipts']));checkpoints=list(map(parse,m['checkpoint_receipts']))
 assert len(queries)==38 and len(checkpoints)==31 and audit['queries_verified']==38
 per_query=[];old_commands=old_transfers=old_time=0
 for i,(observed,expected) in enumerate(zip(queries,audit['receipts']),1):
  assert observed['queries']==i
  assert observed['commands']==expected['cumulative_commands'] and observed['transfers']==expected['cumulative_transfers']
  assert observed['time_ps']>old_time
  local=[cp for cp in checkpoints if old_commands<cp['commands']<=observed['commands']]
  assert len(local)==expected['checkpoint_count'],expected['attempt']
  for cp in local:
   assert old_time<cp['time_ps']<observed['time_ps'] and old_transfers<=cp['transfers']<=observed['transfers']
  per_query.append({'attempt':expected['attempt'],'commands':observed['commands']-old_commands,'transfers':observed['transfers']-old_transfers,'checkpoint_count':len(local),'elapsed_ps':observed['time_ps']-old_time})
  old_commands=observed['commands'];old_transfers=observed['transfers'];old_time=observed['time_ps']
 assert [cp['checkpoints'] for cp in checkpoints]==list(range(1,32))
 assert all(a['commands']<b['commands'] and a['time_ps']<b['time_ps'] for a,b in zip(checkpoints,checkpoints[1:]))
 assert old_time==m['end_ns']*1000
 assert (old_commands,old_transfers,audit['receipts'][-1]['cumulative_fields'])==(21662794,2743929,14047736)
 log=(out/'simulate.log').read_text()
 assert log.count('TEST_PASS memory_endpoint ')==1 and 'Fatal:' not in log
 result={'status':'passed','manifest_sha256':sha(mp),'vector_audit_sha256':sha(vp/'query_audit.json'),'queries':per_query,'checkpoint_receipts':checkpoints,'end_ns':m['end_ns'],'source_sha256':sha(Path(__file__)),'scope':'Full 38 actual-query public-port/raw-byte RTL replay with 31 retained checkpoints. Behavioral simulation only; no full router, SDF, physical clock closure or board speedup.'}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('FULL_REPLAY_AUDIT_PASS queries=38 checkpoints=31')
if __name__=='__main__':main()
