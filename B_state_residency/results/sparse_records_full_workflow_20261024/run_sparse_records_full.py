"""Single full combined WB/RF actual replay, gated by completed WB baseline."""
from pathlib import Path
import hashlib,json,subprocess,os,re
from make_sparse_records import render as rtl_render
from make_sparse_records_tb import render as tb_render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def term(t):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
def main():
 base=ROOT/'results/sparse_writeback_cycle64_full_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert json.loads((ROOT/'results/sparse_writeback_full_workflow_20261024/manifest.json').read_text())['status']=='full_replay_audited'
 gates={}
 for label,p in [('wb_full',base/'source_bound_audit.json'),('combined_pilot',ROOT/'results/sparse_records_20261024/source_bound_audit.json')]:
  assert json.loads(p.read_text())['status']=='passed';gates[label]=sha(p)
 rtl=rtl_render();variant=ROOT/'hardware/variants/sparse_records'
 for filename,s in rtl.items():assert (variant/filename).read_text()==s
 originals=sorted(p for p in (base/'sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in originals:assert sha(p)==bm['sources'][p.name]
 tb=ROOT/'hardware/tb/tb_sparse_records_pilot.sv';assert tb.read_text()==tb_render()[tb.name]
 paths=[variant/p.name if p.name in rtl else p for p in originals]+[tb]
 out=ROOT/'results/sparse_records_full_20261024';out.mkdir();src=out/'sources';src.mkdir()
 m={'status':'running','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'gates':gates,'sources':{},'commands':[],'runner_sha256':sha(Path(__file__))}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]=sha(p)
  vector=ROOT/'results/small_checkpoint_vectors_full_20261023';vm=json.loads((vector/'manifest.json').read_text());assert vm['status']=='passed'
  for filename in ['actual.txt','pages.hex']:assert sha(vector/filename)==vm['artifacts'][filename]
  m['vector_manifest_sha256']=sha(vector/'manifest.json');save()
  (out/'run.tcl').write_text('run all\nquit\n')
  sim=[str(BIN/'xsim'),'sparse','--tclbatch','run.tcl','--log','simulate.log']+bm['commands'][-1]['argv'][6:]
  cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),'tb_sparse_records_large','-s','sparse','--debug','typical','--mt','2']),('simulate',sim)]
  for stage,argv in cmds:
   with (out/f'{stage}.stdout.log').open('w') as f:
    proc=subprocess.Popen(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};m['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,stage
  log=(out/'simulate.log').read_text();assert 'TEST_PASS memory_endpoint' in log and 'Fatal:' not in log and '$finish' in log
  old=(base/'simulate.log').read_text()
  for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
   strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
   assert strip(log)==strip(old)
  counts,previous=term(log),term(old);retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
  assert counts.keys()==previous.keys() and counts['checks']==vm['public_commands']+retries
  assert all(counts[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
  for direction,fields in [('WB',['exports','omitted','masks']),('RF',['beats','omitted','masks'])]:
   match=re.search('SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),log);assert match
   m[direction.lower()+'_counts']=dict(zip(fields,map(int,match.groups())))
  native=json.loads((ROOT/'results/record_epoch16_full_20261024/manifest.json').read_text())['cases']['pilot']['end_ns']
  m.update(status='passed',counts=counts,finish_retries=retries,end_ns=int(re.search(r'\$finish called at time : (\d+) ns',log)[1]),wb_only_end_ns=bm['end_ns'],native16_end_ns=native,log_sha256=sha(out/'simulate.log'));save();print('passed',m['end_ns'],flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
