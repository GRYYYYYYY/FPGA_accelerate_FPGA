from pathlib import Path
import hashlib,json,struct,sys
from prepare_label_baseline import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='prepared'
s=Path(m['source']);assert sha(s)==m['source_sha256'];assert sha(p/'baseline.bin')==m['baseline_sha256']
assert json.loads((s.parent/'source_bound_audit.json').read_text())['status']=='passed'
assert json.loads((s.parent/'manifest.json').read_text())['artifacts']['initial_nodes.u32']==m['source_sha256']
n=0
with s.open('rb')as f,(p/'baseline.bin').open('rb')as g:
 for raw in iter(lambda:f.read(44*16384),b''):
  expected=b''.join(struct.pack('<8I',u[0],u[1],u[3],u[4],u[5],0,0,0)for u in struct.iter_unpack('<11I',raw))
  assert expected==g.read(len(expected));n+=len(raw)//44
 assert g.read()==(bytes(32)if n%2 else b'')
assert n==m['node_count']==9089009
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),all_records_compared=n,baseline_bytes=(p/'baseline.bin').stat().st_size,baseline_sha256=sha(p/'baseline.bin'),source_sha256=sha(s),scope='Complete prepared initial CPU label mapping, no future node-list input. Integrity, not authentication or hardware miss integration.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('LABEL_BASELINE_IMAGE_AUDITED',n)
