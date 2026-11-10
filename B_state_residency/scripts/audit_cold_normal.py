"""Source-bound exact regression against independently audited capture baseline."""
from pathlib import Path
import json,sys
from run_checkpoint_authority import ROOT,sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);fixed=Path(m['production']);bm=json.loads((base/'manifest.json').read_text());fm=json.loads((fixed/'manifest.json').read_text());ba=json.loads((base/'source_bound_audit.json').read_text());fa=json.loads((fixed/'source_bound_audit.json').read_text());assert ba['status']==fa['status']=='passed'and ba['manifest_sha256']==sha(base/'manifest.json')and fa['manifest_sha256']==sha(fixed/'manifest.json')
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
for n in ['query_residency_system.sv','boot_restore_gate.sv']:assert sha(p/'sources'/n)==fm['sources'][n]['sha256']
for n,h in m['sources'].items():
 if n not in ['query_residency_system.sv','boot_restore_gate.sv','tb_query_fault.sv','runner.py']:assert h['sha256']==bm['sources'][n]['sha256']
ties=""".boot_required(1'b0),.boot_cfg_valid(1'b0),.boot_verify_valid(1'b0),.boot_rsp_ready(1'b0),.boot_design(64'd0),.boot_generation(64'd0),.boot_checkpoint(32'd0),.boot_version(32'd0),.boot_nodes(32'd0),.boot_label_count(32'd0),.boot_label_crc(32'd0),.boot_path_crc(32'd0),.boot_query_crc(32'd0),.boot_query(2'd0),.boot_slots(2'd0),.boot_price(4'd0),.boot_payload(2304'd0),"""
tb=(base/'sources/tb_query_fault.sv').read_text().replace(')system(.cp_ready',')system('+ties+'.cp_ready').replace('endmodule','always @(posedge clk)if(!k_cold_rst&&!rst)begin if(system.boot_pending||system.boot_rsp_valid)$fatal(1,"normal start entered bootstrap");end\nendmodule');assert tb==(p/'sources/tb_query_fault.sv').read_text()
assert m['rtl']==bm['rtl']+['boot_restore_gate.sv']
names=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin','natural_trace.txt','directory.txt'];report={}
if not partial:assert set(m['cases'])=={'full_5','pressure_5'}
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 d=p/name;log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and 'QUERY_FAULT_OBSERVED case=5 outcome=recovered_retry'in log
 matches={n:sha(d/n)for n in names}
 for n,h in matches.items():assert h==sha(base/name/n),(name,n)
 observed=next(l for l in log.splitlines()if l.startswith('QUERY_FAULT_OBSERVED '));old=next(l for l in(base/name/'simulate.log').read_text().splitlines()if l.startswith('QUERY_FAULT_OBSERVED '));assert observed==old
 report[name]={'status':'passed','exact_files':matches,'result':observed};print(name,'14 exact files and cycle result matched',flush=True)
r={'status':'partial'if partial else 'passed','manifest_sha256':sha(p/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'production_audit_sha256':sha(fixed/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'cases':report,'scope':'Explicit boot_required=0, two capacities, representative owner-B fault/recovery/full retry/capture fixture; byte-identical 8 AXI logs,4 DDR images,full protocol/directory traces and final cycle result. Not universal equivalence or board performance.'}
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n')
