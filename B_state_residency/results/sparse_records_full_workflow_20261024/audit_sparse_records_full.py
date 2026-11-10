"""Independent full native sparse-record replay audit with WB/RF census."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def term(t):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
def receipts(log,prefix):
 return [{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',x)} for x in re.findall('^'+prefix+r' (.+)$',log,re.M)]
def main():
 out=ROOT/'results/sparse_records_full_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 pilot=ROOT/'results/sparse_records_20261024';pm=json.loads((pilot/'manifest.json').read_text());assert pm['status']=='passed'
 base=ROOT/'results/sparse_writeback_cycle64_full_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 for key,path in [('wb_full',base/'source_bound_audit.json'),('combined_pilot',pilot/'source_bound_audit.json')]:
  assert sha(path)==m['gates'][key] and json.loads(path.read_text())['status']=='passed'
 assert sha(base/'manifest.json')==m['baseline_manifest_sha256']
 assert m['sources']==pm['cases']['candidate']['sources']
 for name,digest in m['sources'].items():assert sha(out/'sources'/name)==digest
 tb=(out/'sources/tb_sparse_records_pilot.sv').read_text()
 for fragment in ['longint unsigned cycle=0;','module tb_sparse_records_large;','.REPLAY_FRAMES(163840)','.REPLAY_INDEX(18)','.EXPECT_COMMANDS(21466914)','.EXPECT_TRANSFERS(2472066)','.EXPECT_QUERIES(38)','.EXPECT_CHECKPOINTS(28)']:assert fragment in tb
 commands=m['commands'];assert [s['stage'] for s in commands]==['compile','elaborate','simulate'] and all(s['exit_code']==0 for s in commands)
 assert commands[1]['argv'][1]=='tb_sparse_records_large'
 assert set(Path(x) for x in commands[0]['argv'] if x.endswith('.sv'))=={out/'sources'/name for name in m['sources']}
 assert commands[2]['argv'][6:]==bm['commands'][-1]['argv'][6:]
 assert sha(ROOT/'hardware/scripts/run_sparse_records_full.py')==m['runner_sha256']
 vec=ROOT/'results/small_checkpoint_vectors_full_20261023';vm=json.loads((vec/'manifest.json').read_text());assert vm['status']=='passed' and sha(vec/'manifest.json')==m['vector_manifest_sha256']
 for filename in ['actual.txt','pages.hex']:assert sha(vec/filename)==vm['artifacts'][filename]
 log=(out/'simulate.log').read_text();old=(base/'simulate.log').read_text();assert sha(out/'simulate.log')==m['log_sha256'] and 'Fatal:' not in log and '$finish' in log
 native=ROOT/'results/record_epoch16_full_20261024';nm=json.loads((native/'manifest.json').read_text());assert nm['status']=='passed'
 na=json.loads((native/'source_bound_audit.json').read_text());assert na['status']=='passed' and na['manifest_sha256']==sha(native/'manifest.json')
 nlog=(native/'pilot/simulate.log').read_text()
 for prefix,length in [('STREAM_QUERY_DONE',38),('STREAM_CHECKPOINT_DONE',28)]:
  q,r,n=receipts(log,prefix),receipts(old,prefix),receipts(nlog,prefix);assert len(q)==len(r)==len(n)==length
  strip=lambda rows:[{k:v for k,v in x.items() if k!='time_ps'} for x in rows]
  assert strip(q)==strip(r)==strip(n)
 counts,previous=term(log),term(old);assert counts==m['counts'] and counts.keys()==previous.keys()
 retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1]);assert retries==m['finish_retries'] and counts['checks']==vm['public_commands']+retries
 assert all(counts[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
 assert counts['fences']==38 and counts['transfers']==2472066 and counts['errors']==0
 for key,source in [('end_ns',log),('wb_only_end_ns',old),('native16_end_ns',nlog)]:assert m[key]==int(re.search(r'\$finish called at time : (\d+) ns',source)[1])
 # Fresh independent census. Full protocol correctness still comes from RTL monitors.
 census={5:{'present':0,'absent':0,'pages':0},6:{'present':0,'absent':0,'pages':0}};transfers=0
 with (vec/'actual.txt').open() as cmd,(vec/'pages.hex').open() as pages:
  for line in cmd:
   op=int(line.split(' ',1)[0],16)
   if op in (5,6):
    assert int(line.rsplit(None,1)[-1],16)==transfers
    words=[pages.readline() for _ in range(3)];assert all(words);transfers+=1
    present=(int(words[0],16)&255).bit_count();census[op]['present']+=present;census[op]['absent']+=8-present;census[op]['pages']+=1
  assert not pages.read()
 assert transfers==2472066
 for op,direction,fields in [(5,'WB',['exports','omitted','masks']),(6,'RF',['beats','omitted','masks'])]:
  match=re.search('SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),log);assert match
  current=dict(zip(fields,map(int,match.groups())))
  assert current==m[direction.lower()+'_counts']==dict(zip(fields,[census[op]['present'],census[op]['absent'],census[op]['pages']]))
 # Paired whole-query intervals, including checkpoint preflush, retries and TB pacing.
 nr,wr,cr=[receipts(t,'STREAM_QUERY_DONE') for t in [nlog,old,log]];rows=[];last=[0,0,0]
 for index,items in enumerate(zip(nr,wr,cr),1):
  intervals=[x['time_ps']-oldtime for x,oldtime in zip(items,last)];assert all(x>0 for x in intervals)
  rows.append({'query':index,'native16_interval_ps':intervals[0],'wb_only_interval_ps':intervals[1],'combined_interval_ps':intervals[2],'incremental_reduction_fraction':1-intervals[2]/intervals[1]})
  last=[x['time_ps'] for x in items]
 for column,key in [('native16_interval_ps','native16_end_ns'),('wb_only_interval_ps','wb_only_end_ns'),('combined_interval_ps','end_ns')]:assert sum(r[column] for r in rows)==m[key]*1000
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'queries':38,'checkpoints':28,'transfers':transfers,'finish_retries':retries,'census':census,'end_ns':m['end_ns'],'wb_only_end_ns':m['wb_only_end_ns'],'native16_end_ns':m['native16_end_ns'],'incremental_time_reduction_fraction':1-m['end_ns']/m['wb_only_end_ns'],'native16_time_reduction_fraction':1-m['end_ns']/m['native16_end_ns'],'faster_query_intervals_vs_wb':sum(r['incremental_reduction_fraction']>0 for r in rows),'slower_query_intervals_vs_wb':sum(r['incremental_reduction_fraction']<0 for r in rows),'axi_payload_bytes':transfers*192,'scope':'38-query native state-endpoint access replay, same page bytes. Not complete routing, platform closure or board speedup.'}
 (out/'query_intervals.json').write_text(json.dumps({'status':'passed','rows':rows,'scope':'Receipt intervals include TB pacing and checkpoint preflush.'},indent=2)+'\n')
 result['query_intervals_sha256']=sha(out/'query_intervals.json')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
