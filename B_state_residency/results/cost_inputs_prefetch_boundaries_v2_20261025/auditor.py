from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 assert sha(out/'runner.py')==m['runner_sha256']
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();assert 'COST_INPUTS_PREFETCH_PASS valid=1024 invalid=12 fault_cases=13'in log and 'Fatal:'not in log and '$finish called'in log
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),
 'controller_sha256':m['sources']['cost_inputs_prefetch.sv']['sha256'],'valid':1024,'invalid_indices':12,'fault_cases':13,
 'scope':'Standalone read-controller mocks, refs 0/1/7/65535 x occupancy0..258, full version/host/index/cookie failures, owner failures, identity/abort/timeout and held request/result; not joined AXI recovery'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
