from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/coordinate_boundaries_20261024';dep=ROOT/'results/coordinate_service_v2_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'and m['functional_manifest_sha256']==sha(dep/'manifest.json')
 for name,s in m['sources'].items():assert sha(out/'sources'/name)==s['sha256']==sha(Path(s['path']))
 cases={}
 for name,cm in m['cases'].items():
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands']);d=out/name
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  cases[name]={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
 assert cases['coordinate_controller']['cases']==40 and cases['geometry_table_reader']['cases']==17
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());report={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':cases,'scope':'Actual frozen controller and table reader; mocked service boundaries. Token3/timeout64. Integrated real-memory fault injection not covered.'};(out/'source_bound_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
