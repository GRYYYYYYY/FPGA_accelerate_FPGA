"""Single dependent full replay owner; observe original WB owner, never restart it."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,time,datetime
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/sparse_records_full_workflow_20261024';out.mkdir()
 assert read(ROOT/'results/sparse_records_20261024/source_bound_audit.json')['status']=='passed'
 names=['run_sparse_records_full.py','audit_sparse_records_full.py','make_sparse_records.py','make_sparse_records_tb.py','make_sparse_writeback.py','make_sparse_writeback_tb.py','make_sparse_writeback_retry_tb.py','make_sparse_writeback_cycle64_tb.py']
 m={'status':'waiting_wb_full','pid':os.getpid(),'commands':[],'frozen_scripts':{},'policy':'one combined full attempt only after original WB full is audited; no restart or resubmission of either chain','monitoring':'luna-selection/delegation unavailable; deterministic30s read-only dependency observation'}
 for name in names:
  p=ROOT/'hardware/scripts'/name;(out/name).write_bytes(p.read_bytes());m['frozen_scripts'][name]=sha(p)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  dependency=ROOT/'results/sparse_writeback_full_workflow_20261024/manifest.json'
  while True:
   wm=read(dependency)
   if wm['status']=='full_replay_audited':break
   assert wm['status'] in ('running_full','auditing'),('dependency terminal/unknown',wm['status'])
   try:
    os.kill(wm['pid'],0)
    command=Path(f"/proc/{wm['pid']}/cmdline").read_bytes().replace(b'\0',b' ').decode()
    assert 'run_sparse_writeback_full_workflow.py' in command,'dependency PID reused'
   except (ProcessLookupError,FileNotFoundError):
    # Re-read after an owner can legitimately write its terminal state and exit.
    if read(dependency)['status']=='full_replay_audited':break
    raise RuntimeError('Original WB supervisor missing without audited terminal state; no restart')
   m['dependency_observation']={'pid':wm['pid'],'status':wm['status'],'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};save();time.sleep(30)
  assert read(ROOT/'results/sparse_writeback_cycle64_full_20261024/source_bound_audit.json')['status']=='passed'
  m['wb_full_manifest_sha256']=sha(dependency);save()
  for name in names[:2]:
   for frozen,digest in m['frozen_scripts'].items():assert sha(out/frozen)==digest
   argv=[sys.executable,str(out/name)];m['status']='running_full' if name.startswith('run_') else 'auditing';save()
   with (out/(name+'.stdout.log')).open('w') as f:
    proc=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);step={'script':name,'argv':argv,'pid':proc.pid};m['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,name
  assert read(ROOT/'results/sparse_records_full_20261024/source_bound_audit.json')['status']=='passed'
  m['status']='full_replay_audited';save();print(m['status'],flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
