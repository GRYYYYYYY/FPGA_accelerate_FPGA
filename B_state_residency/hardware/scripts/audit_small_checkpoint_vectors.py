"""Compare every completed query receipt against the separate retained planner."""
from pathlib import Path
from collections import Counter
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--progress',action='store_true');a=ap.parse_args();out=a.directory.resolve()
 mp=out/'manifest.json';snapshot=mp.read_bytes();m=json.loads(snapshot)
 pp=ROOT/'results/small_page_checkpoint_20261023/manifest.json';assert sha(pp)=='5e5c2e244a9d3e4aa476f334f964ee2fa0a5336d19ce54103aa26b8185be6825'
 p=json.loads(pp.read_text());plans={q['attempt']:q for q in p['queries']}
 assert m['status'] in ('running','passed')
 if not a.progress:assert m['status']=='passed'
 assert [r['attempt'] for r in m['queries_completed']]==m['selected_attempts'][:len(m['queries_completed'])]
 counts=Counter();receipts=[]
 for i,row in enumerate(m['queries_completed'],1):
  plan=plans[row['attempt']]
  for key,value in plan['counts'].items():
   if not key.startswith('max_'):counts[key]+=value
  public={'0':i,'1':counts['bindings'],'2':counts['reads'],'3':counts['writes'],'4':counts['releases'],'5':counts['writebacks'],'6':counts['refills'],'10':i,'11':i,'12':counts['checkpoints']}
  actual=row['cumulative_public_counts']
  assert all(actual.get(k,0)==v for k,v in public.items()),row['attempt']
  assert not set(actual)-set(public),row['attempt']
  field=row['cumulative_field_counts']
  assert field['field_accesses']==counts['accesses'] and field['queries']==i
  for key in ['writebacks','refills','checkpoints']:assert field.get(key,0)==counts[key]
  assert row['cumulative_transfers']==counts['writebacks']+counts['refills']
  receipts.append({'attempt':row['attempt'],'checkpoint_count':plan['counts'].get('checkpoints',0),'cumulative_commands':sum(public.values()),'cumulative_transfers':row['cumulative_transfers'],'cumulative_fields':counts['accesses']})
 for name,digest in m['sources'].items():assert sha(Path(name))==digest
 if m['status']=='passed':
  assert len(receipts)==len(m['selected_attempts'])==m['queries']
  assert sha(mp)==json.loads((out/'completion_audit.json').read_text())['manifest_sha256']
  for name,digest in m['artifacts'].items():assert sha(out/name)==digest
  assert m['public_commands']==receipts[-1]['cumulative_commands']
  assert m['maximum_transaction']<65536 and m['maximum_generation']<65536 and m['peak_reserved_owners']<=163840
  assert m['counts'].get('12',0)==counts['checkpoints']
 result={'status':'passed' if m['status']=='passed' else 'verified_partial_receipts','queries_verified':len(receipts),'total_queries':len(m['selected_attempts']),'manifest_snapshot_sha256':hashlib.sha256(snapshot).hexdigest(),'planner_sha256':sha(pp),'receipts':receipts,'source_sha256':sha(Path(__file__)),'rtl_executed':False}
 path=out/('progress_audit.json' if a.progress else 'query_audit.json');path.write_text(json.dumps(result,indent=2)+'\n')
 if not a.progress:(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 print(result['status'],len(receipts),'queries',receipts[-1])
if __name__=='__main__':main()
