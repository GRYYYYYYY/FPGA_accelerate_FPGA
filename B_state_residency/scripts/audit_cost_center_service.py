"""Bind actual service observations to unchanged frozen HLS vectors and RTL."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text())
 assert m['status']=='passed'
 gate=Path(m['hls_gate']['path']);assert sha(gate)==m['hls_gate']['sha256']
 g=json.loads(gate.read_text());hls=gate.parent;hm=json.loads((hls/'manifest.json').read_text())
 assert g['status']=='passed' and g['manifest_sha256']==sha(hls/'manifest.json')
 assert sha(out/'vectors.txt')==m['vectors_sha256']==hm['vectors_sha256']
 assert sha(out/'runner.py')==m['runner_sha256']
 for name,item in m['sources'].items():
  assert sha(out/'sources'/name)==item['sha256']==sha(Path(item['path'])),name
  if '/syn/verilog/' in item['path']:
   rel=str(Path(item['path']).relative_to(hls));assert item['sha256']==hm['generated_rtl_artifacts'][rel]
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest,name
 for c in m['commands']:assert c['exit_code']==0
 for name,marker in [('cost_center_memory_call','COST_CENTER_MEMORY_CALL_PASS cases=16'),('cost_center_service','COST_CENTER_SERVICE_PASS vectors=110397 reset_abort_offsets=120')]:
  log=(out/(name+'.log')).read_text();assert marker in log and '$finish called' in log
  assert not any(s in log for s in ['Fatal:','ERROR:'])
 vectors=[[int(w,16) for w in line.split()] for line in (out/'vectors.txt').read_text().splitlines()]
 observed=[[int(w,16) for w in line.split()] for line in (out/'observed.txt').read_text().splitlines()]
 assert len(vectors)==len(observed)==110397
 for i,(v,o) in enumerate(zip(vectors,observed)):assert len(v)==6 and o==v[4:],i
 a={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),
 'vectors':len(vectors),'output_words':2*len(vectors),'observed_sha256':sha(out/'observed.txt'),
 'mock_protocol_cases':16,'actual_core_reset_abort_offsets':120,
 'scope':'Standalone actual generated RTL plus center collector; full version and query identity; snapshot, backpressure, synchronous shared reset and abort-stop.',
 'not_verified':['Joined candidate ownership/lease','Live post-prev geometry','23-word cost packet production','Independent core-only reset','Board timing or acceleration']}
 (out/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
if __name__=='__main__':main()
