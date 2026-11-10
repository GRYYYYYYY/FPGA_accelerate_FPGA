"""Persist scratch experiments as verified archives; never overwrite an archive."""
from pathlib import Path
import hashlib,json,shutil,sys,tarfile,tempfile
ROOT=Path(__file__).resolve().parents[1]
def digest(f):
 h=hashlib.sha256()
 for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def sha(p):
 with p.open('rb')as f:return digest(f)
def main():
 p=Path(sys.argv[1]).resolve();assert p.parent==Path('/tmp/B_state_residency_offer_20261025')
 assert json.loads((p/'source_bound_audit.json').read_text())['status']=='passed'
 dest=ROOT/'results/offer_archives_20261025';dest.mkdir(exist_ok=True);target=dest/(p.name+'.tar.gz');index=dest/(p.name+'.json');assert not target.exists() and not index.exists()
 members={str(q.relative_to(p)):sha(q) for q in p.rglob('*') if q.is_file() and not q.is_symlink()}
 with tempfile.TemporaryDirectory(prefix='postprev_archive_')as tmp:
  archive=Path(tmp)/target.name
  with tarfile.open(archive,'w:gz',compresslevel=6)as tf:tf.add(p,arcname=p.name,recursive=True)
  actual={}
  with tarfile.open(archive,'r:gz')as tf:
   for item in tf:
    if item.isfile():
     rel=str(Path(item.name).relative_to(p.name));actual[rel]=digest(tf.extractfile(item))
  assert actual==members
  # Do not publish the final filename until the shared-filesystem copy is complete.
  staged=target.with_suffix(target.suffix+'.partial');shutil.copyfile(archive,staged);assert sha(staged)==sha(archive);staged.rename(target)
 record={'status':'passed','source_root':str(p),'archive':str(target),'archive_sha256':sha(target),'members':members,'scope':'Every regular file verified after compression and archive copy; original scratch kept. Restore with scripts/restore_offer_result.py.'}
 index.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'status':'passed','archive':str(target),'bytes':target.stat().st_size,'files':len(members)}))
if __name__=='__main__':main()
