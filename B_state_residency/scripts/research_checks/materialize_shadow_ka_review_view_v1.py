"""Materialize a new read-only evidence view without touching historical paths."""
from pathlib import Path
import json,tarfile,shutil
from plan_shadow_ka_recovery_v2 import R,sha
B=Path('/tmp/B_state_residency_recovery_20261102');V=B/'ka_dependency_review_view_v1'
def main():
 d=json.loads((R/'results/shadow_ka_dependency_actual_restore_20261102.json').read_text());c=json.loads((R/'results/shadow_authority_core_copy_20261102.json').read_text());assert c['temporary_inspection_terminal_closed']
 a=c['archives'][0];assert sha(a['archive'])==a['archive_sha256'];rest=B/'shadow_authority_core_actual_restore_v1';rest.mkdir()
 with tarfile.open(a['archive']) as tf:
  seen=set()
  for m in tf:
   assert m.isfile() and m.name in a['file_sha256'] and m.name not in seen and '..' not in Path(m.name).parts and not Path(m.name).is_absolute();seen.add(m.name)
   p=rest/m.name;p.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(m) as src,p.open('xb') as dst:shutil.copyfileobj(src,dst)
   assert sha(p)==a['file_sha256'][m.name]
  assert seen==set(a['file_sha256'])
 V.mkdir();mapping={};contents=dict(d['content_index'])
 def link(name,source):
  p=V/name;digest=sha(source)
  if p.exists():assert sha(p)==digest,(name,p,source);return
  p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(source);mapping[name]=dict(source=str(source),sha256=digest)
 for ar in d['archives'].values():
  for n in ar['file_sha256']:
   if n.startswith('ka_'):link(n,Path(ar['actual_restore'])/n)
 for n,h in a['file_sha256'].items():
  contents.setdefault(h,[]).append(str(rest/n))
  if n.startswith('ka_'):link(n,rest/n)
 # Supply full frozen v6 source context, including its original full-shadow TB.
 for p in (B/'stage_static_cp_host_full_static_v1/sources').rglob('*'):
  if p.is_file():
   rel=p.relative_to(B/'stage_static_cp_host_full_static_v1/sources')
   src=R/'hardware/variants/stage_static_cp_shadow_protocol_v5/tb_query_fault.sv' if str(rel)=='tb_query_fault.sv' else p
   link('stage_static_cp_shadow_system_v6/sources/'+str(rel),src)
 # Unambiguous path+digest references can be restored from differently named archive entries.
 old='/tmp/B_state_residency_offer_20261025/'
 def walk(obj):
  if isinstance(obj,dict):
   for k,v in obj.items():
    if isinstance(v,str) and v.startswith(old):
     keys=[k+'_sha256','sha256' if k in ['source','path'] else '', 'source_json_sha256' if k=='source_json' else '']
     hashes=[obj[x] for x in keys if x in obj and isinstance(obj[x],str) and obj[x] in contents]
     if hashes:assert len(set(hashes))==1;link(v[len(old):],Path(contents[hashes[0]][0]))
    walk(v)
  elif isinstance(obj,list):
   for x in obj:walk(x)
 for ar in d['archives'].values():
  for n in ar['file_sha256']:
   if n.endswith('.json') and not n.endswith(('kernel.json','core.json','full.json')):walk(json.loads((Path(ar['actual_restore'])/n).read_text()))
 out=R/'results/shadow_ka_dependency_review_view_20261102.json';assert not out.exists()
 out.write_text(json.dumps(dict(status='new_evidence_view_created_no_experiments',view=str(V),files=mapping,core_restore=str(rest),core_archive_sha256=a['archive_sha256'],core_scope='Only source-bound core preparation consumed; stale running parent manifest is not accepted as proof.',full_system_functional_netlist_validated=False,physical_gate_open=False),indent=2)+'\n')
 print('EVIDENCE_VIEW',len(mapping))
if __name__=='__main__':main()
