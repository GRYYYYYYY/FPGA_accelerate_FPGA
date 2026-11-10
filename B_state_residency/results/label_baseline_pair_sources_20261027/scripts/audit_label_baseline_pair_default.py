from pathlib import Path
import sys,json,runpy
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and m['disabled']and len(m['cases'])==1
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));b['make_disabled'].__globals__['PAIR']=ROOT/'hardware/variants/iter2_pair_v1/build_tb.py';assert b['make_disabled']()==(p/'sources/tb_query_fault.sv').read_text()
f=runpy.run_path(str(p/'sources/baseline_build.py'));f['make'].__globals__['ROOT']=ROOT
for n,t in f['make']().items():assert t==(p/'sources'/n).read_text()
case=next(iter(m['cases']));d=p/case;old=p.parent/('iter2_pair_'+case+'_v1');assert json.loads((old/'source_bound_audit.json').read_text())['status']=='passed'
files=[n+'_axi.txt'for n in ['graph','design','table','cost','qstate','label','owner','snapshot']]+['owners.bin','labels.bin','design.bin','cost.bin','snapshot.bin','pool.bin','allocator.bin','natural_trace.txt']
for n in files:assert sha(d/n)==sha(old/case/n),n
assert not (d/'baseline_axi.txt').exists()
log=(d/'simulate.log').read_text();assert 'ITER2_PAIR_PASS polls=114 expands=113 candidates=564 costs=302'in log and 'Fatal:'not in log and '$finish called'in log
out=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,baseline_audit_sha256=sha(old/'source_bound_audit.json'),exact_files={n:sha(d/n)for n in files},scope='New seven-level sideband/parameter propagation with ENABLE_BASELINE=0, full two-query original preload baseline16 files and cycles exact. Does not prove enabled path.')
(p/'source_bound_audit.json').write_text(json.dumps(out,indent=2)+'\n');print('BASELINE_PAIR_DEFAULT_AUDITED',case)
