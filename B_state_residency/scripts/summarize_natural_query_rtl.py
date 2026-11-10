from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/tmp/B_state_residency_offer_20261025/natural_query_rtl_v1')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 m=json.loads((OUT/'manifest.json').read_text());a=json.loads((OUT/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and a['manifest_sha256']==sha(OUT/'manifest.json')
 bundle=ROOT/'results/natural_query_rtl_audit_sources_20261025';source=json.loads((bundle/'manifest.json').read_text());assert source['status']=='passed'
 for name,h in source['files'].items():assert sha(bundle/Path(name).name)==sha(ROOT/name)==h
 assert a['auditor_sha256']==source['files']['scripts/audit_natural_query_rtl.py']
 r=dict(status='passed',root=str(OUT),manifest_sha256=sha(OUT/'manifest.json'),audit_sha256=sha(OUT/'source_bound_audit.json'),audit_sources_manifest_sha256=sha(bundle/'manifest.json'),completion_sha256=sha(ROOT/'results/natural_query_rtl_completion_20261025.json'),unchanged_production_RTL_dat=a['unchanged_production_RTL_dat'],counts=a['counts'],scope=a['scope'])
 (ROOT/'results/natural_query_rtl_20261025.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:{i:v[i]for i in ['outputs','commits','expands','polls','State_R','cycles']}for k,v in r['counts'].items()}))
if __name__=='__main__':main()
