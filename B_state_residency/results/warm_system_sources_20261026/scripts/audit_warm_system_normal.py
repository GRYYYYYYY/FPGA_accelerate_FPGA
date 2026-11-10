from pathlib import Path
import sys,json,runpy,tempfile
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
changed={'query_lifecycle.sv','query_residency_system.sv','search_residency_system.sv','residency_system.sv','warm_build.py','warm_restore_receipt_join.sv','regression_runner.py'}
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in changed:assert h['sha256']==bm['sources'][n]['sha256'],n
b=runpy.run_path(str(p/'sources/warm_build.py'))
with tempfile.TemporaryDirectory()as t:
 b['make'].__globals__['HERE']=Path(t);b['make']()
 for n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv']:assert (Path(t)/n).read_bytes()==(p/'sources'/n).read_bytes(),n
for name,n in [('query_warm_rebase_v3','query_lifecycle.sv'),('warm_join_context_v1','warm_restore_receipt_join.sv')]:
 dep=p.parent/name;assert json.loads((dep/'source_bound_audit.json').read_text())['status']=='passed';assert sha(p/'sources'/n)==sha(dep/'sources'/n)
assert m['rtl']==bm['rtl']+['warm_restore_receipt_join.sv'];report={}
if not partial:assert set(m['cases'])=={'full_5','pressure_5'}
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 assert all(x['exit_code']==0 for x in c['commands']);names=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin','natural_trace.txt','directory.txt'];exact={n:sha(p/name/n)for n in names}
 for n,h in exact.items():assert h==sha(base/name/n),(name,n)
 log=(p/name/'simulate.log').read_text();old=(base/name/'simulate.log').read_text();assert 'Fatal:'not in log
 result=next(l for l in log.splitlines()if l.startswith('QUERY_FAULT_OBSERVED'));assert result==next(l for l in old.splitlines()if l.startswith('QUERY_FAULT_OBSERVED'));report[name]=dict(exact_files=exact,result=result);print(name,'14 exact files and cycles matched',flush=True)
r=dict(status='partial'if partial else 'passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=report,scope='Full warm plumbing disabled; exact ordinary-path regression, not enabled warm-fault proof.')
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n')
