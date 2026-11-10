"""Verify preserved integration counterexamples and explicitly stopped launch."""
from pathlib import Path
import json,sys
from run_checkpoint_authority import sha

def main():
 p=Path(sys.argv[1]).resolve();cases={}
 for n in ['authority_query_v1','authority_query_v2','authority_query_retry_v2','authority_query_retry_v1']:
  d=p/n;m=json.loads((d/'manifest.json').read_text())
  for name,h in m['sources'].items():assert sha(d/'sources'/name)==h['sha256']
  if n=='authority_query_v1':
   log=(d/'build_full/compile.stdout.log').read_text();assert "'as_attempt_reset' is already implicitly declared"in log and "'as_cfg_lease' is already implicitly declared"in log;assert m['status']=='failed';meaning='Compile failure from declaration order; no functional simulation claim.'
  elif n in ['authority_query_v2','authority_query_retry_v2']:
   log=(d/'full_5/simulate.log').read_text();assert 'Fatal: system target reset before authority retired'in log and m['status']=='failed'
   rtl=(d/'sources/query_residency_system.sv').read_text();lower=(d/'sources/residency_system.sv').read_text();trace=(d/'full_5/natural_trace.txt').read_text()
   if n=='authority_query_v2':assert '.rst(rst||k_cold_rst),.abort'in rtl and 'AS_REARM'not in trace;meaning='Real first target reset would reset immutable authority, violating retirement/binding lifetime.'
   else:assert '.rst(k_cold_rst),.abort'in rtl and '.normal_retired(f_normal_retired&&as_retired)'not in lower and 'AS_REARM'in trace and 'AS_FAIL'in trace;meaning='Real rearm followed by early target reset; coordinator waited for AXI drain but not private-service retirement.'
  else:
   record=json.loads((p/'stopped_launch.json').read_text());assert record['root']==n and record['reason']=='wrong TB selected before authority-fault patch';tb=(d/'sources/tb_query_fault.sv').read_text();assert '.inject_r(as_inject)'not in tb;meaning='Explicitly SIGTERM stopped wrong fault-test launch. Original status is not completion evidence.'
  cases[n]={'status':'verified_development_evidence','meaning':meaning,'manifest_sha256':sha(d/'manifest.json')}
 a={'status':'passed','experiment_status':'counterexamples_or_stopped_not_success','cases':cases,'files':{str(q.relative_to(p)):sha(q)for q in sorted(p.rglob('*'))if q.is_file()and q.name!='source_bound_audit.json'},'auditor_sha256':sha(Path(__file__))}
 (p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'status':'passed','cases':list(cases)}))
if __name__=='__main__':main()
