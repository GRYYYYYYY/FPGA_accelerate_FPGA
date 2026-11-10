"""Source-bound sparse RF incremental ablation, boundaries and actual wrap."""
from pathlib import Path
import hashlib,json,re
from make_sparse_records import render as rtl_render
from make_sparse_records_tb import render as tb_render
from make_sparse_records_boundaries_tb import render as boundary_render
from make_sparse_records_wrap_tb import render as wrap_render
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def txtsha(s):return hashlib.sha256(s.encode()).hexdigest()
def main():
 out=ROOT/'results/sparse_records_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed'
 base=ROOT/'results/sparse_writeback_retry_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert sha(base/'manifest.json')==m['baseline_manifest_sha256'] and sha(base/'source_bound_audit.json')==m['baseline_audit_sha256']
 assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 native={p.name:sha(p) for p in (base/'candidate/sources').glob('*.sv') if not p.name.startswith('tb_')}
 assert all(v==bm['cases']['candidate']['sources'][k] for k,v in native.items())
 candidate=native|{name:txtsha(s) for name,s in rtl_render().items()};tbs=tb_render()
 for name,digest in m['scripts'].items():assert sha(ROOT/name)==digest
 evidence={}
 for case,tb,top,marker in [('masks','tb_sparse_records_masks.sv','tb_sparse_records_masks','SPARSE_RECORD_MASKS_PASS masks=256 transfers=512 fences=256'),('faults','tb_sparse_records_faults.sv','tb_sparse_records_faults','RESPONSE_FAULT_PASS errors=9 transfers=68 checks=267'),('stalls','tb_sparse_records_stalls.sv','tb_sparse_records_stalls','SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4'),('control','tb_sparse_records_pilot.sv','tb_sparse_records_control','TEST_PASS memory_endpoint'),('candidate','tb_sparse_records_pilot.sv','tb_sparse_records_small','TEST_PASS memory_endpoint')]:
  row=m['cases'][case];expected=(native if case=='control' else candidate)|{tb:txtsha(tbs[tb])};d=out/case
  check_case(d,row,expected,top,marker);evidence[case]={'log_sha256':row['log_sha256']}
  if case=='stalls':assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in (d/'simulate.log').read_text()
  if case in ('control','candidate'):assert row['commands'][-1]['argv'][6:]==bm['cases']['candidate']['commands'][-1]['argv'][6:]
  for label,fields in [('WB',['exports','omitted','masks']),('RF',['beats','omitted','masks'])]:
   match=re.search('SPARSE_'+label+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),(d/'simulate.log').read_text());assert match
   assert row[label.lower()+'_counts']==dict(zip(fields,map(int,match.groups())))
 # All 256 masks include empty and full pages and present-zero values.
 assert m['cases']['masks']['wb_counts']=={'exports':1024,'omitted':1024,'masks':256}
 assert m['cases']['masks']['rf_counts']=={'beats':1024,'omitted':1024,'masks':256}
 # Freeze/check both additional protocol-focused tests.
 for folder,tb,top,render,marker,extra in [('sparse_records_boundaries_20261024','tb_sparse_records_boundaries.sv','tb_sparse_records_boundaries',boundary_render,'SPARSE_RF_BOUNDARIES_PASS checks=33',False),('sparse_records_wrap_20261024','tb_sparse_records_wrap.sv','tb_sparse_records_wrap',wrap_render,'EPOCH16_WRAP_PASS queries=65536 transfers=8 data_queries=4 tag_wraps=16384 epoch_wraps=1 clear_cycles=128 ',True)]:
  d=ROOT/'results'/folder;r=json.loads((d/'manifest.json').read_text());assert r['status']=='passed'
  runner='run_sparse_records_wrap.py' if extra else 'run_sparse_records_boundaries.py';generator='make_sparse_records_wrap_tb.py' if extra else 'make_sparse_records_boundaries_tb.py'
  assert sha(ROOT/'hardware/scripts'/runner)==r['runner_sha256'] and sha(ROOT/'hardware/scripts'/generator)==r['tb_generator_sha256']
  expected=(candidate if extra else {k:v for k,v in candidate.items() if k in ('scratch_frame_store_bram.sv','scratch_page_controller_small.sv')})|{tb:txtsha(render())}
  check_case(d,r,expected,top,marker);evidence[folder]={'manifest_sha256':sha(d/'manifest.json'),'log_sha256':r['log_sha256']}
 # Join actual vectors with independent pages by transfer index, for both directions.
 vector=ROOT/'results/small_checkpoint_vectors_pilot_20261023';vm=json.loads((vector/'manifest.json').read_text());assert vm['status']=='passed'
 for filename in ['actual.txt','pages.hex']:assert sha(vector/filename)==vm['artifacts'][filename]
 census={5:{'present':0,'absent':0,'pages':0},6:{'present':0,'absent':0,'pages':0}};transfers=0
 with (vector/'actual.txt').open() as commands,(vector/'pages.hex').open() as pages:
  for line in commands:
   a=[int(x,16) for x in line.split()]
   if a[0] in (5,6):
    assert a[-1]==transfers;words=[pages.readline() for _ in range(3)];assert all(words);transfers+=1
    present=(int(words[0],16)&255).bit_count();census[a[0]]['present']+=present;census[a[0]]['absent']+=8-present;census[a[0]]['pages']+=1
  assert not pages.read()
 assert transfers==vm['transfers']==5183
 cc=m['cases']['candidate'];ctrl=m['cases']['control']
 assert cc['wb_counts']==ctrl['wb_counts']=={'exports':census[5]['present'],'omitted':census[5]['absent'],'masks':census[5]['pages']}
 assert cc['rf_counts']=={'beats':census[6]['present'],'omitted':census[6]['absent'],'masks':census[6]['pages']}
 assert ctrl['rf_counts']=={'beats':0,'omitted':0,'masks':0}
 old=(base/'candidate/simulate.log').read_text();previous=term(old)
 for case in ('control','candidate'):
  log=(out/case/'simulate.log').read_text();row=m['cases'][case];counts=term(log)
  assert row['counts']==counts and counts.keys()==previous.keys()
  assert row['finish_retries']==int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
  assert counts['checks']==75194+row['finish_retries']
  assert all(counts[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
  for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
   strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
   assert strip(log)==strip(old)
  assert row['end_ns']==int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
 control=(out/'control/simulate.log').read_text()
 for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint','FINISH_RETRY_COUNTS','SPARSE_WB_COUNTS']:
  assert re.findall('^'+prefix+r' (.+)$',control,re.M)==re.findall('^'+prefix+r' (.+)$',old,re.M)
 assert ctrl['end_ns']==bm['cases']['candidate']['end_ns']
 increment=1-cc['end_ns']/ctrl['end_ns'];assert m['incremental_time_reduction_fraction']==increment
 native=json.loads((ROOT/'results/record_epoch16_pilot_20261024/manifest.json').read_text())['cases']['pilot']['end_ns']
 result={'status':'passed','manifest_sha256':sha(mp),'auditor_sha256':sha(Path(__file__)),'evidence':evidence,'vector_manifest_sha256':sha(vector/'manifest.json'),'census':census,'queries':19,'transfers':transfers,'wb_only_end_ns':ctrl['end_ns'],'combined_end_ns':cc['end_ns'],'native16_end_ns':native,'incremental_time_reduction_fraction':increment,'native16_time_reduction_fraction':1-cc['end_ns']/native,'candidate_finish_retries':cc['finish_retries'],'scope':'Native closed adapter sparse-WB+RF 19-query actual replay and small-capacity lifetime checks; same192B/AXI, no full38/board/complete-router claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
def term(t):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
def check_case(d,row,expected,top,marker):
 assert row['status']=='passed' and row['sources']==expected
 for name,digest in expected.items():assert sha(d/'sources'/name)==digest
 commands=row['commands'];assert [s['stage'] for s in commands]==['compile','elaborate','simulate'] and all(s['exit_code']==0 for s in commands)
 assert commands[1]['argv'][1]==top
 assert set(Path(x) for x in commands[0]['argv'] if x.endswith('.sv'))=={d/'sources'/name for name in expected}
 log=(d/'simulate.log').read_text();assert sha(d/'simulate.log')==row['log_sha256'] and marker in log and 'Fatal:' not in log and '$finish' in log
if __name__=='__main__':main()
