"""Bind the isolated selection change to the complete CPU-audited search execution."""
from pathlib import Path
import json,hashlib,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();base=ROOT/'results/search_scheduler_join_v1';m=json.loads((out/'manifest.json').read_text());bm=json.loads((base/'manifest.json').read_text());a=json.loads((base/'source_bound_audit.json').read_text())
 assert m['status']==bm['status']==a['status']=='passed' and a['manifest_sha256']==sha(base/'manifest.json')
 assert set(m['sources'])==set(bm['sources']);same=0
 for n,v in m['sources'].items():
  assert sha(out/'sources'/n)==v['sha256'];assert sha(base/'sources'/n)==bm['sources'][n]['sha256']
  if n not in ['runner.py','search_host_fence.sv']:assert v['sha256']==bm['sources'][n]['sha256'];same+=1
 assert sha(out/'sources/runner.py')==sha(ROOT/'scripts/run_search_sparse_join.py')
 p=ROOT/'hardware/variants/search_sparse_v3/build.py';sp=importlib.util.spec_from_file_location('builder',p);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);assert b.make().encode()==(out/'sources/search_host_fence.sv').read_bytes()
 assert sha(out/'sources/search_host_fence.sv')==sha(ROOT/'hardware/variants/search_sparse_v3/search_host_fence.sv')
 for n,v in m['scoreboards'].items():assert sha(out/n)==v==bm['scoreboards'][n]
 for k in ['input_manifest_sha256','base_manifest_sha256','base_audit_sha256','oracle_audit_sha256','graph_audit_sha256','q2_audit_sha256','q2_cost_audit_sha256']:assert m[k]==bm[k]
 assert set(m['cases'])==set(bm['cases'])=={'full','pressure'};cases={}
 for case,c in m['cases'].items():
  assert c['status']=='passed'and len(c['commands'])==3 and all(x['exit_code']==0 for x in c['commands'])
  assert c['result']==bm['cases'][case]['result']
  for n,h in c['artifacts'].items():assert sha(out/case/n)==h
  hashes={}
  for n in ['natural_trace.txt']+[x+'_axi.txt'for x in ['graph','design','label','owner','cost','qstate','table']]+['design.bin','owners.bin','labels.bin','cost.bin']:
   h=sha(out/case/n);assert h==sha(base/case/n)==bm['cases'][case]['artifacts'][n],(case,n);hashes[n]=h
  log=(out/case/'simulate.log').read_text();assert c['result']in log and '$finish called'in log and 'Fatal:'not in log
  cases[case]=dict(result=c['result'],byte_identical=hashes)
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),builder_sha256=sha(p),reference_audit_sha256=sha(base/'source_bound_audit.json'),reference_manifest_sha256=sha(base/'manifest.json'),unchanged_sources_including_tb=same,cases=cases,scope='Static response selection plus search request injection restricted to four scheduler service lanes, while host retains all16 services; complete per-cycle trace, seven AXI logs and four full images equal independently CPU/memory/protocol-audited reference. No new search faults/unknown pages/board performance evidence.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','same_sources':same,'cases':list(cases)}))
if __name__=='__main__':main()
