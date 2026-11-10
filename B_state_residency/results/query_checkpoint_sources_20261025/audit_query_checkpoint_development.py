from pathlib import Path
import json,sys
from run_checkpoint_authority import sha

def main():
 p=Path(sys.argv[1]).resolve();cases={}
 for i in range(1,6):
  d=p/('query_checkpoint_v'+str(i));m=json.loads((d/'manifest.json').read_text())
  for n,h in m['sources'].items():assert sha(d/'sources'/n)==h
  for n,h in m['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text()
  if i==2:
   assert m['status']=='failed'and 'Fatal: cp status  0/          1'in log
   rtl=(d/'sources/query_lifecycle.sv').read_text();tb=(d/'sources/tb_query_checkpoint.sv').read_text();assert 'label_state_dirty&&!cp_stage[7][7]'not in rtl and 'saved_image;image[8]=3;load_cp(1);'in tb
   meaning='Actual old-clean snapshot accepted and cleared dirty; new test expected rejection and stopped.'
  else:
   assert m['status']=='passed'and 'QUERY_CHECKPOINT_PASS'in log and 'Fatal:'not in log
   meaning='Intermediate behavioral test pass; superseded by selected unit with full stream oracle and boundary tests.'
   if i==4:assert 'if(cp_busy&&(dut.cp_drift||abort||backend_fault))'in(d/'sources/tb_query_checkpoint.sv').read_text();meaning+=' Initial independent audit rejected ENV logger retirement id ambiguity; selected logger suppresses DONE observations.'
  cases[d.name]={'manifest_sha256':sha(d/'manifest.json'),'experiment_status':m['status'],'meaning':meaning}
 own=p/'source_bound_audit.json';a={'status':'passed','scope':'Preserved intermediate test results and real dirty-rollback counterexample, not selected proof','cases':cases,'files':{str(q.relative_to(p)):sha(q)for q in sorted(p.rglob('*'))if q.is_file()and q!=own},'auditor_sha256':sha(Path(__file__))}
 own.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'status':'passed','cases':len(cases)}))
if __name__=='__main__':main()
