"""Verify and restore a scratch archive to its recorded location, without overwrites."""
from pathlib import Path
import hashlib,json,sys,tarfile

def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 record=json.loads(Path(sys.argv[1]).read_text());assert record['status']=='passed'
 archive=Path(record['archive']);assert sha(archive)==record['archive_sha256']
 dest=Path(record['source_root']);assert dest.parent==Path('/tmp/B_state_residency_occupied_20261025')
 if not dest.exists():
  dest.mkdir(parents=True)
  with tarfile.open(archive,'r:gz')as tf:
   for item in tf:
    rel=Path(item.name).relative_to(dest.name);assert not rel.is_absolute() and '..'not in rel.parts
    q=dest/rel
    if item.isdir():q.mkdir(parents=True,exist_ok=True)
    elif item.isfile():
     q.parent.mkdir(parents=True,exist_ok=True)
     with q.open('xb')as f:f.write(tf.extractfile(item).read())
     q.chmod(item.mode)
    elif item.issym():
     link=Path(item.linkname);assert not link.is_absolute() and '..'not in link.parts
     q.symlink_to(link)
    else:raise AssertionError('unsupported archive member '+item.name)
 for name,digest in record['members'].items():assert sha(dest/name)==digest,name
 print('OCCUPIED_ARCHIVE_VERIFIED',dest)
if __name__=='__main__':main()
