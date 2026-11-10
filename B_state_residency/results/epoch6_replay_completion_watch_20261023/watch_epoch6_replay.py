"""Observe the original epoch6 runner and audit completion; never launch replay."""
from pathlib import Path
import json,hashlib,time,subprocess,os
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'results/rtl_epoch6_checkpoint_stream_full_20261023'
OUT=ROOT/'results/epoch6_replay_completion_watch_20261023'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir();auditor=ROOT/'hardware/scripts/audit_small_stream.py'
 matches=[]
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:args=p.read_bytes().split(b'\0')
  except (FileNotFoundError,PermissionError):continue
  if any(x.endswith(b'/run_epoch6_checkpoint_stream.py') for x in args) and b'--full' in args:matches.append((p,p.read_bytes()))
 assert len(matches)==1,'Expected one original epoch6 full replay runner'
 proc,identity=matches[0]
 m={'status':'observing_original_runner','pid':os.getpid(),'runner_pid':int(proc.parent.name),'auditor_sha256':sha(auditor),'source_sha256':sha(Path(__file__)),'replay_restarted':False,'goal_complete':False}
 def save():
  t=OUT/'manifest.tmp';t.write_text(json.dumps(m,indent=2)+'\n');t.replace(OUT/'manifest.json')
 save();(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 try:
  while True:
   try:r=json.loads((RUN/'manifest.json').read_text())
   except json.JSONDecodeError:
    assert proc.exists() and proc.read_bytes()==identity
    time.sleep(1);continue
   assert r['status'] in ['running','passed'],r.get('error','replay failure')
   if r['status']=='passed' and (RUN/'completion_audit.json').exists():break
   assert proc.exists() and proc.read_bytes()==identity,'Original runner missing; no restart authorized by watcher'
   m['last_observed_at_unix']=time.time();save();time.sleep(15)
  assert sha(auditor)==m['auditor_sha256']
  m['status']='auditing';save()
  with (OUT/'final_audit.log').open('w') as log:
   done=subprocess.run(['python3',str(auditor),str(RUN),'--full'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  assert done.returncode==0,'Final full audit failed'
  m.update(status='replay_audited',final_audit_sha256=sha(RUN/'final_audit.json'),replay_manifest_sha256=sha(RUN/'manifest.json'));save();print('EPOCH6_REPLAY_AUDITED',flush=True)
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
