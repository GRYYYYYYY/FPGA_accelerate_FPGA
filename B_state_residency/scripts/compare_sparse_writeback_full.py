"""Paired full-replay receipt intervals; not standalone query or board latency."""
from pathlib import Path
import csv,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/sparse_writeback_full_intervals_20261024';out.mkdir()
 candidate=ROOT/'results/sparse_writeback_cycle64_full_20261024'
 baseline=ROOT/'results/record_epoch16_full_20261024'
 gates={}
 for name,path in [('candidate',candidate),('baseline',baseline)]:
  gate=path/'source_bound_audit.json';g=json.loads(gate.read_text());assert g['status']=='passed';gates[name]=sha(gate)
 m=json.loads((candidate/'manifest.json').read_text());assert m['status']=='passed'
 logs={'candidate':candidate/'simulate.log','baseline':baseline/'pilot/simulate.log'}
 texts={k:p.read_text() for k,p in logs.items()}
 for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
  receipts={k:re.findall('^'+prefix+r' (.+)$',text,re.M) for k,text in texts.items()}
  stripped={k:[re.sub(r' ?time_ps=\d+','',line) for line in lines] for k,lines in receipts.items()}
  assert stripped['candidate']==stripped['baseline']
 queries={k:[{a:int(b) for a,b in re.findall(r'(\w+)=(\d+)',line)} for line in re.findall(r'^STREAM_QUERY_DONE (.+)$',text,re.M)] for k,text in texts.items()}
 assert all(len(v)==38 for v in queries.values())
 rows=[];last={'candidate':0,'baseline':0}
 for index in range(38):
  endpoints={key:queries[key][index]['time_ps'] for key in queries}
  durations={key:endpoints[key]-last[key] for key in queries}
  assert all(v>0 for v in durations.values())
  row={'query':index+1,'commands':queries['candidate'][index]['commands'],'transfers':queries['candidate'][index]['transfers'],'baseline_interval_ps':durations['baseline'],'candidate_interval_ps':durations['candidate'],'saved_ps':durations['baseline']-durations['candidate'],'reduction_fraction':1-durations['candidate']/durations['baseline']}
  rows.append(row);last=endpoints
 assert last['candidate']==m['end_ns']*1000 and last['baseline']==m['baseline_end_ns']*1000
 assert sum(r['saved_ps'] for r in rows)==(m['baseline_end_ns']-m['end_ns'])*1000
 with (out/'intervals.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 result={'status':'passed','script_sha256':sha(Path(__file__)),'gates':gates,'logs':{k:sha(p) for k,p in logs.items()},'queries':38,'faster':sum(r['saved_ps']>0 for r in rows),'same':sum(r['saved_ps']==0 for r in rows),'slower':sum(r['saved_ps']<0 for r in rows),'baseline_end_ns':m['baseline_end_ns'],'candidate_end_ns':m['end_ns'],'saved_ns':m['baseline_end_ns']-m['end_ns'],'total_reduction_fraction':1-m['end_ns']/m['baseline_end_ns'],'minimum_interval_reduction_fraction':min(r['reduction_fraction'] for r in rows),'maximum_interval_reduction_fraction':max(r['reduction_fraction'] for r in rows),'intervals_sha256':sha(out/'intervals.csv'),'scope':'Paired cumulative query-receipt intervals with original checkpoints/initialization/TB pacing; not isolated query search time or board speedup.'}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
