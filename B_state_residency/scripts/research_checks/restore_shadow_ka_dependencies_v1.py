"""Actually restore every report-bound archive; retain separate historical verdict scopes."""
from pathlib import Path
import json,tarfile,shutil,datetime
from plan_shadow_ka_recovery_v2 import sha,R
B=Path('/tmp/B_state_residency_recovery_20261102/ka_dependency_actual_restore_v1')
def main():
 cp=R/'results/shadow_ka_dependency_archive_copy_20261102.json';c=json.loads(cp.read_text())
 assert c['temporary_inspection_terminal_closed'] and len(c['archives'])==24
 assert not B.exists();B.mkdir();rows={};index={}
 for row in c['archives']:
  report=Path(row['report']);assert sha(report)==row['report_sha256'];r=json.loads(report.read_text())
  archive=Path(row['archive']);assert sha(archive)==row['archive_sha256']==r['archive_sha256']
  inventory=r[row['inventory_field']]; hashes={n:v['sha256'] if isinstance(v,dict) else v for n,v in inventory.items()}
  target=B/archive.stem;target.mkdir();seen=set()
  with tarfile.open(archive) as tf:
   for member in tf:
    n=Path(member.name);assert member.isfile() and not n.is_absolute() and '..' not in n.parts
    assert member.name in hashes and member.name not in seen;seen.add(member.name)
    p=target/n;p.parent.mkdir(parents=True,exist_ok=True)
    with tf.extractfile(member) as src,p.open('xb') as dst:shutil.copyfileobj(src,dst,1<<20)
    assert sha(p)==hashes[member.name]
    index.setdefault(hashes[member.name],[]).append(str(p))
  assert seen==set(hashes)
  rows[report.name]=dict(report_sha256=sha(report),archive=str(archive),archive_sha256=sha(archive),actual_restore=str(target),file_sha256=hashes,historical_status=r['status'])
 out=R/'results/shadow_ka_dependency_actual_restore_20261102.json';assert not out.exists()
 out.write_text(json.dumps(dict(status='all24_report_bound_archives_actually_restored_exact_inventory',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),copy_receipt_sha256=sha(cp),tool_sha256=sha(Path(__file__)),archives=rows,content_index=index,full_system_functional_netlist_validated=False,physical_gate_open=False,scope='Archive completeness and byte identity only; all original scopes and rejection/conditional histories retained. Source/core/assumption integration review follows.'),indent=2)+'\n')
 print(json.dumps(dict(archives=len(rows),files=sum(len(v['file_sha256']) for v in rows.values()),distinct_contents=len(index))))
if __name__=='__main__':main()
