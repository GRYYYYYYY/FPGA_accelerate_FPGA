"""Audit direct generated-RTL reset, pending-phase and terminal fault recovery."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/children_reset_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 gate=Path(m['hls_gate']['path']);assert sha(gate)==m['hls_gate']['sha256'];g=json.loads(gate.read_text());assert g['status']=='passed' and g['manifest_sha256']==sha(gate.parent/'manifest.json')
 for name,spec in m['sources'].items():
  assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
  if name.endswith('.v'):assert g['cases']['32']['generated_rtl_artifacts'][name]==spec['sha256']
 assert sha(out/'runner.py')==m['runner_sha256']==sha(ROOT/'scripts/verify_children_reset.py')
 assert [x['stage']for x in m['commands']]==['compile','elaborate','simulate'] and all(x['exit_code']==0 for x in m['commands'])
 compiled={Path(x).name for x in m['commands'][0]['argv']if x.endswith(('.sv','.v'))};assert compiled==set(m['sources'])
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest
 log=(out/'simulate.log').read_text();marker='CHILDREN_RESET_PASS phases=8 resets=11 calls=63 fault_recovery=1 high_boundary=1'
 assert log.count(marker)==1 and 'Fatal:' not in log and 'Error:' not in log and '$finish called' in log
 assert (out/'run.tcl').read_text()=='run 100us\nquit\n'
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'hls_audit_sha256':sha(gate),'auditor_sha256':sha(Path(__file__)),'result':marker,'scope':'Actual generated state-reset gen32 RTL, pending service phases0..7, latched service fault, empty publish and 24-bit highest parent/child. Coordinated quiescent cold reset only; no hot cancel/old-message isolation or external side-effect rollback.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
