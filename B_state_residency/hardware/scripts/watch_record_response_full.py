"""Observe one existing replay and run its independent terminal audit; never restart."""
from pathlib import Path
import hashlib,json,os,time,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 target=ROOT/'results/record_response_full_20261024/manifest.json'
 out=ROOT/'results/record_response_full_watch_20261024';out.mkdir()
 auditor=ROOT/'hardware/scripts/audit_record_response_variant.py';digest=sha(auditor)
 m={'status':'observing','pid':os.getpid(),'target':str(target),'auditor_sha256':digest,'policy':'read-only polling, one terminal audit, no recovery/restart'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 while True:
  try:job=json.loads(target.read_text())
  except json.JSONDecodeError:time.sleep(1);continue
  if job['status']!='running':break
  try:os.kill(job['pid'],0)
  except ProcessLookupError:m.update(status='runner_missing_requires_inspection');save();return
  time.sleep(30)
 if job['status']!='passed':m.update(status='replay_failed',error=job.get('error'));save();return
 assert sha(auditor)==digest
 with (out/'audit.stdout.log').open('w') as f:r=subprocess.run([sys.executable,str(auditor),'--full'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 m.update(status='replay_audited' if r.returncode==0 else 'audit_failed',exit_code=r.returncode,replay_manifest_sha256=sha(target));save()
if __name__=='__main__':main()
