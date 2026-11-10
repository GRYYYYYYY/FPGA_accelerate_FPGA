"""Check all paired interval rows against source-audited original receipts."""
from pathlib import Path
import csv,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/sparse_writeback_full_intervals_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 assert sha(ROOT/'scripts/compare_sparse_writeback_full.py')==m['script_sha256']
 paths={'candidate':ROOT/'results/sparse_writeback_cycle64_full_20261024','baseline':ROOT/'results/record_epoch16_full_20261024'}
 parsed={}
 for label,path in paths.items():
  gate=path/'source_bound_audit.json';g=json.loads(gate.read_text());assert g['status']=='passed' and sha(gate)==m['gates'][label]
  assert sha(path/'manifest.json')==g['manifest_sha256']
  manifest=json.loads((path/'manifest.json').read_text())
  log=path/('simulate.log' if label=='candidate' else 'pilot/simulate.log')
  expected=manifest['log_sha256'] if label=='candidate' else manifest['cases']['pilot']['log_sha256']
  assert sha(log)==expected==m['logs'][label]
  parsed[label]=[{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)} for line in re.findall(r'^STREAM_QUERY_DONE (.+)$',log.read_text(),re.M)]
 assert sha(out/'intervals.csv')==m['intervals_sha256']
 rows=list(csv.DictReader((out/'intervals.csv').open()));assert len(rows)==38==m['queries']
 previous={'candidate':0,'baseline':0};saved=0
 for index,row in enumerate(rows):
  assert int(row['query'])==index+1
  durations={}
  for label in parsed:
   receipt=parsed[label][index];assert receipt['queries']==index+1
   assert receipt['commands']==int(row['commands']) and receipt['transfers']==int(row['transfers'])
   durations[label]=receipt['time_ps']-previous[label];previous[label]=receipt['time_ps']
   assert durations[label]==int(row[label+'_interval_ps'])
  delta=durations['baseline']-durations['candidate'];assert delta==int(row['saved_ps'])
  assert abs(float(row['reduction_fraction'])-(1-durations['candidate']/durations['baseline']))<1e-14
  saved+=delta
 assert saved==m['saved_ns']*1000 and previous['candidate']==m['candidate_end_ns']*1000 and previous['baseline']==m['baseline_end_ns']*1000
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'queries':len(rows),'source_audited_log_binding':True,'paired_interval_sums_close':True}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
