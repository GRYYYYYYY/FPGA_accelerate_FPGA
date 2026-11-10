from pathlib import Path
import json,sys,runpy
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and not m['abort_case']and not m['negative']
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));b['make'].__globals__['BASE']=ROOT/'hardware/variants/label_baseline_system_v1/build_tb.py';assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
f=runpy.run_path(str(p/'sources/fence_build.py'));f['make'].__globals__['BASE']=ROOT/'hardware/variants/label_baseline_system_v1'
for n,t in f['make']().items():assert t==(p/'sources'/n).read_text()
case=next(iter(m['cases']));d=p/case;old=p.parent/('label_baseline_pair_'+case+'_v2');assert json.loads((old/'source_bound_audit.json').read_text())['status']=='passed'
files=[n+'_axi.txt'for n in ['graph','design','table','cost','qstate','label','owner','snapshot','baseline']]+['owners.bin','labels.bin','design.bin','cost.bin','snapshot.bin','pool.bin','allocator.bin','natural_trace.txt']
for n in files:assert sha(d/n)==sha(old/case/n),n
assert 'BASE_ABORT_DELAY'not in m['cases'][case]['commands'][0]['argv']
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,baseline_audit_sha256=sha(old/'source_bound_audit.json'),exact_files={n:sha(d/n)for n in files},scope='Enabled ninth-port retirement guard preserves both actual no-preload natural queries: nine AXI, seven DDR and native trace17 files/cycles exact. No warm recovery proof.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('BASELINE_FENCE_NORMAL_AUDITED',case)
