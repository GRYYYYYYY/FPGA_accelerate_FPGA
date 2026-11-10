from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']
 dep=ROOT/'results/access_owner_v3_20261024';g=json.loads((dep/'source_bound_audit.json').read_text());assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
 assert sha(out/'sources/owner_bridge.sv')==sha(dep/'sources/owners/owner_bridge.sv')
 assert [c['stage']for c in m['commands']]==['compile','elaborate','simulate']and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();assert log.count('OWNER_BRIDGE_PASS checks=15 fault_cases=12 cycles=177')==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'integrated_gate_sha256':sha(dep/'source_bound_audit.json'),'checks':15,'fault_cases':12,'cycles':177,'scope':'Actual bridge RTL against controlled backend: captured full identity, kind4/6 result mapping, backend cookie/status, query/price/lock drift, invalid owner/kind, timeout/late abort, host arbitration and unowned reply. Controlled backend is not AXI hardware; integrated functional gate separately uses actual owner store.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
