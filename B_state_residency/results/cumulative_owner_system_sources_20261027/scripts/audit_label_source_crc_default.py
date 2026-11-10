from pathlib import Path
import sys,json,runpy,tempfile
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and len(m['cases'])==1
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));assert b['make_default'](ROOT/'hardware/variants/label_frame_export_v1/build_tb.py')==(p/'sources/tb_query_fault.sv').read_text()
c=runpy.run_path(str(p/'sources/crc_build.py'))
with tempfile.TemporaryDirectory()as tmp:
 c['make'].__globals__['HERE']=Path(tmp);c['make']()
 for n in ['label_restore_controller.sv']+c['PARENTS']:assert (Path(tmp)/n).read_bytes()==(p/'sources'/n).read_bytes()
case=next(iter(m['cases']));d=p/case;base=p.parent/('runtime_label_snapshot_'+case+'_v3');assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
files=[n+'_axi.txt'for n in ['graph','design','table','cost','qstate','label','owner','snapshot','copy','labelsnap']]+['owners.bin','labels.bin','design.bin','cost.bin','snapshot.bin','pool.bin','allocator.bin','natural_trace.txt','runtime_labels.txt']
for n in files:assert sha(d/n)==sha(base/case/n),n
r={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'case':case,'baseline_audit_sha256':sha(base/'source_bound_audit.json'),'exact_files':{n:sha(d/n)for n in files},'scope':'CHECK_LABEL_CRC=0 preserves full prior native runtime snapshot/G2 fault/warm recovery/retry, 10 AXI/7 DDR/native trace/label stream19 files and cycles byte-identical. Named parameter/port compatibility only.'}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('LABEL_SOURCE_CRC_DEFAULT_AUDITED',case)
