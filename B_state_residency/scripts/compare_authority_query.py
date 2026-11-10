from pathlib import Path
import json,sys
from run_checkpoint_authority import sha,ROOT

def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text());assert m['status']=='observed'and a['status']=='passed'and not m.get('authority_fault')
 base=ROOT/'results/route_checkpoint_fault_regression_v1';cases={}
 for mode in ['full_5','pressure_5']:
  ns=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','owners.bin','labels.bin','cost.bin','design.bin'];h={}
  for n in ns:assert sha(p/mode/n)==sha(base/mode/n);h[n]=sha(p/mode/n)
  cases[mode]=h
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'reference_manifest_sha256':sha(base/'manifest.json'),'files_compared':22,'cases':cases,'scope':'All seven original AXI logs and four complete final images byte-identical to owner-B fault baseline; extra snapshot AXI is separate. Not cycle-trace equivalence or performance claim.','script_sha256':sha(Path(__file__))}
 (p/'baseline_comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','files_compared':22}))
if __name__=='__main__':main()
