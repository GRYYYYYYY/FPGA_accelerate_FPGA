"""Attribute measured RTL simulation intervals to audited complete queries."""
from pathlib import Path
import json,re,hashlib,csv
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/small_full_query_concentration_20261023';out.mkdir()
 run=ROOT/'results/rtl_small_checkpoint_stream_full_20261023';mp=run/'manifest.json';m=json.loads(mp.read_text());a=json.loads((run/'final_audit.json').read_text())
 assert m['status']==a['status']=='passed' and a['manifest_snapshot_sha256']==sha(mp)
 vp=ROOT/'results/small_checkpoint_vectors_full_20261023';qa=json.loads((vp/'query_audit.json').read_text());assert qa['status']=='passed' and qa['manifest_snapshot_sha256']==m['vector_manifest_sha256']==sha(vp/'manifest.json')
 previous={'time_ps':0,'commands':0,'transfers':0};rows=[]
 for line,ref in zip(m['query_receipts'],qa['receipts']):
  q={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)}
  assert q['commands']==ref['cumulative_commands'] and q['transfers']==ref['cumulative_transfers']
  rows.append({'query':q['queries'],'attempt':ref['attempt'],'elapsed_ns':(q['time_ps']-previous['time_ps'])//1000,'commands':q['commands']-previous['commands'],'transfers':q['transfers']-previous['transfers'],'checkpoints':ref['checkpoint_count']});previous=q
 assert len(rows)==38 and sum(x['elapsed_ns'] for x in rows)==m['end_ns'] and sum(x['checkpoints'] for x in rows)==28
 ordered=sorted(rows,key=lambda x:x['elapsed_ns'],reverse=True)
 result={'status':'verified_interval_accounting','queries':38,'total_ns':m['end_ns'],'top_queries':ordered[:5],'top2_time_fraction':sum(x['elapsed_ns'] for x in ordered[:2])/m['end_ns'],'top2_transfer_fraction':sum(x['transfers'] for x in ordered[:2])/m['counts']['transfers'],'top2_checkpoints':sum(x['checkpoints'] for x in ordered[:2]),'inputs':{str(p):sha(p) for p in [mp,run/'final_audit.json',vp/'query_audit.json']},'source_sha256':sha(Path(__file__)),'scope':'Simulated query intervals include transfer, host pacing, checkpoints and cold clear in first query; not isolated component latency or host runtime. Large-query completion gaps alone do not establish a stall.'}
 with (out/'queries.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(result['top2_time_fraction'],result['top2_transfer_fraction'],result['top2_checkpoints'])
if __name__=='__main__':main()
