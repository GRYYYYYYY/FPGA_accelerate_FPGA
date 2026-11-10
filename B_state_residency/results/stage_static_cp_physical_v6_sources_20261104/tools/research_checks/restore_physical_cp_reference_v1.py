"""Restore immutable CP physical baseline for same-stage comparison only."""
from pathlib import Path
import datetime,json,shutil,sys,tarfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,read,sha

def main():
 report=R/'results/checkpoint_edit_route_recovery_20261030.json';r=read(report)
 index=Path(r['restoration']['archive_index']);i=read(index)
 assert r['restoration']['status']=='passed' and r['restoration']['audit_byte_identical']
 assert sha(i['archive'])==i['archive_sha256']==r['restoration']['archive_sha256']
 out=BASE/'checkpoint_edit_route_recovery_reference_20261104';assert not out.exists();out.mkdir();seen=set()
 prefix=Path(i['source_root']).name
 with tarfile.open(i['archive']) as tf:
  for item in tf:
   if item.isdir():continue
   n=Path(item.name).relative_to(prefix);key=str(n)
   assert item.isfile() and not n.is_absolute() and '..' not in n.parts and key in i['members'] and key not in seen
   seen.add(key);dest=out/n;dest.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(item) as f,dest.open('xb') as w:shutil.copyfileobj(f,w,1<<20)
   assert sha(dest)==i['members'][key]
 assert seen==set(i['members']) and len(seen)==203
 assert read(out/'source_bound_audit.json')==r['audit']
 assert sha(out/'source_bound_audit.json')==r['restoration']['audit_sha256']
 receipt=R/'results/physical_cp_reference_actual_restore_20261104.json';assert not receipt.exists()
 with receipt.open('x') as f:json.dump(dict(status='all_reference_archive_members_actual_restored_sha_matched',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=str(report),report_sha256=sha(report),index=str(index),index_sha256=sha(index),archive=i['archive'],archive_sha256=i['archive_sha256'],restored_root=str(out),file_sha256=i['members'],tool_sha256=sha(__file__),scope='Reference bytes recovered for report comparison; no historical implementation or simulation rerun.'),f,indent=2)
 print('PHYSICAL_CP_REFERENCE_RESTORED',len(seen))
if __name__=='__main__':main()
