from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];P=Path('/tmp/B_state_residency_offer_20261025/parent_physical_v2')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 m=json.loads((P/'manifest.json').read_text());a=json.loads((P/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed' and a['manifest_sha256']==sha(P/'manifest.json')
 for name,h in m['artifacts'].items():assert sha(P/name)==h
 for name,h in m['sources'].items():assert sha(P/name)==h
 out=dict(status='passed',root=str(P),audit_sha256=sha(P/'source_bound_audit.json'),cases=a['cases'],delta=a['delta'],scope=a['scope'],limitations=a['limitations'])
 (ROOT/'results/parent_physical_20261025.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status='passed',delta=out['delta'])))
if __name__=='__main__':main()
