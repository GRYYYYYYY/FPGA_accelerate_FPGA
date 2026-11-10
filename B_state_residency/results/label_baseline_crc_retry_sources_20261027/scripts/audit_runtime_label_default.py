from pathlib import Path
import sys,json,runpy,tempfile
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and len(m['cases'])==1
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
scan=runpy.run_path(str(p/'sources/scan_build.py'))
with tempfile.TemporaryDirectory()as tmp:
 scan['make'].__globals__['HERE']=Path(tmp);scan['make']()
 for n in scan['FILES']:assert (Path(tmp)/n).read_bytes()==(p/'sources'/n).read_bytes()
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));assert b['make_default'](ROOT/'hardware/variants/iter2_continuous_v1/build_tb.py')==(p/'sources/tb_query_fault.sv').read_text()
case=next(iter(m['cases']));d=p/case;base=p.parent/('iter2_continuous_prep_'+case+'_v1');a=json.loads((base/'source_bound_audit.json').read_text());assert a['status']=='passed'
files=[n+'_axi.txt'for n in ['graph','design','table','cost','qstate','label','owner','snapshot']]+['owners.bin','labels.bin','design.bin','cost.bin','snapshot.bin','pool.bin','allocator.bin','natural_trace.txt']
for name in files:assert sha(d/name)==sha(base/case/name),name
assert all(x['exit_code']==0 for x in m['cases'][case]['commands'])
r={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'baseline_audit_sha256':sha(base/'source_bound_audit.json'),'case':case,'exact_files':{n:sha(d/n)for n in files},'scope':'Default ENABLE_FRAME_SCAN=0 preserves prior native query180327/history-ripup baseline byte-for-byte: 8 AXI,7 DDR,full native trace and cycles. Named parameter/port compatibility only; no formal equivalence or synthesis claim.'}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('RUNTIME_LABEL_DEFAULT_AUDITED',case)
