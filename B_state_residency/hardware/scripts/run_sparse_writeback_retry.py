"""Paired frozen pilot, identical bounded retry TB, candidate vs native16."""
from pathlib import Path
import hashlib,json,subprocess,os,re
from make_sparse_writeback import render as rtl_render
from make_sparse_writeback_retry_tb import render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def receipts(log,prefix):return [re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',log,re.M)]
def terminal(log):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])}
def main():
 out=ROOT/'results/sparse_writeback_retry_20261024';out.mkdir()
 base=ROOT/'results/record_epoch16_pilot_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items()}
 originals=sorted(p for p in (base/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in originals:assert sha(p)==expected[p.name]
 variant=ROOT/'hardware/variants/sparse_writeback';rtl=rtl_render()
 for name,s in rtl.items():assert (variant/name).read_text()==s
 tb=ROOT/'hardware/tb/tb_sparse_writeback_retry.sv';assert tb.read_text()==render()
 m={'status':'running','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'cases':{},'scripts':{}}
 for name in ['run_sparse_writeback_retry.py','make_sparse_writeback.py','make_sparse_writeback_tb.py','make_sparse_writeback_retry_tb.py']:
  p=ROOT/'hardware/scripts'/name;m['scripts'][str(p.relative_to(ROOT))]=sha(p)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  old=(base/'pilot/simulate.log').read_text()
  for case,top in [('control','tb_sparse_writeback_retry_control'),('candidate','tb_sparse_writeback_checkpoint_retry_small')]:
   paths=([variant/p.name if p.name in rtl else p for p in originals] if case=='candidate' else originals)+[tb]
   d=out/case;d.mkdir();src=d/'sources';src.mkdir();row={'status':'running','sources':{},'commands':[]};m['cases'][case]=row
   for p in paths:(src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   sim=[str(BIN/'xsim'),'sparse','--tclbatch','run.tcl','--log','simulate.log']+bm['cases']['pilot']['commands'][-1]['argv'][6:]
   cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),top,'-s','sparse','--debug','typical','--mt','2']),('simulate',sim)]
   for stage,argv in cmds:
    with (d/f'{stage}.stdout.log').open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert 'TEST_PASS memory_endpoint' in log and 'Fatal:' not in log and '$finish' in log
   for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:assert receipts(log,prefix)==receipts(old,prefix)
   counts=terminal(log);oldcounts=terminal(old);retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
   assert set(counts)==set(oldcounts)
   assert all(counts[k]==v for k,v in oldcounts.items() if k not in ('checks','gap_cycles','host_stalls'))
   assert counts['checks']==oldcounts['checks']+retries
   sparse=re.search(r'SPARSE_WB_COUNTS exports=(\d+) omitted=(\d+) masks=(\d+)',log);assert sparse
   row.update(status='passed',log_sha256=sha(d/'simulate.log'),counts=counts,finish_retries=retries,sparse_counts={k:int(v) for k,v in zip(['exports','omitted','masks'],sparse.groups())},end_ns=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]));save();print(case,'passed',row['end_ns'],'retries',retries,flush=True)
  control=m['cases']['control'];candidate=m['cases']['candidate']
  assert control['end_ns']==bm['cases']['pilot']['end_ns'] and control['finish_retries']==0
  m['time_reduction_fraction']=1-candidate['end_ns']/control['end_ns'];m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
