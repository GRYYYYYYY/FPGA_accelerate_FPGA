from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=ROOT/'results/access_fabric_20261024';b=ROOT/'results/access_fabric_v2_20261024';am=json.loads((a/'manifest.json').read_text());bm=json.loads((b/'manifest.json').read_text())
 assert am['status']==bm['status']=='passed'
 for n,s in bm['sources'].items():
  if not n.endswith(('.sv','.v')):continue
  x=(a/'sources'/n).read_text();y=(b/'sources'/n).read_text()
  if n=='fabric/access_fabric.sv':assert x.replace('SERVICE_MAX_CYCLES=262144','SERVICE_MAX_CYCLES=(1<<HASH_BITS)+262144')==y
  else:assert x==y,n
 for case in bm['cases']:
  assert am['cases'][case]['result']==bm['cases'][case]['result']
  for name in ['observed.txt','graph_axi.txt','table_axi.txt','label_axi.txt','labels.bin']:assert sha(a/case/name)==sha(b/case/name),(case,name)
 (b/'budget_auditor.py').write_bytes(Path(__file__).read_bytes());r={'status':'passed','old_manifest_sha256':sha(a/'manifest.json'),'new_manifest_sha256':sha(b/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'design_delta':'Only default service budget = directory reset bound + operation budget','all_normal_results_cycles_and_memory_traces_identical':True};(b/'budget_change_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
