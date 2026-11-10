from pathlib import Path
import sys,json
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());ba=json.loads((base/'source_bound_audit.json').read_text());assert ba['status']=='passed'and ba['manifest_sha256']==sha(base/'manifest.json')
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in ['query_lifecycle.sv','regression_runner.py']:assert h['sha256']==bm['sources'][n]['sha256'],n
native=p.parent/'query_warm_rebase_v3';assert json.loads((native/'source_bound_audit.json').read_text())['status']=='passed';assert sha(p/'sources/query_lifecycle.sv')==sha(native/'sources/query_lifecycle.sv')
assert m['rtl']==bm['rtl'];report={}
if not partial:assert set(m['cases'])=={'full_5','pressure_5'}
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 assert all(x['exit_code']==0 for x in c['commands'])
 names=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin','natural_trace.txt','directory.txt'];exact={n:sha(p/name/n)for n in names}
 for n,h in exact.items():assert h==sha(base/name/n),(name,n)
 log=(p/name/'simulate.log').read_text();old=(base/name/'simulate.log').read_text();assert 'Fatal:'not in log
 result=next(l for l in log.splitlines()if l.startswith('QUERY_FAULT_OBSERVED'));assert result==next(l for l in old.splitlines()if l.startswith('QUERY_FAULT_OBSERVED'))
 report[name]=dict(exact_files=exact,result=result);print(name,'14 exact files and cycles matched',flush=True)
r=dict(status='partial'if partial else 'passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=report,scope='Default-disabled full-system behavior and cycle regression only; not enabled warm recovery.')
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n')
