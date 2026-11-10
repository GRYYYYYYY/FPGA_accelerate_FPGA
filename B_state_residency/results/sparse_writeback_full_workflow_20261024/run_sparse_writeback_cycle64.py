"""Unsigned64-cycle sparse WB pilot/full replay, with bounded fence retries."""
from pathlib import Path
import hashlib,json,subprocess,os,re,argparse
from make_sparse_writeback import render as rtl_render
from make_sparse_writeback_cycle64_tb import render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args()
 name='sparse_writeback_cycle64_full_20261024' if args.full else 'sparse_writeback_cycle64_pilot_20261024'
 out=ROOT/'results'/name;out.mkdir()
 base=ROOT/'results'/('record_epoch16_full_20261024' if args.full else 'record_epoch16_pilot_20261024')
 bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 gates={}
 for label,path in [('sparse_pilot',ROOT/'results/sparse_writeback_retry_20261024/source_bound_audit.json'),('native_full',ROOT/'results/record_epoch16_full_20261024/source_bound_audit.json')]:
  assert json.loads(path.read_text())['status']=='passed';gates[label]=sha(path)
 if args.full:
  p=ROOT/'results/sparse_writeback_cycle64_pilot_20261024/source_bound_audit.json';assert json.loads(p.read_text())['status']=='passed';gates['cycle64_pilot']=sha(p)
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items()}
 originals=sorted(p for p in (base/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in originals:assert sha(p)==expected[p.name]
 variant=ROOT/'hardware/variants/sparse_writeback';rtl=rtl_render()
 for filename,s in rtl.items():assert (variant/filename).read_text()==s
 tb=ROOT/'hardware/tb/tb_sparse_writeback_cycle64.sv';assert tb.read_text()==render()
 paths=[variant/p.name if p.name in rtl else p for p in originals]+[tb]
 m={'status':'running','pid':os.getpid(),'full':args.full,'baseline':str(base.relative_to(ROOT)),'baseline_manifest_sha256':sha(base/'manifest.json'),'gates':gates,'sources':{},'commands':[],'runner_sha256':sha(Path(__file__))}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  src=out/'sources';src.mkdir()
  for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]=sha(p)
  vector=ROOT/'results'/('small_checkpoint_vectors_full_20261023' if args.full else 'small_checkpoint_vectors_pilot_20261023')
  vm=json.loads((vector/'manifest.json').read_text());assert vm['status']=='passed'
  for filename in ['actual.txt','pages.hex']:assert sha(vector/filename)==vm['artifacts'][filename]
  m['vector_manifest_sha256']=sha(vector/'manifest.json');save()
  (out/'run.tcl').write_text('run all\nquit\n')
  sim=[str(BIN/'xsim'),'sparse','--tclbatch','run.tcl','--log','simulate.log']+bm['cases']['pilot']['commands'][-1]['argv'][6:]
  top='tb_sparse_writeback_cycle64_large' if args.full else 'tb_sparse_writeback_cycle64_small'
  commands=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),top,'-s','sparse','--debug','typical','--mt','2']),('simulate',sim)]
  for stage,argv in commands:
   with (out/f'{stage}.stdout.log').open('w') as f:
    proc=subprocess.Popen(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};m['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,stage
  log=(out/'simulate.log').read_text();assert 'TEST_PASS memory_endpoint' in log and 'Fatal:' not in log and '$finish' in log
  old=(base/'pilot/simulate.log').read_text()
  for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
   stripped=lambda x:[re.sub(r' ?time_ps=\d+','',s) for s in re.findall('^'+prefix+r' (.+)$',x,re.M)]
   assert stripped(log)==stripped(old)
  terminal=lambda x:{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',x,re.M)[1])}
  counts,oldcounts=terminal(log),terminal(old);retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
  assert set(counts)==set(oldcounts)
  assert all(counts[k]==v for k,v in oldcounts.items() if k not in ('checks','gap_cycles','host_stalls'))
  assert counts['checks']==oldcounts['checks']+retries
  sparse=re.search(r'SPARSE_WB_COUNTS exports=(\d+) omitted=(\d+) masks=(\d+)',log);assert sparse
  m.update(log_sha256=sha(out/'simulate.log'),counts=counts,finish_retries=retries,sparse_counts={k:int(v) for k,v in zip(['exports','omitted','masks'],sparse.groups())},end_ns=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]),baseline_end_ns=bm['cases']['pilot']['end_ns'])
  if not args.full:
   old=(ROOT/'results/sparse_writeback_retry_20261024/candidate/simulate.log').read_text()
   for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint','FINISH_RETRY_COUNTS','SPARSE_WB_COUNTS']:
    assert re.findall('^'+prefix+r' (.+)$',log,re.M)==re.findall('^'+prefix+r' (.+)$',old,re.M)
   oldm=json.loads((ROOT/'results/sparse_writeback_retry_20261024/manifest.json').read_text());assert m['end_ns']==oldm['cases']['candidate']['end_ns']
   m['signed32_pilot_cycle_equivalence']=True
  m['status']='passed';save();print(name,'passed',m['end_ns'],flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
