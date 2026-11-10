"""Actually restore each optimization archive, then require byte-identical re-audit."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];SCRATCH=Path('/tmp/B_state_residency_offer_20261025')
TASKS={}
for kind in ['static','sparse']:
 TASKS['search_'+kind+'_lease_v1']=['audit_search_'+kind+'_lease.py']
 TASKS['search_'+kind+'_equivalence_v1']=['audit_search_mux_equivalence.py',kind]
 TASKS['search_'+kind+'_join_v1']=['audit_search_'+kind+'_join.py']
 TASKS['search_'+kind+'_synth_v1']=['audit_search_'+kind+'_synth.py']
def main():
 receipt=ROOT/'results/search_optimization_restore_20261025.json';r=json.loads(receipt.read_text())if receipt.exists()else dict(status='partial',method='Originals moved aside, archives actually extracted and all files verified, then independent audits rerun and compared byte-for-byte.',results={})
 for name,args in TASKS.items():
  if name in r['results']:continue
  idx=ROOT/'results/offer_archives_20261025'/(name+'.json')
  if not idx.exists():continue
  p=SCRATCH/name;before=(p/'source_bound_audit.json').read_bytes();backup=SCRATCH/'.preserved'/name;assert not backup.exists();p.rename(backup)
  subprocess.run(['python3',str(ROOT/'scripts/restore_offer_result.py'),str(idx)],check=True)
  with(SCRATCH/(name+'.reaudit_stdout.json')).open('w')as f:subprocess.run(['python3',str(ROOT/'scripts'/args[0]),str(p),*args[1:]],stdout=f,check=True)
  assert (p/'source_bound_audit.json').read_bytes()==before
  rec=json.loads(idx.read_text());r['results'][name]=dict(status='passed',archive_index=str(idx.relative_to(ROOT)),archive_sha256=rec['archive_sha256'],files=len(rec['members']),bytes=sum((p/n).stat().st_size for n in rec['members']),restored_audit_sha256=hashlib.sha256(before).hexdigest(),audit_byte_identical=True)
  r['status']='passed'if len(r['results'])==len(TASKS)else'partial';receipt.write_text(json.dumps(r,indent=2)+'\n')
 print('RESTORED',len(r['results']),'OF',len(TASKS))
if __name__=='__main__':main()
