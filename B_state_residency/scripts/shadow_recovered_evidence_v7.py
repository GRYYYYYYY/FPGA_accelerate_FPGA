"""Immutable old evidence recovered on this host; no legacy /tmp execution."""
from pathlib import Path
from host_edit_system_common_v1 import ROOT,read,sha,identity,load
BASE=Path('/tmp/B_state_residency_recovery_20261102')
OLD=Path('/tmp/B_state_residency_offer_20261025')
RECOVERED={}
def relocated(p):
 p=Path(p)
 return BASE/p.relative_to(OLD) if p.is_relative_to(OLD) else p

def restored(path):
 mf,af=path/'manifest.json',path/'source_bound_audit.json';rp=ROOT/'results'/f'{path.name}_restore_20261025.json'
 m,a,r=read(mf),read(af),read(rp);ip=Path(r['archive_index']);idx=read(ip)
 assert m['status']=='observed' and a['status']==r['status']=='passed'
 assert a['manifest_sha256']==sha(mf) and r['audit_byte_identical'] and r['audit_sha256']==sha(af)
 assert idx['archive_sha256']==r['archive_sha256']==sha(idx['archive'])
 for n,h in idx['members'].items():assert sha(path/n)==h,(path,n)
 RECOVERED[str(path)]=dict(index=str(ip),index_sha256=sha(ip),archive_sha256=idx['archive_sha256'],files=len(idx['members']))
 return m,a,[mf,af,rp,ip]

def verify_freeze(directory):
 m=read(directory/'manifest.json');assert m['status']=='frozen'
 for name,e in m['files'].items():
  frozen=directory/name;assert sha(frozen)==e['sha256']
  source=relocated(e['source'])
  if source.is_file():assert sha(source)==e['sha256']
  else:
   # Frozen bytes are themselves the preserved source copy, not a newly fabricated source.
   # Require the original source to be a historical scratch path, never hide current-source drift.
   assert Path(e['source']).is_relative_to(OLD),e['source']
   RECOVERED[str(e['source'])]=dict(recovered_source=str(frozen),sha256=e['sha256'],method='original_frozen_source_copy')
 return directory/'manifest.json'
