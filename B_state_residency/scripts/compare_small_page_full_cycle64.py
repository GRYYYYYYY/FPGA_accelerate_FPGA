"""Matched actual-query comparison of two validated RTL prototype configurations."""
from pathlib import Path
import json,hashlib,re,csv
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/small_page_full_comparison_cycle64_20261023';
 pending=[]
 for folder in ['rtl_checkpoint_stream_cycle64_full_20261023','rtl_small_checkpoint_stream_full_20261023']:
  directory=ROOT/'results'/folder
  if json.loads((directory/'manifest.json').read_text())['status']!='passed' or not (directory/'final_audit.json').exists():pending.append(folder)
 if pending:
  print(json.dumps({'status':'waiting_for_complete_audited_inputs','pending':pending}));return
 out.mkdir()
 cases=[('old','rtl_checkpoint_stream_cycle64_full_20261023','checkpoint_vectors_full_20261023',1344),('small','rtl_small_checkpoint_stream_full_20261023','small_checkpoint_vectors_full_20261023',192)]
 data={};inputs={}
 for name,rtl,vec,stride in cases:
  rp=ROOT/'results'/rtl;vp=ROOT/'results'/vec;m=json.loads((rp/'manifest.json').read_text());v=json.loads((vp/'manifest.json').read_text())
  for p,x in [(rp,m),(vp,v)]:
   assert x['status']=='passed' and sha(p/'manifest.json')==json.loads((p/'completion_audit.json').read_text())['manifest_sha256']
   for fn,h in x['artifacts'].items():assert sha(p/fn)==h
   inputs[str(p/'manifest.json')]=sha(p/'manifest.json')
  assert m['vector_manifest_sha256']==sha(vp/'manifest.json')
  fa=json.loads((rp/'final_audit.json').read_text());assert fa['status']=='passed'
  assert fa.get('manifest_sha256',fa.get('manifest_snapshot_sha256'))==sha(rp/'manifest.json')
  assert len(m['checkpoint_receipts'])==v['counts']['12']
  receipts=[{k:int(val) for k,val in re.findall(r'(\w+)=(\d+)',row)} for row in m['query_receipts']]
  assert len(receipts)==len(v['selected_attempts'])==38
  previous={'time_ps':0,'commands':0,'transfers':0};rows=[]
  for i,(receipt,oracle) in enumerate(zip(receipts,v['queries_completed']),1):
   assert receipt['queries']==i and receipt['commands']==sum(oracle['cumulative_public_counts'].values()) and receipt['transfers']==oracle['cumulative_transfers']
   rows.append({'attempt':oracle['attempt'],'ns':(receipt['time_ps']-previous['time_ps'])//1000,'commands':receipt['commands']-previous['commands'],'transfers':receipt['transfers']-previous['transfers']});previous=receipt
  assert previous['time_ps']==m['end_ns']*1000
  data[name]={'rows':rows,'end_ns':m['end_ns'],'commands':v['public_commands'],'transfers':v['transfers'],'bytes':v['transfers']*stride,'capture_inputs':{n:h for n,h in v['inputs'].items() if '/real_field_values_' in n},'fields':v['field_replay']['field_accesses'],'checkpoints':len(m['checkpoint_receipts'])}
 assert data['old']['capture_inputs']==data['small']['capture_inputs'] and data['old']['fields']==data['small']['fields']==14047736
 rows=[]
 for a,b in zip(data['old']['rows'],data['small']['rows']):
  assert a['attempt']==b['attempt'];rows.append({'attempt':a['attempt'],'old_ns':a['ns'],'small_ns':b['ns'],'old_commands':a['commands'],'small_commands':b['commands'],'old_transfers':a['transfers'],'small_transfers':b['transfers']})
 with (out/'queries.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 a=data['old'];b=data['small'];result={'status':'passed','inputs':inputs,'queries':38,'field_accesses':14047736,'old':{k:v for k,v in a.items() if k not in ['rows','capture_inputs']},'small':{k:v for k,v in b.items() if k not in ['rows','capture_inputs']},'simulated_time_reduction_percent':100*(1-b['end_ns']/a['end_ns']),'byte_reduction_percent':100*(1-b['bytes']/a['bytes']),'queries_lower_simulated_time':sum(r['small_ns']<r['old_ns'] for r in rows),'scope':'Prototype-configuration comparison, not isolated page-size ablation. Changes include slots, codec, directory sizes/hash and cookie. Same trace/10ns simulation clock/periodic slave scheduling, cold clear included. Not full router, platform timing or board speedup.','source_sha256':sha(Path(__file__))}
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
