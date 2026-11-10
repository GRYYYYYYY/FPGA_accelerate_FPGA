"""Recover the exact missing authority core plus its preparation provenance."""
from pathlib import Path
import json,tarfile,socket,datetime
from copy_shadow_ka_archives_remote_v1 import sha,R
B=Path('/tmp/B_state_residency_offer_20261025')
def main():
 assert socket.gethostname()=='fpgaacc1--cfc8cd109508-jnnrja5s7q'
 p=B/'ka_active_configured_formal_v1';core=p/'core.json';assert sha(core)=='8abc283b78c12846b498fda668ce6f1835f47c05d339145796f2733d00182fac'
 files={str(core.relative_to(B)):core}
 for n in ['manifest.json','prepare.ys','prepare.log','core.ys','core.log']:
  f=p/n
  if f.is_file():files[str(f.relative_to(B))]=f
 m=json.loads((p/'manifest.json').read_text())
 for n,e in m.get('sources',{}).items():
  if isinstance(e,dict):
   source=Path(e.get('source',e.get('path','')))
   if source.is_file() and 'sha256' in e:assert sha(source)==e['sha256'];files['bound/'+source.name]=source
 target=R/'results/recovery_archives_20261102/shadow_authority_core_provenance_v1.tar';assert not target.exists()
 with tarfile.open(target,'w') as tf:
  for n,f in files.items():tf.add(f,arcname=n,recursive=False)
 result=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),hostname=socket.gethostname(),archives=[dict(archive=str(target),archive_sha256=sha(target),file_sha256={n:sha(f) for n,f in files.items()})],old_experiment_files_modified=False,core_sha256=sha(core),manifest=m)
 print('KA_REVIEWS_COPIED:'+json.dumps(result),flush=True)
if __name__=='__main__':main()
