from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());dep=Path(m['sources']['fabric/access_fabric.sv']['path']).parents[2];dm=json.loads((dep/'manifest.json').read_text());g=json.loads((dep/'source_bound_audit.json').read_text())
 assert m['status']=='passed'and m['functional_manifest_sha256']==sha(dep/'manifest.json')and g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
 assert all(c['exit_code']==0 for c in m['commands'])
 for n,s in m['sources'].items():
  assert sha(out/'sources'/n)==s['sha256']
  if n in dm['sources']:assert s['sha256']==dm['sources'][n]['sha256']
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 log=(out/'simulate.log').read_text();assert m['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
 counts={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',m['result'])};cold=m['result'].startswith('ACCESS_FABRIC_COLD_PASS')
 errors={}
 for kind in ['graph','table','label']:
  lines=[s.split()for s in (out/(kind+'_axi.txt')).read_text().splitlines()]
  errors[kind+'_r_errors']=sum(r[0]=='R'and int(r[3])!=0 for r in lines);errors[kind+'_b_errors']=sum(r[0]=='B'and int(r[1])!=0 for r in lines)
 if cold:
  assert counts['cases']==2 and counts['max_service_cycles']==262129 and all(v==0 for v in errors.values())
 else:
  assert counts['faults']==counts['recoveries']==19 and counts['max_service_cycles']==32753
  assert errors['graph_r_errors']==errors['table_r_errors']==errors['label_b_errors']==1 and errors['label_r_errors']>=1
  records=[{k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',s)}for s in log.splitlines()if s.startswith('FAULT_CONTEXT ')]
  assert [r['case']for r in records]==list(range(19));assert sum(r['timeout']for r in records)==1 and records[5]['timeout']==1
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'actual_axi_errors':errors,'scope':'Default-capacity cold admission'if cold else 'Actual integrated HLS/dispatch/label/coordinate error propagation and coordinated reset recovery; owner endpoint is a model.'};(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
