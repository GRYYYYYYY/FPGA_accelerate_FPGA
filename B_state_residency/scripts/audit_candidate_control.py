"""Bind the reproduced negative and controlled reply fault tests to their RTL."""
from pathlib import Path
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 assert all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log
 hits=[s for s in log.splitlines()if s.startswith('CANDIDATE_CONTROL_PASS ')];assert hits==[m['result']]
 counts={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',hits[0])};assert counts=={'checks':268,'errors':27,'cycles':419}
 negative=ROOT/'results/candidate_control_negative_20261024';old=(negative/'simulate.log').read_text();assert 'Fatal: final must await accepted metadata reply drain state=6'in old
 oldrtl=negative/'sources/candidate_controller.sv';assert sha(oldrtl)!=sha(out/'sources/candidate_controller.sv')
 original=ROOT/'results/candidate_pipeline_full_20261024/sources/candidate/candidate_controller.sv';assert sha(original)==sha(oldrtl)
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'counts':counts,'auditor_sha256':sha(Path(__file__)),'negative_log_sha256':sha(negative/'simulate.log'),'negative_rtl_sha256':sha(oldrtl),'negative_status':'verified terminal failing XSim run; original runner left manifest running after its missing-PASS assertion','scope':'Candidate controller with controlled leaf replies: accepted metadata/access drain, echoes, drift/timeout, error/final tie, stable exposed responses, unowned replies, invalid input and reset per case. Not AXI fault injection or interconnect drain proof.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
