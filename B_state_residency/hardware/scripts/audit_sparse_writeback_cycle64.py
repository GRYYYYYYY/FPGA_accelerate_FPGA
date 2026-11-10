"""Audit signed32/unsigned64 pilot equality or complete sparse-WB actual replay."""
from pathlib import Path
import argparse,hashlib,json,re
from make_sparse_writeback import render as rtl_render
from make_sparse_writeback_cycle64_tb import render
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args()
 out=ROOT/'results'/('sparse_writeback_cycle64_full_20261024' if args.full else 'sparse_writeback_cycle64_pilot_20261024')
 m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and m['full']==args.full
 base=ROOT/m['baseline'];bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed' and sha(base/'manifest.json')==m['baseline_manifest_sha256']
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items() if not Path(k).name.startswith('tb_')}
 expected|={name:hashlib.sha256(s.encode()).hexdigest() for name,s in rtl_render().items()}
 expected['tb_sparse_writeback_cycle64.sv']=hashlib.sha256(render().encode()).hexdigest()
 assert m['sources']==expected
 for name,digest in expected.items():assert sha(out/'sources'/name)==digest
 assert 'longint unsigned cycle=0;' in (out/'sources/tb_sparse_writeback_cycle64.sv').read_text()
 steps=m['commands'];assert [s['stage'] for s in steps]==['compile','elaborate','simulate'] and all(s['exit_code']==0 for s in steps)
 assert set(Path(x) for x in steps[0]['argv'] if x.endswith('.sv'))=={out/'sources'/name for name in expected}
 assert steps[1]['argv'][1]==('tb_sparse_writeback_cycle64_large' if args.full else 'tb_sparse_writeback_cycle64_small')
 assert sha(ROOT/'hardware/scripts/run_sparse_writeback_cycle64.py')==m['runner_sha256']
 gates={'sparse_pilot':ROOT/'results/sparse_writeback_retry_20261024/source_bound_audit.json','native_full':ROOT/'results/record_epoch16_full_20261024/source_bound_audit.json'}
 if args.full:gates['cycle64_pilot']=ROOT/'results/sparse_writeback_cycle64_pilot_20261024/source_bound_audit.json'
 assert set(m['gates'])==set(gates)
 for key,path in gates.items():assert sha(path)==m['gates'][key] and json.loads(path.read_text())['status']=='passed'
 vec=ROOT/'results'/('small_checkpoint_vectors_full_20261023' if args.full else 'small_checkpoint_vectors_pilot_20261023')
 vm=json.loads((vec/'manifest.json').read_text());assert vm['status']=='passed' and sha(vec/'manifest.json')==m['vector_manifest_sha256']
 for name in ['actual.txt','pages.hex']:assert sha(vec/name)==vm['artifacts'][name]
 assert steps[2]['argv'][6:]==bm['cases']['pilot']['commands'][-1]['argv'][6:]
 log=(out/'simulate.log').read_text();old=(base/'pilot/simulate.log').read_text();assert sha(out/'simulate.log')==m['log_sha256']
 assert 'Fatal:' not in log and '$finish' in log
 for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
  strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
  assert strip(log)==strip(old)
 terminal=lambda t:{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
 current,previous=terminal(log),terminal(old);assert current==m['counts'] and current.keys()==previous.keys()
 retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1]);assert retries==m['finish_retries']
 assert current['checks']==previous['checks']+retries
 assert all(current[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
 assert m['end_ns']==int(re.search(r'\$finish called at time : (\d+) ns',log)[1]) and m['baseline_end_ns']==bm['cases']['pilot']['end_ns']
 assert current['fences']==vm['queries'] and current['transfers']==vm['transfers']
 # Independent WB-only record census, joined by transfer index to public vectors.
 exports=omitted=masks=transfers=0
 with (vec/'actual.txt').open() as commands,(vec/'pages.hex').open() as pages:
  for line in commands:
   # Only transfer headers need full parsing; other public rows remain hash-bound.
   op=int(line.split(' ',1)[0],16)
   if op in (5,6):
    a=line.split();assert int(a[-1],16)==transfers
    words=[pages.readline() for _ in range(3)];assert all(words);transfers+=1
    if op==5:
     bitmap=int(words[0],16)&255;exports+=bitmap.bit_count();omitted+=8-bitmap.bit_count();masks+=1
  assert not pages.read()
 assert transfers==vm['transfers'] and masks==vm['counts']['5']
 sparse={k:int(v) for k,v in zip(['exports','omitted','masks'],re.search(r'SPARSE_WB_COUNTS exports=(\d+) omitted=(\d+) masks=(\d+)',log).groups())}
 assert sparse==m['sparse_counts']=={'exports':exports,'omitted':omitted,'masks':masks}
 if not args.full:
  signed=(ROOT/'results/sparse_writeback_retry_20261024/candidate/simulate.log').read_text()
  for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint','FINISH_RETRY_COUNTS','SPARSE_WB_COUNTS']:
   assert re.findall('^'+prefix+r' (.+)$',log,re.M)==re.findall('^'+prefix+r' (.+)$',signed,re.M)
  assert m['end_ns']==json.loads((ROOT/'results/sparse_writeback_retry_20261024/manifest.json').read_text())['cases']['candidate']['end_ns']
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'queries':current['fences'],'transfers':transfers,'sparse_counts':sparse,'finish_retries':retries,'end_ns':m['end_ns'],'baseline_end_ns':m['baseline_end_ns'],'time_reduction_fraction':1-m['end_ns']/m['baseline_end_ns'],'unsigned64_pilot_matches_signed32':not args.full,'scope':'Sparse WB native endpoint actual-value access replay; identical AXI bytes, no full-router/board claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
