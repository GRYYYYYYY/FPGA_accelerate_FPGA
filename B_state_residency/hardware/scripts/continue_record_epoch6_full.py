"""One owner: await audited upstream gates, run one composite replay, audit it.
Never restarts the upstream replay or retries a failed downstream submission.
"""
from pathlib import Path
import json,hashlib,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 try:return json.loads(p.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return None
def live(pid,script):
 try:return script in Path(f'/proc/{pid}/cmdline').read_bytes().decode(errors='replace')
 except FileNotFoundError:return False
def main():
 out=ROOT/'results/record_epoch6_full_workflow_20261024';out.mkdir()
 m={'status':'waiting_for_audited_dependencies','pid':os.getpid(),'dependencies':{},'commands':[],'policy':'one downstream attempt; no upstream mutation or automatic recovery'}
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 names=['run_record_epoch6_full.py','audit_record_epoch6_full.py','compare_record_epoch6_queries.py']
 m['frozen_scripts']={}
 for name in names:
  p=out/name;p.write_bytes((ROOT/'hardware/scripts'/name).read_bytes());m['frozen_scripts'][name]=sha(p)
 save()
 try:
  while True:
   upstream=read(ROOT/'results/record_response_full_20261024/manifest.json')
   watch=read(ROOT/'results/record_response_full_watch_20261024/manifest.json')
   physical=read(ROOT/'results/record_epoch6_timing_20261024/final_audit.json')
   if upstream and upstream['status']=='failed':raise RuntimeError('upstream replay failed; inspect preserved evidence')
   if watch and watch['status'] in ['audit_failed','replay_failed','runner_missing_requires_inspection']:raise RuntimeError('upstream observer stopped: '+watch['status'])
   if physical and not (physical['status']=='evidence_verified' and physical['internal_constraints_met_in_this_model']):raise RuntimeError('composite physical gate did not meet internal constraints')
   if upstream and upstream['status']=='running' and not live(upstream['pid'],'run_record_response_full.py'):raise RuntimeError('upstream runner missing or changed; do not resubmit')
   if watch and watch['status']=='observing' and not live(watch['pid'],'watch_record_response_full.py'):raise RuntimeError('upstream observer missing or changed')
   if upstream and upstream['status']=='passed' and watch and watch['status']=='replay_audited' and physical:break
   time.sleep(30)
  assert not (ROOT/'results/record_epoch6_full_20261024').exists(),'downstream result exists; inspect instead of duplicating'
  for name,digest in m['frozen_scripts'].items():assert sha(out/name)==digest
  for name in ['record_response_full_20261024/manifest.json','record_response_full_20261024/source_bound_audit.json','record_response_full_watch_20261024/manifest.json','record_epoch6_timing_20261024/final_audit.json']:
   m['dependencies'][name]=sha(ROOT/'results'/name)
  m['status']='running_composite';save()
  for name in names:
   argv=[sys.executable,str(out/name)]
   with (out/(name+'.stdout.log')).open('w') as f:
    proc=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);row={'script':name,'argv':argv,'pid':proc.pid};m['commands'].append(row);save();row['exit_code']=proc.wait();save();assert row['exit_code']==0,name
  result=read(ROOT/'results/record_epoch6_full_20261024/manifest.json');audit=read(ROOT/'results/record_epoch6_full_20261024/source_bound_audit.json');assert result['status']=='passed' and audit['status']=='passed'
  m.update(status='composite_replay_audited',cycle_comparison=result['cycle_comparison']);save()
 except Exception as e:m.update(status='stopped_requires_inspection',error=repr(e));save();raise
if __name__=='__main__':main()
