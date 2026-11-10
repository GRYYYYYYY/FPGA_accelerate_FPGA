from pathlib import Path
import sys,json,runpy,tempfile
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
changed={'residency_system.sv','search_residency_system.sv','query_residency_system.sv','recovery_coordinator.sv','cancel_build.py','regression_runner.py','warm_restore_receipt_join.sv','capacity_build.py','recovery_coordinator.sv','restore_build.py'}
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256']
 if n not in changed:assert h['sha256']==bm['sources'][n]['sha256'],n
b=runpy.run_path(str(p/'sources/cancel_build.py'))
with tempfile.TemporaryDirectory()as d:
 b['make'].__globals__['HERE']=Path(d);b['make']()
 for n in ['warm_restore_receipt_join.sv']:assert (Path(d)/n).read_bytes()==(p/'sources'/n).read_bytes()

w=runpy.run_path(str(p/'sources/restore_build.py'))
with tempfile.TemporaryDirectory()as d:
 w['make'].__globals__['HERE']=Path(d);w['make']()
 for n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv']:assert (Path(d)/n).read_bytes()==(p/'sources'/n).read_bytes()
cb=runpy.run_path(str(p/'sources/capacity_build.py'));assert cb['make']()==(p/'sources/recovery_coordinator.sv').read_text()
report={}
if not partial and '--single'not in sys.argv:assert set(m['cases'])=={'full_5','pressure_5'}
if '--single'in sys.argv:assert len(m['cases'])==1
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 names=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin','natural_trace.txt','directory.txt'];exact={n:sha(p/name/n)for n in names}
 for n,h in exact.items():assert h==sha(base/name/n),(name,n)
 log=(p/name/'simulate.log').read_text();old=(base/name/'simulate.log').read_text();assert 'Fatal:'not in log
 result=next(x for x in log.splitlines()if x.startswith('QUERY_FAULT_OBSERVED'));assert result==next(x for x in old.splitlines()if x.startswith('QUERY_FAULT_OBSERVED'));report[name]=dict(exact_files=exact,result=result);print(name,'14 exact files and cycles matched',flush=True)
r=dict(status='partial'if partial else 'passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=report)
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n')
