from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and not m['baseline_expected_failure']
 base=Path('/tmp/B_state_residency_commit_20261025/pilot_v2');bm=json.loads((base/'manifest.json').read_text());assert m['base_manifest_sha256']==sha(base/'manifest.json') and sha(out/'runner.py')==m['runner_sha256']
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h==bm['sources'][n]['sha256']
 assert set(m['cases'])=={'1','2'}
 for mode,cm in m['cases'].items():
  assert cm['status']=='passed' and all(c['exit_code']==0 for c in cm['commands']);d=out/('mode'+mode)
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text();assert f'COMMIT_BAD_COST_GUARD_PASS mode={mode} accepted=0'in log and 'Fatal:'not in log
  assert (d/'commit_order.txt').read_text()=='' and (d/'commit_observed.txt').read_text()==''
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':2,'cost_label_requests_accepted':0,'scope':'Actual joined RTL with forced malformed cost identity/status before admission; all cost commit signals stay idle. Prefix prev/CLEAR side effects may already exist. Not actual AXI failure or coordinated recovery.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
