"""Old-host read-only source copy of exact plan archives to shared persistent files."""
from pathlib import Path
import hashlib,json,shutil,datetime,socket
R=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 assert socket.gethostname()=='fpgaacc1--cfc8cd109508-jnnrja5s7q'
 plan=R/'results/shadow_ka_dependency_recovery_plan_v1_20261102.json';d=json.loads(plan.read_text());rows=[]
 for row in d['archives']:
  report=Path(row['report']);assert sha(report)==row['report_sha256']
  source,target=Path(row['source']),Path(row['archive'])
  assert sha(source)==row['archive_sha256']
  if not target.exists():
   partial=target.with_suffix('.tar.partial')
   with source.open('rb') as inp,partial.open('xb') as out:shutil.copyfileobj(inp,out,1<<20)
   assert sha(partial)==row['archive_sha256'];partial.rename(target)
  assert sha(target)==row['archive_sha256']
  rows.append(dict(row,bytes=target.stat().st_size))
 result=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),hostname=socket.gethostname(),archives=rows,plan_sha256=sha(plan),old_experiment_files_modified=False)
 print('KA_REVIEWS_COPIED:'+json.dumps(result),flush=True)
if __name__=='__main__':main()
