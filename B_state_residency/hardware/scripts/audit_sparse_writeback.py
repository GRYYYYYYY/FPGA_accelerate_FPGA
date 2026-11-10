"""Independent frozen-source and actual-vector audit of sparse WB evidence."""
from pathlib import Path
import hashlib,json,re
from make_sparse_writeback import render as rtl_render
from make_sparse_writeback_tb import render as tb_render,adapt
from make_sparse_writeback_retry_tb import render as retry_render
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def main():
 base=ROOT/'results/record_epoch16_pilot_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 native={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items() if not Path(k).name.startswith('tb_')}
 candidate=native|{k:sha_text(v) for k,v in rtl_render().items()}
 tb=tb_render();records={}
 cases=[('sparse_writeback_20261024','masks',candidate|{'tb_sparse_writeback_masks.sv':sha_text(tb['tb_sparse_writeback_masks.sv'])},'tb_sparse_writeback_masks','SPARSE_WB_MASKS_PASS masks=256 transfers=512 fences=256 checks=5377'),('sparse_writeback_20261024','faults',candidate|{'tb_sparse_writeback_faults.sv':sha_text(tb['tb_sparse_writeback_faults.sv'])},'tb_response_faults','RESPONSE_FAULT_PASS errors=9 transfers=68 checks=267')]
 stalls=adapt((ROOT/'hardware/tb/tb_record_epoch16_stalls.sv').read_text().replace('tb_record_epoch16_stalls','tb_sparse_writeback_stalls'))
 cases += [('sparse_writeback_boundaries_20261024','controller',candidate|{'tb_sparse_writeback_boundaries.sv':sha(ROOT/'hardware/tb/tb_sparse_writeback_boundaries.sv')},'tb_sparse_writeback_boundaries','SPARSE_WB_BOUNDARIES_PASS checks=22'),('sparse_writeback_boundaries_20261024','stalls',candidate|{'tb_sparse_writeback_stalls.sv':sha_text(stalls)},'tb_sparse_writeback_stalls','SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4')]
 for case,rtl,top in [('control',native,'tb_sparse_writeback_retry_control'),('candidate',candidate,'tb_sparse_writeback_checkpoint_retry_small')]:
  cases.append(('sparse_writeback_retry_20261024',case,rtl|{'tb_sparse_writeback_retry.sv':sha_text(retry_render())},top,'TEST_PASS memory_endpoint'))
 for folder,case,sources,top,marker in cases:
  out=ROOT/'results'/folder;m=json.loads((out/'manifest.json').read_text());row=m['cases'][case]
  assert m['status']==('failed' if folder=='sparse_writeback_20261024' else 'passed')
  assert m['baseline_manifest_sha256']==sha(base/'manifest.json')
  for name,digest in m['scripts'].items():assert sha(ROOT/name)==digest
  assert row['status']=='passed' and row['sources']==sources
  for name,digest in sources.items():assert sha(out/case/'sources'/name)==digest
  steps=row['commands'];assert [s['stage'] for s in steps]==['compile','elaborate','simulate']
  assert all(s['exit_code']==0 for s in steps)
  assert steps[1]['argv'][1]==top
  assert set(Path(x) for x in steps[0]['argv'] if x.endswith('.sv'))=={out/case/'sources'/name for name in sources}
  log=(out/case/'simulate.log').read_text();assert marker in log and 'Fatal:' not in log and '$finish' in log
  assert sha(out/case/'simulate.log')==row['log_sha256']
  records[folder+'/'+case]={'manifest_sha256':sha(out/'manifest.json'),'log_sha256':row['log_sha256']}
 # Independently derive number of exported/omitted WB records from actual pages.
 vectors=ROOT/'results/small_checkpoint_vectors_pilot_20261023';vm=json.loads((vectors/'manifest.json').read_text())
 assert vm['status']=='passed'
 for name in ['actual.txt','pages.hex']:assert sha(vectors/name)==vm['artifacts'][name]
 exports=omitted=masks=transfers=0
 with (vectors/'actual.txt').open() as commands,(vectors/'pages.hex').open() as pages:
  for line in commands:
   a=[int(x,16) for x in line.split()]
   if a[0] in (5,6):
    words=[pages.readline() for _ in range(3)];assert all(words)
    bitmap=int(words[0],16)&255
    assert a[-1]==transfers;transfers+=1
    if a[0]==5:
     exports+=bitmap.bit_count();omitted+=8-bitmap.bit_count();masks+=1
  assert not pages.read()
 assert transfers==vm['transfers']
 out=ROOT/'results/sparse_writeback_retry_20261024';m=json.loads((out/'manifest.json').read_text());control=m['cases']['control'];new=m['cases']['candidate']
 assert new['sparse_counts']=={'exports':exports,'omitted':omitted,'masks':masks}
 assert control['sparse_counts']=={'exports':0,'omitted':0,'masks':0}
 oldlog=(base/'pilot/simulate.log').read_text()
 oldcounts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',oldlog,re.M)[1])}
 for case in ['control','candidate']:
  log=(out/case/'simulate.log').read_text();r=m['cases'][case]
  for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
   strips=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
   assert strips(log)==strips(oldlog)
  parsed={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])}
  assert r['counts']==parsed and parsed.keys()==oldcounts.keys()
  assert all(parsed[k]==v for k,v in oldcounts.items() if k not in ('checks','gap_cycles','host_stalls'))
  assert parsed['checks']==oldcounts['checks']+r['finish_retries']
  assert r['end_ns']==int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
 assert control['end_ns']==bm['cases']['pilot']['end_ns'] and control['finish_retries']==0
 gain=1-new['end_ns']/control['end_ns'];assert m['time_reduction_fraction']==gain
 result={'status':'passed','auditor_sha256':sha(Path(__file__)),'evidence':records,'vector_manifest_sha256':sha(vectors/'manifest.json'),'independent_sparse_counts':new['sparse_counts'],'queries':19,'transfers':transfers,'control_end_ns':control['end_ns'],'candidate_end_ns':new['end_ns'],'finish_retries':new['finish_retries'],'time_reduction_fraction':gain,'scope':'WB-only control ablation, frozen 19-query actual-value pilot. AXI bytes unchanged. Initial strict-FINISH pilot remains failed. Not full38/board/performance closure.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
