from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']
 dep=ROOT/'results/metadata_v2_20261024';g=json.loads((dep/'source_bound_audit.json').read_text());assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
 assert sha(out/'sources/metadata_controller.sv')==sha(dep/'sources/metadata/metadata_controller.sv')
 assert all(c['exit_code']==0 for c in m['commands'])and [c['stage']for c in m['commands']]==['compile','elaborate','simulate']
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log and log.count('METADATA_CONTROL_PASS checks=17 errors=16 cycles=244')==1
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'checks':17,'errors':16,'cycles':244,'functional_gate_sha256':sha(dep/'source_bound_audit.json'),'scope':'Actual metadata controller with controlled graph/design replies: full descriptor snapshot, four graph echo corruptions and status, design cookie/status, active/query/price/claim drift, unowned replies, accepted read draining, completion/timeout tie and stable exposed response. AXI leaf behavior proven separately.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
