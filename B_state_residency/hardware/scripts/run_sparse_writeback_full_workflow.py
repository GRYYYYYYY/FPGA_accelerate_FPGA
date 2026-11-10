"""Single full attempt then independent terminal audit; never auto-restart."""
from pathlib import Path
import hashlib,json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/sparse_writeback_full_workflow_20261024';out.mkdir()
 assert json.loads((ROOT/'results/record_epoch16_full_workflow_20261024/manifest.json').read_text())['status']=='full_replay_audited'
 assert json.loads((ROOT/'results/sparse_writeback_cycle64_pilot_20261024/source_bound_audit.json').read_text())['status']=='passed'
 names=['run_sparse_writeback_cycle64.py','audit_sparse_writeback_cycle64.py','make_sparse_writeback.py','make_sparse_writeback_tb.py','make_sparse_writeback_retry_tb.py','make_sparse_writeback_cycle64_tb.py']
 m={'status':'prepared','pid':os.getpid(),'commands':[],'frozen_scripts':{},'policy':'one full attempt followed by independent audit; no automatic restart'}
 for name in names:
  p=ROOT/'hardware/scripts'/name;(out/name).write_bytes(p.read_bytes());m['frozen_scripts'][name]=sha(p)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for name in names[:2]:
   for frozen,digest in m['frozen_scripts'].items():assert sha(out/frozen)==digest
   argv=[sys.executable,str(out/name),'--full'];m['status']='running_full' if name.startswith('run_') else 'auditing';save()
   with (out/(name+'.stdout.log')).open('w') as f:
    proc=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);step={'script':name,'argv':argv,'pid':proc.pid};m['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,name
  assert json.loads((ROOT/'results/sparse_writeback_cycle64_full_20261024/source_bound_audit.json').read_text())['status']=='passed'
  m['status']='full_replay_audited';save();print(m['status'],flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
