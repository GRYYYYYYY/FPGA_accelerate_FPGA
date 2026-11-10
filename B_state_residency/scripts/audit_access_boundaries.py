from pathlib import Path
import hashlib,json,re,itertools
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/access_boundaries_20261024';dep=ROOT/'results/access_service_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'and m['functional_manifest_sha256']==sha(dep/'manifest.json')
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 counts={}
 for name,cm in m['cases'].items():
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands']);d=out/name
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  counts[name]={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
 lines=(out/'tb_access_memory_call/collector_cases.txt').read_text().splitlines();orders=[tuple(map(int,s.split()[1:]))for s in lines if s.startswith('ORDER ')];assert len(orders)==720 and set(orders)==set(itertools.permutations(range(6)))
 assert [int(s.split()[1])for s in lines if s.startswith('FAULT ')]==list(range(18))and lines[-1]=='END 720 18'
 assert counts['tb_access_boundaries']['cases']==122 and counts['tb_access_boundaries']['reset_offsets']==96 and counts['tb_access_boundaries']['resets']==217
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'scope':'Actual access HLS + resident controller errors/reset; collector mock output permutation/protocol tests. Dynamic services are models, not physical label/coordinate/occupancy integration.'};(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
