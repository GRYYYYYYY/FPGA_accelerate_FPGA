"""Freeze the selected isolated change and its independent evidence readers."""
from pathlib import Path
import json,shutil
from run_query_fault import ROOT,sha
p=ROOT/'results/search_fault_retire_sources_20261025';assert not p.exists();p.mkdir()
files=list((ROOT/'hardware/variants/search_fault_retire_v1').rglob('*.sv'))+list((ROOT/'hardware/variants/search_fault_retire_v1').glob('*.py'))+[ROOT/'hardware/variants/search_fault_retire_v1/CONTRACT.md']
files += [ROOT/'scripts'/n for n in ['run_query_fault.py','audit_query_fault.py','audit_route_fault_axi.py','audit_natural_axi.py','run_search_retire_join.py','audit_search_retire_join.py','prepare_query_lifecycle_synth.py','audit_search_retire_synth.py','run_search_capture_retire_unit.py','audit_search_capture_retire_unit.py','archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py','finalize_search_retire_run.py','compare_search_retire_normal.py','freeze_search_retire_sources.py']]
files += [ROOT/'hardware/variants/query_recovery_v2/query_residency_system.sv',ROOT/'hardware/variants/query_fault_v1/tb_query_fault.sv']
record={}
for q in files:
 rel=q.relative_to(ROOT);dest=p/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest);assert sha(q)==sha(dest);record[str(rel)]=sha(dest)
(p/'manifest.json').write_text(json.dumps({'status':'frozen','files':record,'reference':'results/query_lifecycle_join_v2','reference_manifest_sha256':sha(ROOT/'results/query_lifecycle_join_v2/manifest.json'),'scope':'Selected revision source closure and audit/restore tools. Prior baseline source/result archives remain dependencies; no claim this small closure is a standalone simulator distribution.'},indent=2)+'\n')
print('FROZEN',len(record))
