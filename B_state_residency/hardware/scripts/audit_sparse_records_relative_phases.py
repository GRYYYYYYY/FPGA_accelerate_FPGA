"""Independently audit paired, deterministic phase-sensitivity pilot runs."""
from pathlib import Path
import json,hashlib,re
from make_sparse_records_relative_phases_tb import render,PHASES
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def term(t):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
def main():
 out=ROOT/'results/sparse_records_relative_phases_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 base=ROOT/'results/sparse_records_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert sha(base/'source_bound_audit.json')==m['pilot_audit_sha256'] and json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(ROOT/'hardware/scripts/run_sparse_records_relative_phases.py')==m['runner_sha256']
 assert sha(ROOT/'hardware/scripts/make_sparse_records_relative_phases_tb.py')==m['tb_generator_sha256']
 tbname='tb_sparse_records_relative_phases.sv';tbhash=hashlib.sha256(render().encode()).hexdigest();comparisons=[]
 vec=ROOT/'results/small_checkpoint_vectors_pilot_20261023';vm=json.loads((vec/'manifest.json').read_text());assert vm['status']=='passed'
 for name in ['actual.txt','pages.hex']:assert sha(vec/name)==vm['artifacts'][name]
 for phase in PHASES:
  for label in ('control','candidate'):
   name=f'{label}{phase}';d=out/name;row=m['cases'][name]
   expected={k:v for k,v in bm['cases'][label]['sources'].items() if not k.startswith('tb_')}|{tbname:tbhash}
   assert row['status']=='passed' and row['phase']==phase and row['label']==label and row['sources']==expected
   for filename,digest in expected.items():assert sha(d/'sources'/filename)==digest
   cmds=row['commands'];assert [s['stage'] for s in cmds]==['compile','elaborate','simulate'] and all(s['exit_code']==0 for s in cmds)
   assert set(Path(x) for x in cmds[0]['argv'] if x.endswith('.sv'))=={d/'sources'/filename for filename in expected}
   assert cmds[1]['argv'][1]==f'tb_sparse_records_relative_phase_{label}{phase}'
   assert cmds[2]['argv'][6:]==bm['cases'][label]['commands'][-1]['argv'][6:]
   log=(d/'simulate.log').read_text();old=(base/label/'simulate.log').read_text()
   assert sha(d/'simulate.log')==row['log_sha256'] and 'Fatal:' not in log and '$finish' in log
   for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
    strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
    assert strip(log)==strip(old)
   counts,previous=term(log),term(old);retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
   assert row['counts']==counts and row['finish_retries']==retries and counts['checks']==75194+retries
   assert counts.keys()==previous.keys() and all(counts[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
   for direction,fields in [('WB',['exports','omitted','masks']),('RF',['beats','omitted','masks'])]:
    match=re.search('SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),log);assert match
    assert row[direction.lower()+'_counts']==dict(zip(fields,map(int,match.groups())))==bm['cases'][label][direction.lower()+'_counts']
   assert row['end_ns']==int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
   if phase==0:
    assert row['end_ns']==bm['cases'][label]['end_ns']
    for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint','FINISH_RETRY_COUNTS']:
     assert re.findall('^'+prefix+r' (.+)$',log,re.M)==re.findall('^'+prefix+r' (.+)$',old,re.M)
  c=m['cases'][f'control{phase}']['end_ns'];n=m['cases'][f'candidate{phase}']['end_ns']
  comparisons.append({'phase':phase,'control_end_ns':c,'candidate_end_ns':n,'incremental_reduction_fraction':1-n/c})
 assert comparisons==m['phase_comparisons']
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'queries_per_case':19,'cases':6,'comparisons':comparisons,'scope':'Eight queue/AXI readiness expressions use distinct offset multipliers1,3,5,7,11,13,17,19; channel-relative phases vary. Fixed host4cycle checking. Deterministic3-schedule sensitivity, no random-confidence/general platform/board claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
