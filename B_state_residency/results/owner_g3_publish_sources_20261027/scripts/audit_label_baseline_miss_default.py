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
b=runpy.run_path(str(ROOT/'hardware/variants/label_baseline_miss_v1/build.py'))
assert b['make']()==(p/'sources/expansion_20261024/pager/pager/resident_page_manager.sv').read_text()
pg='expansion_20261024/pager/pager/paged_exclusion_engine.sv'
old=(ROOT/'hardware/variants/label_frame_export_v1'/pg).read_text()
ties=".baseline_req_valid(),.baseline_req_node(),.baseline_req_epoch(),.baseline_rsp_ready(),.baseline_permit(1'b0),.baseline_epoch(64'b0),.baseline_req_ready(1'b0),.baseline_rsp_valid(1'b0),.baseline_rsp_status(4'b0),.baseline_rsp_node(32'b0),.baseline_rsp_epoch(64'b0),.baseline_rsp_payload(160'b0),.idle(manager_idle),"
assert old.replace('.idle(manager_idle),',ties)==(p/'sources'/pg).read_text()
case=next(iter(m['cases']));d=p/case;base=p.parent/('runtime_label_snapshot_'+case+'_v3');assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
files=[n+'_axi.txt'for n in ['graph','design','table','cost','qstate','label','owner','snapshot','copy','labelsnap']]+['owners.bin','labels.bin','design.bin','cost.bin','snapshot.bin','pool.bin','allocator.bin','natural_trace.txt','runtime_labels.txt']
for n in files:assert sha(d/n)==sha(base/case/n),n
r={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'case':case,'baseline_audit_sha256':sha(base/'source_bound_audit.json'),'exact_files':{n:sha(d/n)for n in files},'scope':'ENABLE_BASELINE=0 with explicit idle sideband ties preserves full prior native runtime snapshot/G2 fault/warm recovery/retry, 10 AXI/7 DDR/native trace/label stream19 files and cycles byte-identical. Named parameter/port compatibility only.'}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('BASELINE_MISS_DEFAULT_AUDITED',case)
