"""Join paired query intervals with independent WB bitmap work; no causal fit."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def receipts(p):
 result=[]
 for match in re.finditer(r'^STREAM_QUERY_DONE queries=(\d+) commands=(\d+) transfers=(\d+) time_ps=(\d+)$',p.read_text(),re.M):
  result.append(tuple(map(int,match.groups())))
 return result

def main():
 base=ROOT/'results/sparse_records_20261024';audit=json.loads((base/'source_bound_audit.json').read_text());assert audit['status']=='passed'
 m=json.loads((base/'manifest.json').read_text());assert m['status']=='passed'
 a,b=receipts(base/'control/simulate.log'),receipts(base/'candidate/simulate.log');assert len(a)==len(b)==19
 rows=[];last_a=last_b=0
 for old,new in zip(a,b):
  assert old[:3]==new[:3]
  dt_a,dt_b=old[3]-last_a,new[3]-last_b
  rows.append({'query':old[0],'control_interval_ps':dt_a,'candidate_interval_ps':dt_b,'reduction_fraction':1-dt_b/dt_a,'writebacks':0,'refills':0,'present_wb_records':0,'omitted_wb_records':0,'present_rf_records':0,'omitted_rf_records':0})
  last_a,last_b=old[3],new[3]
 vec=ROOT/'results/small_checkpoint_vectors_pilot_20261023';vm=json.loads((vec/'manifest.json').read_text())
 for name in ['actual.txt','pages.hex']:assert sha(vec/name)==vm['artifacts'][name]
 query=0;transfers=0
 with (vec/'actual.txt').open() as commands,(vec/'pages.hex').open() as pages:
  for line in commands:
   op=int(line.split(' ',1)[0],16)
   if op in (5,6):
    words=[pages.readline() for _ in range(3)];assert all(words);transfers+=1
    if op==5:
     present=(int(words[0],16)&255).bit_count();rows[query]['writebacks']+=1;rows[query]['present_wb_records']+=present;rows[query]['omitted_wb_records']+=8-present
    else:
     present=(int(words[0],16)&255).bit_count();rows[query]['refills']+=1;rows[query]['present_rf_records']+=present;rows[query]['omitted_rf_records']+=8-present
   if op==11:query+=1
  assert not pages.read()
 assert query==19 and transfers==5183
 assert sum(r['omitted_wb_records'] for r in rows)==audit['census']['5']['absent']
 assert sum(r['omitted_rf_records'] for r in rows)==audit['census']['6']['absent']
 assert sum(r['control_interval_ps'] for r in rows)==m['cases']['control']['end_ns']*1000
 assert sum(r['candidate_interval_ps'] for r in rows)==m['cases']['candidate']['end_ns']*1000
 result={'status':'passed','audit_sha256':sha(base/'source_bound_audit.json'),'script_sha256':sha(Path(__file__)),'queries':19,'faster_queries':sum(r['reduction_fraction']>0 for r in rows),'slower_queries':sum(r['reduction_fraction']<0 for r in rows),'unchanged_queries':sum(r['reduction_fraction']==0 for r in rows),'rows':rows,'scope':'Receipt intervals include fixed TB pacing, retries and phase-shifted backpressure. Work counts describe WB and RF density, not a causal cycle estimate.'}
 out=ROOT/'results/sparse_records_pilot_intervals_20261024';out.mkdir();(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
 print('range',min(r['reduction_fraction'] for r in rows),max(r['reduction_fraction'] for r in rows))
if __name__=='__main__':main()
