"""Locate SHA-bound KA archives without equating report statuses with acceptance."""
from pathlib import Path
import hashlib,json,re,socket,datetime
R=Path(__file__).resolve().parents[2]
B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 index=R/'results/session_handoff_ka_dependency_inventory_20261102.json'
 d=json.loads(index.read_text()); scripts={sha(p):p for p in (R/'scripts/research_checks').glob('*.py')}
 rows=[]
 for name,v in d['reports'].items():
  p=Path(v['path']);assert sha(p)==v['sha256'];r=json.loads(p.read_text())
  if not r.get('archive_sha256'):continue
  copied=json.loads((R/'results/old_host_ka_review_archive_copy_20261102.json').read_text())['archives']
  by_hash={x['archive_sha256']:x['source'] for x in copied}
  src=r.get('archive') or by_hash.get(r['archive_sha256']);reviewer=None
  if not src:
   reviewer=scripts[r['reviewer_sha256']]
   names=re.findall(r"cap\s*=\s*B\s*/\s*['\"]([^'\"]+_evidence_v\d+)['\"]",reviewer.read_text())
   assert len(names)==1,(name,names)
   src=str(B/names[0]/'evidence.tar')
  target=R/'results/recovery_archives_20261102'/(Path(src).parent.name+'.tar')
  present=target.is_file()
  if present:assert sha(target)==r['archive_sha256']
  field=next(k for k in ['file_sha256','evidence_inventory','restored_sha256'] if k in r)
  rows.append(dict(report=str(p),report_sha256=sha(p),source=src,archive=str(target),archive_sha256=r['archive_sha256'],inventory_field=field,files=len(r[field]),local_verified=present,locator_auditor=str(reviewer) if reviewer else None))
 for e in d['edges']:assert sha(R/'results'/e['to'])==e['sha256']
 out=R/'results/shadow_ka_dependency_recovery_plan_v1_20261102.json';assert not out.exists()
 out.write_text(json.dumps(dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),hostname=socket.gethostname(),index_sha256=sha(index),reports=30,archives=rows,scope='Archive locations from bound reports or exact-SHA auditor source; no new proof or full-shadow acceptance.'),indent=2)+'\n')
 print(json.dumps(dict(archives=len(rows),local_verified=sum(x['local_verified'] for x in rows),missing=sum(not x['local_verified'] for x in rows))))
if __name__=='__main__':main()
