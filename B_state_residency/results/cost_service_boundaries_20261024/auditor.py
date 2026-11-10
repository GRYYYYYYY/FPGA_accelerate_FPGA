"""Audit actual arithmetic stop/recovery behavior and freeze all evidence."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/cost_service_boundaries_20261024';m=read(out/'manifest.json')
 assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path'])),name
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest,name
 assert sha(out/'runner.py')==m['runner_sha256']
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 gate=Path(m['hls_gate']['path']);assert sha(gate)==m['hls_gate']['sha256'] and read(gate)['status']=='passed'
 sim=ROOT/'results/cost_service_v2_20261024';sg=read(sim/'source_bound_audit.json')
 assert sg['status']=='passed' and sg['manifest_sha256']==sha(sim/'manifest.json')
 for name in ['cost_memory_call.sv','cost_service.sv']:assert sha(out/'sources'/name)==sha(sim/'sources'/name)
 offsets=[0,1,2,20,50,100,200,400,600,680,720];cases=[];late=0;timeouts=0
 for line in (out/'boundaries.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='FAULT':
   mode,offset,had=map(int,v[1:]);assert had in (0,1);cases.append((mode,offset));late+=had
  elif v[0]=='TIMEOUT':assert v[1]=='8';timeouts+=1
  else:assert v==['END','45',str(late),'44']
 assert cases==[(mode,offset) for mode in range(4)for offset in offsets] and timeouts==1 and 0<late<44
 log=(out/'cost_service_boundaries.log').read_text()
 assert not re.search(r'Fatal:|ERROR:',log) and '$finish called' in log
 assert f'COST_SERVICE_BOUNDARIES_PASS fault_cases=45 late_cases={late} recovered=44 single_cycle_reset=1' in log
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),
  'fault_cases':45,'active_cases':44-late,'late_reply_cases':late,'post_reset_correct_calls':44,
  'single_cycle_reset':True,'actual_short_timeout':8,'fault_hold_cycles':1030,
  'scope':'Actual frozen exact_v2 arithmetic, abort/query/price/inactive at 11 offsets and short timeout. Cold reset recovery, not board or complete router.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
